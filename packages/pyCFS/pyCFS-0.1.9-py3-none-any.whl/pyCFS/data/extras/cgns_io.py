import os
import shutil
import subprocess
from typing import List

import h5py
import numpy as np

from pyCFS.data.extras.cgns_types import (
    cgns_element_type,
    cgns_element_node_num,
    cgns_to_cfs_elem_type,
    type_link_cgns_cfs,
)
from pyCFS.data.io import CFSRegData, CFSMeshData
from pyCFS.data.io.cfs_types import cfs_element_type, cfs_element_dimension, cfs_element_node_num
from pyCFS.data.util import vprint, apply_dict_vectorized


def reorder_nodes(connectivity: np.ndarray, elem_types: np.ndarray) -> np.ndarray:
    """
    Reorder the nodes in the connectivity array for element types that have different node ordering in cfs than cgns.

    Parameters
    ----------
    connectivity : np.ndarray
        The connectivity array where each row contains the node indices of a certain element in cgns ordering.
    elem_types : np.ndarray
        The array of cfs element types corresponding to each element in the connectivity array.

    Returns
    -------
    np.ndarray
        The reordered connectivity array with cfs node ordering.
    """
    # elements that have different node ordering in cgns and cfs
    reorder_map = {
        cfs_element_type.WEDGE15: [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 9, 10, 11],
        cfs_element_type.WEDGE18: [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 9, 10, 11, 15, 16, 17],
        cfs_element_type.HEXA20: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 19, 12, 13, 14, 15],
        cfs_element_type.HEXA27: [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            16,
            17,
            18,
            19,
            12,
            13,
            14,
            15,
            25,
            24,
            26,
            23,
            21,
            22,
            20,
        ],
    }

    reordered_connectivity = np.copy(connectivity)

    # reorder the connectivity for the elements in reorder_map
    for elem_type, reorder in reorder_map.items():
        matching_elem_types = elem_types == elem_type
        if np.any(matching_elem_types):
            reordered_connectivity[matching_elem_types, : len(reorder)] = connectivity[matching_elem_types][:, reorder]

    return reordered_connectivity


def read_cgns_region(
    reg_name: str, file: str, mesh_path: str, verbose=True
) -> tuple[CFSRegData, np.ndarray, np.ndarray]:

    vprint(f"Reading region: {reg_name}", verbose=verbose)

    with h5py.File(file, "r") as f:
        h5_region = f[f"{mesh_path}/{reg_name}"]

        region_type = cgns_element_type(int(h5_region[" data"][0]))

        region_conn_raw = np.array(h5_region["ElementConnectivity"][" data"], dtype=int)

    region_conn_lst: List[np.ndarray] = []
    region_type_lst = []

    if region_type == cgns_element_type.MIXED:
        idx = 0
        idx_1 = 0

        prefix = " - Reading mixed element connectivity: "
        size = 20
        update_step = region_conn_raw.size / 1000
        while idx < region_conn_raw.size:
            # Progress bar
            if idx - idx_1 > update_step:
                x = int(size * (idx / region_conn_raw.size))
                vprint(
                    f"{prefix}[{u'█' * x}{('.' * (size - x))}] {len(region_conn_lst):>6} elements",
                    end="\r",
                    flush=True,
                    verbose=verbose,
                )
                idx_1 = idx

            element_type = cgns_element_type(int(region_conn_raw[idx]))
            element_node_num = cgns_element_node_num[element_type]

            region_conn_lst.append(region_conn_raw[idx + 1 : idx + element_node_num + 1])
            region_type_lst.append(element_type)

            idx += element_node_num + 1

        vprint(
            f"\x1b[2K\r{prefix} {len(region_conn_lst)} elements",
            flush=True,
            verbose=verbose,
        )

        reg_elem_type = cgns_to_cfs_elem_type(np.array(region_type_lst))

        max_elem_node_num = max(apply_dict_vectorized(reg_elem_type, cfs_element_node_num))

        reg_conn = np.zeros((len(region_conn_lst), max_elem_node_num), dtype=int)
        for i, conn in enumerate(region_conn_lst):
            reg_conn[i, : len(conn)] = conn

    else:
        element_node_num = cgns_element_node_num[region_type]
        reg_num_elements = int(region_conn_raw.size / element_node_num)

        vprint(f" - Reading unitary element connectivity: {reg_num_elements} elements", verbose=verbose)

        reg_conn = region_conn_raw.reshape(reg_num_elements, element_node_num)
        reg_elem_type = np.array([type_link_cgns_cfs[region_type]] * reg_num_elements)

    reg_conn = reorder_nodes(connectivity=reg_conn, elem_types=reg_elem_type)

    node_idx, unique_indices, inverse_indices = np.unique(
        reg_conn,
        return_index=True,
        return_inverse=True,
    )

    reg_elem_dim = apply_dict_vectorized(data=reg_elem_type, dictionary=cfs_element_dimension)

    reg = CFSRegData(
        name=reg_name,
        nodes=node_idx[node_idx != 0],
        elements=np.arange(reg_conn.shape[0], dtype=int) + 1,
        dimension=reg_elem_dim.max(),
        is_group=False,
    )

    return reg, reg_conn, reg_elem_type


