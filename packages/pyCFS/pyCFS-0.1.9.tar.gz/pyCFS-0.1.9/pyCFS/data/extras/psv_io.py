"""
Module containing data processing utilities for reading PSV export data files
"""

from __future__ import annotations

import os

import matplotlib.pyplot as plt
import numpy as np
import pyuff
from typing import Dict, List, Tuple, Optional, Callable

from pyCFS.data import io
from pyCFS.data import util
from pyCFS.data.io import CFSMeshData, CFSResultContainer, CFSRegData
from pyCFS.data.io.cfs_types import cfs_element_type, cfs_result_type, cfs_analysis_type
from pyCFS.data.util import progressbar, vecnorm, trilateration, apply_dict_vectorized


def check_unv(file_path: str) -> Dict:
    """
    Check the contents of a UNV file and extract relevant information. (AI-generated)

    Parameters
    ----------
    file_path : str
        Path to the UNV file.

    Returns
    -------
    dict
        Dictionary containing the number of points, elements, steps, and data entry labels.

    Notes
    -----
    The function reads the UNV file and extracts the number of points, elements, and line elements.
    It also extracts data entries and processes their descriptions.

    Examples
    --------
    >>> file_path = 'path/to/unv_file.unv'
    >>> unv_info = check_unv(file_path)
    """
    num_points = 0
    num_elements = 0

    if not os.path.exists(file_path):
        raise IOError(f"File {file_path} does not exist.")

    uff_file = pyuff.UFF(file_path)

    uff_setn_coord = np.where(uff_file.get_set_types() == 2411)[0]
    if uff_setn_coord.size > 0:
        uff_set_coord = uff_file.read_sets(setn=list(uff_setn_coord))
        num_points = uff_set_coord["node_nums"].size

    uff_setn_elements = np.where(uff_file.get_set_types() == 2412)[0]
    if uff_setn_elements.size > 0:
        uff_set_elements = uff_file.read_sets(setn=list(uff_setn_elements))
        num_elements_tria = 0
        num_elements_quad = 0
        if "triangle" in uff_set_elements:
            num_elements_tria = uff_set_elements["triangle"]["element_nums"].size
        if "quad" in uff_set_elements:
            num_elements_quad = uff_set_elements["quad"]["element_nums"].size
        num_elements = num_elements_tria + num_elements_quad

    uff_setn_line_elements = np.where(uff_file.get_set_types() == 82)[0]
    num_line_elements = uff_setn_line_elements.size

    uff_setn_data = np.where(uff_file.get_set_types() == 58)[0]
    num_steps = uff_file.read_sets(setn=uff_setn_data[0])["x"].size

    data_entries = uff_file.read_sets(setn=list(uff_setn_data))

    id2_str_lst = [item["id2"] for item in data_entries]
    id2_str_set = set(id2_str_lst)

    data = []

    for id2_str in id2_str_set:
        data_set = dict()
        data_set["description"] = id2_str
        id2_lst = id2_str.split(" ")
        id2_lst = [s for s in id2_lst if s]

        data_set["data_channel"] = id2_lst[0]
        if id2_lst[1] in ["X", "Y", "Z"]:
            data_set["dim"] = id2_lst[1]
            idx_match = 2
        else:
            idx_match = 1

        match id2_lst[idx_match]:
            case "AP" | "PSD" | "ESD" | "AvgFFT" | "FFT":
                data_set["data_type"] = id2_lst[idx_match]
                data_set["data_name"] = id2_lst[idx_match + 1].replace("^2", "")
            case _:
                if len(id2_lst) > idx_match + 1:
                    match id2_lst[idx_match + 1]:
                        case "CP" | "FRF" | "H1" | "H2":
                            data_set["ref_channel"] = id2_lst[idx_match]
                            data_set["data_type"] = id2_lst[idx_match + 1]
                            data_set["data_name"] = id2_lst[idx_match + 2]
                            data_set["ref_name"] = id2_lst[idx_match + 4]
                        case "Coherence":
                            data_set["ref_channel"] = id2_lst[idx_match]
                            data_set["data_type"] = id2_lst[idx_match + 1]
                else:
                    data_set["data_name"] = id2_lst[idx_match]
        data.append(data_set)

    unv_info = {
        "num_points": num_points,
        "num_elements": num_elements,
        "num_line_elements": num_line_elements,
        "num_steps": num_steps,
        "data": data,
    }

    # Print info
    print(f"Number of points: {num_points}")
    print(f"Number of elements: {num_elements}")
    print(f"Number of line elements: {num_line_elements}")
    print(f"Number of steps: {num_steps}")
    print("Data entries:")
    for data_set in data:
        print(f" - {data_set['description']}")

    return unv_info


