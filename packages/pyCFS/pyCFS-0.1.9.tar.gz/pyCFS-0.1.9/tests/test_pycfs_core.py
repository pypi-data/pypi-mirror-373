import numpy as np
from os import path
from .pycfs_fixtures import (
    default_params,
    dummy_params,
    default_pycfs_obj,
    dummy_pycfs_obj,
    dummy_pycfs_project,
    cap3d_pycfs_project,
    DEFAULT_PROJECT,
    DEFAULT_PROJECT_ROOT,
    DEFAULT_CFS_DIR,
    DEFAULT_PARAMS,
    DEFAULT_TEMPLATES_DIR,
    DEFAULT_RESULTS_HDF_PATH,
    DEFAULT_LOGS_PATH,
    DEFAULT_HISTORY_PATH,
    CFS_EXT,
    XML_EXT,
    JOU_EXT,
    CDB_EXT,
)


def test_pycfs_arguments_exist_and_are_set(dummy_pycfs_obj, dummy_params):
    """Tests if all of the pycfs arguments exist and are set correctly
    for the given dummy inputs.

    Args:
        dummy_pycfs_obj (fixture): Dummy object fixture.
        dummy_params (fixture): Dummy params fixture.
    """
    assert dummy_pycfs_obj.project_name == dummy_params.project_name
    assert dummy_pycfs_obj.cfs_install_dir == dummy_params.cfs_path
    assert np.all(dummy_pycfs_obj.params == dummy_params.init_params)
    assert dummy_pycfs_obj.cfs_params_names == dummy_params.cfs_params_names
    assert dummy_pycfs_obj.mat_params_names == dummy_params.material_params_names
    assert dummy_pycfs_obj.trelis_params_names == dummy_params.trelis_params_names
    assert dummy_pycfs_obj.trelis_version == dummy_params.trelis_version
    assert dummy_pycfs_obj.proj_root_path == dummy_params.proj_root_path
    assert dummy_pycfs_obj.templates_dir == dummy_params.templates_dir
    assert dummy_pycfs_obj.init_file_extension == dummy_params.init_file_extension
    assert dummy_pycfs_obj.mat_file_name == dummy_params.mat_file_name
    assert dummy_pycfs_obj.n_threads == dummy_params.n_threads
    assert dummy_pycfs_obj.res_manip_fun == dummy_params.res_manip_fun
    assert dummy_pycfs_obj.quiet_mode == dummy_params.quiet_mode
    assert dummy_pycfs_obj.detail_mode == dummy_params.detail_mode
    assert dummy_pycfs_obj.clean_finish == dummy_params.clean_finish
    assert dummy_pycfs_obj.save_hdf_results == dummy_params.save_hdf_results
    assert dummy_pycfs_obj.array_fill_value == dummy_params.array_fill_value
    assert dummy_pycfs_obj.parallelize == dummy_params.parallelize
    assert dummy_pycfs_obj.remeshing_on == dummy_params.remeshing_on
    assert dummy_pycfs_obj.n_jobs_max == dummy_params.n_jobs_max
    assert dummy_pycfs_obj.testing == dummy_params.testing
    assert dummy_pycfs_obj.track_quantities == dummy_params.track_quantities
    assert dummy_pycfs_obj.track_regions == dummy_params.track_regions
    assert dummy_pycfs_obj.track_quantities_hist == dummy_params.track_quantities_hist
    assert dummy_pycfs_obj.dump_results == dummy_params.dump_results


