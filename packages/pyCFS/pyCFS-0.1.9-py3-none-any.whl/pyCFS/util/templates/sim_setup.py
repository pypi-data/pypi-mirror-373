# Import the needed libraries :
import numpy as np
from pyCFS import pyCFS
from typing import List


def get_sim() -> pyCFS:
    """

    **get_sim** generates the simulation object file and returns it. This function
    is intended to be extended such that it contains all of the needed configuration
    parameters and setup information.

    Returns:
        sim (pyCFS): pyCFS simulation object
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

    # Construct cfssimulation object :
    # Running this the constructor will perform one forward simulation with the initial parameters

    # to determine all outputs as set up by the initial configuration done previosly.
    sim = pyCFS(
        project_name,
        cfs_path,
        init_params,
        cfs_params_names=cfs_params,
        material_params_names=mat_params,
        trelis_params_names=trelis_params,
        trelis_version=mesher_alias,
        n_threads=num_threads,
    )

    return sim