def read_unv(
    file_path: str,
    data_type="H1",
    data_channel="Vib",
    data_name="Velocity",
    ref_channel="Ref1",
    ref_name="Force",
    measurement_3d=False,
    read_coordinates=False,
    read_elements=False,
    dist_file: str | None = None,
) -> dict:
    """
    Reads data from unv file, returns data['frequency'] and data['data'] in format usable in sdypy-EMA

    Parameters
    ----------
    file_path : str
        path to unv file, incl. file name
    data_type : str, optional
        type of data:
         None|'' = Time or Frequency data,
         'AP' = Auto Power,
         'PSD' = Power Spectral Density,
         'ESD' = Energy Spectral Density,
         'CP' = Cross Power to the reference signal,
         'FRF' = Frequency Response Function to the reference signal,
         'H1' = H1 estimate of the FRF to the reference signal,
         'H2' = H2 estimate of the FRF to the reference signal,
         'Coherence' = Coherence
         _custom_string_ = data labeled with "{data_channel}  _custom_string_"
         'raw' = returns all datasets of the unv file
    data_channel : str, optional
        Name of data channel: Vib (default), Usr (SignalProcessor data)
    data_name : str, optional
        Name of data: Velocity (default), Displacement, Acceleration, Force, Voltage, etc.
    ref_channel : str, optional
        Name of reference channel: Ref1 (default), Ref2, etc.
    ref_name : str, optional
        Name of reference data: Force (default), Voltage, etc.
    measurement_3d : bool, optional
        read data from 3D measurement into 3D vector data
    read_coordinates : bool, optional
        read Coordinates of nodes
    read_elements : bool, optional
        read element Connectivity and elem_types (Triangle = 3, Quad = 4) (requires read_coordinates)
    dist_file : str, optional
        path to csv file containing the distance from the scanning head to each measurement point

    Returns
    -------
    psv_data : dict
        Dictionary with keys:
         'Coordinates': np.ndarray,
         'Connectivity': np.ndarray,
         'elem_types': np.ndarray,
         'frequency': np.ndarray,
         'data_type': str,
         'data_name': str,
         'data_descriptor': str
         'data': List[np.ndarray] | 'data3D': np.ndarray (if measurement_3d),
         'ref_channel': int,
    """

    if not os.path.exists(file_path):
        raise IOError(f"File {file_path} does not exist.")

    uff_file = pyuff.UFF(file_path)

    if data_type == "raw":
        print("Reading unv file")
        raw_meas_data = uff_file.read_sets()

        psv_data = raw_meas_data

        return psv_data

    psv_data = {"data_type": data_type, "data_name": data_name}

    if read_coordinates:
        print("Reading Coordinates: ", end="")
        uff_setn_coord = int(np.where(uff_file.get_set_types() == 2411)[0].item())
        uff_set_coord = uff_file.read_sets(setn=uff_setn_coord)
        psv_data["Coordinates"] = np.vstack([uff_set_coord["x"], uff_set_coord["y"], uff_set_coord["z"]]).T
        node_renumbering = {v: k + 1 for k, v in dict(enumerate(uff_set_coord["node_nums"])).items()}

        print(f"Found {psv_data['Coordinates'].shape[0]} points")

        if read_elements:
            print("Reading elements: ", end="")
            uff_setn_elements = np.where(uff_file.get_set_types() == 2412)
            uff_setn_line_elements = np.where(uff_file.get_set_types() == 82)
            if uff_setn_elements[0].size == 0 and uff_setn_line_elements[0].size == 0:
                raise IOError(f"UNV file {file_path} doesn't contain element data.")

            conn_shape = (0, 0)
            conn_tria = None
            conn_quad = None
            idx_tria = None
            idx_quad = None

            if uff_setn_elements[0].size > 0:
                uff_set_elements = uff_file.read_sets(setn=int(uff_setn_elements[0].item()))

                if "triangle" in uff_set_elements:
                    conn_tria = uff_set_elements["triangle"]["nodes_nums"]
                    conn_tria = apply_dict_vectorized(data=conn_tria, dictionary=node_renumbering)
                    idx_tria = uff_set_elements["triangle"]["element_nums"]
                    conn_shape = conn_tria.shape
                if "quad" in uff_set_elements:
                    conn_quad = uff_set_elements["quad"]["nodes_nums"]
                    conn_quad = apply_dict_vectorized(data=conn_quad, dictionary=node_renumbering)
                    idx_quad = uff_set_elements["quad"]["element_nums"]
                    conn_shape = (conn_shape[0] + conn_quad.shape[0], 4)

            uff_set_line_elements = uff_file.read_sets(setn=list(uff_setn_line_elements[0]))
            if type(uff_set_line_elements) is dict:  # in case of only 1 single line element
                uff_set_line_elements = [uff_set_line_elements]

            conn_line_lst = []
            idx_line_lst = []
            idx_line_offset = conn_shape[0]
            for i in range(len(uff_set_line_elements)):
                conn_line_lst.append(uff_set_line_elements[i]["nodes"][0:2])
                idx_line_lst.append(idx_line_offset + i + 1)
            conn_line = np.array(conn_line_lst)
            idx_line = np.array(idx_line_lst)
            if idx_line.size > 0:
                conn_line = apply_dict_vectorized(data=conn_line, dictionary=node_renumbering)
                conn_shape = (conn_shape[0] + conn_line.shape[0], max(conn_shape[1], 2))

            conn = np.zeros(conn_shape, dtype=int)
            elem_types = np.zeros((conn_shape[0]))
            if idx_tria is not None:
                conn[idx_tria - 1, 0:3] = conn_tria
                elem_types[idx_tria - 1] = 3

            if idx_quad is not None:
                conn[idx_quad - 1, :] = conn_quad
                elem_types[idx_quad - 1] = 4

            if idx_line.size > 0:
                conn[idx_line - 1, 0:2] = conn_line
                elem_types[idx_line - 1] = 2

            psv_data["Connectivity"] = conn
            psv_data["elem_types"] = elem_types

        print(f"Found {psv_data['elem_types'].size} elements")

        if dist_file is not None:
            print("Computing PSV position from distance file: ", end="")
            dist_dict = np.load(dist_file, allow_pickle=True).item()
            dist = dist_dict["distance"]
            if "Coordinates" in dist_dict:
                print("Allocate distances based on Coordinates")
                # Reorder dist based on Coordinates
                coord_indices = util.compare_coordinate_arrays(
                    arrays=[psv_data["Coordinates"], dist_dict["Coordinates"]]
                )
                dist = dist[coord_indices[1]]
            else:
                print("No Coordinates in distance file. Make sure distances are ordered equally as Coordinates.")
            # Read from CSV
            # with open(dist_file) as f:
            #     dist = np.array([line for line in csv.reader(f)], dtype=float).flatten()
            psv_data["psv_coord"] = compute_psv_coord(coord=psv_data["Coordinates"], dist=dist)

    print("Reading frequency steps: ", end="")
    uff_setn_data = np.where(uff_file.get_set_types() == 58)[0]
    print(f"Found {uff_setn_data.size} items")
    psv_data["frequency"] = uff_file.read_sets(setn=uff_setn_data[0])["x"]

    match data_type:
        case None | "":
            data_descriptor = f"{data_name}"
        case "AP":
            data_descriptor = f"{data_type} {data_name}^2"
        case "PSD":
            data_descriptor = f"{data_type} {data_name}^2 / Frequency"
        case "ESD":
            data_descriptor = f"{data_type} {data_name}^2 * Time / Frequency"
        case "CP":
            data_descriptor = f"{ref_channel}  {data_type} {data_name} * {ref_name}"
        case "FRF" | "H1" | "H2":
            data_descriptor = f"{ref_channel}  {data_type} {data_name} / {ref_name}"
        case "Coherence":
            data_descriptor = f"{ref_channel}  {data_type}"
        case _:
            data_descriptor = f"{data_type}"

    psv_data["data_descriptor"] = data_descriptor

    print(f"Reading {uff_setn_data.size} datasets")
    data_entries = uff_file.read_sets(setn=list(uff_setn_data))

    data_entries_id2_str_set = set(item["id2"] for item in data_entries)
    for id2_str_read in data_entries_id2_str_set:
        print(f" - {id2_str_read}")

    if measurement_3d:
        id2_str_lst = tuple(f"{data_channel} {dim}  {data_descriptor}" for dim in ["X", "Y", "Z"])
        data_x = np.array([entry["data"] for entry in data_entries if entry["id2"] == id2_str_lst[0]])
        data_y = np.array([entry["data"] for entry in data_entries if entry["id2"] == id2_str_lst[1]])
        data_z = np.array([entry["data"] for entry in data_entries if entry["id2"] == id2_str_lst[2]])
        try:
            data = np.stack([data_x, data_y, data_z], axis=2)
        except ValueError:
            print("Warning: 3D Data could not be combined. Returning only the X coordinate.")
            data = data_x
        psv_data["data3D"] = data

        if data.size == 0:
            print(f"Warning: No data found for ids {id2_str_lst}")
    else:
        id2_str = f"{data_channel}  {data_descriptor}"
        data = np.array([entry["data"] for entry in data_entries if entry["id2"] == id2_str])
        psv_data["data"] = data

        if data.size == 0:
            print(f"Warning: No data found for id {id2_str}")

    return psv_data


