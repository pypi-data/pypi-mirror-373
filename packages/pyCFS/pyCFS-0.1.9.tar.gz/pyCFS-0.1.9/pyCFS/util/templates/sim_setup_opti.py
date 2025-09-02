from typing import Any, Dict, List
import numpy as np
from py import PyCfs


PyCFSSim = object


def get_setup() -> Dict[str, Any]:
    """

    **get_setup** generates the simulation object file, the optimization setup,
    packages it into a dict and returns it. This function
    is intended to be extended such that it contains all of the needed configuration
    parameters and setup information.

    Returns:
        Dict (str: Any): Dictionary containing the simulation object
                         and the optimization setup
    """

    # Set up project :
    project_name = "PROJECT_NAME"

    # set path to cfs on your system :
    cfs_path = "CFS_PATH"
    mesher_alias = "MESHER_ALIAS"

    num_threads = 1

    # Set simulation parameter names :
    cfs_params: List[str] = []
    mat_params: List[str] = []
    trelis_params: List[str] = []

    # Set initial parameter vector ( length is equal to : len(cfs_params)
    # + len(mat_params) + len(trelis_params))
    init_params = np.array([], dtype=np.float32)

    # define parameter ranges :
    ranges = np.array([], dtype=np.float32)

    # Empty dictionary for the optimization setup :
    opti_setup: Dict[str, Any] = {}

    opti_setup["ranges"] = ranges
    opti_setup["n_vars"] = len(cfs_params)
    opti_setup["n_obj"] = 1

    # Construct cfssimulation object :
    # Running this the constructor will perform one forward simulation with the initial parameters

    # to determine all outputs as set up by the initial configuration done previosly.
    opti_setup["sim"] = PyCfs(
        project_name,
        cfs_path,
        init_params,
        cfs_params_names=cfs_params,
        material_params_names=mat_params,
        trelis_params_names=trelis_params,
        trelis_version=mesher_alias,
        n_threads=num_threads,
    )

    return opti_setup


def objective(simulation: PyCFSSim, x: np.ndarray) -> np.ndarray:
    """
        This function calculates the objective values
        used for the optimization process.

    Args:
        simulation (PyCFSSim): PyCFS Simulation object
        x (np.ndarray): parameter array.

    Returns:
        np.ndarray: objective values corresponding to the given parameters.
    """

    objective_val = np.array([0.0])

    return objective_val