def test_pycfs_default_arguments(default_pycfs_obj, default_params):
    """Tests if all of the pycfs arguments exist and are set correctly
    for the given default inputs. (Only the required arguments are
    passed to create default_pycfs_obj and checked if others are ok).

    Args:
        default_pycfs_obj (fixture): Default object fixture.
        default_params (fixture): Default params fixture.
    """
    assert default_pycfs_obj.project_name == DEFAULT_PROJECT
    assert default_pycfs_obj.cfs_install_dir == DEFAULT_CFS_DIR
    assert np.all(default_pycfs_obj.params == DEFAULT_PARAMS)
    assert default_pycfs_obj.cfs_params_names == default_params.cfs_params_names
    assert default_pycfs_obj.mat_params_names == default_params.material_params_names
    assert default_pycfs_obj.trelis_params_names == default_params.trelis_params_names
    assert default_pycfs_obj.trelis_version == default_params.trelis_version
    assert default_pycfs_obj.proj_root_path == default_params.proj_root_path
    assert default_pycfs_obj.templates_dir == default_params.templates_dir
    assert default_pycfs_obj.init_file_extension == default_params.init_file_extension
    assert default_pycfs_obj.mat_file_name == default_params.mat_file_name
    assert default_pycfs_obj.n_threads == default_params.n_threads
    assert default_pycfs_obj.res_manip_fun == default_params.res_manip_fun
    assert default_pycfs_obj.quiet_mode == default_params.quiet_mode
    assert default_pycfs_obj.detail_mode == default_params.detail_mode
    assert default_pycfs_obj.clean_finish == default_params.clean_finish
    assert default_pycfs_obj.save_hdf_results == default_params.save_hdf_results
    assert np.isnan(default_pycfs_obj.array_fill_value) and np.isnan(default_params.array_fill_value)
    assert default_pycfs_obj.parallelize == default_params.parallelize
    assert default_pycfs_obj.remeshing_on == default_params.remeshing_on
    assert default_pycfs_obj.n_jobs_max == default_params.n_jobs_max
    assert default_pycfs_obj.testing == default_params.testing
    assert default_pycfs_obj.track_quantities == default_params.track_quantities
    assert default_pycfs_obj.track_regions == default_params.track_regions
    assert default_pycfs_obj.track_quantities_hist == default_params.track_quantities_hist
    assert default_pycfs_obj.dump_results == default_params.dump_results


def test_init_placeholders(default_pycfs_obj):
    """Test if init placeholders are initialized correctly.

    Args:
        default_pycfs_obj (fixture): Default object fixture.
    """
    assert default_pycfs_obj.files == []
    assert np.all(default_pycfs_obj.params_changed == np.ones((4,), dtype=bool))
    assert default_pycfs_obj.results_keys == []
    assert default_pycfs_obj.result_regions == None
    assert default_pycfs_obj.ind == 0
    assert default_pycfs_obj.mesh_present == False


def test_init_filenames(default_pycfs_obj):
    """Test if file names are initialized correctly.

    Args:
        default_pycfs_obj (fixture): Default object fixture.
    """
    temp_ext = default_pycfs_obj.init_file_extension
    mat_file_name = default_pycfs_obj.mat_file_name

    assert default_pycfs_obj.cfs_file_init == path.join(
        DEFAULT_PROJECT_ROOT, DEFAULT_TEMPLATES_DIR, f"{DEFAULT_PROJECT}_{temp_ext}.{XML_EXT}"
    )
    assert default_pycfs_obj.mat_file_init == path.join(
        DEFAULT_PROJECT_ROOT, DEFAULT_TEMPLATES_DIR, f"{mat_file_name}_{temp_ext}.{XML_EXT}"
    )
    assert default_pycfs_obj.jou_file_init == path.join(
        DEFAULT_PROJECT_ROOT, DEFAULT_TEMPLATES_DIR, f"{DEFAULT_PROJECT}_{temp_ext}.{JOU_EXT}"
    )
    assert default_pycfs_obj.cfs_file == path.join(DEFAULT_PROJECT_ROOT, f"{default_pycfs_obj.project_name}.{XML_EXT}")
    assert default_pycfs_obj.jou_file == path.join(DEFAULT_PROJECT_ROOT, f"{default_pycfs_obj.project_name}.{JOU_EXT}")
    assert default_pycfs_obj.mat_file == path.join(DEFAULT_PROJECT_ROOT, f"{mat_file_name}.{XML_EXT}")
    assert default_pycfs_obj.cdb_file == path.join(DEFAULT_PROJECT_ROOT, f"{default_pycfs_obj.project_name}.{CDB_EXT}")
    assert default_pycfs_obj.sim_files == [
        default_pycfs_obj.cfs_file,
        default_pycfs_obj.jou_file,
        default_pycfs_obj.mat_file,
        path.join(DEFAULT_PROJECT_ROOT, f"{default_pycfs_obj.project_name}.info.{XML_EXT}"),
        path.join(DEFAULT_PROJECT_ROOT, f"{default_pycfs_obj.project_name}.{CDB_EXT}"),
    ]