def integrate_frf_data(psv_data: Dict) -> Dict:
    """
    Integrate Frequency Response Function (FRF) data. (AI-generated)

    Parameters
    ----------
    psv_data : dict
        Dictionary containing the PSV data.

    Returns
    -------
    dict
        Dictionary containing the integrated FRF data.
    """
    data_name_conversion_dict = {"Velocity": "Displacement", "Acceleration": "Velocity"}

    def operator(data: np.ndarray) -> np.ndarray:
        return data / (1j * psv_data["frequency"] * 2 * np.pi)

    return convert_frf_data(psv_data, operator, data_name_conversion_dict)


def differentiate_frf_data(psv_data: Dict) -> Dict:
    """
    Differentiate Frequency Response Function (FRF) data. (AI-generated)

    Parameters
    ----------
    psv_data : dict
        Dictionary containing the PSV data.

    Returns
    -------
    dict
        Dictionary containing the differentiated FRF data.
    """
    data_name_conversion_dict = {"Velocity": "Acceleration", "Displacement": "Velocity"}

    def operator(data: np.ndarray) -> np.ndarray:
        return data * 1j * psv_data["frequency"] * 2 * np.pi

    return convert_frf_data(psv_data, operator, data_name_conversion_dict)


def convert_frf_data(psv_data: Dict, operator: Callable, data_name_conversion_dict: Dict) -> Dict:
    """
    Convert Frequency Response Function (FRF) data using a specified operator. (AI-generated)

    Parameters
    ----------
    psv_data : dict
        Dictionary containing the PSV data.
    operator : Callable
        Function to apply to the FRF data.
    data_name_conversion_dict : dict
        Dictionary for converting data names.

    Returns
    -------
    dict
        Dictionary containing the converted FRF data.
    """
    if psv_data["data_name"] in data_name_conversion_dict:
        psv_data["data_descriptor"].replace(psv_data["data_name"], data_name_conversion_dict[psv_data["data_name"]])
        psv_data["data_name"] = data_name_conversion_dict[psv_data["data_name"]]
    else:
        print(f"Data name {psv_data['data_name']} not renamed.")

    psv_data["data"] = list(operator(np.array(psv_data["data"])))

    return psv_data


