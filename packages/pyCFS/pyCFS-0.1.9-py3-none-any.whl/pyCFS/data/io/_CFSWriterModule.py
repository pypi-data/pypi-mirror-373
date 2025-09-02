"""
Module containing data processing utilities for writing HDF5 files in openCFS format
"""

from __future__ import annotations

import os
import pathlib

import h5py
import numpy as np
from typing import List, Dict, Tuple, Sequence

from pyCFS.data.io import cfs_types, CFSRegData, CFSResultArray
from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
from pyCFS.data.util import vprint, progressbar

from pyCFS.data.io._CFSMeshDataModule import CFSMeshData, CFSMeshInfo
from pyCFS.data.io._CFSResultContainerModule import CFSResultContainer, CFSResultInfo

from pyCFS.data._v_def import v_def


class CFSWriter:
    """
    Base class for all writing operations

    Parameters
    ----------
    filename : str
        Path to the hdf5 file.
    h5driver : str, optional
        Driver used to read the hdf5 file (see h5py documentation). The default is ``None``, in which case the standard
        driver is used.
    compression_lvl : int, optional
        Defines the GZIP compression level used for writing all large datasets in the hdf5 file.
        The default level is ``6``.
    verbosity : int, optional
        Verbosity level <=1000 ; see _v_def.py for predefined levels. Default is v_def.release.

    Attributes
    ----------
    CompressionLvl : int
        GZIP compression level used for writing all large datasets in the hdf5 file.

    Notes
    -----
    -  ``create_file`` Perform all steps to create an empty HDF5 file and write Mesh and (optionally) Results to it.

    -  ``create_mesh`` Create Mesh structure and write mesh information to the active hdf5 file.

    -  ``write_mesh`` Write Mesh data to the active hdf5 file.

    -  ``write_dataset`` Write dataset to active HDF5 file

    -  ``write_dataset_parallel`` Write dataset to active HDF5 file

    -  ``get_create_history_result`` Create a new 'History' group or get existing one within the given 'Result' group.

    -  ``get_create_mesh_result`` Create a new 'Mesh' group or get existing one within the given 'Result' group.

    -  ``get_create_multistep`` Create a new 'MultiStep' group or get existing one within the given 'Mesh' or 'History' group.

    -  ``create_result_description`` Create a ResultDescription and write information.

    -  ``finalize_result_description`` Write dimension names and entity names to the given quantity group.

    -  ``create_step`` Create a step in MultiStep without updating LastStep-Attributes and ResultDescription for increased performance.

    -  ``create_step_add`` Create a step in MultiStep updating LastStep-Attributes and ResultDescription.

    -  ``set_step_attributes`` Set step values and numbers.

    -  ``add_step_update_attributes`` Add step and update (last) step values and numbers.

    -  ``create_step_result`` Create a result in a step.

    -  ``write_step_result`` Write step result data to the dataset.

    -  ``create_external`` Create an external HDF5 file for storing data.

    -  ``write_history_multistep`` Write history data. Write ResultDescription and create datasets, write data to MultiStep.

    -  ``prepare_write_multistep`` Write ResultDescription and create datasets

    -  ``perform_write_multistep`` Write data to MultiStep

    -  ``finalize_write_multistep`` Write datasets to ResultsDescription that need to be written after the data in case of parallel write

    -  ``write_mesh_multistep`` Write mesh result data to multistep.

    -  ``write_multistep``
        Write ResultDescription and create datasets, write data to multistep and write datasets to ResultsDescription
        that need to be written after the data in case of parallel write

    -  ``add_steps_to_multistep`` Add additional result steps to the end of an existing MultiStep.

    -  ``round_step_values`` Round all step values of the defined multistep to a given amount of digits.

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader, CFSWriter
    >>> with CFSReader('file.cfs') as f:
    >>>     mesh = f.MeshData
    >>>     results = f.MultiStepData
    >>> with CFSWriter('file.cfs') as f:
    >>>     f.create_file(mesh=mesh,result=results)

    """

    def __init__(self, filename: str, h5driver=None, compression_lvl=6, verbosity=v_def.release) -> None:
        """Initialize the writer"""
        self._filename = filename
        self._h5driver = h5driver
        self.CompressionLvl = compression_lvl
        self._Verbosity = verbosity

    def __enter__(self):
        vprint(f"Opened {self._filename} (CFSWriter)", verbose=self._Verbosity >= v_def.debug)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        vprint(f"Closed {self._filename} (CFSWriter)", verbose=self._Verbosity >= v_def.debug)
        self._filename = ""
        return

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        if self._filename:
            return f"CFSWriter linked to file_src '{self._filename}', Verbosity {self._Verbosity}"
        else:
            return "Closed CFSWriter"

    def create_file(
        self,
        mesh: CFSMeshData | None = None,
        result: (
            Dict[int, CFSResultContainer]
            | Sequence[CFSResultContainer]
            | CFSResultContainer
            | Sequence[CFSResultArray]
            | None
        ) = None,
    ):
        """
        Perform all steps to create an empty HDF5 file and write Mesh and (optionally) Results to it.

        Parameters
        ----------
        mesh : CFSMeshData, optional
            Data structure containing all information about the mesh. The default is ``None``, in which case no mesh
            nor result data is written.
        result : dict[int, CFSResultContainer] or Sequence[CFSResultContainer] or CFSResultContainer or Sequence[CFSResultArray], optional
            Data structure containing all information about the multiSteps that will be written to the active file.
            Can be a dictionary mapping multi-step IDs to result containers, a list of result containers,
            a single result container, or a list of result arrays.
            The default is ``None``, in which case no result data is written.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>>     results = f.MultiStepData
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.create_file(mesh=mesh,result=results)

        """
        vprint(f"Creating file {self._filename}", verbose=self._Verbosity >= v_def.min)
        pathlib.Path(os.path.split(self._filename)[0]).mkdir(parents=True, exist_ok=True)
        # check if the file is already existing
        if os.path.exists(self._filename):
            os.remove(self._filename)
        with h5py.File(self._filename, "w", driver=self._h5driver) as f:
            f.require_group("FileInfo")

            f.require_group("Mesh")
            f.require_group("Results")
        if mesh is not None:
            mesh.check_mesh()
            self.create_mesh(mesh_info=mesh.MeshInfo, regions_data=mesh.Regions)
            self.write_mesh(mesh_data=mesh)
            if result is not None:
                if isinstance(result, dict):
                    for mid in result:
                        res_data = CFSResultContainer.require_container(result=result[mid], verbosity=self._Verbosity)
                        res_data.check_result(mesh=mesh)
                        self.write_multistep(result=res_data, multi_step_id=mid, perform_check=False)
                elif isinstance(result, Sequence) and all([isinstance(item, CFSResultContainer) for item in result]):
                    for midx, item in enumerate(result):
                        res_data = CFSResultContainer.require_container(result=item, verbosity=self._Verbosity)  # type: ignore
                        res_data.check_result(mesh=mesh)
                        self.write_multistep(result=res_data, multi_step_id=midx + 1, perform_check=False)
                elif (
                    isinstance(result, CFSResultContainer)
                    or isinstance(result, Sequence)
                    and all([isinstance(item, CFSResultArray) for item in result])
                ):
                    res_data = CFSResultContainer.require_container(result=result, verbosity=self._Verbosity)  # type: ignore
                    res_data.check_result(mesh=mesh)
                    self.write_multistep(result=res_data, multi_step_id=1, perform_check=False)
                else:
                    raise TypeError(f"Result type {type(result)} not supported.")

    def create_mesh(self, mesh_info: CFSMeshInfo, regions_data: List[CFSRegData]):
        """
        Create Mesh structure and write mesh information to the active hdf5 file.

        Parameters
        ----------
        mesh_info : CFSMeshInfo
            Data structure containing all mesh attributes.
        regions_data : list[CFSRegData]
            List of data structures containing data of all regions/groups.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh_info = f.MeshInfo
        >>>     regions_data = f.MeshGroupsRegions
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.create_file()
        >>>     f.create_mesh(mesh_info=mesh_info,regions_data=regions_data)

        """
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            grp_mesh = f["Mesh"]
            grp_mesh.attrs.create("Dimension", mesh_info.Dimension, dtype=np.dtype("uint32"))

            vprint("Creating Mesh Structure", verbose=self._Verbosity >= v_def.more)
            # Elements
            vprint(" - Creating Elements", verbose=self._Verbosity >= v_def.debug)
            grp_elem = grp_mesh.require_group("Elements")
            grp_elem.attrs.create("Num1DElems", mesh_info.Num1DElems, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num2DElems", mesh_info.Num2DElems, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num3DElems", mesh_info.Num3DElems, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("NumElems", mesh_info.NumElems, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_HEXA20", mesh_info.Num_HEXA20, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_HEXA27", mesh_info.Num_HEXA27, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_HEXA8", mesh_info.Num_HEXA8, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_LINE2", mesh_info.Num_LINE2, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_LINE3", mesh_info.Num_LINE3, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_POINT", mesh_info.Num_POINT, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_POLYGON", mesh_info.Num_POLYGON, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_POLYHEDRON", mesh_info.Num_POLYHEDRON, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_PYRA13", mesh_info.Num_PYRA13, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_PYRA14", mesh_info.Num_PYRA14, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_PYRA5", mesh_info.Num_PYRA5, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_QUAD4", mesh_info.Num_QUAD4, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_QUAD8", mesh_info.Num_QUAD8, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_QUAD9", mesh_info.Num_QUAD9, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_TET10", mesh_info.Num_TET10, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_TET4", mesh_info.Num_TET4, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_TRIA3", mesh_info.Num_TRIA3, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_TRIA6", mesh_info.Num_TRIA6, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_UNDEF", mesh_info.Num_UNDEF, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_WEDGE15", mesh_info.Num_WEDGE15, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_WEDGE18", mesh_info.Num_WEDGE18, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_WEDGE6", mesh_info.Num_WEDGE6, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("QuadraticElems", mesh_info.QuadraticElems, dtype=np.dtype("int32"))
            # dset = grp_elem.require_dataset('Connectivity', shape=mesh_data_demo.Connectivity.shape,
            #                                dtype=np.dtype('uint32'),compression='gzip',
            #                                compression_opts=self.CompressionLvl)
            # cfsWriteDataset(dset, np.uint32(mesh_data_demo.Connectivity))
            # dset = grp_elem.require_dataset('Types', shape=mesh_data_demo.Types.shape, dtype=np.dtype('int32'),
            #                                compression='gzip',
            #                                compression_opts=self.CompressionLvl)
            # cfsWriteDataset(dset, np.int32(mesh_data_demo.Types))

            # Nodes
            vprint(" - Creating Nodes", verbose=self._Verbosity >= v_def.debug)
            grp_nodes = grp_mesh.require_group("Nodes")
            grp_nodes.attrs.create("NumNodes", mesh_info.NumNodes, dtype=np.dtype("uint32"))
            # dset = grp_nodes.require_dataset('Coordinates', shape=mesh_data_demo.Coordinates.shape, dtype=np.float64,
            #                                 compression='gzip', compression_opts=self.CompressionLvl)
            # cfsWriteDataset(dset, np.float64(mesh_data_demo.Coordinates))

            # Groups / Regions
            grp_groups = grp_mesh.require_group("Groups")
            grp_reg = grp_mesh.require_group("Regions")

            for reg in regions_data:
                if reg.IsGroup:
                    reg_type = "Group"
                    grp_write = grp_groups
                else:
                    reg_type = "Region"
                    grp_write = grp_reg
                vprint(
                    f" - Creating {reg_type} {reg.Name}",
                    verbose=self._Verbosity >= v_def.debug,
                )
                grp_regname = grp_write.require_group(reg.Name)
                grp_regname.attrs.create("Dimension", reg.Dimension, dtype=np.dtype("uint32"))

    def write_mesh(self, mesh_data: CFSMeshData):
        """
        Write Mesh data to the active hdf5 file.

        Parameters
        ----------
        mesh_data : CFSMeshData
            Data structure containing all mesh data.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshInfo
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.create_file()
        >>>     f.create_mesh(mesh_info=mesh.MeshInfo,regions_data=mesh.Regions)
        >>>     f.write_mesh(MeshData=mesh)

        """
        vprint("Writing Mesh Data", verbose=self._Verbosity >= v_def.release)
        vprint(" - Writing Element Connectivity", verbose=self._Verbosity >= v_def.debug)
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            dset = f["Mesh/Elements"].require_dataset(
                "Connectivity",
                shape=mesh_data.Connectivity.shape,
                dtype=np.dtype("uint32"),
                compression="gzip",
                compression_opts=self.CompressionLvl,
            )
            CFSWriter.write_dataset(dset, mesh_data.Connectivity.astype(np.uint32))
        vprint(" - Writing Element Types", verbose=self._Verbosity >= v_def.debug)
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            dset = f["Mesh/Elements"].require_dataset(
                "Types",
                shape=mesh_data.Types.shape,
                dtype=np.dtype("int32"),
                compression="gzip",
                compression_opts=self.CompressionLvl,
            )
            CFSWriter.write_dataset(dset, mesh_data.Types.astype(np.int32))
        vprint(" - Writing Node Coordinates", verbose=self._Verbosity >= v_def.debug)
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            dset = f["Mesh/Nodes"].require_dataset(
                "Coordinates",
                shape=mesh_data.Coordinates.shape,
                dtype=np.float64,
                compression="gzip",
                compression_opts=self.CompressionLvl,
            )
            CFSWriter.write_dataset(dset, mesh_data.Coordinates.astype(np.float64))

        for reg in mesh_data.Regions:
            if reg.IsGroup:
                reg_type = "Group"
            else:
                reg_type = "Region"
            vprint(
                f" - Writing {reg_type}: {reg.Name}",
                verbose=self._Verbosity >= v_def.release,
            )
            vprint(
                f" -- Writing Elements: Region {reg.Name}",
                verbose=self._Verbosity >= v_def.debug,
            )
            with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
                dset = f[f"Mesh/{reg_type}s/{reg.Name}"].require_dataset(
                    "Elements",
                    shape=reg.Elements.shape,
                    dtype=np.dtype("int32"),
                    compression="gzip",
                    compression_opts=self.CompressionLvl,
                )
                CFSWriter.write_dataset(dset, reg.Elements.astype(np.int32))
            vprint(
                f" -- Writing Nodes: Region {reg.Name}",
                verbose=self._Verbosity >= v_def.debug,
            )
            with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
                dset = f[f"Mesh/{reg_type}s/{reg.Name}"].require_dataset(
                    "Nodes",
                    shape=reg.Nodes.shape,
                    dtype=np.dtype("uint32"),
                    compression="gzip",
                    compression_opts=self.CompressionLvl,
                )
                CFSWriter.write_dataset(dset, reg.Nodes.astype(np.uint32))

    @staticmethod
    def write_dataset(dset: h5py.Dataset, data: np.ndarray):
        """
        Write dataset to active HDF5 file

        Parameters
        ----------
        dset : h5py.Dataset
            dataset object of opened HDF5 file
        data : numpy.ndarray
            data to write to active HDF5 file

        """
        # TODO investigate performance gain of write_direct vs. normal assignment
        # try:
        #     dset.write_direct(data)
        # except TypeError as e:
        #     # If write_direct fails, fall back to normal assignment
        #     dset[:] = data

        dset[:] = data

    @staticmethod
    def write_dataset_parallel(dset: h5py.Dataset, data: np.ndarray, comm=None):
        """
        Write dataset to active HDF5 file

        Parameters
        ----------
        dset : h5py.Dataset
            dataset object of opened HDF5 file
        data : numpy.ndarray
            data to write to active HDF5 file
        comm : None, optional
            MPI communicator, The default is ``None``, in which case MPI.COMM_WORLD is used.

        """
        # TODO add parallel support again (h5pyp - h5py parallel build), once h5pyp fixes numpy bug
        raise NotImplementedError(
            "Parallel writing currently unavailable. See h5pyp (h5py parallel build) not working cause of numpy change"
        )

    #     # MPI communicator
    #     if not comm:
    #         comm = MPI.COMM_WORLD
    #
    #     ll = comm.rank * -(-data.shape[0] // comm.size)
    #     if comm.rank == comm.size - 1:
    #         ul = data.shape[0]
    #     else:
    #         ul = (comm.rank + 1) * -(-data.shape[0] // comm.size)
    #     with dset.collective:
    #         dset[ll:ul] = data[ll:ul]

    @staticmethod
    def get_create_history_result(grp_result: h5py.Group) -> h5py.Group:
        """
        Create a new 'History' group or get existing one within the given 'Result' group.

        Parameters
        ----------
        grp_result : h5py.Group
            'Result' group object of the opened HDF5 file.

        Returns
        -------
        h5py.Group
            'History' group object of the opened HDF5 file.

        """
        if "History" in grp_result:
            grp_result_history = grp_result["History"]
        else:
            grp_result_history = grp_result.require_group("History")

        return grp_result_history

    @staticmethod
    def get_create_mesh_result(grp_result: h5py.Group, externalFiles=False) -> h5py.Group:
        """
        Create a new 'Mesh' group or get existing one within the given 'Result' group.

        Parameters
        ----------
        grp_result : h5py.Group
            'Result' group object of the opened HDF5 file.
        externalFiles : bool, optional
            Flag indicating whether data is stored in external files. Default is False.

        Returns
        -------
        h5py.Group
            'Mesh' group object of the opened HDF5 file.

        """
        if "Mesh" in grp_result:
            grp_result_mesh = grp_result["Mesh"]
        else:
            grp_result_mesh = grp_result.require_group("Mesh")
            grp_result_mesh.attrs.create("ExternalFiles", data=externalFiles, dtype=np.dtype("int32"))

        return grp_result_mesh

    @staticmethod
    def get_create_multistep(
        grp_result_child: h5py.Group,
        multi_step_id=1,
        analysis_type=cfs_analysis_type.NO_ANALYSIS,
    ) -> Tuple[h5py.Group, h5py.Group]:
        """
        Create a new 'MultiStep' group or get existing one within the given 'Mesh' or 'History' group.

        Parameters
        ----------
        grp_result_child : h5py.Group
            'Mesh' or 'History' group object of the opened HDF5 file.
        multi_step_id : int, optional
            Identifier for the multi-step. Default is 1.
        analysis_type : cfs_analysis_type, optional
            Type of analysis being performed. Default is cfs_analysis_type.NO_ANALYSIS.

        Returns
        -------
        tuple of h5py.Group
            'MultiStep' group and 'ResultDescription' group objects of the opened HDF5 file.

        """
        if f"MultiStep_{multi_step_id}" in grp_result_child:
            grp_multi_step = grp_result_child[f"MultiStep_{multi_step_id}"]
            grp_result_description = grp_multi_step["ResultDescription"]
        else:
            if analysis_type == cfs_analysis_type.NO_ANALYSIS:
                print(f"WARNING: Created MultiStep result with analysis type {analysis_type}")
            grp_multi_step = grp_result_child.require_group(f"MultiStep_{multi_step_id}")
            grp_multi_step.attrs.create("AnalysisType", analysis_type, dtype=h5py.special_dtype(vlen=bytes))
            grp_multi_step.attrs.create("LastStepNum", data=0, dtype=np.dtype("uint32"))
            grp_multi_step.attrs.create("LastStepValue", data=0, dtype=np.dtype("float64"))

            grp_result_description = grp_multi_step.require_group("ResultDescription")

        return grp_multi_step, grp_result_description

    @staticmethod
    def create_result_description(
        grp_resultDescription: h5py.Group,
        qName: str,
        dim_names: List[str] | None = None,
        definedOn=cfs_result_type.NODE,
        entryType=1,
        step_values: np.ndarray | List[float] | None = None,
    ) -> None:
        """
        Create a ResultDescription and write information.

        Parameters
        ----------
        grp_resultDescription : h5py.Group
            'ResultDescription' group object of the opened HDF5 file.
        qName : str
            Name of the quantity.
        dim_names : list of str, optional
            Names of the dimensions. Default is None, which sets it to ["-"].
        definedOn : cfs_result_type, optional
            Type of result definition. Default is cfs_result_type.NODE.
        entryType : int, optional
            Type of entry. Default is 1.

        """
        # TODO Allow variables to be defined on multiple ResTypes
        # TODO Variable length with parallel io
        # TODO entryType based on data type (according to CFS source code: DataInOut/SimInOut/hdf5/hdf5io.cc::1877)
        if dim_names is None:
            dim_names = ["-"]
        if step_values is None:
            step_numbers: np.ndarray | List[float] = []
            step_values = []
        else:
            step_numbers = np.arange(len(step_values)) + 1
        grp_quantitiy = grp_resultDescription.require_group(qName)

        grp_quantitiy.require_dataset(
            "DefinedOn", data=int(definedOn), dtype=np.dtype("uint32"), shape=(1,)
        )  # 1 - Node, 4 - Element
        grp_quantitiy.require_dataset("EntryType", data=entryType, dtype=np.dtype("uint32"), shape=(1,))
        grp_quantitiy.require_dataset("NumDOFs", data=len(dim_names), dtype=np.dtype("uint32"), shape=(1,))
        grp_quantitiy.require_dataset(
            "StepNumbers",
            data=step_numbers,
            dtype=np.dtype("uint32"),
            shape=None,
            maxshape=(None,),
        )
        grp_quantitiy.require_dataset(
            "StepValues",
            data=step_values,
            dtype=np.dtype("float64"),
            shape=None,
            maxshape=(None,),
        )

    @staticmethod
    def finalize_result_description(
        grp_quantity: h5py.Group,
        reg_names: List[str],
        dim_names: List[str] | None = None,
        unit="",
    ) -> None:
        """
        Write dimension names and entity names to the given quantity group.
        (This function needs to be called after data writing, in the case of parallel writes.)

        Parameters
        ----------
        grp_quantity : h5py.Group
            'Quantity' group object of the opened HDF5 file.
        reg_names : list of str
            List of region names.
        dim_names : list of str, optional
            List of dimension names. Default is None, which sets it to ["-"].
        unit : str, optional
            Unit of the quantity. Default is an empty string.

        """
        if dim_names is None:
            dim_names = ["-"]
        ds_dim_name = grp_quantity.create_dataset(
            "DOFNames", shape=(len(dim_names),), dtype=h5py.special_dtype(vlen=bytes)
        )
        for i in range(len(dim_names)):
            ds_dim_name[i] = dim_names[i].encode("utf-8")
        ds_entity_name = grp_quantity.create_dataset(
            "EntityNames", shape=(len(reg_names),), dtype=h5py.special_dtype(vlen=bytes)
        )
        for i in range(len(reg_names)):
            ds_entity_name[i] = reg_names[i]
        grp_quantity.create_dataset("Unit", data=unit, dtype=h5py.special_dtype(vlen=bytes))

    @staticmethod
    def create_step(
        grp_multi_step: h5py.Group,
        step_value: float = 0,
        step_num: int = 1,
        filename_external: str = "",
    ) -> h5py.Group:
        """
        Create a step in MultiStep without updating LastStep-Attributes and ResultDescription for increased performance.

        Parameters
        ----------
        grp_multi_step : h5py.Group
            'MultiStep' group object of the opened HDF5 file.
        step_value : float, optional
            Value of the step. Default is 0.
        step_num : int, optional
            Number of the step. Default is 1.
        filename_external : str, optional
            Name of the external file. Default is an empty string.

        Returns
        -------
        h5py.Group
            'Step' group object of the opened HDF5 file.

        """
        # Create Step
        grp_step = grp_multi_step.require_group(f"Step_{step_num}")
        grp_step.attrs.create("StepValue", data=step_value, dtype=np.dtype("float64"))

        if filename_external:
            grp_step.require_dataset(
                "ExtHDF5FileName",
                data=filename_external,
                dtype=h5py.special_dtype(vlen=bytes),
            )

        return grp_step

    @staticmethod
    def create_step_add(
        grp_multi_step: h5py.Group,
        q_list: List[str],
        step_value: float = 0,
        filename_external: str = "",
    ) -> h5py.Group:
        """
        Create a step in MultiStep updating LastStep-Attributes and ResultDescription.

        Parameters
        ----------
        grp_multi_step : h5py.Group
            'MultiStep' group object of the opened HDF5 file.
        q_list : list of str
            List of quantities to be updated.
        step_value : float, optional
            Value of the step. Default is 0.
        filename_external : str, optional
            Name of the external file, if present.
            Default is an empty string, indicating that no external file is present.
            Creates the attribute "ExtHDF5FileName" and passes the given filename_external.
            Overwrites existing attibutes.

        Returns
        -------
        h5py.Group
            'Step' group object of the opened HDF5 file.

        """
        step_num = CFSWriter.add_step_update_attributes(grp_multi_step, q_list, step_value)
        # Create Step
        grp_step = grp_multi_step.require_group(f"Step_{step_num}")
        grp_step.attrs.create("StepValue", data=step_value, dtype=np.dtype("float64"))

        if filename_external:
            grp_step.attrs.create("ExtHDF5FileName", data=filename_external, dtype=h5py.special_dtype(vlen=bytes))
        return grp_step

    @staticmethod
    def set_step_attributes(
        grp_multi_step: h5py.Group,
        q_list: List[str],
        step_values: np.ndarray,
        step_nums: np.ndarray | None = None,
        process_step_groups: bool = True,
    ) -> None:
        """
        Set step values and numbers.

        Parameters
        ----------
        grp_multi_step : h5py.Group
            'MultiStep' group object of the opened HDF5 file.
        q_list : list of str
            List of quantities to be updated.
        step_values : numpy.ndarray
            Array of step values.
        step_nums : numpy.ndarray, optional
            Array of step numbers. If None, step numbers are generated in ascending order.
        process_step_groups : bool, optional
            Indicate if the step attributes (step number and step value) should be updated or not.
            Default is True.
        Returns
        -------
        None

        """
        # Number steps axcending if not specified
        if step_nums is None:
            step_nums = np.array([i + 1 for i in range(step_values.shape[0])])
        # Get Step Numbers and Values from description
        dset_step_numbers = [
            grp_multi_step["ResultDescription/" + q_list[i] + "/StepNumbers"] for i in range(len(q_list))
        ]
        dset_step_values = [
            grp_multi_step["ResultDescription/" + q_list[i] + "/StepValues"] for i in range(len(q_list))
        ]
        # Update Attributes
        grp_multi_step.attrs["LastStepNum"] = step_nums[-1]
        grp_multi_step.attrs["LastStepValue"] = step_values[-1]
        # Update Result Description
        for dset in dset_step_numbers:
            dset.resize(step_values.shape[0], axis=0)
            dset[...] = step_nums
        for dset in dset_step_values:
            dset.resize(step_values.shape[0], axis=0)
            dset[...] = step_values

        # Update Step attributes
        if process_step_groups:
            for stp_idx, step_num in enumerate(step_nums):
                grp_stp = grp_multi_step[f"Step_{step_num}"]
                grp_stp.attrs["StepValue"] = step_values[stp_idx]

        return

    @staticmethod
    def add_step_update_attributes(grp_multi_step: h5py.Group, q_list: List[str], step_value: float = 0) -> int:
        """
        Add step and update (last) step values and numbers.

        Parameters
        ----------
        grp_multi_step : h5py.Group
            'MultiStep' group object of the opened HDF5 file.
        q_list : list of str
            List of quantities to be updated.
        step_value : float, optional
            Value of the step. Default is 0.

        Returns
        -------
        int
            The step number.

        """
        # Get Step Numbers and Values from description
        dset_step_numbers = [
            grp_multi_step["ResultDescription/" + q_list[i] + "/StepNumbers"] for i in range(len(q_list))
        ]
        dset_step_values = [
            grp_multi_step["ResultDescription/" + q_list[i] + "/StepValues"] for i in range(len(q_list))
        ]
        # Update Attributes
        step_num = grp_multi_step.attrs["LastStepNum"] + 1
        grp_multi_step.attrs["LastStepNum"] += 1
        grp_multi_step.attrs["LastStepValue"] = step_value
        # Update Result Description
        for dset in dset_step_numbers:
            dset.resize(dset.shape[0] + 1, axis=0)
            dset[dset.shape[0] - 1] = step_num
        for dset in dset_step_values:
            dset.resize(dset.shape[0] + 1, axis=0)
            dset[dset.shape[0] - 1] = step_value

        return step_num

    @staticmethod
    def create_step_result(
        grp_step: h5py.Group,
        quantity: str,
        region: str,
        defined_on: str | cfs_result_type,
        shape: tuple,
        is_complex=False,
        filename_external: str | None = None,
        filename_master: str = "",
        compression_lvl: int = 6,
    ) -> Tuple[List[h5py.Group], h5py.File]:
        """
        Create a result in a step.

        Parameters
        ----------
        grp_step : h5py.Group
            'Step' group object of the opened HDF5 file.
        quantity : str
            Name of the quantity.
        region : str
            Name of the region.
        defined_on : str or cfs_result_type
            Type of result definition.
        shape : tuple
            Shape of the dataset.
        is_complex : bool, optional
            Flag indicating if the data is complex. Default is False.
        filename_external : str or None, optional
            Name of the external file. Default is None.
        filename_master : str, optional
            Name of the master file. Default is an empty string.
        compression_lvl : int, optional
            GZIP compression level. Default is 6.

        Returns
        -------
        tuple of list of h5py.Group and h5py.File
            Dataset object of the opened HDF5 file and file handle of the opened HDF5 file for external data.

        """
        if is_complex:
            result_name = ["Real", "Imag"]
        else:
            result_name = ["Real"]

        if filename_external:
            f_external = CFSWriter.create_external(filename_external, filename_master, grp_step.name)
            grp_data = f_external.require_group(f"{quantity}/{region}/{defined_on}")
        else:
            f_external = None
            grp_data = grp_step.require_group(f"{quantity}/{region}/{defined_on}")

        ds_data = []
        for name in result_name:
            ds_data.append(
                grp_data.require_dataset(
                    name,
                    shape=shape,
                    dtype=np.dtype("float64"),
                    compression="gzip",
                    compression_opts=compression_lvl,
                )
            )

        return ds_data, f_external

    @staticmethod
    def write_step_result(ds_data: h5py.Dataset, data, f_external: h5py.File = None):
        """
        Write step result data to the dataset.

        Parameters
        ----------
        ds_data : h5py.Dataset
            Dataset object of the opened HDF5 file.
        data : numpy.ndarray
            Data to write to the dataset.
        f_external : h5py.File, optional
            File handle of the opened HDF5 file for external data. Default is None.
        """
        CFSWriter.write_dataset(ds_data, data.astype(np.float64))

        if f_external:
            f_external.close()

    @staticmethod
    def create_external(filename_external: str, filename_master: str, masterGroup: str) -> h5py.File:
        """
        Create an external HDF5 file for storing data.

        Parameters
        ----------
        filename_external : str
            Name of the external file.
        filename_master : str
            Name of the master file.
        step_name : str
            Name of the step.

        Returns
        -------
        h5py.File
            File handle of the opened external HDF5 file.

        """
        f_external = h5py.File(os.path.join(filename_external, ".h5"), "a")

        f_external.attrs.create("MasterGroup", data=masterGroup, dtype=h5py.special_dtype(vlen=bytes))
        f_external.attrs.create(
            "MasterHDF5FileName",
            data=filename_master,
            dtype=h5py.special_dtype(vlen=bytes),
        )

        return f_external

    def write_history_multistep(
        self,
        result: CFSResultContainer | Sequence[CFSResultArray],
        multi_step_id=1,
        analysis_type: cfs_analysis_type | None = None,
        perform_check=True,
    ):
        """
        Write history data. Write ResultDescription and create datasets, write data to MultiStep. (AI-generated)

        Parameters
        ----------
        result : CFSResultContainer or Sequence[CFSResultArray]
            Data structure containing all information about the multiStep that will be written to the active file.
        multi_step_id : int, optional
            Identifier for the multi-step. Default is 1.
        analysis_type : cfs_analysis_type, optional
            Type of analysis being performed. Default is cfs_analysis_type.NO_ANALYSIS.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     results = f.HistoryData
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.write_history_multistep(result=results)
        """
        result_data = CFSResultContainer.require_container(result=result, verbosity=self._Verbosity)

        if perform_check:
            result_data.check_result()

        if analysis_type is None:
            analysis_type = result_data.AnalysisType

        for result_array in result_data.Data:

            if result_array.ResType in [cfs_result_type.NODE, cfs_result_type.ELEMENT]:
                # Consider different folder structure for node and element history results
                raise NotImplementedError(
                    f"Writing of {result_array.ResultInfo} as History Result not supported. Use 'write_multistep' instead."
                )

            # Check and correct array dimensions
            if result_array.ndim == 1:
                result_array = result_array.reshape((result_array.size, 1))  # type: ignore[assignment]

            with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
                grp_result_history = CFSWriter.get_create_history_result(f["Results"])

                grp_multi_step, grp_result_description = CFSWriter.get_create_multistep(
                    grp_result_history, multi_step_id=multi_step_id, analysis_type=analysis_type
                )

                qName = str(result_array.Quantity) if result_array.Quantity is not None else ""
                CFSWriter.create_result_description(
                    grp_resultDescription=grp_result_description,
                    qName=qName,
                    dim_names=result_array.DimNames,
                    definedOn=result_array.ResType,
                    step_values=result_array.StepValues,
                )

                if result_array.Quantity is None or result_array.Region is None:
                    raise ValueError(f"Region {result_array.__repr__()} not properly defined!")

                # Create history result
                if result_array.IsComplex:
                    result_name = ["Real", "Imag"]
                else:
                    result_name = ["Real"]

                quantity = result_array.Quantity
                region = result_array.Region
                res_type = result_array.ResType

                grp_data = grp_multi_step.require_group(f"{quantity}/{res_type}/{region}")

                ds_data = []
                for name in result_name:
                    ds_data.append(
                        grp_data.require_dataset(
                            name,
                            shape=result_array.shape,
                            dtype=np.dtype("float64"),
                            compression="gzip",
                            compression_opts=self.CompressionLvl,
                        )
                    )

                dname = "Real"
                data_write = result_array.real
                dset = f[f"Results/History/MultiStep_{multi_step_id}/{quantity}/{res_type}/{region}/{dname}"]
                CFSWriter.write_step_result(dset, data_write)

                if result_array.IsComplex:
                    dname = "Imag"
                    data_write = result_array.imag
                    dset = f[f"Results/History/MultiStep_{multi_step_id}/{quantity}/{res_type}/{region}/{dname}"]
                    CFSWriter.write_step_result(dset, data_write)

        self.finalize_write_multistep(res_info=result_data.ResultInfo, multi_step_id=multi_step_id, is_history=True)
        # CFSWriter.finalize_result_description(
        #     grp_quantity=f[f"Results/History/MultiStep_{multi_step_id}/ResultDescription/{quantity}"],
        #     reg_names=[region],
        #     dim_names=result_array.DimNames,
        # )

    def prepare_write_multistep(
        self,
        res_info: List[CFSResultInfo],
        multi_step_id=1,
        analysis_type=cfs_analysis_type.NO_ANALYSIS,
    ):
        """
        Write ResultDescription and create datasets (needs to be done a priori in case of parallel write).

        Parameters
        ----------
        res_info : list of CFSResultInfo
            List containing single MultiStep results only.
        res_shape_dict : dict of str to tuple of int
            Dictionary mapping result names to their shapes.
        multi_step_id : int, optional
            Identifier for the multi-step. Default is 1.
        analysis_type : cfs_analysis_type, optional
            Type of analysis being performed. Default is cfs_analysis_type.NO_ANALYSIS.

        """
        for info in res_info:
            if info.ResType not in [cfs_result_type.NODE, cfs_result_type.ELEMENT]:
                raise NotImplementedError(
                    f"Writing of {info} as Mesh Result not supported. "
                    f"Mesh results only supported for {[cfs_result_type.NODE, cfs_result_type.ELEMENT]}. "
                    "Use 'write_history_multistep' instead."
                )

        # Create Result
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            grp_result_mesh = CFSWriter.get_create_mesh_result(f["Results"])
            grp_multi_step, grp_result_description = CFSWriter.get_create_multistep(
                grp_result_mesh, multi_step_id=multi_step_id, analysis_type=analysis_type
            )
            q_set = set()
            for r_info in res_info:
                vprint(
                    f"Initializing result: {r_info}",
                    verbose=self._Verbosity >= v_def.debug,
                )
                if r_info.Quantity is None:
                    raise ValueError(f"Region {r_info.__repr__()} not properly defined!")
                CFSWriter.create_result_description(
                    grp_result_description,
                    r_info.Quantity,
                    dim_names=r_info.DimNames,
                    definedOn=r_info.ResType,
                )
                q_set.add(r_info.Quantity)

            q_list: List[str] = list(q_set)
            # Get Step Values from description
            dset_step_values = [grp_multi_step[f"ResultDescription/{q_list[i]}/StepValues"] for i in range(len(q_list))]
            step_values_overwrite = []
            for step_value in progressbar(
                res_info[0].StepValues,
                "Checking Data for write: ",
                30,
                verbose=self._Verbosity >= v_def.more,
            ):
                # Check if step exists
                if all([step_value in dset for dset in dset_step_values]):
                    step_values_overwrite.append(step_value)
            # Set step values apriori in result description
            CFSWriter.set_step_attributes(
                grp_multi_step, q_list, step_values=res_info[0].StepValues, process_step_groups=False
            )
            # counter = 0
            for step_idx, step_value in enumerate(
                progressbar(
                    res_info[0].StepValues,
                    prefix="Creating Step: ",
                    size=40,
                    verbose=self._Verbosity >= v_def.more,
                )
            ):
                # for step_value in progressbar(res_info[0].StepValues, f"Creating Step: ", 40,
                #                               verbose=self.Verbosity >= v_def.debug):
                # counter += 1
                # vprint(f'Creating Step {counter} (Step Value: {float(step_value)})', verbose=self.Verbosity >= v_def.debug)

                step_num = step_idx + 1
                if step_value in step_values_overwrite:
                    step_num = int(np.where(np.array(dset_step_values[0]) == step_value)[0].item() + 1)
                    grp_stp = grp_multi_step[f"Step_{step_num}"]
                else:
                    # grp_stp = CFSWriter.create_step_add(grp_multi_step, q_list, step_value=step_value)
                    grp_stp = CFSWriter.create_step(grp_multi_step, step_value=step_value, step_num=step_num)
                for r_info in res_info:
                    if r_info.Quantity is None or r_info.Region is None:
                        raise ValueError(f"Region {r_info.__repr__()} not properly defined!")
                    CFSWriter.create_step_result(
                        grp_stp,
                        r_info.Quantity,
                        r_info.Region,
                        r_info.ResType,
                        r_info.DataShape[1:],
                        is_complex=r_info.IsComplex,
                        compression_lvl=self.CompressionLvl,
                    )

    def perform_write_multistep(self, result_data: CFSResultContainer, multi_step_id: int | None = None):
        """
        Write data to MultiStep.

        Parameters
        ----------
        result_data : CFSResultContainer
            Data structure containing all information about the multiStep that will be written to the active file.
        multi_step_id : int, optional
            Identifier for the multi-step. Default is None.

        """
        if multi_step_id is None:
            multi_step_id = result_data.MultiStepID
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            for stepnum in progressbar(
                range(len(result_data.StepValues)),
                "Writing Step:  ",
                40,
                verbose=self._Verbosity >= v_def.release,
            ):
                for data in result_data.Data:
                    q_name = data.Quantity
                    reg = data.Region
                    res_type = data.ResType
                    dname = "Real"
                    data_write = data[stepnum, ...].real
                    dset = f[
                        f"Results/Mesh/MultiStep_{multi_step_id}/Step_{stepnum + 1}/{q_name}/{reg}/{res_type}/{dname}"
                    ]

                    CFSWriter.write_step_result(dset, data_write)

                    if data.IsComplex:
                        dname = "Imag"
                        data_write = data[stepnum, ...].imag
                        dset = f[
                            f"Results/Mesh/MultiStep_{multi_step_id}/Step_{stepnum + 1}/{q_name}/{reg}/{res_type}/{dname}"
                        ]

                        CFSWriter.write_step_result(dset, data_write)

    def rename_quantities(self, quant_name_dict: Dict[str, str], multi_step_id: int = 1):
        """
        Rename available result quantities to specified names, directly in the hdf5 file.
        So far, only implemented for mesh results and history node results.

        Parameters
        ----------
        quant_name_dict : dict of str to str
            Dictionary mapping original quantity names to new quantity names.
        multi_step_id : int, optional
            Identifier for the multi-step. Default is 1.

        Examples
        --------
        >>> from pyCFS.data.io import CFSWriter
        >>> quant_name_dict = {'quantity': 'new_quantity'}
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.rename_quantities(quant_name_dict):
        """

        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            # check if mesh results are present
            if "Mesh" in f["Results"]:
                process_mesh = True
                grp_result_mesh = f["Results"]["Mesh"]
                grp_multi_step = CFSWriter.get_create_multistep(grp_result_mesh, multi_step_id=multi_step_id)[0]
            else:
                process_mesh = False
            # check if history results are present
            if "History" in f["Results"]:
                process_hist = True
                grp_result_history = f["Results"]["History"]
                grp_multi_step_history = CFSWriter.get_create_multistep(
                    grp_result_history, multi_step_id=multi_step_id
                )[0]
            else:
                process_hist = False

            # loop over quantities to change
            for quant_orig, quant_new in quant_name_dict.items():
                # Rename the dataset path
                orig_res_descr_path = f"ResultDescription/{quant_orig}"
                new_res_descr_path = f"ResultDescription/{quant_new}"
                # process mesh data
                if process_mesh:
                    if orig_res_descr_path in grp_multi_step and orig_res_descr_path != new_res_descr_path:
                        if new_res_descr_path in grp_multi_step:
                            # Check if all but the regions are equal
                            if (
                                np.array_equal(
                                    grp_multi_step[f"{orig_res_descr_path}/DOFNames"][:],
                                    grp_multi_step[f"{new_res_descr_path}/DOFNames"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step[f"{orig_res_descr_path}/DefinedOn"][:],
                                    grp_multi_step[f"{new_res_descr_path}/DefinedOn"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step[f"{orig_res_descr_path}/EntryType"][:],
                                    grp_multi_step[f"{new_res_descr_path}/EntryType"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step[f"{orig_res_descr_path}/NumDOFs"][:],
                                    grp_multi_step[f"{new_res_descr_path}/NumDOFs"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step[f"{orig_res_descr_path}/StepNumbers"][:],
                                    grp_multi_step[f"{new_res_descr_path}/StepNumbers"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step[f"{orig_res_descr_path}/StepValues"][:],
                                    grp_multi_step[f"{new_res_descr_path}/StepValues"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step[f"{orig_res_descr_path}/Unit"][:],
                                    grp_multi_step[f"{new_res_descr_path}/Unit"][:],
                                )
                            ):
                                # Find matching regions between old and new
                                entity_names_orig = grp_multi_step[f"{orig_res_descr_path}/EntityNames"][:]
                                # Convert bytes to strings for comparison
                                entity_names_new = grp_multi_step[f"{new_res_descr_path}/EntityNames"][:]
                                matching_regions = np.intersect1d(entity_names_orig, entity_names_new)
                                if len(matching_regions) == 0:
                                    # try merging the datasets if they only differ by regions
                                    entity_names_update = np.concatenate([entity_names_orig, entity_names_new])
                                    # Delete the old EntityNames dataset and create the updated one
                                    del grp_multi_step[f"{new_res_descr_path}/EntityNames"]
                                    grp_multi_step[f"{new_res_descr_path}"].create_dataset(
                                        "EntityNames",
                                        shape=(len(entity_names_update),),
                                        dtype=h5py.special_dtype(vlen=bytes),
                                        data=entity_names_update,
                                    )
                                    print(f"Merged regions: {orig_res_descr_path} --> {new_res_descr_path}")
                                    # Delete the old ResultDescription
                                    del grp_multi_step[orig_res_descr_path]
                                    print(f"Deleted path: Results/Mesh/MultiStep_{multi_step_id}/{orig_res_descr_path}")
                                    # rename the step groups
                                    step_numbers = grp_multi_step[new_res_descr_path + "/StepNumbers"][:]
                                    for it_step in step_numbers:
                                        # move regions individually
                                        for it_reg in entity_names_orig:
                                            orig_step_path = f"Step_{it_step}/{quant_orig}/{it_reg.decode('utf-8')}"
                                            new_step_path = f"Step_{it_step}/{quant_new}/{it_reg.decode('utf-8')}"
                                            grp_multi_step.move(orig_step_path, new_step_path)
                                            print(
                                                f"Renamed path: Results/Mesh/MultiStep_{multi_step_id}/{orig_step_path} "
                                                f"--> Results/Mesh/MultiStep_{multi_step_id}/{new_step_path}"
                                            )
                                        rm_path = f"Step_{it_step}/{quant_orig}/"
                                        del grp_multi_step[rm_path]
                                        print(f"Deleted path: Results/Mesh/MultiStep_{multi_step_id}/{rm_path}")
                                else:
                                    raise ValueError(
                                        f"Merging quantity {quant_new} into {quant_orig} not possible. There must not be any overlapping regions (EntityNames)!"
                                    )
                            else:
                                raise ValueError(
                                    f"Merging quantity {quant_new} into {quant_orig} not possible. "
                                    "All ResultDescription parameters except the regions (EntityNames) must match exactly!"
                                )
                        else:
                            # mesh results...
                            grp_multi_step.move(orig_res_descr_path, new_res_descr_path)
                            print(
                                f"Renamed path: Results/Mesh/MultiStep_{multi_step_id}/{orig_res_descr_path} "
                                f"--> Results/Mesh/MultiStep_{multi_step_id}/{new_res_descr_path}"
                            )
                            # rename the step groups
                            step_numbers = grp_multi_step[new_res_descr_path + "/StepNumbers"][:]
                            for it_step in step_numbers:
                                orig_step_path = f"Step_{it_step}/{quant_orig}"
                                new_step_path = f"Step_{it_step}/{quant_new}"
                                grp_multi_step.move(orig_step_path, new_step_path)
                                print(
                                    f"Renamed path: Results/Mesh/MultiStep_{multi_step_id}/{orig_step_path} "
                                    f"--> Results/Mesh/MultiStep_{multi_step_id}/{new_step_path}"
                                )

                # process history data
                if process_hist:
                    if orig_res_descr_path in grp_multi_step_history and orig_res_descr_path != new_res_descr_path:
                        if new_res_descr_path in grp_multi_step_history:
                            # Check if all but the regions are equal
                            if (
                                np.array_equal(
                                    grp_multi_step_history[f"{orig_res_descr_path}/DOFNames"][:],
                                    grp_multi_step_history[f"{new_res_descr_path}/DOFNames"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step_history[f"{orig_res_descr_path}/DefinedOn"][:],
                                    grp_multi_step_history[f"{new_res_descr_path}/DefinedOn"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step_history[f"{orig_res_descr_path}/EntryType"][:],
                                    grp_multi_step_history[f"{new_res_descr_path}/EntryType"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step_history[f"{orig_res_descr_path}/NumDOFs"][:],
                                    grp_multi_step_history[f"{new_res_descr_path}/NumDOFs"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step_history[f"{orig_res_descr_path}/StepNumbers"][:],
                                    grp_multi_step_history[f"{new_res_descr_path}/StepNumbers"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step_history[f"{orig_res_descr_path}/StepValues"][:],
                                    grp_multi_step_history[f"{new_res_descr_path}/StepValues"][:],
                                )
                                and np.array_equal(
                                    grp_multi_step_history[f"{orig_res_descr_path}/Unit"][:],
                                    grp_multi_step_history[f"{new_res_descr_path}/Unit"][:],
                                )
                            ):
                                # Find matching regions between old and new
                                entity_names_orig = grp_multi_step_history[f"{orig_res_descr_path}/EntityNames"][:]
                                # Convert bytes to strings for comparison
                                entity_names_new = grp_multi_step_history[f"{new_res_descr_path}/EntityNames"][:]
                                matching_regions = np.intersect1d(entity_names_orig, entity_names_new)
                                if len(matching_regions) == 0:
                                    # try merging the datasets if they only differ by regions
                                    entity_names_update = np.concatenate([entity_names_orig, entity_names_new])
                                    # Delete the old EntityNames dataset and create the updated one
                                    del grp_multi_step_history[f"{new_res_descr_path}/EntityNames"]
                                    grp_multi_step_history[f"{new_res_descr_path}"].create_dataset(
                                        "EntityNames",
                                        shape=(len(entity_names_update),),
                                        dtype=h5py.special_dtype(vlen=bytes),
                                        data=entity_names_update,
                                    )
                                    print(f"Merged regions: {orig_res_descr_path} --> {new_res_descr_path}")
                                    # Delete the old ResultDescription
                                    del grp_multi_step_history[orig_res_descr_path]
                                    print(
                                        f"Deleted path: Results/History/MultiStep_{multi_step_id}/{orig_res_descr_path}"
                                    )
                                    # rename the node/element groups...
                                    # here we need to check for the result type as it occurs in the path name
                                    res_type = cfs_result_type(
                                        int(grp_multi_step_history[f"{new_res_descr_path}/DefinedOn"][0])
                                    )
                                    if res_type == cfs_result_type.NODE:
                                        nodes_orig_path = f"{quant_orig}/Nodes"
                                        nodes_new_path = f"{quant_new}/Nodes"
                                    else:
                                        raise NotImplementedError(
                                            f"Renaming Quantity '{quant_orig}' with result type '{res_type}' is not possible."
                                            f"The result type is not implemented or untested."
                                        )
                                    nodes_orig = list(grp_multi_step_history[f"{nodes_orig_path}"].keys())
                                    nodes_new = list(grp_multi_step_history[f"{nodes_new_path}"].keys())
                                    matching_nodes = np.intersect1d(nodes_orig, nodes_new)
                                    if len(matching_nodes) == 0:
                                        for i_node in nodes_orig:
                                            grp_multi_step_history.move(
                                                f"{nodes_orig_path}/{i_node}", f"{nodes_new_path}/{i_node}"
                                            )
                                            print(
                                                f"Renamed path: Results/History/MultiStep_{multi_step_id}/{nodes_orig_path}/{i_node} "
                                                f"--> Results/History/MultiStep_{multi_step_id}/{nodes_new_path}/{i_node}"
                                            )
                                        del grp_multi_step_history[f"{quant_orig}"]
                                        print(f"Deleted path: Results/History/MultiStep_{multi_step_id}/{quant_orig}")
                                    else:
                                        raise ValueError(
                                            f"Merging quantity {quant_new} into {quant_orig} not possible."
                                            f"There must not be any overlapping nodes in the history results!"
                                        )
                                else:
                                    raise ValueError(
                                        f"Merging quantity {quant_new} into {quant_orig} not possible. There must not be any overlapping regions (EntityNames)!"
                                    )
                            else:
                                raise ValueError(
                                    f"Merging quantity {quant_new} into {quant_orig} not possible. "
                                    "All ResultDescription parameters except the regions (EntityNames) must match exactly!"
                                )
                        else:
                            grp_multi_step_history.move(orig_res_descr_path, new_res_descr_path)
                            print(
                                f"Renamed path: Results/History/MultiStep_{multi_step_id}/{orig_res_descr_path} --> "
                                f"Results/History/MultiStep_{multi_step_id}/{new_res_descr_path}"
                            )
                            # rename the node/elem groups
                            orig_step_path = f"{quant_orig}"
                            new_step_path = f"{quant_new}"
                            grp_multi_step_history.move(orig_step_path, new_step_path)
                            print(
                                f"Renamed path: Results/History/MultiStep_{multi_step_id}/{orig_step_path} --> "
                                f"Results/History/MultiStep_{multi_step_id}/{new_step_path}"
                            )
                    else:
                        print(f"Skipped renaming quantity name: {quant_orig}.")

    def finalize_write_multistep(self, res_info: List[CFSResultInfo], multi_step_id=1, is_history=False):
        """
        Write datasets to ResultsDescription that need to be written after the data (in case of parallel write).

        Parameters
        ----------
        res_info : list of CFSResultInfo
            List containing single MultiStep results only.
        multi_step_id : int, optional
            Identifier for the multi-step. Default is 1.

        """
        result_def = cfs_types.is_history_dict[is_history]

        reg_dict: Dict[str, List[str]] = dict()
        dim_names_dict: Dict[str, List[str]] = dict()
        for r_info in res_info:
            if r_info.Quantity is None or r_info.Region is None:
                raise ValueError(f"Region {r_info.__repr__()} not properly defined!")
            if r_info.Quantity in reg_dict:
                reg_dict[r_info.Quantity].append(r_info.Region)
                if r_info.DimNames != dim_names_dict[r_info.Quantity]:
                    raise Exception("Dimension labels of single quantity must be the same for all result arrays!")
            else:
                reg_dict[r_info.Quantity] = [r_info.Region]
                dim_names_dict[r_info.Quantity] = r_info.DimNames

        with h5py.File(self._filename, "r+") as f:
            for q_name in reg_dict:
                vprint(
                    f"Finalizing result: {q_name}",
                    verbose=self._Verbosity >= v_def.debug,
                )
                CFSWriter.finalize_result_description(
                    f[f"Results/{result_def}/MultiStep_{multi_step_id}/ResultDescription/{q_name}"],
                    reg_dict[q_name],
                    dim_names_dict[q_name],
                )

    def write_mesh_multistep(
        self,
        result: CFSResultContainer | Sequence[CFSResultArray],
        multi_step_id: int | None = None,
        analysis_type: cfs_analysis_type | None = None,
        perform_check: bool = True,
    ):
        """
        Write ResultDescription and create datasets, write data to multistep and write datasets to ResultsDescription
        that need to be written after the data (in case of parallel write)

        Parameters
        ----------
        result : CFSResultContainer or Sequence[CFSResultArray]
            Data structure containing all information about the multiStep that will be written to the active file.
        multi_step_id : int, optional
            Identifier for the multi-step. Default is None.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     results = f.MultiStepData
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.write_multistep(result=results)

        """
        result_data = CFSResultContainer.require_container(result=result, verbosity=self._Verbosity)

        if perform_check:
            result_data.check_result()

        if analysis_type is None:
            analysis_type = result_data.AnalysisType

        if multi_step_id is None:
            multi_step_id = result_data.MultiStepID

        self.prepare_write_multistep(
            res_info=result_data.ResultInfo, multi_step_id=multi_step_id, analysis_type=analysis_type
        )
        self.perform_write_multistep(result_data=result_data, multi_step_id=multi_step_id)
        self.finalize_write_multistep(res_info=result_data.ResultInfo, multi_step_id=multi_step_id, is_history=False)

    def write_multistep(
        self,
        result: CFSResultContainer | Sequence[CFSResultArray],
        multi_step_id: int | None = None,
        analysis_type: cfs_analysis_type | None = None,
        perform_check: bool = True,
    ):
        """
        Write ResultDescription and create datasets, write data to multistep and write datasets to ResultsDescription
        that need to be written after the data (in case of parallel write)

        Parameters
        ----------
        result : CFSResultContainer or Sequence[CFSResultArray]
            Data structure containing all information about the multiStep that will be written to the active file.
        multi_step_id : int, optional
            Identifier for the multi-step. Default is None.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     results = f.MultiStepData
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.write_multistep(result=results)

        """
        result_data = CFSResultContainer.require_container(result=result, verbosity=self._Verbosity)

        if perform_check:
            result_data.check_result()

        if analysis_type is None:
            analysis_type = result_data.AnalysisType

        if multi_step_id is None:
            multi_step_id = result_data.MultiStepID

        data_mesh = []
        data_history = []
        for result_array in result_data.Data:
            if result_array.ResType in [cfs_result_type.NODE, cfs_result_type.ELEMENT]:
                data_mesh.append(result_array)
            else:
                data_history.append(result_array)

        if data_mesh:
            result_data_mesh = CFSResultContainer(
                data=data_mesh, analysis_type=analysis_type, multi_step_id=multi_step_id, verbosity=self._Verbosity
            )
            self.write_mesh_multistep(
                result=result_data_mesh,
                multi_step_id=multi_step_id,
                analysis_type=analysis_type,
                perform_check=False,
            )
        if data_history:
            result_data_history = CFSResultContainer(
                data=data_history, analysis_type=analysis_type, multi_step_id=multi_step_id, verbosity=self._Verbosity
            )
            self.write_history_multistep(
                result=result_data_history,
                multi_step_id=multi_step_id,
                analysis_type=analysis_type,
                perform_check=False,
            )

    def add_steps_to_multistep(
        self,
        add_step_values: np.ndarray,
        q_list: List[str],
        multi_step_id: int = 1,
        external_file_names: Sequence[str] | None = None,
    ):
        """
        Add additional result steps to the end of an existing MultiStep.

        Parameters
        ----------
        add_step_values : np.ndarray[float]
            Values of the added steps
        q_list : List[str]
            All quantities contained in the given multistep (can be determined via the CFSReaderModule)
        multi_step_id : int, optional
            Identifier for the multi-step. Default is 1.
        external_file_names : Sequence[str], optional
            If the cfs file has external files for steps, the external_file_names are used to set the file names as attributes.
            Must have the same length as add_step_values.
        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     results = f.MultiStepData
        >>>     q_list = f.ResultQuantities
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.add_steps_to_multistep(add_step_values=add_steps, q_list=q_list, 1, ext_file_names)

        """
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            if external_file_names is not None:
                grp_result_mesh = CFSWriter.get_create_mesh_result(f["Results"], externalFiles=True)
                grp_multi_step = CFSWriter.get_create_multistep(grp_result_mesh, multi_step_id)[0]
                if len(external_file_names) != add_step_values.shape[0]:
                    raise ValueError(
                        f"Number of external file names ({len(external_file_names)}) does not match number of step values ({len(add_step_values)})."
                    )
                for i_step, it_step in enumerate(progressbar(add_step_values)):
                    CFSWriter.create_step_add(grp_multi_step, q_list, it_step, external_file_names[i_step])
            else:
                grp_result_mesh = CFSWriter.get_create_mesh_result(f["Results"])
                grp_multi_step = CFSWriter.get_create_multistep(grp_result_mesh, multi_step_id)[0]
                for i_step, it_step in enumerate(progressbar(add_step_values)):
                    CFSWriter.create_step_add(grp_multi_step, q_list, it_step)

    def round_step_values(self, rounding_digits: int, q_list: List[str], multi_step_id: int = 1):
        """
        Round all step values of the defined multistep to a given amount of digits.

        Parameters
        ----------
        rounding_digits: int
            Given amount of digits to round the step values to.
        q_list : List[str]
            All quantities contained in the given multistep (can be determined via the CFSReaderModule)
        multi_step_id : int, optional
            Identifier for the multi-step. Default is 1.
        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     results = f.MultiStepData
        >>>     q_list = f.ResultQuantities
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.round_step_values(rounding_digits=6, q_list=q_list)

        """
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            grp_result_mesh = CFSWriter.get_create_mesh_result(f["Results"])
            grp_multi_step = CFSWriter.get_create_multistep(grp_result_mesh, multi_step_id)[0]
            for quant in q_list:
                step_values = grp_multi_step["ResultDescription/" + quant + "/StepValues"][:]
                step_numbers = grp_multi_step["ResultDescription/" + quant + "/StepNumbers"][:]
                CFSWriter.set_step_attributes(
                    grp_multi_step, [quant], step_values=np.round(step_values, rounding_digits), step_nums=step_numbers
                )
