"""
Module containing methods for interpolation operations.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Callable, Sequence

import numpy as np
import scipy

from pyCFS.data.io import cfs_types
from pyCFS.data import io, util, v_def
from pyCFS.data.operators import _rbf_interpolation, _projection_interpolation
from pyCFS.data.operators._nearest_neighbor_interpolation import (
    _interpolation_matrix_nearest_neighbor_forward,
    _interpolation_matrix_nearest_neighbor_backward,
)
from pyCFS.data.util import progressbar, TimeRecord, vprint


def interpolation_matrix_cell_to_node(
    coordinates: np.ndarray, connectivity: np.ndarray, verbosity: int = v_def.release
) -> scipy.sparse.csr_array:
    """
    Computes interpolation matrix such that :math:`v = (1/n) \\sum_{i=1}^n e_i`. Thereby, :math:`v` is the data
    located to the node, :math:`n` the number of adjacent elements to the node, and :math:`e_i` the data of
    cell :math:`i`.

    Parameters
    ----------
    coordinates: np.ndarray
        Coordinate array (n,d) of n nodes in d dimensions
    connectivity: np.ndarray
        Connectivity array (N,M) of N elements consisting of M nodes. Arrays of mixed element types contain 0 entries.
    verbosity: int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    scipy.sparse.csr_array
        Interpolation matrix

    Notes
    -----
    .. figure:: ../../../docs/source/resources/cell2node.png


    Examples
    --------
    >>> from pyCFS.data.io import CFSReader
    >>> from pyCFS.data.operators.interpolators import interpolation_matrix_cell_to_node
    >>> with CFSReader(filename="source.cfs") as h5r:
    >>>     src_mesh = h5r.MeshData
    >>> reg_coord = src_mesh.get_region_coordinates(region="Region1")
    >>> reg_conn = src_mesh.get_region_connectivity(region="Region1")
    >>> m_interp = interpolation_matrix_cell_to_node(coordinates=reg_coord, connectivity=reg_conn)

    """
    matrix_shape = (coordinates.shape[0], connectivity.shape[0])

    val_lst = []
    col_ind_lst = []
    row_ptr_lst = []
    counter = 0

    for node_ind in progressbar(
        range(coordinates.shape[0]), prefix="Creating interpolation matrix: ", verbose=verbosity >= v_def.release
    ):
        conn_idx = np.where(connectivity == node_ind + 1)[0]
        if conn_idx.size > 0:
            w = 1.0 / conn_idx.size
            val_lst.append(np.full(conn_idx.shape, fill_value=w))
            col_ind_lst.append(conn_idx)
            row_ptr_lst.append(counter)
            counter += conn_idx.size
        else:
            vprint(
                f"Node {node_ind} skipped, as it is not contained in any element.", verbose=verbosity >= v_def.release
            )
            row_ptr_lst.append(counter)
    row_ptr_lst.append(counter)

    val = np.concatenate(val_lst)
    col_ind = np.concatenate(col_ind_lst)
    row_ptr = np.array(row_ptr_lst)
    interpolation_matrix = scipy.sparse.csr_array((val, col_ind, row_ptr), matrix_shape, dtype=float)
    return interpolation_matrix


def interpolation_matrix_node_to_cell(
    coordinates: np.ndarray, connectivity: np.ndarray, verbosity: int = v_def.release
) -> scipy.sparse.csr_array:
    """
    Computes interpolation matrix such that :math:`e = (1/n) \\sum_{i=1}^n  v_i`. Thereby, :math:`e` is the data
    assigned to the cell, :math:`n` the number of nodes of one element, and :math:`v_i` the nodal data.

    Parameters
    ----------
    coordinates: np.ndarray
        Coordinate array (n,d) of n nodes in d dimensions
    connectivity: np.ndarray
        Connectivity array (N,M) of N elements consisting of M nodes. Arrays of mixed element types contain 0 entries.
    verbosity: int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    scipy.sparse.csr_array
        Interpolation matrix

    Notes
    -----
    .. figure:: ../../../docs/source/resources/node2cell.png


    Examples
    --------
    >>> from pyCFS.data.io import CFSReader
    >>> from pyCFS.data.operators.interpolators import interpolation_matrix_node_to_cell
    >>> with CFSReader(filename="source.cfs") as h5r:
    >>>     src_mesh = h5r.MeshData
    >>> reg_coord = src_mesh.get_region_coordinates(region="Region1")
    >>> reg_conn = src_mesh.get_region_connectivity(region="Region1")
    >>> m_interp = interpolation_matrix_node_to_cell(coordinates=reg_coord, connectivity=reg_conn)
    """
    matrix_shape = (connectivity.shape[0], coordinates.shape[0])

    val_lst = []
    col_ind_lst = []
    row_ptr_lst = []
    counter = 0
    for el_ind in progressbar(
        range(connectivity.shape[0]), prefix="Creating interpolation matrix: ", verbose=verbosity >= v_def.release
    ):
        el_conn = connectivity[el_ind, np.flatnonzero(connectivity[el_ind, :])]
        w = 1.0 / el_conn.size

        val_lst.append(np.full(el_conn.shape, fill_value=w))
        col_ind_lst.append(el_conn - 1)
        row_ptr_lst.append(counter)
        counter += el_conn.size
    row_ptr_lst.append(counter)

    val = np.concatenate(val_lst)
    col_ind = np.concatenate(col_ind_lst)
    row_ptr = np.array(row_ptr_lst)
    interpolation_matrix = scipy.sparse.csr_array((val, col_ind, row_ptr), matrix_shape, dtype=float)
    return interpolation_matrix


def interpolation_matrix_nearest_neighbor(
    source_coord: np.ndarray,
    target_coord: np.ndarray,
    num_neighbors=20,
    interpolation_exp=2.0,
    max_distance: float | None = None,
    formulation: Optional[str] = None,
    workers=-1,
    verbosity=v_def.release,
) -> scipy.sparse.sparray:
    """
    Computes interpolation matrix based on nearest neighbor search with inverse distance weighting (Shepard's method)
    (see https://opencfs.gitlab.io/userdocu/DataExplanations/NN/). Nearest neighbors are searched for each point on the
    source (forward) or target (backward) grid. Forward search is depicted in the following:

    .. figure:: ../../../docs/source/resources/nearest_neighbor.png

    Parameters
    ----------
    source_coord: np.ndarray
        Coordinate array of m source points. Expected shape (m, 3)
    target_coord: np.ndarray
        Coordinates of n target points. Expected shape (n, 3)
    num_neighbors: int
        Number of neighbors considered for nearest neighbor search
    interpolation_exp: float, optional
        Exponent of inverse distance weighting (Shepard's method)
    max_distance: str, optional
        Set interpolation weights to zero if max_distance is exceeded.
    formulation: str, optional
        Search direction for nearest neighbor search. By default, direction is chosen automatically based on number of
        source and target points.
        'forward': Nearest neighbors are searched for each point on the (coarser) target grid. Leads to checkerboard
        if the target grid is finer than the source grid.
        'backward': Nearest neighbors are searched for each point on the (coarser) source grid. Leads to overprediction
        if the source grid is finer than the target grid.
    workers : int, optional
        Number of processes to use in parallel. The default is ``-1``, in which case all cores are used.
    verbosity: int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    scipy.sparse.csr_array or scipy.sparse.csc_array
        Sparse operator matrix. Type depends on formulation. 'forward' returns csc_array, 'backward' returns csr_array.
    """
    if formulation is None:
        if source_coord.shape[0] < target_coord.shape[0]:
            vprint(
                "Detected fine target grid (based on number of points). "
                "Automatically selected 'forward' nearest neighbor search. This can lead to checkerboard structures. "
                "Please check the result, "
                " 'backward' formulation yields better results for coarse target grids.",
                verbose=verbosity >= v_def.release,
            )
            formulation = "forward"
        else:
            vprint(
                "Detected coarse target grid (based on number of points). "
                "Automatically selected 'backward' nearest neighbor search. This can lead to overprediction. "
                "Please check the result, "
                " 'forward' formulation yields better results for fine target grids.",
                verbose=verbosity >= v_def.release,
            )
            formulation = "backward"

    interpolation_arg = {
        "source_coord": source_coord,
        "target_coord": target_coord,
        "num_neighbors": num_neighbors,
        "interpolation_exp": interpolation_exp,
        "max_distance": max_distance,
        "workers": workers,
        "verbosity": verbosity,
    }

    if formulation == "forward":
        return _interpolation_matrix_nearest_neighbor_forward(**interpolation_arg)
    elif formulation == "backward":
        return _interpolation_matrix_nearest_neighbor_backward(**interpolation_arg)
    else:
        raise ValueError("formulation argument has to be one of: None, 'forward', or 'backward'")


def interpolation_matrix_projection_based(
    src_coord: np.ndarray,
    src_conn: np.ndarray,
    src_reg_node: np.ndarray,
    src_reg_elem: np.ndarray,
    trgt_coord: np.ndarray,
    trgt_conn: np.ndarray,
    trgt_reg_node: np.ndarray,
    trgt_reg_elem: np.ndarray,
    proj_direction: np.ndarray | List[np.ndarray] | None = None,
    max_distance=0.03,
    search_radius: float | None = None,
    workers: Optional[int] = None,
):
    """
    Interpolation matrix for projection-based interpolation. Points of the target mesh are projected onto the
    source mesh and evaluated based on linear FE basis functions.

    .. figure:: ../../../docs/source/resources/projection_interpolation.png

    Parameters
    ----------
    src_coord : np.ndarray
        Source mesh coordinate array
    src_conn : np.ndarray
        Source mesh connectivity array
    src_reg_node : np.ndarray
        Source mesh region node ids
    src_reg_elem : np.ndarray
        Source mesh region element ids
    trgt_coord : np.ndarray
        Target mesh coordinate array
    trgt_conn : np.ndarray
        Target mesh connectivity array
    trgt_reg_node : np.ndarray
        Target mesh region node ids
    trgt_reg_elem : np.ndarray
        Target mesh region element ids
    proj_direction : np.ndarray, List[np.ndarray], optional
        Direction vector used for projection. Can be specified constant, or indivitually for each node.
        By default, the node normal vector (based on averaded neighboring element normal vectors) is used.
    max_distance : float, optional
        Lower values speed up interpolation matrix build and prevent projecting onto far surfaces.
    search_radius : float, optional
        Should be chosed at least to the maximum element size of the target grid.
    workers : int, optional
        Number of processes to use in parallel. The default is ``None``, in which case all cores are used.

    Returns
    -------
    scipy.sparse.csr_array
        Sparse operator matrix.

    References
    ----------
    Wurzinger A, Kraxberger F, Maurerlehner P, Mayr-Mittermüller B, Rucz P, Sima H, Kaltenbacher M, Schoder S.
    Experimental Prediction Method of Free-Field Sound Emissions Using the Boundary Element Method and
    Laser Scanning Vibrometry. Acoustics. 2024; 6(1):65-82. https://doi.org/10.3390/acoustics6010004

    """
    return _projection_interpolation.interpolation_matrix_projection_based(
        src_coord=src_coord,
        src_conn=src_conn,
        src_reg_node=src_reg_node,
        src_reg_elem=src_reg_elem,
        trgt_coord=trgt_coord,
        trgt_conn=trgt_conn,
        trgt_reg_node=trgt_reg_node,
        trgt_reg_elem=trgt_reg_elem,
        proj_direction=proj_direction,
        max_distance=max_distance,
        search_radius=search_radius,
        workers=workers,
    )


def apply_interpolation(
    result_array: io.CFSResultArray,
    interpolation_matrix: scipy.sparse.sparray,
    restype_out: Optional[cfs_types.cfs_result_type] = None,
    quantity_out: Optional[str] = None,
    region_out: Optional[str] = None,
    verbosity: int = v_def.release,
) -> io.CFSResultArray:
    """
    Performs interpolation based on sparse interpolation matrix for all data steps.

    Parameters
    ----------
    result_array: io.CFSResultArray
        Result array containing source data to be interpolated.
    interpolation_matrix: scipy.sparse.sparray
        Interpolation matrix to be applied to result array
    restype_out: cfs_result_type, optional
        Result type of the output array. Defaults to the result type of the input array.
    quantity_out: str, optional
        Quantity name of the output array. Defaults to the quantity name of the source array.
    region_out: str, optional
        Region name of the output array. Defaults to the region name of the input array.
    verbosity: int, optional

    Returns
    -------
    io.CFSResultArray
        Result array containing interpolated data.

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader
    >>> from pyCFS.data.io.cfs_types import cfs_result_type
    >>> from pyCFS.data.operators.interpolators import apply_interpolation, interpolation_matrix_cell_to_node
    >>> with CFSReader(filename="source.cfs") as h5r:
    >>>     mesh = h5r.MeshData
    >>>     src_data = h5r.MultiStepData
    >>> m_interp = interpolation_matrix_cell_to_node(coordinates=mesh.Coordinates, connectivity=mesh.Connectivity)
    >>> src_array = src_data.get_data_array(quantity="Quantity1", region="Region1", restype=cfs_result_type.ELEMENT)
    >>> interpolated_array = apply_interpolation(
    >>>    result_array=src_array, interpolation_matrix=m_interp, restype_out=cfs_result_type.NODE
    >>> )


    """
    if quantity_out is None:
        quantity_out = result_array.Quantity
    if region_out is None:
        region_out = result_array.Region
    if restype_out is None:
        restype_out = result_array.ResType

    step_values = result_array.StepValues
    result_array = result_array.require_shape(verbose=verbosity >= v_def.debug)
    result_array_out = io.CFSResultArray(
        np.full(
            (result_array.shape[0], interpolation_matrix.shape[0], result_array.shape[2]),
            fill_value=np.nan,
            dtype=result_array.dtype,
        )
    )
    result_array_out.MetaData = result_array.MetaData
    result_array_out.Quantity = quantity_out
    result_array_out.Region = region_out
    result_array_out.ResType = restype_out
    for i in progressbar(range(len(step_values)), prefix="Perform interpolation:", verbose=verbosity >= v_def.release):
        result_array_out[i, ...] = interpolation_matrix.dot(np.array(result_array[i, ...]))

    # perform sanity checks
    result_array_out.check_result_array()

    return result_array_out


def interpolate_cell_to_node(
    mesh: io.CFSMeshData,
    result: io.CFSResultContainer | Sequence[io.CFSResultArray],
    regions: List[str | io.CFSRegData] | None = None,
    quantity_names: List[str] | Dict[str, str] | None = None,
    verbosity: int = v_def.release,
) -> io.CFSResultContainer:
    """
    Interpolates data defined on elements from source mesh to nodes.

    Parameters
    ----------
    mesh: CFSMeshData
        Mesh data object containing the source mesh
    result: io.CFSResultContainer, Sequence[io.CFSResultArray]
        Result data object containing the result data
    regions: List[str], optional
        List of regions to perform interpolation on. If None, all regions are considered.
    quantity_names: List[str], Dict[str, str], optional
        List of quantity names to interpolate. If None, all quantities are considered.. If a dictionary is provided,
        the quantity names (keys) are renamed to the corresponding values.
    verbosity: int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    io.CFSResultContainer
        Interpolated result data object.

    Notes
    -----
    The interpolation is performed such that :math:`v = (1/n) \\sum_{i=1}^n e_i`. Thereby, :math:`v` is the data
    located to the node, :math:`n` the number of adjacent elements to the node, and :math:`e_i` the data of
    cell :math:`i`.

    .. figure:: ../../../docs/source/resources/cell2node.png

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader
    >>> quantities = ["quantity1", "quantity2"]
    >>> region_list = ["Region1","Region2"]
    >>> with CFSReader(filename="source.cfs") as h5r:
    >>>     src_mesh = h5r.MeshData
    >>>     src_data = h5r.MultiStepData
    >>> result_data_write = interpolate_node_to_cell(mesh=src_mesh,result=src_data,regions=region_list,quantity_names=quantities)
    """
    result_data = io.CFSResultContainer.require_container(result=result, verbosity=verbosity)

    if regions is None:
        regions = mesh.Regions  # type: ignore[assignment]
    if quantity_names is None:
        quantity_names = [res_info.Quantity for res_info in result_data.ResultInfo]  # type: ignore[misc]

    return _interpolate_node_cell(
        mesh_data=mesh,
        result_data=result_data,
        regions=regions,  # type: ignore[arg-type]
        quantity_names=quantity_names,
        interpolation_matrix_functor=interpolation_matrix_cell_to_node,
        restype_in=cfs_types.cfs_result_type.ELEMENT,
        restype_out=cfs_types.cfs_result_type.NODE,
        verbosity=verbosity,
    )


def interpolate_node_to_cell(
    mesh: io.CFSMeshData,
    result: io.CFSResultContainer | Sequence[io.CFSResultArray],
    regions: List[str | io.CFSRegData] | None = None,
    quantity_names: List[str] | Dict[str, str] | None = None,
    verbosity: int = v_def.release,
) -> io.CFSResultContainer:
    """
    Interpolates data defined on nodes from source mesh to elements.

    Parameters
    ----------
    mesh: CFSMeshData
        Mesh data object containing the source mesh
    result: io.CFSResultContainer, Sequence[io.CFSResultArray]
        Result data object containing the result data
    regions: List[str], optional
        List of regions to perform interpolation on. If None, all regions are considered.
    quantity_names: List[str], Dict[str, str], optional
        List of quantity names to interpolate. If None, all quantities are considered.. If a dictionary is provided,
        the quantity names (keys) are renamed to the corresponding values.
    verbosity: int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    io.CFSResultContainer
        Interpolated result data object.

    Notes
    -----
    The interpolation is performed such that :math:`e = (1/n) \\sum_{i=1}^n  v_i`. Thereby, :math:`e` is the data
    assigned to the cell, :math:`n` the number of nodes of one element, and :math:`v_i` the nodal data.

    .. figure:: ../../../docs/source/resources/node2cell.png


    Examples
    --------
    >>> from pyCFS.data.io import CFSReader
    >>> quantities = ["quantity1", "quantity2"]
    >>> region_list = ["Region1","Region2"]
    >>> with CFSReader(filename="source.cfs") as h5r:
    >>>     src_mesh = h5r.MeshData
    >>>     src_data = h5r.MultiStepData
    >>> result_data_write = interpolate_node_to_cell(mesh=src_mesh,result=src_data,regions=region_list,quantity_names=quantities)
    """
    result_data = io.CFSResultContainer.require_container(result=result, verbosity=verbosity)

    regions = mesh.Regions if regions is None else regions  # type: ignore[assignment]

    quantity_names = result_data.Quantities if quantity_names is None else quantity_names  # type: ignore[assignment]

    return _interpolate_node_cell(
        mesh_data=mesh,
        result_data=result_data,
        regions=regions,  # type: ignore[arg-type]
        quantity_names=quantity_names,  # type: ignore[arg-type]
        interpolation_matrix_functor=interpolation_matrix_node_to_cell,
        restype_in=cfs_types.cfs_result_type.NODE,
        restype_out=cfs_types.cfs_result_type.ELEMENT,
        verbosity=verbosity,
    )


def _interpolate_node_cell(
    mesh_data: io.CFSMeshData,
    result_data: io.CFSResultContainer,
    regions: List[str | io.CFSRegData],
    quantity_names: List[str] | Dict[str, str],
    interpolation_matrix_functor: Callable,
    restype_in: cfs_types.cfs_result_type,
    restype_out: cfs_types.cfs_result_type,
    verbosity: int = v_def.release,
) -> io.CFSResultContainer:
    result_array_list = []
    for reg in regions:
        vprint(f'Compute interpolation matrix: "{reg}"', verbose=verbosity >= v_def.release)
        reg_coord = mesh_data.get_region_coordinates(reg)
        reg_conn = mesh_data.get_region_connectivity(reg, renumber_nodes=True)

        m_interp = interpolation_matrix_functor(reg_coord, reg_conn)

        for quantity in quantity_names:
            vprint(f'Perform interpolation ({quantity}): "{reg}"', verbose=verbosity >= v_def.release)
            if type(quantity_names) is dict:
                quantity_out = quantity_names[quantity]
            else:
                quantity_out = quantity

            r_array = result_data.get_data_array(quantity=quantity, region=reg, restype=restype_in)

            if r_array.ResType != restype_in:
                vprint(
                    f'Warning: Result type of "{quantity}" is "{r_array.ResType}", but "{restype_in}" is expected!',
                    verbose=verbosity >= v_def.release,
                )

            r_array_interpolated = apply_interpolation(
                result_array=r_array,
                interpolation_matrix=m_interp,
                restype_out=restype_out,
                quantity_out=quantity_out,
            )
            result_array_list.append(r_array_interpolated)

    return io.CFSResultContainer(
        data=result_array_list, analysis_type=result_data.AnalysisType, multi_step_id=result_data.MultiStepID
    )


def interpolate_nearest_neighbor(
    mesh_src: io.CFSMeshData,
    result_src: io.CFSResultContainer | Sequence[io.CFSResultArray],
    mesh_target: io.CFSMeshData,
    region_src_target: List[Dict],
    quantity_names: List[str] | Dict[str, str] | None = None,
    num_neighbors=20,
    interpolation_exp=2.0,
    max_distance: float | None = None,
    formulation: Optional[str] = None,
    workers=-1,
    element_centroid_data_src=False,
    element_centroid_data_target=False,
    verbosity=v_def.release,
) -> io.CFSResultContainer:
    """
    Interpolates regions from source file to regions in target file based on nearest neighbor search.

    Parameters
    ----------
    mesh_src: CFSMeshData
        Mesh data object containing the source mesh
    result_src: io.CFSResultContainer, Sequence[io.CFSResultArray]
        Result data object containing the source data
    mesh_target: CFSMeshData
        Mesh data object containing the target mesh
    region_src_target: List[Dict],
        List of dictionaries linking source regions (key="source") to target regions (key="target").
    quantity_names: List[str], Dict[str, str], optional
        List of quantity names to interpolate. If None, all quantities are considered. If a dictionary is provided,
        the quantity names (keys) are renamed to the corresponding values
    num_neighbors: int
        Number of neighbors considered for nearest neighbor search
    interpolation_exp: float, optional
        Exponent of inverse distance weighting (Shepard's method)
    max_distance: str, optional
        Set interpolation weights to zero if max_distance is exceeded.
    formulation: str, optional
        Search direction for nearest neighbor search. By default, direction is chosen automatically based on number of
        source and target points.
        'forward': Nearest neighbors are searched for each point on the (coarser) target grid. Leads to checkerboard
        if the target grid is finer than the source grid.
        'backward': Nearest neighbors are searched for each point on the (coarser) source grid. Leads to overprediction
        if the source grid is finer than the target grid.
    workers : int, optional
        Number of processes to use in parallel. The default is ``-1``, in which case all cores are used.
    element_centroid_data_src: bool, optional
        Set ``True`` if source data is defined on Elements instead of Nodes. Default is ``False``.
    element_centroid_data_target: bool, optional
        Use element centroids as target coordinates. Default is ``False``.
    verbosity: int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    io.CFSResultContainer
        Interpolated result data object.

    Notes
    -----
    Computes interpolation matrix based on nearest neighbor search with inverse distance weighting (Shepard's method)
    (see https://opencfs.gitlab.io/userdocu/DataExplanations/NN/). Nearest neighbors are searched for each point on the
    source (forward) or target (backward) grid. Forward search is depicted in the following:

    .. figure:: ../../../docs/source/resources/nearest_neighbor.png

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader
    >>> from pyCFS.data.operators import interpolators
    >>> quantities = ["quantity1", "quantity2"]
    >>> region_src_target = [
    >>>    {"source": ["S_source1"], "target": ["S_target1"]},
    >>>    {"source": ["S_source1", "S_source2"], "target": ["S_target2", "S_target3"]},
    >>> ]
    >>> with CFSReader(filename="source.cfs") as h5r:
    >>>     src_mesh = h5r.MeshData
    >>>     src_data = h5r.MultiStepData
    >>> with CFSReader(filename="target.cfs") as h5r:
    >>>     target_mesh = h5r.MeshData
    >>> result_data_write = interpolators.interpolate_region_nearest_neighbor(
    >>>     mesh_src=src_mesh,
    >>>     data_src=src_data,
    >>>     mesh_target=target_mesh,
    >>>     region_src_target=region_src_target,
    >>>     quantity_names=quantities,
    >>> )
    """
    data_src = io.CFSResultContainer.require_container(result=result_src, verbosity=verbosity)

    if quantity_names is None:
        quantity_names = [res_info.Quantity for res_info in data_src.ResultInfo]  # type: ignore[misc]

    result_array_list = []
    for region_src_target_dict in region_src_target:
        with TimeRecord(
            f'Prepare interpolation: {region_src_target_dict["source"]} -> {region_src_target_dict["target"]}',
            verbose=verbosity >= v_def.release,
        ):

            # Get source coordinates
            src_coord = np.zeros((0, 3), dtype=float)
            src_region_counter = [0]
            for src_region_name in region_src_target_dict["source"]:
                if element_centroid_data_src:
                    src_coord_reg = mesh_src.get_region_centroids(region=src_region_name)
                else:
                    src_coord_reg = mesh_src.get_region_coordinates(region=src_region_name)

                src_coord = np.concatenate((src_coord, src_coord_reg), axis=0)
                src_region_counter.append(src_coord.shape[0])

            # Get target coordinates
            target_coord = np.zeros((0, 3), dtype=float)
            target_region_counter = [0]
            for target_region_name in region_src_target_dict["target"]:
                if element_centroid_data_target:
                    target_coord_reg = mesh_target.get_region_centroids(region=target_region_name)
                else:
                    target_coord_reg = mesh_target.get_region_coordinates(region=target_region_name)

                target_coord = np.concatenate((target_coord, target_coord_reg), axis=0)
                target_region_counter.append(target_coord.shape[0])

        # Get interpolation matrix
        vprint(
            f'Compute interpolation matrix: {region_src_target_dict["source"]} -> {region_src_target_dict["target"]}',
            verbose=verbosity >= v_def.release,
        )
        interpolation_matrix = interpolation_matrix_nearest_neighbor(
            source_coord=src_coord,
            target_coord=target_coord,
            num_neighbors=num_neighbors,
            interpolation_exp=interpolation_exp,
            max_distance=max_distance,
            formulation=formulation,
            workers=workers,
            verbosity=verbosity,
        )
        for quantity in quantity_names:
            if type(quantity_names) is dict:
                quantity_out = quantity_names[quantity]
            else:
                quantity_out = quantity
            src_array_list = []
            for src_idx, src_region_name in enumerate(region_src_target_dict["source"]):
                if element_centroid_data_src:
                    src_type = cfs_types.cfs_result_type.ELEMENT
                else:
                    src_type = cfs_types.cfs_result_type.NODE

                src_array_reg = data_src.get_data_array(quantity=quantity, region=src_region_name, restype=src_type)
                # TODO add support for history data
                if src_array_reg.IsHistory:
                    raise NotImplementedError(
                        f"History data {src_array_reg.ResultInfo} is not supported for interpolation yet."
                    )
                src_array_list.append(src_array_reg)

            src_array = io.CFSResultArray(np.concatenate(src_array_list, axis=1))
            src_array.MetaData = src_array_reg.MetaData

            for target_idx, target_region_name in enumerate(region_src_target_dict["target"]):
                vprint(
                    f'Perform interpolation ({quantity}): "{src_region_name}" -> "{target_region_name}"',
                    verbose=verbosity >= v_def.release,
                )

                target_lb = target_region_counter[target_idx]
                target_ub = target_region_counter[target_idx + 1]

                if element_centroid_data_target:
                    target_type = cfs_types.cfs_result_type.ELEMENT
                else:
                    target_type = cfs_types.cfs_result_type.NODE

                result_array = apply_interpolation(
                    result_array=src_array,
                    interpolation_matrix=interpolation_matrix[target_lb:target_ub, :],
                    restype_out=target_type,
                    quantity_out=quantity_out,
                    region_out=target_region_name,
                    verbosity=verbosity,
                )
                result_array_list.append(result_array)

    return io.CFSResultContainer(
        data=result_array_list,
        analysis_type=data_src.AnalysisType,
        multi_step_id=data_src.MultiStepID,
        verbosity=verbosity,
    )


def interpolate_distinct_nodes(
    mesh: io.CFSMeshData,
    result: io.CFSResultContainer | Sequence[io.CFSResultArray],
    quantity_name: str,
    interpolate_node_ids: List[int],
    regions: List[str | io.CFSRegData] | None = None,
    num_neighbors: float = 20,
    interpolation_exp: float = 0.5,
    max_distance: float | None = None,
    workers: int = -1,
    verbosity: int = v_def.release,
) -> io.CFSResultContainer:
    """
    Remove the content and interpolate distinct nodes that are passed as a list of global node ids.
    The interpolation is done via Shepard's method (nearest neighbor interpolation).

    Parameters
    ----------
    mesh: CFSMeshData
        Mesh data object containing the mesh
    result: io.CFSResultContainer, Sequence[io.CFSResultArray]
        Result data object containing the source data
    quantity_name: str
        Name of the quantity to be treated.
    interpolate_node_ids: List[int]
        List of global node ids on the mesh to be interpolated.
    regions: List[str | io.CFSRegData] | None, optional
        List of regions that should be treated. 'None' will use all available regions.
    num_neighbors: int, optional
        Number of neighbors considered for nearest neighbor search.
    interpolation_exp: float, optional
        Exponent of inverse distance weighting (Shepard's method).
    max_distance: float | None, optional
        Set interpolation weights to zero if max_distance is exceeded.
    workers: int, optional
        Number of processes to use in parallel. The default is ``-1``, in which case all cores are used.
    verbosity: int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    io.CFSResultContainer
        Interpolated result data object.

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader
    >>> quantities = ["quantity1", "quantity2"]
    >>> regions = ["S_source1"]
    >>> with CFSReader(filename="source.cfs") as h5r:
    >>>     src_mesh = h5r.MeshData
    >>>     src_data = h5r.MultiStepData
    >>> result_data_write = interpolate_distinct_nodes(mesh=src_mesh,result=src_data,quantity_name="quantity1",interpolate_node_ids=[1, 2, 3],regions=regions)
    """
    result_data = io.CFSResultContainer.require_container(result=result, verbosity=verbosity)

    if regions is None or regions is []:
        # get mesh data
        connectivity = mesh.Connectivity
        coordinates = mesh.Coordinates
        # specify node ids for the whole mesh
        region_node_ids = [mesh.get_region_nodes(it_region) for it_region in mesh.Regions]
        # get result arrays
        result_arrays = result_data.get_data_arrays(regions=mesh.Regions, quantities=[quantity_name])
    else:
        region_node_ids = []
        coordinates = np.ndarray((0, 3))
        connectivity = np.array([])
        for it_region in regions:
            # get mesh data
            tmp_coord = mesh.get_region_coordinates(region=it_region)
            coordinates = np.concatenate((coordinates, tmp_coord), axis=0)
            # Get connectivity
            tmp_connect = mesh.get_region_elements(it_region)
            connectivity = np.concatenate((connectivity, tmp_connect), axis=0)
            # set ids for nodes per region
            region_node_ids.append(mesh.get_region_nodes(it_region))
        # get result arrays
        result_arrays = result_data.get_data_arrays(regions=regions, quantities=[quantity_name])

    # concatenate and set dummy metadata
    all_result_array = io.CFSResultArray(np.concatenate(result_arrays, axis=1))
    all_result_array.MetaData = result_arrays[0].MetaData
    all_node_ids = np.concatenate(region_node_ids)

    # get the indices of the outlier nodes in the considered regions
    outlier_node_idx = np.where(np.isin(all_node_ids, interpolate_node_ids))[0]
    outlier_coords = coordinates[outlier_node_idx, :]

    # determine other nodes
    other_node_ids = np.setdiff1d(all_node_ids, interpolate_node_ids)
    other_node_idx = np.where(np.isin(all_node_ids, other_node_ids))[0]
    other_coords = coordinates[other_node_idx, :]

    # Get interpolation matrix
    vprint("Compute interpolation matrix:", verbose=verbosity >= v_def.release)
    interpolation_matrix = interpolation_matrix_nearest_neighbor(
        source_coord=other_coords,
        target_coord=outlier_coords,
        num_neighbors=num_neighbors,
        interpolation_exp=interpolation_exp,
        max_distance=max_distance,
        formulation="backward",
        workers=workers,
        verbosity=verbosity,
    )
    # remove the outlier nodes from the result arrays
    other_results = io.CFSResultArray(np.delete(all_result_array, outlier_node_idx, axis=1))
    other_results.MetaData = all_result_array.MetaData
    # interpolate the outlier values
    interpolated_result_array = apply_interpolation(
        result_array=other_results,
        interpolation_matrix=interpolation_matrix,
        restype_out=result_arrays[0].ResType,
        quantity_out=quantity_name,
        region_out="Interpolated",
        verbosity=verbosity,
    )
    # add to results
    all_result_array[:, outlier_node_idx, :] = interpolated_result_array

    # embed the interpolated regions into the original file and write metadata
    nr_region_nodes = [len(it_nodes) for it_nodes in region_node_ids]
    for i_region, it_nr_nodes in enumerate(nr_region_nodes):
        start = np.sum(nr_region_nodes[:i_region]).astype(int)
        stop = start + it_nr_nodes
        meta_data = result_arrays[i_region].MetaData
        result_arrays[i_region] = all_result_array[:, start:stop, :]  # type: ignore[call-overload]
        result_arrays[i_region].MetaData = meta_data

    # append the non-treated regions
    if regions is not None and regions is not []:
        remaining_regions = [region for region in mesh.Regions if region not in regions]
        remaining_result_arrays = result_data.get_data_arrays(regions=remaining_regions, quantities=[quantity_name])
        result_arrays += remaining_result_arrays

    return io.CFSResultContainer(
        data=result_arrays,
        analysis_type=result_data.AnalysisType,
        multi_step_id=result_data.MultiStepID,
        verbosity=verbosity,
    )


def interpolate_rbf(
    mesh_src: io.CFSMeshData,
    result_src: io.CFSResultContainer | Sequence[io.CFSResultArray],
    mesh_target: io.CFSMeshData,
    region_src_target: List[Dict],
    quantity_names: List[str] | Dict[str, str] | None = None,
    element_centroid_data_src=False,
    element_centroid_data_target=False,
    verbosity=v_def.release,
    kernel="gaussian",
    epsilon=1.0,
    smoothing=1e-12,
) -> io.CFSResultContainer:
    """
    Interpolate field values from a source mesh to a target mesh using global RBF interpolation.

    Parameters
    ----------
    mesh_src : io.CFSMeshData
        Source mesh data object.
    result_src : io.CFSResultContainer or Sequence[io.CFSResultArray]
        Source result data container or list of result arrays.
    mesh_target : io.CFSMeshData
        Target mesh data object.
    region_src_target: List[Dict],
        List of dictionaries linking source regions (key="source") to target regions (key="target").
    quantity_names : list of str or dict or None, optional
        List or mapping of quantity names to interpolate. If None, all quantities are used.
    element_centroid_data_src : bool, optional
        If True, use element centroids for source data. Default is False.
    element_centroid_data_target : bool, optional
        If True, use element centroids for target data. Default is False.
    verbosity : int, optional
        Verbosity level. Default is `v_def.release`.
    kernel : str, optional
        Type of RBF kernel to use. Available kernels: "gaussian", "multiquadratic", "wendland_c2".
        Default is "gaussian".
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.
    smoothing : float, optional
        Smoothing parameter added to the diagonal of the kernel matrix. Default is 1e-12.

    Returns
    -------
    results : io.CFSResultContainer
        Interpolated results on the target mesh.

    Examples
    --------

    """
    return _rbf_interpolation._process_rbf(
        flag_grad=False,
        flag_local=False,
        mesh_src=mesh_src,
        result_src=result_src,
        mesh_target=mesh_target,
        region_src_target=region_src_target,
        quantity_names=quantity_names,
        element_centroid_data_src=element_centroid_data_src,
        element_centroid_data_target=element_centroid_data_target,
        verbosity=verbosity,
        kernel=kernel,
        epsilon=epsilon,
        smoothing=smoothing,
    )


def interpolate_rbf_local(
    mesh_src: io.CFSMeshData,
    result_src: io.CFSResultContainer | Sequence[io.CFSResultArray],
    mesh_target: io.CFSMeshData,
    region_src_target: List[Dict],
    quantity_names: List[str] | Dict[str, str] | None = None,
    element_centroid_data_src=False,
    element_centroid_data_target=False,
    verbosity=v_def.release,
    kernel="gaussian",
    epsilon=1.0,
    smoothing=1e-12,
    neighbors=20,
    min_neighbors: Optional[int] = None,
    radius_factor: float = 2.0,
) -> io.CFSResultContainer:
    """
    Interpolate field values from a source mesh to a target mesh using local RBF interpolation.

    Parameters
    ----------
    mesh_src : io.CFSMeshData
        Source mesh data object.
    result_src : io.CFSResultContainer or Sequence[io.CFSResultArray]
        Source result data container or list of result arrays.
    mesh_target : io.CFSMeshData
        Target mesh data object.
    region_src_target : list of dict
        List of dictionaries mapping source regions to target regions.
    quantity_names : list of str or dict or None, optional
        List or mapping of quantity names to interpolate. If None, all quantities are used.
    element_centroid_data_src : bool, optional
        If True, use element centroids for source data. Default is False.
    element_centroid_data_target : bool, optional
        If True, use element centroids for target data. Default is False.
    verbosity : int, optional
        Verbosity level. Default is `v_def.release`.
    kernel : str, optional
        Type of RBF kernel to use. Default is "gaussian".
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.
    smoothing : float, optional
        Smoothing parameter added to the diagonal of the kernel matrix. Default is 1e-12.
    neighbors : int, optional
        Number of nearest neighbors to use for local interpolation. Default is 100.
    min_neighbors : int or None, optional
        Minimum number of neighbors to use. Default is None.
    radius_factor : float, optional
        Factor to determine the local neighborhood radius. Default is 2.0.

    Returns
    -------
    results : io.CFSResultContainer
        Interpolated results on the target mesh.
    """
    return _rbf_interpolation._process_rbf(
        flag_grad=False,
        flag_local=True,
        mesh_src=mesh_src,
        result_src=result_src,
        mesh_target=mesh_target,
        region_src_target=region_src_target,
        quantity_names=quantity_names,
        element_centroid_data_src=element_centroid_data_src,
        element_centroid_data_target=element_centroid_data_target,
        verbosity=verbosity,
        kernel=kernel,
        epsilon=epsilon,
        smoothing=smoothing,
        neighbors=neighbors,
        min_neighbors=min_neighbors,
        radius_factor=radius_factor,
    )


def interpolate_projection_based(
    mesh_src: io.CFSMeshData,
    result_src: io.CFSResultContainer | Sequence[io.CFSResultArray],
    mesh_target: io.CFSMeshData,
    region_src_target_dict: Dict,
    quantity_name: str,
    projection_direction: np.ndarray | None = None,
    max_projection_distance=0.1,
    search_radius=None,
    workers: Optional[int] = None,
    verbosity: int = v_def.release,
) -> io.CFSResultContainer:
    """
    Interpolate data from a source region to a target region using projection-based interpolation. (AI-generated)

    Parameters
    ----------
    mesh_src : io.CFSMeshData
        Source mesh data object.
    result_src : io.CFSResultContainer or Sequence[io.CFSResultArray]
        Source result data container or list of result arrays.
    mesh_target : io.CFSMeshData
        Target mesh data object.
    region_src_target_dict : dict
        Dictionary mapping source region names to target region names.
    quantity_name : str
        Name of the quantity to interpolate.
    projection_direction : np.ndarray or None, optional
        Direction vector used for projection. If None, the node normal vector is used, by default None.
    max_projection_distance : float, optional
        Maximum projection distance. Lower values speed up interpolation matrix build and prevent projecting onto far surfaces, by default 0.1.
    search_radius : float or None, optional
        Search radius for finding the nearest elements. Should be at least the maximum element size of the target grid, by default None.
    workers : int or None, optional
        Number of processes to use in parallel. If None, all cores are used, by default None.
    verbosity : int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    io.CFSResultContainer
        Interpolated result data.

    Examples
    --------
    >>> from pyCFS.data import io
    >>> from pyCFS.data.operators import interpolators
    >>>
    >>> file_src = "source.cfs"
    >>> file_target = "target.cfs"
    >>> region_src_target_dict = {
    >>>     "IFs_mount_inlet": ["IFs_mount_inlet"],
    >>>     "IF_pipe_outer": ["IF_pipe_outer"],
    >>> }
    >>> quantity_name = "mechVelocity"
    >>>
    >>> mesh_src = io.read_mesh(file_src)
    >>> result_src = io.read_data(file_src)
    >>> mesh_target = io.read_mesh(file_target)
    >>>
    >>> return_data = interpolators.interpolate_projection_based(
    >>>     mesh_src=file_src,
    >>>     result_src=result_src,
    >>>     mesh_target=mesh_target,
    >>>     region_src_target_dict=region_src_target_dict,
    >>>     quantity_name=quantity_name,
    >>>     dim_names=["x", "y", "z"],
    >>>     is_complex=True,
    >>>     projection_direction=None,
    >>>     max_projection_distance=5e-3,
    >>>     search_radius=5e-2,
    >>> )

    """
    data_src = io.CFSResultContainer.require_container(result=result_src, verbosity=verbosity)

    # Convert quads to triangles in target mesh (for normal vector calculation)
    mesh_target.convert_quad2tria()

    result_array_list = []
    for src_region_name in region_src_target_dict:
        # Convert quads to triangles in src mesh
        mesh_src.convert_quad2tria()
        src_region = util.list_search(mesh_src.Regions, src_region_name)

        target_region_list = []
        for target_region_name in region_src_target_dict[src_region_name]:
            target_region_list.append(util.list_search(mesh_target.Regions, target_region_name))

        # Source grid
        src_coord = mesh_src.Coordinates
        src_connectivity = mesh_src.Connectivity
        src_reg_nodes = src_region.Nodes
        src_reg_elems = src_region.Elements

        for target_region in target_region_list:
            # Target grid
            target_coord = mesh_target.Coordinates
            target_connectivity = mesh_target.Connectivity
            target_reg_nodes = target_region.Nodes
            target_reg_elems = target_region.Elements

            # Get interpolation matrix
            print(f'Computing interpolation matrix: "{src_region.Name}"-> "{target_region.Name}"')
            interpolation_matrix = interpolation_matrix_projection_based(
                src_coord,
                src_connectivity,
                src_reg_nodes,
                src_reg_elems,
                target_coord,
                target_connectivity,
                target_reg_nodes,
                target_reg_elems,
                proj_direction=projection_direction,
                max_distance=max_projection_distance,
                search_radius=search_radius,
                workers=workers,
            )

            # Perform interpolation
            src_array = data_src.get_data_array(
                quantity=quantity_name, region=src_region_name, restype=cfs_types.cfs_result_type.NODE
            )
            result_array = apply_interpolation(
                result_array=src_array,
                interpolation_matrix=interpolation_matrix,
                restype_out=cfs_types.cfs_result_type.NODE,
                region_out=target_region.Name,
            )

            result_array_list.append(result_array)

    return io.CFSResultContainer(
        data=result_array_list, analysis_type=data_src.AnalysisType, multi_step_id=data_src.MultiStepID
    )