def interpolate_data_points(psv_data: Dict, nodes_interpolate: np.ndarray | List[int], interpolation_exp=0.5) -> dict:
    """
    Interpolate data sequentially from neighboring elements with valid or previously interpolated data using Shepards
    method. Ordering based on number of neighbors containing valid data.
    TODO: Investigate PINN-based interpolation
    """
    coord = psv_data["Coordinates"]
    conn = psv_data["Connectivity"]

    if type(nodes_interpolate) is np.ndarray:
        nodes_interpolate = list(nodes_interpolate.flatten())

    # Get neighbor nodes
    neighbor_list = []
    for node in progressbar(nodes_interpolate, "Get neighbors:   ", size=25):
        conn_idx = np.where(conn == node)[0]
        neighbor_set = set(conn[conn_idx].flatten())
        neighbor_set.remove(node)
        if 0 in neighbor_set:
            neighbor_set.remove(0)
        neighbor_list.append([node, neighbor_set])

    # Sort neighbor list by number of node with valid data
    neighbor_list.sort(key=lambda x: len(x[1].difference(nodes_interpolate)), reverse=True)
    nodes_interpolate_sorted = [item[0] for item in neighbor_list]
    psv_data["nodes_interpolated"] = np.array(nodes_interpolate_sorted)
    # Perform interpolation
    data = np.array(psv_data["data"])
    for i in progressbar(range(len(neighbor_list)), "Performing interpolation: ", size=16):
        node_idx = neighbor_list[i][0] - 1
        neighbor_data_ids = neighbor_list[i][1].difference(nodes_interpolate_sorted[i:])
        neighbor_idx = np.array([x - 1 for x in neighbor_data_ids], dtype=int)
        node_coord = coord[node_idx, :]
        neighbor_coord = coord[neighbor_idx, :]
        dist = np.linalg.norm(neighbor_coord - node_coord, axis=1)
        dmax = 1.01 * max(dist)
        w = ((dmax - dist) / (dmax * dist)) ** interpolation_exp
        w /= sum(w)

        data[node_idx, :] = w.reshape((w.shape[0], 1)).T @ data[neighbor_idx, :]

    psv_data["data"] = list(data)

    return psv_data