def test_init_paths(default_pycfs_obj):
    """Test if paths are initialized correctly.

    Args:
        default_pycfs_obj (fixture): Default object fixture.
    """
    assert default_pycfs_obj.history_path == f"{DEFAULT_HISTORY_PATH}"
    assert default_pycfs_obj.hdf_res_path == f"{DEFAULT_RESULTS_HDF_PATH}{default_pycfs_obj.project_name}{path.sep}"
    assert default_pycfs_obj.hdf_file_path == f"{DEFAULT_RESULTS_HDF_PATH}{default_pycfs_obj.project_name}.{CFS_EXT}"
    assert default_pycfs_obj.logs_path == f"{DEFAULT_LOGS_PATH}"


def test_init_param_setup(default_pycfs_obj):
    """Test if params are initialized correctly.

    Args:
        default_pycfs_obj (fixture): Default object fixture.
    """
    assert default_pycfs_obj.additional_params_exist == False
    assert default_pycfs_obj.n_base_params == 0
    assert default_pycfs_obj.params_names == []


def test_init_param_parallel(default_pycfs_obj):
    """Test if parallel params are initialized correctly.

    Args:
        default_pycfs_obj (fixture): Default object fixture.
    """
    assert np.all(default_pycfs_obj.cfs_params == DEFAULT_PARAMS)
    assert np.all(default_pycfs_obj.mat_params == DEFAULT_PARAMS)
    assert np.all(default_pycfs_obj.trelis_params == DEFAULT_PARAMS)
    assert np.all(default_pycfs_obj.add_params == DEFAULT_PARAMS)


def test_init_functions(default_pycfs_obj):
    """Test if functions are initialized correctly.

    Args:
        default_pycfs_obj (fixture): Default object fixture.
    """
    assert default_pycfs_obj._forward == default_pycfs_obj._forward_serial
    assert default_pycfs_obj._clean_sim_files_if_on == default_pycfs_obj.dummy_fun_noarg
    assert default_pycfs_obj._save_hdf_results_if_on == default_pycfs_obj.dummy_fun_int_bool
    assert default_pycfs_obj._save_all_hdf_results_if_on == default_pycfs_obj.dummy_fun_noarg
    assert default_pycfs_obj._clean_sim_files_parallel_if_on == default_pycfs_obj.dummy_fun_noarg
    assert default_pycfs_obj._clean_hdf_results_parallel_if_on == default_pycfs_obj._clean_hdf_results_parallel


def test_dummy_project_setup(dummy_pycfs_project):
    """Test if a dummy project (project root at tests/data/sim/dummy)
    gets initialized correctly.

    Args:
        dummy_pycfs_project (fixture): Dummy pycfs problem fixture.
    """

    # Check result initializations :
    assert dummy_pycfs_project.results == []
    assert dummy_pycfs_project.hist_results == []


def test_cap3d_project_run_serial(cap3d_pycfs_project):
    """Test if a dummy project (project root at tests/data/sim/dummy)
    gets initialized correctly.

    Args:
        dummy_pycfs_project (fixture): Dummy pycfs problem fixture.
    """

    # Check result initializations :
    assert cap3d_pycfs_project.results == []
    assert cap3d_pycfs_project.hist_results == []