def read_mesh(file: str, verbose=True, *, flag_restart=False) -> CFSMeshData:
    """
    Read CGNS mesh file and convert to CFSMeshData object.

    Only HDF5 type CGNS format is currently supported! In case you are using an ADF CGNS file, convert the file to HDF
    before reading.

    Parameters
    ----------
    file: str
        Path to the CGNS file.
    verbose: bool
        If True, print progress messages.
    flag_restart: bool
        If True, indicates that the function is being called after a failed attempt to read the file.

    Returns
    -------
    CFSMeshData
        Mesh data object.

    Notes
    -----
    Use the following command (cgnslib) to convert ADF into HDF file format
    ``` bash
    adf2hdf $CGNS_FILE
    ```

    Examples
    --------
    >>> from pyCFS.data.extras.cgns_io import read_mesh
    >>> mesh = read_mesh("example.cgns")

    """

    # Get Node coordinates
    try:
        with h5py.File(file, "r") as f:
            mesh_path = f"BASE#1/{list(f['BASE#1'].keys())[1]}"
            h5_mesh = f[mesh_path]

            # Coordinates
            vprint("Reading coordinates", verbose=verbose)
            coord = np.stack(
                [
                    np.array(h5_mesh["GridCoordinates/CoordinateX/ data"]),
                    np.array(h5_mesh["GridCoordinates/CoordinateY/ data"]),
                    np.array(h5_mesh["GridCoordinates/CoordinateZ/ data"]),
                ],
                axis=1,
            )

            # Get Region names
            region_names = list(h5_mesh.keys())
            region_names.pop(region_names.index(" data"))
            region_names.pop(region_names.index("ZoneType"))
            region_names.pop(region_names.index("ZoneBC"))
            region_names.pop(region_names.index("PID"))
            region_names.pop(region_names.index("GridCoordinates"))

    except OSError as e:
        if not flag_restart and shutil.which("adf2hdf"):
            try:
                tmp_file = f"{file}.tmp"
                subprocess.run(["adf2hdf", file, tmp_file], check=True)
                print(f"Successfully converted {file} from ADF to HDF format using adf2hdf.")

                m = read_mesh(tmp_file, verbose=verbose, flag_restart=True)
                os.remove(tmp_file)

                return m
            except subprocess.CalledProcessError as conv_err:
                print(f"adf2hdf failed: {conv_err}")
                raise e
        else:
            print(
                f"""
---
Error: Could not open CGNS file! Make sure to use HDF5 type CGNS format.
       In case you are using an ADF CGNS file, convert the file to HDF!

Hint: Use the following command (Ubuntu: cgns-convert) to convert ADF into HDF file format:
---
adf2hdf {file}
---
"""
            )
            raise e
    except Exception as e:
        raise e

    conn_lst = []
    elem_type_lst = []
    reg_lst: list[CFSRegData] = []

    for reg_name in region_names:

        reg, reg_conn, reg_elem_type = read_cgns_region(reg_name, file, mesh_path, verbose=verbose)

        reg_lst.append(reg)
        conn_lst.append(reg_conn)
        elem_type_lst.append(reg_elem_type)

    # Merge regions
    vprint("Merging regions", verbose=verbose)

    max_cols = max(arr.shape[1] for arr in conn_lst)
    conn_lst = [np.pad(arr, ((0, 0), (0, max_cols - arr.shape[1])), constant_values=0) for arr in conn_lst]

    conn = np.concatenate(conn_lst)
    elem_types = np.concatenate(elem_type_lst)

    counter = 0
    for i, reg in enumerate(reg_lst):
        reg.Elements += counter
        counter += reg.Elements.size

    mesh = CFSMeshData(coordinates=coord, connectivity=conn, types=elem_types, regions=reg_lst)

    return mesh