def compute_psv_coord(coord: np.ndarray, dist: np.ndarray, eps=1e-9) -> np.ndarray:
    """
    Computation of the location of the PSV scan head based on given distances.
    """
    if coord.shape[0] < 4:
        raise Exception("Not enough data points to compute unique location. Requires a minimum of 4 locations")

    pos_list = []
    for i in range(0, coord.shape[0] - 3, 2):

        offset = i
        k1 = trilateration(
            coord[offset + 0, :],
            coord[offset + 1, :],
            coord[offset + 2, :],
            dist[offset + 0],
            dist[offset + 1],
            dist[offset + 2],
        )
        offset = i + 1
        k2 = trilateration(
            coord[offset + 0, :],
            coord[offset + 1, :],
            coord[offset + 2, :],
            dist[offset + 0],
            dist[offset + 1],
            dist[offset + 2],
        )
        pos_list.append(k1)
        for pos1 in k1:
            for pos2 in k2:
                if np.linalg.norm(pos2 - pos1) < eps:
                    return pos1
        print(
            f"Warning: Could not find unique location based on 4 distances. Offset: {offset}",
            end="\r",
            flush=True,
        )
    print(
        f"Warning: Could not find unique location based on 4 distances. Offset: 0 - {offset}",
        flush=True,
    )
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    for pos in pos_list:
        ax.scatter(pos[0][0], pos[0][1], pos[0][2])
        ax.scatter(pos[1][0], pos[1][1], pos[1][2])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")  # type: ignore[attr-defined]
    plt.title("PSV location candidates")
    plt.show()
    raise Exception("Could not find unique location. Check Coordinates and distances.")


