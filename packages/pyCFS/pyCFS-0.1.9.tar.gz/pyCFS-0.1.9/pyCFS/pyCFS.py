"""
pyCFS.pyCFS
==========
pyCFS is an automation and data processing library for the `openCFS <https://opencfs.org/>`_ software. It enables the user to build an abstraction
layer around the openCFS simulation which means that the user can execute simulations directly from a python script or notebook without worrying
about the individual simulation files.
"""

import os
from os import path
import subprocess
import re
import time
from glob import glob
from tqdm.auto import tqdm
from multiprocessing import Pool
import numpy as np
import numpy.typing as npt
from scipy.io import mmread
from typing import List, Callable, Optional, Tuple, TypeAlias, Dict
import shutil
from itertools import chain

from .util.lib_types import (
    pyCFSparamVec,
    pyCFSparam,
    nestedResultDict,
    resultVec,
    resultDict,
    sensorArrayResult,
)
from pyCFS.data.io import CFSReader, CFSWriter, CFSRegData, CFSResultArray, CFSResultContainer
from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
import pyCFS.util.consts as const
from pyCFS.data import v_def


class pyCFS:
    def __init__(
        self,
        project_name: str,
        cfs_install_dir: str,
        cfs_params_names: List[str] = [],
        material_params_names: List[str] = [],
        trelis_params_names: List[str] = [],
        trelis_version: str = "trelis",
        proj_root_path: str = ".",
        templates_dir: str = "templates",
        init_file_extension: str = "init",
        mat_file_name: str = "mat",
        n_threads: int = 1,
        res_manip_fun: Optional[Callable[["pyCFS"], None]] = None,
        quiet_mode: bool = False,
        detail_mode: bool = False,
        clean_finish: bool = False,
        save_hdf_results: bool = False,
        array_fill_value: pyCFSparam = np.nan,
        parallelize: bool = False,
        remeshing_on: bool = False,
        n_jobs_max: int = 1000,
        testing: bool = False,
        track_quantities: List[str] = ["all"],
        track_regions: List[str] = ["all"],
        track_quantities_hist: List[str] = ["all"],
        dump_results: bool = False,
        sensor_arrays: List[Dict[str, str]] = [],
        verbosity: int = 0,
    ):
        """

        OpenCFS and Trelis/CoreformCubit python interfacing package. The main
        goal of this module is to make an easy to use interface which provides
        a class that handles the automatic simulation setup from given CFS and
        Trelis parameters and the result storage.

        Args:
            project_name (str): Name of the simulation project (needs to be
            the same as the .xml file name)

            cfs_install_dir (str): Install path of CFS.

            cfs_params_names (list): List of trelis parameter names as defined in
                                        the associated .jou file.

            material_params_names (list): List of trelis parameter names as defined in
                                        the associated .jou file.

            trelis_params_names (list): List of trelis parameter names as defined in
                                        the associated .jou file.

            additional_param_fun (Callable): Handle to a function which modifies the
                                           additional parameters.

            additional_file_name (str): Additional file containing parameters changed
                                       by the additional_param_fun.

            trelis_version (str, optional): If 'coreform_cubit' is installed use it
                                            so that the correct one is run. Defaults
                                            to 'trelis'.

            parallelize (bool): Flag which chooses whether to parallelize the runs for
                                the given parameter matrices. Defaults to False.

            n_jobs_max (int): Max number of jobs to constrain the pool manager. Defaults
                              to inf.

            templates_dir (str, optional): Path to template files. Defaults to "templates".

            proj_root_path (str, optional): Project path. Defaults to "./".

            init_file_extension (str): Extension added to project_name to identify
                                     init files which are used as templates.

            mat_file_name (str): Material file name. (default = "mat")

            n_threads (int): Number of threads to be used by OpenCFS. (default = 1).

            quiet_mode (bool): Turns a more conservative OpenCFS output on. (default = false).

            detail_mode (bool): Write detailed OpenCFS output to file. (default = false).

            clean_finish (bool): Delete all generated simulation files. Does not touch
                                result files. Defaults to False.

            testing (bool): If true will indicate to not create any directories or leave
                            footprints. Used for clean automated testing.

            track_quantities (List[str], optional): List of results which are to be tracked from
                                                 the main hdf file. If `None` then no results
                                                 are tracked. If 'all' then all results are tracked.
                                                 Else one can select individual results by name.
                                                 (default = None).

            dump_results (bool, optional): If True then after each run the tracked results are
                                           saved to disk. (default = False).

            sensor_arrays (List[Dict[str, str]], optional) : List containing dictionaries which
            consist of two entries "file_path" denoting the path to the sensor array csv file
            (',' delimiter) containing the positions of the sensors and the entry "result_name"
            denoting the name of this sensor array which is also used within the simulation xml
            file.
        """

        self.pyCFSobj: TypeAlias = pyCFS

        # Set init params from args :
        self.project_name = project_name
        self.proj_root_path = proj_root_path
        self.cfs_install_dir = cfs_install_dir
        self.templates_dir = templates_dir
        self.n_threads = n_threads
        self.quiet_mode = quiet_mode
        self.detail_mode = detail_mode
        self.clean_finish = clean_finish
        self.save_hdf_results = save_hdf_results
        self.array_fill_value = array_fill_value
        self.parallelize = parallelize
        self.remeshing_on = remeshing_on
        self.n_jobs_max = n_jobs_max
        self.mat_file_name = mat_file_name
        self.init_file_extension = init_file_extension
        self.res_manip_fun = res_manip_fun
        self.trelis_version = trelis_version
        self.testing = testing
        self.track_quantities = track_quantities
        self.track_quantities_hist = track_quantities_hist
        self.track_regions = track_regions
        self.dump_results = dump_results
        self.sensor_arrays = sensor_arrays
        self.verbosity = verbosity

        self.trelis_params_names = trelis_params_names
        self.n_trelis_params = len(trelis_params_names)

        self.mat_params_names = material_params_names
        self.n_mat_params = len(material_params_names)

        self.cfs_params_names = cfs_params_names
        self.n_cfs_params = len(cfs_params_names)

        self.n_params = self.n_cfs_params + self.n_mat_params + self.n_trelis_params
        self.params = np.zeros((self.n_params,)).reshape(1, -1)

        # Initialize operating system dependent setups :
        self._init_os_defs()

        # Initialize placeholders :
        self._init_placeholders()

        # # Set up paths and folder structure for results :
        self._init_paths()

        # # finalize parameter setup :
        self._init_param_setup()

        # # Generate file names :
        self._init_file_names()

        # Set functions -> less branches in code :
        self._init_functions()

        # Init templates for files :
        self._init_templates_variables()

        # Init sensor array setup :
        # self._init_sensor_array_setup()
        self._init_sensor_arrays_if_exist()

        # Print status report :
        self._print_init_status_report()

    def __call__(
        self, X: pyCFSparamVec, mesh_only: bool = False, mesh_present: bool = False, export_matrices: bool = False
    ) -> None:
        """

        Simulation forward function. Performs the simulation for the passed
        parameter combinations. Does not return anything as the results are
        stored in the self.results dictionary.

        Args:
            self (pyCFS): PyCfs class object.

            X (pyCFSparamVec): N x M Array containing the simulation parameters. Here
                            the M is the number of parameters in total.

            mesh_only (bool): If true only mesh files are generated for the
                             given parameters. (default = False).

            export_matrices (bool): If true, each time a simulation is run, the system
                            matrix, rhs and sol vectors are written out and saved. (This
                            is currently only working in serial mode!)
        Returns:
            None
        """

        self._set_mesh_present_status(mesh_present)

        # adapts the simulation xml file such that the system matrices
        # and vectors are written out from CFS
        self._set_export_system_matrices(export_matrices, sim_name_id=self.project_name)

        # check parameter shape :
        self._check_given_params(X)

        # run meshing only if True :
        if mesh_only:
            self._generate_meshes(X)

        # else run whole pipeline :
        else:

            # record start time :
            self._record_time(const.LAST_EXEC_START)

            self._forward(X)  # type: ignore[attr-defined]

            # record finish time :
            self._record_time(const.LAST_EXEC_STOP)

            # dump results if on :
            self._contruct_run_metadata(X)
            self._dump_results_if_on()

            # print run status report :
            self._print_run_status_report()

    # * ------------------ Init methods ------------------
    def _init_os_defs(self) -> None:
        self.machine_os = os.name
        self.is_unix = True

        if self.machine_os is const.WIN_ID:
            self.is_unix = False

    def _init_placeholders(self) -> None:
        self.files: List[str] = []
        self.sim_files: List[str] = []
        self.params_changed: npt.NDArray[np.bool_] = np.ones((const.N_PARAM_GROUPS,), dtype=bool)

        self._init_results()
        self.results_keys: List[str] = []
        self.matrix_exports: List[resultDict] = []
        self.result_regions: Optional[List[str]] = None
        self.ind: int = 0
        self.mesh_present: bool = False
        self.time: Dict[str, str] = {
            const.LAST_EXEC_START: "",
            const.LAST_EXEC_STOP: "",
            "init_time": time.ctime(time.time()),
        }
        self.result_dump_path: str = ""
        self.topopt_regions_data: Optional[CFSRegData] = None  # noqa

    def _init_paths(self) -> None:
        """

        Initializes path variables and generates result paths if not present.

        """

        self.hdf_res_path = path.join(self.proj_root_path, const.RESULTS_HDF_DIR, self.project_name) + path.sep
        self.hdf_file_path = path.join(
            self.proj_root_path, const.RESULTS_HDF_DIR, f"{self.project_name}.{const.CFS_EXT}"
        )
        self.logs_path = path.join(self.proj_root_path, const.LOGS_DIR) + path.sep
        self.history_path = path.join(self.proj_root_path, const.HISTORY_DIR) + path.sep
        self.data_dump_path = path.join(self.proj_root_path, const.DATA_DUMP_DIR) + path.sep
        self.sa_storage_path = path.join(self.proj_root_path, const.SA_STORAGE_DIR) + path.sep

        if not self.testing:

            if not path.exists(self.history_path):
                os.makedirs(self.history_path)

            if not path.exists(self.hdf_res_path):
                os.makedirs(self.hdf_res_path)

            if not path.exists(self.hdf_res_path):
                os.makedirs(self.hdf_res_path)

            if not path.exists(self.logs_path):
                os.makedirs(self.logs_path)

            if not path.exists(self.data_dump_path):
                os.makedirs(self.data_dump_path)

            if not path.exists(self.sa_storage_path):
                os.makedirs(self.sa_storage_path)

    def _init_param_setup(self) -> None:
        """

        Initializes the parameters by splitting these into the main groups.

        """

        # Additional params setup :
        self.additional_params_exist = False

        # Parameter setup :
        self.n_base_params = self.n_cfs_params + self.n_mat_params + self.n_trelis_params

        self._init_params_parallel(self.params)

        # Concatenate all params names :
        self.params_names = self.cfs_params_names + self.mat_params_names + self.trelis_params_names

    def _init_params_parallel(self, X: pyCFSparamVec) -> None:
        """

        Initializes the parameters for parallel execution. Essenatially
        splits up the parameter matrix X into the 4 different parameter
        groups which are used within the simulations.

        Args:
            X (pyCFSparamVec): N x M Array containing the simulation parameters. Here
                            the M is the number of parameters in total.
        """

        self.cfs_params = X[:, 0 : self.n_cfs_params]
        self.mat_params = X[:, self.n_cfs_params : self.n_cfs_params + self.n_mat_params]
        self.trelis_params = X[:, self.n_cfs_params + self.n_mat_params : self.n_base_params]
        self.add_params = X[:, self.n_cfs_params + self.n_mat_params + self.n_trelis_params :]

    def _init_file_names(self) -> None:
        """

        Generate names for the different simulation files which are used.

        """
        self.cfs_file_init = path.join(
            self.proj_root_path, self.templates_dir, f"{self.project_name}_{self.init_file_extension}.xml"
        )
        self.mat_file_init = path.join(
            self.proj_root_path, self.templates_dir, f"{self.mat_file_name}_{self.init_file_extension}.xml"
        )
        self.jou_file_init = path.join(
            self.proj_root_path, self.templates_dir, f"{self.project_name}_{self.init_file_extension}.jou"
        )

        self.sim_file_noext = path.join(self.proj_root_path, self.project_name)
        self.cfs_file = path.join(self.proj_root_path, f"{self.project_name}.xml")
        self.cfs_info_file = path.join(self.proj_root_path, f"{self.project_name}.info.xml")
        self.jou_file = path.join(self.proj_root_path, f"{self.project_name}.jou")
        self.mat_file = path.join(self.proj_root_path, f"{self.mat_file_name}.xml")
        self.cdb_file = path.join(self.proj_root_path, f"{self.project_name}.cdb")
        self.sim_files = [
            self.cfs_file,
            self.jou_file,
            self.mat_file,
            self.cfs_info_file,
            self.cdb_file,
        ]
        self.mesh_convert_file = path.join(self.proj_root_path, f"{const.MESHCONVERT_XML_NAME}.xml")
        self.mesh_convert_info_file = path.join(self.proj_root_path, f"{const.MESHCONVERT_XML_NAME}.info.xml")
        self.mesh_convert_mat_file = path.join(self.proj_root_path, f"{const.MESHCONVERT_MAT_NAME}.xml")
        self.topopt_input_template_file = path.join(
            self.proj_root_path, const.RESULTS_HDF_DIR, f"{const.MESHCONVERT_XML_NAME}.cfs"
        )
        self.topopt_input_file = path.join(self.proj_root_path, f"{const.TOPOPT_PARAM_FILE_NAME}.cfs")

        self.cfs_exports_names = {
            const.SOL_TOKEN: path.join(self.proj_root_path, f"{self.project_name}_{const.SOL_TOKEN}.{const.VEC_TOKEN}"),
            const.RHS_TOKEN: path.join(self.proj_root_path, f"{self.project_name}_{const.RHS_TOKEN}.{const.VEC_TOKEN}"),
            const.MAT_TOKEN: path.join(
                self.proj_root_path, f"{self.project_name}_{const.MAT_TOKEN}_0_0.{const.MTX_TOKEN}"
            ),
        }

    def _init_functions(self) -> None:
        """

        Initializes the functions to avoid branches in the code based on some
        logical flags.

        """
        self._forward: Callable[[pyCFSparamVec], None] = (
            self._forward_parallel if self.parallelize else self._forward_serial
        )
        self._clean_sim_files_if_on: Callable[[], None] = (
            self._clean_sim_files if self.clean_finish else self.dummy_fun_noarg
        )
        self._save_hdf_results_if_on: Callable[[int, bool], None] = (
            self._save_hdf_results if self.save_hdf_results else self.dummy_fun_int_bool
        )
        self._save_all_hdf_results_if_on: Callable[[], None] = (
            self._save_all_hdf_results if self.save_hdf_results else self.dummy_fun_noarg
        )
        self._clean_sim_files_parallel_if_on: Callable[[], None] = (
            self._clean_sim_files_parallel if self.clean_finish else self.dummy_fun_noarg
        )
        self._clean_hdf_results_parallel_if_on: Callable[[], None] = (
            self._clean_hdf_results_parallel if not self.save_hdf_results else self.dummy_fun_noarg
        )
        self._dump_results_if_on: Callable[[], None] = self._dump_results if self.dump_results else self.dummy_fun_noarg
        self._init_sensor_arrays_if_exist: Callable[[], None] = (
            self._init_sensor_arrays if len(self.sensor_arrays) > 0 else self.dummy_fun_noarg
        )

    def _init_results(self) -> None:
        """

        Initializes an empty list for storing the hdf file results into.

        """
        self.results: List[nestedResultDict] = []
        self.hist_results: List[nestedResultDict] = []

    def _set_mesh_present_status(self, present: bool) -> None:
        self.mesh_present = present

    def _set_export_system_matrices(self, export_matrices: bool, sim_name_id: str) -> None:

        self.export_matrices = export_matrices

        if export_matrices:
            if self.parallelize:
                print(
                    """[pyCFS-Warning] Export matrices enabled in parallel mode - this
                         result in the exported matrices being overwritten. Please run matrix
                         export only in serial model."""
                )

            # insert simulation name into template
            export_matrices_xml = const.EXPORT_MATRICES_TEMPLATE.replace(const.SIM_NAME_TOKEN, sim_name_id)

            # check if there are already linear systems present if so insert only
            # small portion needed to export the matrices
            if const.EXPORT_MATRICES_TOKEN in self.templates[self.cfs_file_init]:
                self.templates[self.cfs_file_init] = self.templates[self.cfs_file_init].replace(
                    const.EXPORT_MATRICES_TOKEN, const.EXPORT_MATRICES_TOKEN + "\n" + export_matrices_xml
                )
            # otherwise if no linear systems is present, then insert the whole setup
            else:
                export_matrices_xml = const.LINEAR_SYSTEMS_TEMPLATE.replace(const.INSERT, export_matrices_xml)
                self.templates[self.cfs_file_init] = self.templates[self.cfs_file_init].replace(
                    const.LINEAR_SYSTEMS_TOKEN, export_matrices_xml
                )

    def _init_templates_variables(self) -> None:
        if not self.testing:
            self.templates = {}
            self.templates[self.cfs_file_init] = pyCFS.read_file_contents(self.cfs_file_init)
            self.templates[self.mat_file_init] = pyCFS.read_file_contents(self.mat_file_init)
            self.templates[self.jou_file_init] = pyCFS.read_file_contents(self.jou_file_init)

    # * ------------------ Execution methods ------------------
    def _forward_serial(self: "pyCFS", X: pyCFSparamVec) -> None:
        """

        Performs the forward pass over all data. Determines number of parameter
        combinations N. Allocates the result arrays and stores the results
        of the performed calculations.

        Args:
            self (object): PyCfs class object.
            X (np.ndarray): N x M Array containing the simulation parameters. Here
                            the M is the number of parameters in total.

        Returns:
            None.
        """

        self.N = X.shape[0]
        self._init_results()

        for ind in tqdm(range(self.N)):
            self.ind = ind
            x = X[ind : ind + 1, :]
            self._forward_once_serial(x)

            self._set_results()

            self._handle_exported_matrices_if_on()

            self._save_hdf_results_if_on(ind)  # type: ignore[call-arg]

        self._clean_sim_files_if_on()

    def _forward_parallel(self: "pyCFS", X: pyCFSparamVec) -> None:
        """

        Performs the forward pass over all data in a parallel manner. Does the
        preprocessing step where the passed matrix is prepared for parallel computation
        and determines the number of parameter combinations N. Allocates the
        result arrays and stores the results of the performed calculations.

        Args:
            self (object): PyCfs class object.
            X (pyCFSparamVec): N x M Array containing the simulation parameters. Here
                            the M is the number of parameters in total.

        Returns:
            None.
        """

        self.N = X.shape[0]
        self._init_results()

        self._init_params_parallel(X)

        # generate data indices for parallel computing :
        data_list = np.arange(0, self.N)

        # determine number of jobs :
        n_jobs = min(len(data_list), self.n_jobs_max)

        # construct pool and pass jobs - starts the computation also:
        with Pool(processes=n_jobs) as p:
            with tqdm(total=len(data_list)) as pbar:
                for _ in p.imap_unordered(self._forward_once_parallel, data_list):
                    pbar.update()

                pbar.close()

        for ind in range(self.N):
            self._set_results(ind)

        self._save_all_hdf_results_if_on()
        self._clean_hdf_results_parallel_if_on()
        self._clean_sim_files_parallel_if_on()

    def _forward_once_serial(self, x: pyCFSparamVec) -> None:
        """

        Performs the forward pass for one parameter configuration. Updates the
        simulation files. Runs the pipeline (trelis, cfs calculation), gets the
        results, stores them and cleans the history files from the history folder.

        Args:
            self (object): PyCfs class object.
            x (np.ndarray): Array containing the simulation parameters. Here
                            the M is the number of parameters in total.
            ind (int): Index of current parameter array out of the total N
                       configurations.

        Returns:
            None.
        """

        self._update_params(x)
        self._run_pipeline()
        self._set_all_params_changed_status(False)

        # add clean of hdf results if turned on !

    def _forward_once_parallel(self, ind: int) -> None:
        """

        Runs one process from the pool of currently active ones. Does
        this for the process with id = ind.

        Args:
            ind (int): job index to get correct parameters for simulation
                       and to read correct results from the result dir.
        """

        self._set_all_params_changed_status(True)
        self._run_pipeline(ind)

    def _run_pipeline(self, ind: Optional[int] = None) -> None:
        """

        Performs a check to see which parameters changes. If the parameter
        group in question did change then the appropriate file gets updated
        and if necessary further actions carried out. If any parameter
        group changed then the simulation is carried out.

        Args:
            self (object): PyCfs class object.
            ind (int): Pool job index to get correct parameters for simulation
                       and to read correct results from the result dir.

        Returns:
            None.
        """

        # Check if CFS xml parameters changed :
        if self.params_changed[0]:
            self._update_cfs_xml(ind)

        # Check if CFS mat parameters changed :
        if self.params_changed[1]:
            self._update_mat_xml(ind)

        # Check if meshing is needed :
        if self._is_meshing_needed(ind):
            self._run_meshing(ind)

        # If any config changes happened run simulation :
        if self.parallelize or np.any(self.params_changed) or self.n_params == 0:
            cfs_comm, log_path = self._make_cfs_command(ind)
            self._run(cfs_comm, log_path)

    def _run_meshing(self, ind: Optional[int] = None) -> None:
        """Updates the journal file and runs the meshing for this file.

        Args:
            ind (Optional[int], optional): Index of the job. Defaults to None.
        """
        self._update_trelis_jou(ind)
        mesher_comm, log_path = self._make_mesher_command(ind)
        self._run(mesher_comm, log_path)

    def _generate_meshes(self, X: pyCFSparamVec) -> None:
        """Generates the mesh files for the given parameters.

        Args:
            X (pyCFSparamVec): Parameter vector.

        Raises:
            ValueError: If parameter vector is empty.
        """
        if X.shape[0] == 1:
            self._generate_meshes_serial(X)
        else:
            self._generate_meshes_parallel(X)

    def _generate_meshes_serial(self, x: pyCFSparamVec) -> None:

        self._update_params(x)
        self._run_meshing()

    def _generate_meshes_parallel(self, X: pyCFSparamVec) -> None:

        self.N = X.shape[0]

        self._init_params_parallel(X)

        # generate data indices for parallel computing :
        data_list = np.arange(0, self.N)

        # determine number of jobs :
        n_jobs = min(len(data_list), self.n_jobs_max)

        # construct pool and pass jobs - starts the computation also:
        with Pool(processes=n_jobs) as p:
            with tqdm(total=len(data_list)) as pbar:
                for _ in p.imap_unordered(self._run_meshing, data_list):
                    pbar.update()

                pbar.close()

    def _is_meshing_needed(self, ind: Optional[int] = None) -> bool:
        """Checks if there is need to do meshing. In the case of non parallel execution
        this will be True when params_changed[2] is True and False if not (ind is always None
        for serial execution mode!). In the case of parallel execution it will return
        True only when parallelize and remeshing_on are both True (ind is never None when
        in parallel execution mode so first part is False).

        Args:
            ind (Optional[int], optional): Index of the job. Defaults to None.

        Returns:
            bool: Indicates if meshing should be performed.
        """
        return (self.params_changed[2] and (ind is None) and not self.mesh_present) or (
            self.remeshing_on and self.parallelize and not self.mesh_present
        )

    # * ------------------ pyCFS Sensor Array functions ------------
    @staticmethod
    def _get_template_for(template, item: str) -> str:
        return template.replace(const.ITEM, item)

    @staticmethod
    def _replace_coords_in_str(coord_str: str, x, y, z) -> str:
        coord_str = coord_str.replace(const.X_COORD_SA, str(x))
        coord_str = coord_str.replace(const.Y_COORD_SA, str(y))
        coord_str = coord_str.replace(const.Z_COORD_SA, str(z))
        return coord_str

    @staticmethod
    def _fill_item_templates(item, item_name, item_template, sensor_locations) -> List[str]:

        items = []

        for id_num in range(sensor_locations.shape[0]):
            id_str = f"_{id_num}"
            item = item_template.replace(const.ITEM, item)
            item = item.replace(const.ITEM_NAME, item_name + id_str)
            item = pyCFS._replace_coords_in_str(item, *sensor_locations[id_num])

            items.append(item)

        return items

    @staticmethod
    def _generate_items(result_name, item, sensor_locations) -> Tuple[List[str], List[str]]:

        item_name = f"{result_name}_{item}"

        item_template = pyCFS._get_template_for(const.ITEM_TEMPLATE, item)
        item_res_template = pyCFS._get_template_for(const.ITEM_RES_TEMPLATE, item)

        items = pyCFS._fill_item_templates(item, item_name, item_template, sensor_locations)
        res_items = pyCFS._fill_item_templates(item, item_name, item_res_template, sensor_locations)

        return items, res_items

    @staticmethod
    def _generate_sa_setup_dict(sensor_arrays: List[Dict[str, str]]) -> Dict[str, Dict[str, List[str]]]:

        sa_setup_dict = {}

        for sa_id in range(len(sensor_arrays)):

            sensor_locations = np.loadtxt(sensor_arrays[sa_id]["file_path"], delimiter=",")
            result_name = sensor_arrays[sa_id]["result_name"]

            # generate individual nodes/elems and result nodes/elems :
            nodes, res_nodes = pyCFS._generate_items(result_name, const.NODE, sensor_locations)
            elems, res_elems = pyCFS._generate_items(result_name, const.ELEM, sensor_locations)

            sa_setup_dict[result_name] = {
                const.NODES: nodes,
                const.RES_NODES: res_nodes,
                const.ELEMS: elems,
                const.RES_ELEMS: res_elems,
            }

        return sa_setup_dict

    @staticmethod
    def _find_all_sensorarray_inserts(xml_content) -> List[str]:
        return re.findall(const.RESLIST_PATTERN, xml_content)

    @staticmethod
    def _construct_result_list_for(sa_result: str, sa_setup_dict: Dict[str, Dict[str, List[str]]]) -> str:
        split_sa_result = sa_result.split("_")
        restype = (split_sa_result[-1].replace("LIST", "")).lower()
        restype_full = const.RES_NODES if restype == const.NODE else const.RES_ELEMS
        resitems_str = "\n".join(
            list(chain.from_iterable(sa_setup_dict[sa_name][restype_full] for sa_name in split_sa_result[:-1]))
        )
        return pyCFS._get_template_for(const.LIST_TEMPLATE, restype).replace("INSERT", resitems_str)

    def _init_sensor_arrays(self) -> None:

        if not self.testing:

            self.sa_setup_dict = self._generate_sa_setup_dict(self.sensor_arrays)

            nodes_list_def_str = "\n".join(
                list(chain.from_iterable(sa_setup[const.NODES] for _, sa_setup in self.sa_setup_dict.items()))
            )
            elems_list_def_str = "\n".join(
                list(chain.from_iterable(sa_setup[const.ELEMS] for _, sa_setup in self.sa_setup_dict.items()))
            )

            # generate list for nodes and elements :
            self.nodelist_str = self._get_template_for(const.LIST_TEMPLATE, const.NODE).replace(
                "INSERT", nodes_list_def_str
            )
            self.elemlist_str = self._get_template_for(const.LIST_TEMPLATE, const.ELEM).replace(
                "INSERT", elems_list_def_str
            )

            # using </domain> as an identifier to add these lists to the end of the domain definition
            list_defs_str = self.elemlist_str + "\n" + self.nodelist_str + "\n</domain>"

            self.templates[self.cfs_file_init] = self.templates[self.cfs_file_init].replace("</domain>", list_defs_str)

            reslist_matches = self._find_all_sensorarray_inserts(self.templates[self.cfs_file_init])

            unique_reslist_matches = np.unique(reslist_matches)

            reslist_dict = {
                res_name: self._construct_result_list_for(res_name, self.sa_setup_dict)
                for res_name in unique_reslist_matches
            }

            for resname in reslist_matches:
                self.templates[self.cfs_file_init] = self.templates[self.cfs_file_init].replace(
                    resname, reslist_dict[resname]
                )

    # * ------------------ Result handler methods ------------------
    def _generate_data_dump_path(self) -> str:
        t = time.ctime(time.time())
        t = t.replace("  ", " ").replace(" ", "_").replace(":", "-")
        return f"{self.data_dump_path}data_dump_run_{t}.npy"

    def _contruct_run_metadata(self, X: pyCFSparamVec) -> None:
        file_paths = glob(path.join(self.proj_root_path, "**", "*.csv"), recursive=True) + glob(
            path.join(self.proj_root_path, "**", "*.py"), recursive=True
        )
        other_files = {k: pyCFS.read_file_contents(k) for k in file_paths}
        self.run_metadata = {
            "xml_template": pyCFS.read_file_contents(self.cfs_file_init),
            "mat_template": pyCFS.read_file_contents(self.mat_file_init),
            "jou_template": pyCFS.read_file_contents(self.jou_file_init),
            "other_files": other_files,
            "X": X,
            "run_start": self.time[const.LAST_EXEC_START],
            "run_finish": self.time[const.LAST_EXEC_STOP],
            "note": "",
        }

    def _dump_results(self) -> None:
        result_packet = {
            "results_hdf": self.results,
            "results_history_hdf": self.hist_results,
            "meta_data": self.run_metadata,
        }

        self.result_dump_path = self._generate_data_dump_path()
        np.save(self.result_dump_path, result_packet, allow_pickle=True)  # type: ignore[arg-type]

    def _get_hdf_curr_package(self, ind: Optional[int] = None) -> Tuple[nestedResultDict, nestedResultDict]:
        """

        Generates packages containing the results for the current simulation. This
        function saves all results that are present in the result hdf file if the
        tracking options of `pyCFS` are left as default. Otherwise only the selected
        results for the selected regions are stored (note, for the history results,
        all regions are always stored - cannot be selected currently - only the
        quantity which is to be tracked).

        Returns:
            Tuple[Dict[str,np.ndarray],Dict[str,np.ndarray]]: Dict containing the main results
            and Dict containing the hist results.

        """
        file_path = self.hdf_file_path if ind is None else f"{self.hdf_file_path[:-4]}_{ind}.cfs"

        with CFSReader(file_path) as resreader:
            main_result_data = self._get_main_result_data(resreader)
            hist_result_data = self._get_hist_result_data(resreader)

        return (main_result_data, hist_result_data)

    def _get_main_result_data(self, resreader: CFSReader) -> nestedResultDict:
        """

        Extracts the main results from the CFS simulation results hdf file.

        Args:
            resreader (CFSReader): CFSReader instance.

        Returns:
            nestedResultDict: Dict containing the main results.
        """

        result_data: nestedResultDict = {}

        for ms_id in resreader.MultiStepIDs:

            result_packet = {}  # type: ignore[var-annotated]

            # Get result quantities :
            res_quantities = resreader.get_result_quantities(multi_step_id=ms_id)

            for res_quantity in res_quantities:

                if self.track_quantities[0].lower() == "all" or res_quantity in self.track_quantities:

                    # Set new subdict for given quantity :
                    result_packet[res_quantity] = {}

                    # Get result regions :
                    res_regions = resreader.get_result_regions(res_quantity)

                    for res_region in res_regions:
                        if self.track_regions[0].lower() == "all" or res_region in self.track_regions:

                            # Get results for given region :
                            result_packet[res_quantity][res_region] = resreader.get_data_steps(
                                res_quantity, res_region
                            )[
                                0
                            ]  # noqa

            # Add data packet for current multi step :
            result_data[ms_id] = result_packet

        return result_data

    def _get_hist_result_data(self, resreader: CFSReader) -> nestedResultDict:
        """

        Extracts the history results from the CFS simulation results hdf file.

        Args:
            resreader (CFSReader): CFSReader instance.

        Returns:
            nestedResultDict: Dict containing the hist results.
        """

        result_data: nestedResultDict = {}

        for ms_id in resreader.MultiStepIDs:

            try:
                hist_data_packet = {}  # type: ignore[var-annotated]
                histdata = resreader.get_history_data(multi_step_id=ms_id)

                hist_info_list = histdata.ResultInfo

                for hist_info in hist_info_list:

                    if self.track_quantities_hist[0].lower() == "all" or hist_info.Quantity in self.track_quantities:

                        if hist_info.Quantity not in hist_data_packet.keys():
                            hist_data_packet[hist_info.Quantity] = {}

                        hist_data_packet[hist_info.Quantity][hist_info.Region] = histdata.extract_quantity_region(
                            hist_info.Quantity, hist_info.Region  # type: ignore[var-annotated]
                        ).Data[0]

            except KeyError:
                print(f"[pyCFS-Warning] There is no history data for MultiStep {ms_id}")

            result_data[ms_id] = hist_data_packet

        return result_data

    def _save_hdf_results(self, ind: int = 0, is_parallel: bool = False) -> None:
        """

        Moves the current hdf results to another folder for saving purposes.

        Args:
            ind (int, optional): Index of the parameter set to relate to.
                                 Defaults to 0.
        """

        source_path = ""
        dest_path = path.join(self.hdf_res_path, f"{self.project_name}_{ind}.{const.CFS_EXT}")

        if is_parallel:
            source_path = path.join(
                self.proj_root_path, const.RESULTS_HDF_DIR, f"{self.project_name}_{ind}.{const.CFS_EXT}"
            )
            shutil.move(source_path, dest_path)
        else:
            source_path = path.join(self.proj_root_path, const.RESULTS_HDF_DIR, f"{self.project_name}.{const.CFS_EXT}")
            shutil.copy(source_path, dest_path)

    def _save_all_hdf_results(self) -> None:
        for i in range(self.N):
            self._save_hdf_results(i, is_parallel=True)

    @staticmethod
    def _read_cfs_export(file_name: str) -> resultVec:
        if file_name[-3:] == const.VEC_TOKEN:
            return np.loadtxt(file_name)
        else:
            return mmread(file_name)

    def _handle_exported_matrices_if_on(self) -> None:
        if self.export_matrices:
            # get all matrix files :
            mat_files = glob(f"./*.{const.MTX_TOKEN}") + glob(f"./*.{const.VEC_TOKEN}")

            # read matrix files contents into dictionary
            export_packet: resultDict = {file: self._read_cfs_export(file) for file in mat_files}

            self.matrix_exports.append(export_packet)

    def _set_results(self, ind: Optional[int] = None) -> None:
        """

        Reads the hdf results from the current file and appends the generated packet
        to the list of hdf results.

        Args:
            ind (int): Job index to get correct parameters for simulation
                       and to read correct results from the result dir.
        """
        hdf_package, hdf_hist_package = self._get_hdf_curr_package(ind)
        self.results.append(hdf_package)
        self.hist_results.append(hdf_hist_package)

    @staticmethod
    def _is_coord_col(col_name: str) -> bool:
        return True in [key in col_name for key in const.SA_COORD_KEYS]

    @staticmethod
    def _remove_coord_cols(sa_res: sensorArrayResult) -> sensorArrayResult:
        cols: List[str] = []
        data_inds = np.zeros(len(sa_res["columns"]), dtype=bool)

        for ind, col in enumerate(sa_res["columns"]):
            if not pyCFS._is_coord_col(col):
                cols.append(col)
                data_inds[ind] = True

        res: sensorArrayResult = {"data": sa_res["data"][:, data_inds], "columns": cols}

        return res

    def get_results(self, ind: int) -> nestedResultDict:
        """Returns the stored hdf results from self.results located at the
        given index `ind`.

        Args:
            ind (int): Index from which to return the results. Represents
            the index of the parameter set.

        Returns:
            nestedResultDict: Nested result dict for the given index.
        """
        return self.results[ind]

    def get_sensor_array_results(
        self, sensor_array_name: str, ind: int, ms: int, quantity: str
    ) -> Tuple[resultVec, List[str]]:
        """Retrieve the sensor array result quantity for a given parameter set index and MultiStep index.

        Args:
            sensor_array_name (str): Name given to the sensor array as passed to `pyCFS`.
            ind (int): Index of the passed parameter set (if only one parameter set used for last simulation run then it is 0).
            ms (int): Index of the MultiStep.
            quantity (str): Quantity for which to get the results.

        Returns:
            Tuple[resultVec, List[str]]: A tuple containing the result array and a list with the keys of the names belonging to
            the entries of this sensor array.

        Examples
        --------
        >>> # Getting the `elecPotential` from parameter set index 0 (ind=0), MultiStep 1 (ms=1) for the
        >>> # sensor array defined as `SENSPOS1`
        >>> elecPot, res_keys = cap_sim.get_sensor_array_results("SENSPOS1", ind=0, ms=1, quantity="elecPotential")
        """
        result = []
        result_keys = []

        for key, val in self.hist_results[ind][ms][quantity].items():  # type: ignore[index]
            if sensor_array_name in key:
                result.append(np.array(val))
                result_keys.append(key)

        return np.array(result), result_keys

    # * ------------------ Param handler methods ------------------
    def _check_given_params(self, X: pyCFSparamVec) -> None:

        if len(X.shape) == 1:
            raise ValueError(
                "Parameter vector has only one dimension - the passed parameters \
must have shape (N x num_params) where N is the number of parameter sets."
            )
        elif len(X.shape) > 2:
            raise ValueError(
                "Parameter vector has more than 2 dimensions! - the passed parameters \
must have shape (N x num_params) where N is the number of parameter sets."
            )
        elif X.shape[1] != self.n_params:
            raise ValueError(
                f"Parameter vector does not have [{self.n_params}] parameters! - the passed parameters \
must have shape (N x num_params) where N is the number of parameter sets."
            )

    def _set_all_params_changed_status(self, flag: bool) -> None:
        """

        Sets the params changed variable elements all to the given flag.

        Args:
            flag (bool): Value to set params changed variable elements to.
        """
        self.params_changed = np.full((const.N_PARAM_GROUPS,), flag)

    def _update_file(
        self,
        init_file_name: str,
        file_out_name: str,
        params: np.ndarray,
        param_names: List[str],
        ind: Optional[int] = None,
    ) -> None:
        """

        Main update function for the individual files. Loads the init (template) file.
        Sets the parameter values and writes this to the appropriate simulation file.

        Args:
            self (object): PyCfs class object.
            init_file_name (str): Name of the init file.
            file_out_name (str): Name of the output file.
            params (np.ndarray): Array of parameter values to be set.
            param_names (List[str]): Names of the parameters to be set.

        Returns:
            None.
        """

        end_ext = file_out_name.split(".")[-1]
        ind_ext = f".{end_ext}" if ind is None else f"_{ind}.{end_ext}"
        ind_ext_cdb = f".{const.CDB_EXT}" if (ind is None or self.mesh_present) else f"_{ind}.{const.CDB_EXT}"
        ind_int = 0 if ind is None else ind

        if len(param_names) > 0:
            params = params[ind_int, :]

        file_out_name = file_out_name.replace(f".{end_ext}", ind_ext)

        # Previously the file was read from disk every time it
        # was to be edited. Not very efficient and also prevents
        # from making initial changes without writing these to
        # init file making the process complicated unnecessary.
        # data = pyCFS.read_file_contents(init_file_name)
        data = self.templates[init_file_name]

        for param, pname in zip(params, param_names):
            param_str = str(int(param)) if "_ID" in pname else str(param)
            data = data.replace(pname, param_str)

        if end_ext == const.XML_EXT:
            data = data.replace('file="mat.xml"', f'file="mat{ind_ext}"')
            data = data.replace(
                f'cdb fileName="{self.cdb_file}"',
                f'cdb fileName="{self.cdb_file[:-4]}{ind_ext_cdb}"',
            )

        elif end_ext == const.JOU_EXT:
            data = data.replace(f'"{self.cdb_file}"', f'"{self.cdb_file[:-4]}{ind_ext_cdb}"')

        pyCFS.write_file_contents(file_out_name, data)

    def _update_params(self, params: np.ndarray) -> None:
        """

        Updates only parameters which changed and sets these in the param.
        arrays. If any group changed the appropriate flag is also set.

        Args:
            self (object): PyCfs class object.
            params (np.ndarray): Array containing all of the M parameters.

        Returns:
            None.
        """

        if ~np.all(self.cfs_params == params[:, 0 : self.n_cfs_params]):
            self.cfs_params = params[:, 0 : self.n_cfs_params]
            self.params_changed[0] = True

        if ~np.all(self.mat_params == params[:, self.n_cfs_params : self.n_cfs_params + self.n_mat_params]):
            self.mat_params = params[:, self.n_cfs_params : self.n_cfs_params + self.n_mat_params]
            self.params_changed[1] = True

        if ~np.all(self.trelis_params == params[:, self.n_cfs_params + self.n_mat_params : self.n_base_params]):
            self.trelis_params = params[:, self.n_cfs_params + self.n_mat_params : self.n_base_params]
            self.params_changed[2] = True

        if ~np.all(self.add_params == params[:, self.n_cfs_params + self.n_mat_params + self.n_trelis_params :]):
            self.add_params = params[:, self.n_cfs_params + self.n_mat_params + self.n_trelis_params :]
            self.params_changed[3] = True

    def _update_cfs_xml(self, ind: Optional[int] = None) -> None:
        """

        Updates the main cfs xml file with the new parameters.

        Args:
            self (object): PyCfs class object.

        Returns:
            None.
        """
        self._update_file(
            self.cfs_file_init,
            self.cfs_file,
            self.cfs_params,
            self.cfs_params_names,
            ind,
        )

    def _update_mat_xml(self, ind: Optional[int] = None) -> None:
        """

        Updates the material cfs xml file with the new parameters.

        Args:
            self (object): PyCfs class object.

        Returns:
            None.
        """
        self._update_file(
            self.mat_file_init,
            self.mat_file,
            self.mat_params,
            self.mat_params_names,
            ind,
        )

    def _update_trelis_jou(self, ind: Optional[int] = None) -> None:
        """

        Updates the trelis journal file with the new parameters.

        Args:
            self (object): PyCfs class object.

        Returns:
            None.
        """
        self._update_file(
            self.jou_file_init,
            self.jou_file,
            self.trelis_params,
            self.trelis_params_names,
            ind,
        )

    # * ------------------ Housekeeping methods ------------------
    def _clean_hist_results(self) -> None:
        """

        Removes all files from the hist folder and resets the
        file list.

        Args:
            self (object): PyCfs class object.

        Returns:
            None.
        """
        self._clean_files(self.files)
        self.files = []

    def _clean_sim_files_parallel(self) -> None:

        wildcards = [
            path.join(self.proj_root_path, f"{self.project_name}*.{const.XML_EXT}"),
            path.join(self.proj_root_path, f"{self.mat_file_name}*.{const.XML_EXT}"),
            path.join(self.proj_root_path, f"{self.project_name}*.{const.JOU_EXT}"),
        ]
        pyCFS._find_and_remove_files(wildcards)

    def _clean_hdf_results_parallel(self) -> None:
        wildcards = [path.join(self.proj_root_path, const.RESULTS_HDF_DIR, f"*.{const.CFS_EXT}")]
        pyCFS._find_and_remove_files(wildcards)

    @staticmethod
    def _find_and_remove_files(wildcards: List[str] = []):
        for wildcard in wildcards:
            files = glob(wildcard)

            for file in files:
                os.remove(file)

    def _clean_sim_files(self) -> None:
        """

        Removes all generated simulation files from the hist folder and resets the
        file list.

        Args:
            self (object): PyCfs class object.

        Returns:
            None.
        """
        # self._reset_param_changed_status()
        self._clean_files(self.sim_files)

    def _clean_files(self, files: List[str]) -> None:
        """

        Removes all files from the passed files list.

        Args:
            self (object): PyCfs class object.
            files (List[str]): List of paths to files to delete.

        Returns:
            None.
        """
        for file in files:
            if path.exists(file) and const.CDB_EXT not in file:
                os.remove(file)

    # * ------------------ CFS and Mesher methods ------------------
    def _run(self, cmd: List[str], log_path: Optional[str] = None) -> None:
        """

        Runs the passed command line command.

        Args:
            self (object): PyCfs class object.
            cmd (List[str]): Command to be executed with all flags and inputs.
            log_path (Optional[str]): path to file where to save output.
        Returns:
            None.
        """

        try:
            run_res = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if log_path is not None:
                self.write_file_contents(log_path, "\n" + run_res.stdout + "\n" + run_res.stderr)

        except subprocess.CalledProcessError as e:
            print(f"[pyCFS-subprocess]: {e}")

    def _make_mesher_command(self, ind: Optional[int] = None) -> Tuple[List[str], str]:
        """

        Generates a mesher command str. If from Pool of processes ind won't be
        None and it will generate correct command for the current process.

        Args:
            ind (Optional[int]): job index to get correct parameters for simulation
                       and to read correct results from the result dir.
                       Default : None.

        Returns:
            str: A string containing a command runnable in the shell.
        """

        mesher_options = self._get_mesher_options()
        log_path = self._get_log_output_path(ind, is_sim=False)

        ind_ext = "" if ind is None else f"_{ind}"
        subjou_name = f"{self.sim_file_noext}{ind_ext}.jou"

        return [self.trelis_version, *mesher_options, subjou_name], log_path

    def _make_cfs_command(self, ind: Optional[int] = None) -> Tuple[List[str], str]:
        """

        Generates a cfs command str. If from Pool of processes ind won't be
        None and it will generate correct command for the current process.

        Args:
            ind (Optional[int]): job index to get correct parameters for simulation
                       and to read correct results from the result dir.
                       Default : None.

        Returns:
            str: A string containing a command runnable in the shell.
        """

        cfs_options = self._get_cfs_options()
        log_path = self._get_log_output_path(ind)

        ind_ext = "" if ind is None else f"_{ind}"
        subsim_name = f"{self.sim_file_noext}{ind_ext}"

        return [self.cfs_install_dir, *cfs_options, subsim_name], log_path

    def _make_cfs_meshconvert_command(self) -> List[str]:
        xmlfile_name = self.mesh_convert_file[:-4]
        return [self.cfs_install_dir, "-q", "-g", xmlfile_name]

    def _get_mesher_options(self) -> List[str]:
        return ["-batch", "-nographics", "-nojournal"]

    def _get_cfs_options(self) -> List[str]:
        """

        Constructs the CFS command with the selected
        optional arguments.

        Args:
            self (object): PyCfs class object.

        Returns:
            (str): String with the cfs options.
        """
        cfs_options = [f"-t{self.n_threads}"]

        # Enable quiet mode
        if self.quiet_mode:
            cfs_options.append("-q")

        # Enable detailed mode to "info.xml" file
        if self.detail_mode:
            cfs_options.append("-d")

        return cfs_options

    def _get_log_output_path(self, ind: Optional[int] = None, is_sim: bool = True) -> str:
        run_name = "sim" if is_sim else "mesher"
        return (
            f"{self.logs_path}{run_name}_output.log" if ind is None else f"{self.logs_path}{run_name}_output_{ind}.log"
        )

    # * ------------------ TopOpt methods ------------------
    def init_topopt_setup(self, geom_type: str = "plane", design_domain: str = "V_design") -> None:
        """Sets up pyCFS for topology optimization. This includes setting the correct
        design domain and geometry type and then determine the mesh elements for the
        design domains such that later the parameters can easily be generated.

        Args:
            geom_type (str, optional): Type of geometry in the mesh file. Can be either "3d",
            "plane" or "axi". Defaults to "plane".
        """

        # check if the mesh is present :
        if not path.exists(self.cdb_file):
            raise FileNotFoundError(f"Mesh file not found at : {self.cdb_file}")

        # construct mesh convert xml file and write it to working directory :
        mesh_convert = const.MESH_CONVERT_TEMPLATE.replace(const.CDB_FILENAME, self.project_name)
        mesh_convert = mesh_convert.replace(const.MAT_FILENAME, const.MESHCONVERT_MAT_NAME)
        mesh_convert = mesh_convert.replace(const.GEOMETRY_TYPE, geom_type)

        # write mesh conversion file - no need for full simulation file here
        self.write_file_contents(self.mesh_convert_file, mesh_convert)
        # write a sample material file needed to just run the mesh convert
        self.write_file_contents(self.mesh_convert_mat_file, const.MESH_CONVERT_MAT_TEMPLATE)

        # execute mesh conversion to cfs file :
        mesh_convert_cmd = self._make_cfs_meshconvert_command()
        self._run(mesh_convert_cmd)

        # remove conversion files from working directory :
        self._clean_files([self.mesh_convert_file, self.mesh_convert_info_file, self.mesh_convert_mat_file])

        # read the contents of the generated file and store the data
        with CFSReader(self.topopt_input_template_file) as f:
            self.topopt_regions_data = f.MeshGroupsRegions
            self.topopt_design_centroids = f.MeshData.get_region_centroids(region=design_domain)
            self.topopt_design_volumes = f.MeshData.get_region_elements_volumes(region=design_domain)

    def _get_topt_regions(self, regions_name_list: List[str]) -> List[CFSRegData]:
        """Returns a filtered regions data list containing only the data
        for the regions given in regions_name_list.

        Args:
            regions_name_list (List[str]): Contains names of regions to keep.

        Returns:
            List[CFSRegData]: Contains region data for chosen regions.
        """
        regions_data_list = []
        for region_data in self.topopt_regions_data:  # type: ignore[union-attr]
            if region_data.Name in regions_name_list:
                regions_data_list.append(region_data)

        return regions_data_list

    def set_topopt_params(self, regions_params_dict: Dict[str, Dict[str, pyCFSparamVec]]) -> None:
        """Writes the parameters given in `params_dict` into the input file needed
        by CFS to perform a forward and gradient calculation in the Topology Optimization
        mode.

        Args:
            regions_params_dict (Dict[str, Dict[str, pyCFSparamVec]]): A dictionary containing dictionaries.
            The inner dictionaries contain the *element-parameter-name* and *element-parameter-vector*
            pairs and the outter dictionary contains the *domain-region* and *inner-element-param-dict*
            pairs.
        """
        result_arrays_list = []

        for region, elem_params in regions_params_dict.items():
            for param_name, data in elem_params.items():
                result_arrays_list.append(
                    CFSResultArray(
                        data.reshape(1, len(data), 1),
                        quantity=param_name,
                        region=region,
                        step_values=np.array([0]),
                        dim_names=["x"],
                        res_type=cfs_result_type.ELEMENT,
                        is_complex=False,
                    )
                )

        result_data = CFSResultContainer(
            analysis_type=cfs_analysis_type.STATIC, multi_step_id=1, data=result_arrays_list
        )

        self._clean_files([self.topopt_input_file])
        shutil.copy(self.topopt_input_template_file, self.topopt_input_file)

        with CFSWriter(self.topopt_input_file, verbosity=v_def.min) as h5writer:
            h5writer.write_multistep(result=result_data)

    # * ------------------ Time methods ------------------
    def _record_time(self, time_id: str) -> None:
        self.time[time_id] = time.ctime(time.time())

    # * ------------------ Report methods ------------------
    @staticmethod
    def _print_one_line_box(
        line_content: str = "", padding: bool = False, header: bool = False, n_times: int = 1, n_pads: int = 1
    ) -> None:

        pad = " " * n_pads if padding else ""
        filler = const.INFO_BOX_CHAR if header else " "
        padded_content = f"{pad}{line_content}{pad}"

        for _ in range(n_times):
            print(f"{const.INFO_BOX_CHAR}{padded_content:{filler}^{const.INFO_BOX_WIDTH - 2}}{const.INFO_BOX_CHAR}")

    def _print_init_status_report(self) -> None:
        pyCFS._print_one_line_box(header=True)
        title = f"Project : {self.project_name}"
        pyCFS._print_one_line_box(title, header=True, padding=True, n_pads=10)
        pyCFS._print_one_line_box(header=True)
        pyCFS._print_one_line_box(n_times=2)

        init_time = self.time["init_time"]
        pyCFS._print_one_line_box(f"Init at : {init_time}", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- Number of parameters : {self.n_params}", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- CFS parameters : {self.n_cfs_params}", padding=True)
        p_names = ", ".join(self.cfs_params_names)
        pyCFS._print_one_line_box(f"[{p_names}]", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- MAT parameters : {self.n_mat_params}", padding=True)
        p_names = ", ".join(self.mat_params_names)
        pyCFS._print_one_line_box(f"[{p_names}]", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- JOU parameters : {self.n_trelis_params}", padding=True)
        p_names = ", ".join(self.trelis_params_names)
        pyCFS._print_one_line_box(f"[{p_names}]", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- Tracked quantities : {self.track_quantities}", padding=True)
        pyCFS._print_one_line_box(f"- Parallelize : {self.parallelize}", padding=True)
        pyCFS._print_one_line_box(f"- Remeshing on : {self.remeshing_on}", padding=True)

        pyCFS._print_one_line_box(n_times=2)
        pyCFS._print_one_line_box(header=True)

    def _print_run_status_report(self) -> None:
        if self.verbosity > 0:
            pyCFS._print_one_line_box(header=True)
            title = f"Run report : {self.project_name}"
            pyCFS._print_one_line_box(title, header=True, padding=True, n_pads=10)
            pyCFS._print_one_line_box(header=True)
            pyCFS._print_one_line_box(n_times=2)

            pyCFS._print_one_line_box(f" Start at : {self.time[const.LAST_EXEC_START]}", padding=True)
            pyCFS._print_one_line_box(f"Finish at : {self.time[const.LAST_EXEC_STOP]}", padding=True)

            pyCFS._print_one_line_box(n_times=2)
            pyCFS._print_one_line_box(f"- Total runs : {self.N}", padding=True)
            pyCFS._print_one_line_box()
            pyCFS._print_one_line_box(f"- Data dumped : {self.dump_results}", padding=True)
            if self.dump_results:
                pyCFS._print_one_line_box(f"@ : {self.result_dump_path}", padding=True)

            pyCFS._print_one_line_box(n_times=2)
            pyCFS._print_one_line_box(header=True)

    # * ------------------ I/O methods ------------------
    @staticmethod
    def read_file_contents(file_path: str) -> str:

        file = open(file_path, "r")
        contents = file.read()
        file.close()

        return contents

    @staticmethod
    def write_file_contents(file_path: str, contents: str) -> None:

        file = open(file_path, "w")
        file.write(contents)
        file.close()

    # * ------------------ Helper methods ------------------
    def dummy_fun(self, ind: int = 0) -> None:
        pass

    def dummy_fun_int_bool(self, ind: int = 0, is_parallel: bool = False) -> None:
        pass

    def dummy_fun_noarg(self) -> None:
        pass

    def _default_external_result_manip(self, obj: object) -> None:
        """

        Dummy function for external results manipulation. If no external
        result manipulation function is passed this one is executed and
        does nothing which is the goal.

        Args:
            obj (object): pycfs object instance.
        """
        pass
