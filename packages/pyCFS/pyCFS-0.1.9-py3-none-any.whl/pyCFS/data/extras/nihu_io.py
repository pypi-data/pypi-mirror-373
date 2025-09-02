"""
Module containing data processing utilities for reading NiHu structures as Matlab export files
"""

from __future__ import annotations

import scipy
import numpy as np
from typing import List, Dict

from pyCFS.data.io import cfs_types
from pyCFS.data.extras import nihu_types
from pyCFS.data import io
from pyCFS.data.util import reshape_connectivity


def convert_mesh_to_cfs(nihu_mesh: Dict, reg_name="surface"):
    nodes = np.array(nihu_mesh["Nodes"][0][0])
    elements = np.array(nihu_mesh["Elements"][0][0])

    coordinates = nodes[:, 1:]
    types = nihu_types.nihu_to_cfs_elem_type(elements[:, 1])
    connectivity = elements[:, 4:]

    # Remove columns containing zeros only
    connectivity = reshape_connectivity(connectivity)

    cfs_mesh = io.CFSMeshData(coordinates=coordinates, connectivity=connectivity, types=types)

    reg_all = io.CFSRegData(name=reg_name, dimension=2)
    reg_all.Nodes = np.array([i + 1 for i in range(cfs_mesh.MeshInfo.NumNodes)])
    reg_all.Elements = np.array([i + 1 for i in range(cfs_mesh.MeshInfo.NumElems)])

    cfs_mesh.Regions = [reg_all]

    return cfs_mesh


def convert_mat_to_cfs(
    file_mat: str,
    mat_mesh_name="surface_mesh",
    mat_steps_name="data_freq",
    mat_data_name_list: List[str] | None = None,
    cfs_name_list: List[str] | None = None,
    reg_name="surface",
    restype_list: List | None = None,
    dim_name_dict: Dict | None = None,
):
    if mat_data_name_list is None:
        mat_data_name_list = ["p_surf", "q_surf"]
    if cfs_name_list is None:
        cfs_name_list = ["acouPressure", "acouPressureNormalDerivative"]
    if restype_list is None:
        restype_list = [cfs_types.cfs_result_type.ELEMENT for i in mat_data_name_list]

    print("Reading mat file")
    result_mat = scipy.io.loadmat(file_mat)

    print("Converting mesh")
    cfs_mesh = convert_mesh_to_cfs(nihu_mesh=result_mat[mat_mesh_name], reg_name=reg_name)

    steps = result_mat[mat_steps_name].flatten()
    cfs_result = io.CFSResultContainer(analysis_type=cfs_types.cfs_analysis_type.HARMONIC, multi_step_id=1)
    for i, mat_data_name in enumerate(mat_data_name_list):
        print(f"Converting data: {mat_data_name}")

        if dim_name_dict is None or cfs_name_list[i] not in dim_name_dict:
            if result_mat[mat_data_name].ndim > 2:
                if result_mat[mat_data_name].shape[2] == 3:
                    dim_names = ["x", "y", "z"]
                elif result_mat[mat_data_name].shape[2] == 2:
                    dim_names = ["x", "y"]
                else:
                    dim_names = [f"part {i}" for i in range(result_mat[mat_data_name].shape[2])]
            else:
                dim_names = None
        else:
            dim_names = dim_name_dict[cfs_name_list[i]]

        cfs_result.add_data(
            data=result_mat[mat_data_name],
            step_values=steps,
            quantity=cfs_name_list[i],
            region=reg_name,
            restype=restype_list[i],
            dim_names=dim_names,
            is_complex=True,
        )

    return cfs_mesh, cfs_result