def convert_to_cfs(
    psv_data: Dict,
    reg_name="surface",
    quantitity_name="data",
    analysis_type=cfs_analysis_type.HARMONIC,
    scalar_data=False,
    data_direction: np.ndarray | None = None,
) -> Tuple[CFSMeshData, CFSResultContainer]:
    """Create CFS data structures from psv_data dict"""
    type_link = {
        2: cfs_element_type.LINE2,
        3: cfs_element_type.TRIA3,
        4: cfs_element_type.QUAD4,
    }
    elem_types = apply_dict_vectorized(data=psv_data["elem_types"], dictionary=type_link)

    reg_data = []
    reg_all = CFSRegData(name=reg_name, dimension=2)
    reg_all.Nodes = np.array([i + 1 for i in range(psv_data["Coordinates"].shape[0])])
    reg_all.Elements = np.array([i + 1 for i in range(psv_data["Connectivity"].shape[0])])
    reg_data.append(reg_all)
    # if any(elem_types == cfs_element_type.TRIA3) or any(elem_types == cfs_element_type.QUAD4):
    #     reg_surf = CFSRegData(name=f'{reg_name}_2D', dimension=1)
    #     reg_surf.Nodes = np.array([i + 1 for i in range(MeshInfo.NumNodes)])
    #     reg_surf.Elements = \
    #         np.where(np.logical_or(elem_types == cfs_element_type.TRIA3, elem_types == cfs_element_type.QUAD4))[0] + 1
    #     reg_data.append(reg_surf)
    # if any(elem_types == cfs_element_type.LINE2):
    #     reg_line = CFSRegData(name=f'{reg_name}_1D', dimension=1)
    #     reg_line.Nodes = np.array([i + 1 for i in range(MeshInfo.NumNodes)])
    #     reg_line.Elements = np.where(elem_types == cfs_element_type.LINE2)[0] + 1
    #     reg_data.append(reg_line)

    mesh_data = CFSMeshData(
        coordinates=psv_data["Coordinates"],
        connectivity=psv_data["Connectivity"],
        types=elem_types,
        regions=reg_data,
    )

    result_data = CFSResultContainer(analysis_type=analysis_type)
    if scalar_data:
        data = [d for d in list(np.array(psv_data["data"]).T)]
        dim_names = None
    else:
        dim_names = ["x", "y", "z"]
        if "data3D" in psv_data:
            data = list(psv_data["data3D"].swapaxes(0, 1))
        elif data_direction is None:
            if "psv_coord" in psv_data:
                dir_unit_vec = util.vecnorm(psv_data["Coordinates"] - psv_data["psv_coord"], axis=1)
                data = [np.tile(d, (3, 1)).T * dir_unit_vec for d in list(np.array(psv_data["data"]).T)]
            else:
                raise Exception(
                    '"psv_coord" is not defined in frf_data. Please specify data_direction or define "psv_coord"!'
                )
        else:
            data = [np.outer(d, data_direction) for d in list(np.array(psv_data["data"]).T)]

    if analysis_type in (cfs_analysis_type.HARMONIC, cfs_analysis_type.EIGENFREQUENCY, cfs_analysis_type.EIGENVALUE):
        is_complex_flag = True
    else:
        is_complex_flag = None

    result_data.add_data(
        data=np.array(data),
        step_values=psv_data["frequency"],
        quantity=quantitity_name,
        region=reg_name,
        restype=cfs_result_type.NODE,
        dim_names=dim_names,
        is_complex=is_complex_flag,
    )

    return mesh_data, result_data


def convert_from_cfs(
    mesh_data: io.CFSMeshData,
    result_data: io.CFSResultContainer,
    psv_data=None,
    reg_name="surface",
    quantitity_name="data",
    psv_coord: np.ndarray | None = None,
) -> dict:
    """Convert CFS data structures to psv_data dict."""
    if psv_data is None:
        psv_data = dict()

    psv_data["Coordinates"] = mesh_data.get_region_coordinates(reg_name)
    psv_data["Connectivity"] = mesh_data.get_region_connectivity(reg_name)
    type_link = {
        cfs_element_type.LINE2: 2,
        cfs_element_type.TRIA3: 3,
        cfs_element_type.QUAD4: 4,
    }
    psv_data["elem_types"] = apply_dict_vectorized(data=mesh_data.Types, dictionary=type_link)

    psv_data["frequency"] = result_data.StepValues

    r_array = result_data.get_data_array(quantity=quantitity_name, region=reg_name, restype=cfs_result_type.NODE)

    if psv_coord is None and len(r_array.DimNames) > 1:
        psv_data["data3D"] = list(r_array.DataArray.swapaxes(0, 1))

    elif len(r_array.DimNames) == 1:
        psv_data["data"] = list(r_array.DataArray.swapaxes(0, 1))
    else:
        psv_data["psv_coord"] = psv_coord
        dir_vec = util.vecnorm(psv_data["Coordinates"] - psv_data["psv_coord"], axis=1)

        r_array = result_data.get_data_array(quantity=quantitity_name, region=reg_name, restype=cfs_result_type.NODE)
        psv_data["data"] = list(
            np.sum(r_array.DataArray * np.tile(dir_vec, (r_array.shape[0], 1, 1)), axis=2).swapaxes(0, 1)
        )

    return psv_data


def combine_3D(psv_data1: Dict, psv_data2: Dict, psv_data3: Dict, eps=1e-9) -> Dict:
    """
    Compute 3D dataset from three 1D datasets including PSV coordinate information. (AI-generated)

    Parameters
    ----------
    psv_data1 : dict
        Dictionary containing the first set of PSV data.
    psv_data2 : dict
        Dictionary containing the second set of PSV data.
    psv_data3 : dict
        Dictionary containing the third set of PSV data.
    eps : float, optional
        Tolerance for comparing coordinates, by default 1e-9.

    Returns
    -------
    dict
        Dictionary containing the combined 3D FRF data.
    """

    data1 = np.array(psv_data1["data"])
    data2 = np.array(psv_data2["data"])
    data3 = np.array(psv_data3["data"])

    data_coord = psv_data1["Coordinates"]
    if (
        np.linalg.norm(data_coord - psv_data2["Coordinates"]) > eps
        or np.linalg.norm(data_coord - psv_data3["Coordinates"]) > eps
    ):
        raise Exception("FRF data must have identical data locations")

    psv_coord1 = psv_data1["psv_coord"]
    psv_coord2 = psv_data2["psv_coord"]
    psv_coord3 = psv_data3["psv_coord"]

    dir_vec1 = vecnorm(psv_coord1 - data_coord, axis=1)
    dir_vec2 = vecnorm(psv_coord2 - data_coord, axis=1)
    dir_vec3 = vecnorm(psv_coord3 - data_coord, axis=1)

    u1_real = dir_vec1[:, np.newaxis, :] * data1.real[:, :, np.newaxis]
    u2_real = dir_vec2[:, np.newaxis, :] * data2.real[:, :, np.newaxis]
    u3_real = dir_vec3[:, np.newaxis, :] * data3.real[:, :, np.newaxis]

    u1_imag = dir_vec1[:, np.newaxis, :] * data1.imag[:, :, np.newaxis]
    u2_imag = dir_vec2[:, np.newaxis, :] * data2.imag[:, :, np.newaxis]
    u3_imag = dir_vec3[:, np.newaxis, :] * data3.imag[:, :, np.newaxis]

    A_real = np.stack([u1_real, u2_real, u3_real], axis=2)
    A_imag = np.stack([u1_imag, u2_imag, u3_imag], axis=2)

    b_real = np.stack(
        [
            np.linalg.norm(u1_real, axis=2) ** 2,
            np.linalg.norm(u2_real, axis=2) ** 2,
            np.linalg.norm(u3_real, axis=2) ** 2,
        ],
        axis=2,
    )
    b_imag = np.stack(
        [
            np.linalg.norm(u1_imag, axis=2) ** 2,
            np.linalg.norm(u2_imag, axis=2) ** 2,
            np.linalg.norm(u3_imag, axis=2) ** 2,
        ],
        axis=2,
    )

    vec3d_real = np.linalg.solve(A_real, b_real)
    vec3d_imag = np.linalg.solve(A_imag, b_imag)

    data_3d = vec3d_real + 1j * vec3d_imag

    psv_data_3d = psv_data1.copy()
    psv_data_3d["data"] = None
    psv_data_3d["psv_coord"] = [psv_coord1, psv_coord2, psv_coord3]
    psv_data_3d["data3D"] = data_3d

    return psv_data_3d


def drop_nodes_elements(
    psv_data: Dict, node_idx: List[int] | np.ndarray | None = None, el_idx: List[int] | np.ndarray | None = None
):
    """
    Drop nodes and elements based on indices.

    Parameters
    ----------
    psv_data : dict
        Dictionary containing PSV data with keys 'Coordinates', 'Connectivity', 'elem_types', and optionally 'data' and 'data3D'.
    node_idx : list of int or np.ndarray, optional
        List or array of node indices (starting with 0) to be dropped. Default is None.
    el_idx : list of int or np.ndarray, optional
        List or array of element indices (starting with 0) to be dropped. Default is None.

    """

    el_idx_drop: Optional[List[int] | np.ndarray] = None
    if node_idx is not None:
        print(f"Dropping {len(node_idx)} nodes")
        # Drop Elements from connectivity
        conn = psv_data["Connectivity"].astype(int)
        mask = np.ones(conn.shape[0], dtype=bool)

        for idx in node_idx:
            # Check for rows that do not contain the specified value
            mask = ~np.any(conn == idx + 1, axis=1) & mask

        print(f"Selected {np.sum(~mask)} elements containing dropped nodes to be removed")
        el_idx_drop = np.where(~mask)[0]

    if el_idx_drop is None or len(el_idx_drop) == 0:
        el_idx_drop = el_idx
    elif el_idx is not None:
        el_idx_drop = np.union1d(el_idx, el_idx_drop)

    if el_idx_drop is not None:
        print(f"Dropping {len(el_idx_drop)} elements")
        _drop_elements(psv_data, el_idx=el_idx_drop)


def _drop_elements(psv_data: Dict, el_idx: List[int] | np.ndarray):
    """Drop elements based on indices."""
    psv_data["elem_types"] = np.delete(psv_data["elem_types"], el_idx, axis=0)

    nodes = np.unique(psv_data["Connectivity"].astype(int))
    conn_new = np.delete(psv_data["Connectivity"].astype(int), el_idx, axis=0)
    nodes_new = np.unique(conn_new)
    # Remove zero entry
    nodes = np.delete(nodes, np.where(nodes == 0)[0])
    nodes_new = np.delete(nodes_new, np.where(nodes_new == 0)[0])

    # Extract Coordinates
    _, idx_intersect, node_idx = np.intersect1d(nodes_new, nodes, return_indices=True)
    psv_data["Coordinates"] = psv_data["Coordinates"][node_idx, :]

    # Renumber Connectivity
    renumber_dict = {node_idx[idx] + 1: idx + 1 for idx in range(node_idx.size)}
    renumber_dict[0] = 0
    psv_data["Connectivity"] = apply_dict_vectorized(dictionary=renumber_dict, data=conn_new)

    # Extract data
    if "data" in psv_data:
        psv_data["data"] = list(np.array(psv_data["data"])[node_idx])

    if "data3D" in psv_data:
        psv_data["data3D"] = list(np.array(psv_data["data3D"])[node_idx])
