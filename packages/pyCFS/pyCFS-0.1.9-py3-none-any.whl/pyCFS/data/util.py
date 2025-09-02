"""
Module containing utility functions for pyCFS.data project
"""

from __future__ import annotations

import datetime
import sys
import time

from math import floor
from typing import Collection, List, Dict, Tuple, Optional, Any

import numpy as np

from pyCFS.data.io.cfs_types import cfs_element_type


def array_memory_usage(shape: Tuple[int, ...], dtype: Any) -> int:
    """
    Calculate the memory usage of a numpy array with given shape and dtype.

    Parameters
    ----------
    shape: Tuple[int, ...]
        Shape of the numpy array (e.g., (N, M, P)).
    dtype: numpy.dtype
        Data type of the numpy array (e.g., np.float64, np.int32).

    Returns
    -------
    int
        Memory usage in bytes of the numpy array.

    """
    n_elements = np.prod(shape)
    bytes_per_element = np.dtype(dtype).itemsize
    return int(n_elements * bytes_per_element)


def connectivity_structured_grid(nx: int, ny: int, nz: Optional[int] = None) -> np.ndarray:
    """
    Build connectivity matrix for structured grid with quadrilateral (2D) or hexahedral (3D) elements.

    Parameters
    ----------
    nx : int
        Number of nodes in x-direction.
    ny : int
        Number of nodes in y-direction.
    nz : Optional[int], optional
        Number of nodes in z-direction. If None, creates 2D quadrilateral elements.
        If provided, creates 3D hexahedral elements.

    Returns
    -------
    np.ndarray
        Connectivity matrix with 1-based indexing.
        - For 2D: shape (num_elements, 4) with [n0, n1, n2, n3] node indices per quad
        - For 3D: shape (num_elements, 8) with [n0, n1, n2, n3, n4, n5, n6, n7] node indices per hex

    Examples
    --------
    >>> from pyCFS.data.util import connectivity_structured_grid
    >>> conn_2d = connectivity_structured_grid(nx=3, ny=3)
    >>> conn_3d = connectivity_structured_grid(nx=3, ny=3, nz=3)

    Notes
    -----
    2D Quadrilateral connectivity convention:

    n3 --- n2
    |      |
    |      |
    n0 --- n1

    3D Hexahedral connectivity convention:

       n7 -------- n6
      /|          /|
     / |         / |
    n4 -------- n5 |
    |  |        |  |
    |  n3 ------|--n2
    | /         | /
    |/          |/
    n0 -------- n1
    """
    if nz is None:
        # 2D quadrilateral elements
        j, i = np.meshgrid(np.arange(nx - 1), np.arange(ny - 1))

        n0 = i * nx + j  # bottom-left
        n1 = n0 + 1  # bottom-right
        n2 = n0 + 1 + nx  # top-right
        n3 = n0 + nx  # top-left

        conn = np.stack([n0, n1, n2, n3], axis=-1).reshape(-1, 4) + 1

    else:
        # 3D hexahedral elements
        j, i = np.meshgrid(np.arange(nx - 1), np.arange(ny - 1))

        conn_lst = []
        for k in range(nz - 1):
            # Bottom face nodes (z level)
            n0 = k * (nx * ny) + i * nx + j  # bottom-left-front
            n1 = n0 + 1  # bottom-right-front
            n2 = n0 + 1 + nx  # bottom-right-back
            n3 = n0 + nx  # bottom-left-back

            # Top face nodes (z+1 level)
            n4 = n0 + (nx * ny)  # top-left-front
            n5 = n1 + (nx * ny)  # top-right-front
            n6 = n2 + (nx * ny)  # top-right-back
            n7 = n3 + (nx * ny)  # top-left-back

            conn_lst.append(np.stack([n0, n1, n2, n3, n4, n5, n6, n7], axis=-1).reshape(-1, 8) + 1)

        conn = np.concatenate(conn_lst, axis=0)

    return conn


def _conn_list_to_matrix(i, offsets, connectivity_list):
    """Helper function for connectivity_list_to_matrix"""
    return offsets[i + 1] - offsets[i], connectivity_list[offsets[i] : offsets[i + 1]]


def connectivity_list_to_matrix(connectivity_list: np.ndarray, offsets: np.ndarray) -> np.ndarray:
    """
    Put Connectivity list data into a 2D numpy array where each row contains the Connectivity data of one cell. Empty
    array elements are indicated by value -1.

    Parameters
    ----------
    connectivity_list : numpy.ndarray
        Connectivity list array (N*M,). N number of elements, M number of nodes per element.
    offsets : numpy.ndarray
        offset list array (N*M,). N number of elements, M number of nodes per element.

    Returns
    -------
    numpy.ndarray
        Data array where each row contains the Connectivity data of one cell (N,M). N number of elements, M number of
        nodes per element. Empty array elements are indicated by value -1.
    """

    connectivity_array_lst = [connectivity_list[offsets[i] : offsets[i + 1]] for i in range(len(offsets) - 1)]

    if len(set([len(row) for row in connectivity_array_lst])) == 1:
        connectivity_array = np.array(connectivity_array_lst)
    else:
        n_cells = offsets.size - 1
        max_cell_size = np.max(offsets[1:] - offsets[0:-1])
        conn_shape = (n_cells, max_cell_size)
        connectivity_array = np.zeros(conn_shape, dtype=int) - 1

        for i, row in enumerate(connectivity_array_lst):
            connectivity_array[i, : len(row)] = row

    return connectivity_array


def renumber_connectivity(connectivity: np.ndarray) -> Tuple[np.ndarray, Dict[int, int]]:
    nid_used = set(connectivity.flatten())
    if 0 in nid_used:
        nid_used.remove(0)

    eid_dict: Dict[int, int] = {eid: i + 1 for i, eid in enumerate(sorted(tuple(nid_used)))}
    eid_dict[0] = 0

    return apply_dict_vectorized(data=connectivity, dictionary=eid_dict), eid_dict


def reshape_connectivity(connectivity: np.ndarray) -> np.ndarray:
    """
    Reshape connectivity array to delete all columns containing zeros only.

    Parameters
    ----------
    connectivity: np.ndarray
        Connectivity array with shape (N, M), where N is the number of elements and M is the number of nodes per element.

    Returns
    -------
    np.ndarray
        Reshaped connectivity array with shape (N, M'), where M' is the number of nodes per element after removing columns
        containing zeros only.

    Examples
    --------
    >>> connectivity = np.array([[1, 2, 3, 0], [4, 5, 0, 0], [6, 0, 0, 0]])
    >>> new_connectivity = reshape_connectivity(connectivity)
    """
    # Remove columns containing zeros only
    idx = np.argwhere(np.all(connectivity[..., :] == 0, axis=0))
    return np.delete(connectivity, idx, axis=1)


def compare_coordinate_arrays(arrays: List[np.ndarray], eps: Optional[float] = 1e-9) -> List[np.ndarray]:
    """
    Find indices of rows in multiple arrays where the Euclidean distance
    between rows is smaller than the specified `eps` threshold.

    Parameters
    ----------
    arrays : list of np.ndarray
        A list of 2D NumPy arrays of shape (N, 3), (M, 3), ...,
        where each array contains rows of 3D coordinates.
    eps : float, optional
        The distance threshold for considering two rows as "equal". Default is 1e-9.

    Returns
    -------
    indices : list of np.ndarray
        A list of NumPy arrays, where each array contains the indices of the
        matching rows in the corresponding input array. If no matching rows
        are found, an empty list is returned for each array.

    Raises
    ------
    ValueError
        If fewer than two arrays are provided.

    Notes
    -----
    This function uses broadcasting and NumPy operations to efficiently compute
    pairwise Euclidean distances between rows of the arrays. It starts by comparing
    the first two arrays, and progressively checks for matching rows in the
    subsequent arrays.

    Examples
    --------
    >>> arr1 = np.array([[1.0, 2.0, 3.0], [4.1, 5.2, 6.1], [7.0, 8.0, 9.0]])
    >>> arr2 = np.array([[7.05, 8.02, 9.01], [1.02, 2.03, 3.01], [10.0, 11.0, 12.0]])
    >>> arr3 = np.array([[1.0, 2.0, 3.0], [7.02, 8.01, 9.03], [0.0, 0.0, 0.0]])
    >>> arrays = [arr1, arr2, arr3]
    >>> eps = 0.05
    >>> indices = compare_coordinate_arrays(arrays, eps)
    >>> indices
    [array([0]), array([1]), array([0])]

    """
    num_arrays = len(arrays)
    if num_arrays < 2:
        raise ValueError("At least two arrays are required.")

    # Start by computing pairwise distances between the first two arrays
    diff = arrays[0][:, np.newaxis, :] - arrays[1][np.newaxis, :, :]
    distances = np.linalg.norm(diff, axis=2)

    # Find initial pairs that are within the epsilon threshold
    indices = [np.where(distances < eps)]

    # Loop through the remaining arrays and filter matches
    for i in range(2, num_arrays):
        valid_pairs = []
        for idx1, idx2 in zip(indices[0][0], indices[0][1]):
            # Compute distances between matched rows of the current array and the new array
            diff = arrays[0][idx1] - arrays[i]
            distances = np.linalg.norm(diff, axis=1)
            # Find valid matches in the new array
            valid_matches = np.where(distances < eps)[0]
            if len(valid_matches) > 0:
                for match in valid_matches:
                    valid_pairs.append((idx1, idx2, match))

        # If no valid pairs, return empty lists as NumPy arrays
        if len(valid_pairs) == 0:
            return [np.array([], dtype=np.int64) for _ in range(num_arrays)]  # Ensure correct empty array type

        # Update indices as list of tuples of arrays
        indices = [tuple(np.array([pair[j] for pair in valid_pairs], dtype=np.int64) for j in range(num_arrays))]

    # Ensure the return is a list of NumPy arrays
    return [np.array(ind, dtype=np.int64) for ind in indices[0]]


def list_search(obj: List, item):
    """
    Search list object for item.

    Parameters
    ----------
    obj : list
    item
        Obj list items type must have ``__eq__`` method that is compatible with item.


    Returns
    -------
    Any
        Obj list item

    """
    return obj[obj.index(item)]


def angle(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Compute angle between two vectors v1, v2.

    Parameters
    ----------
    v1 : numpy.ndarray
        Vector 1
    v2 : numpy.ndarray
        Vector 2

    Returns
    -------
    float
        Angle between vectors v1 and v2 in radians.

    """
    cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return np.arccos(cosine_angle)


def element_normal_2d(element_coordinates: np.ndarray) -> np.ndarray:
    """
    Compute normal vector of flat 2d elements.

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Coordinate array of N point flat element. shape = (N,3) or (M,N,3) for M elements

    Returns
    -------
    np.ndarray

    Examples
    --------
    >>> element_normal_vec = element_normal_2d(element_coordinates)

    """

    # get edge vectors
    if element_coordinates.ndim == 2:
        edge_vec = element_coordinates[[1, 2], :] - element_coordinates[[0], :]
        return vecnorm(np.cross(edge_vec[0, :], edge_vec[1, :]))
    elif element_coordinates.ndim == 3:
        edge_vec = element_coordinates[:, [1, 2], :] - element_coordinates[:, [0], :]
        return vecnorm(np.cross(edge_vec[:, 0, :], edge_vec[:, 1, :]), axis=1)
    else:
        raise ValueError("element_coordinates must be of shape (N,3) or (M,N,3).")


def node_normal_2d(element_coordinates: np.ndarray) -> np.ndarray:
    """
    Computes surface normal vector by averaging the element normal vectors of neighboring elements.

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Coordinate array of M neighboring N-point flat elements. shape = (M,N,3)
        The common node must be at the first index [:,0,:]

    Returns
    -------
    np.ndarray
        Normalized normal vector. shape=(3,)

    Examples
    --------
    >>> node_normal_vec = node_normal_2d(element_coordinates)

    """

    element_normal_vec = element_normal_2d(element_coordinates)

    return vecnorm(np.mean(element_normal_vec, axis=0))


def element_angle_2d(element_coordinates: np.ndarray) -> List[float]:
    """
    Compute corner angles of 2D element

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.

    Returns
    -------
    list[float]
        List of corner angles. Index matches index N in element_coordinates.

    """
    corner_angles = []
    for i in range(element_coordinates.shape[0]):
        v1 = element_coordinates[i - 2, :] - element_coordinates[i - 1, :]
        v2 = element_coordinates[i, :] - element_coordinates[i - 1, :]
        corner_angles.append(angle(v1, v2))

    return corner_angles


def element_skew(element_coordinates: np.ndarray, element_type: cfs_element_type) -> float:
    """
    Compute element skewness. Supported element types: TRIA3, QUAD4

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.
    element_type : pyCFS.data.cfs_types.cfs_element_type
        Element type

    Returns
    -------
    float
        Element skewness

    Notes
    -----
    Skewness determines how close to ideal (equilateral or equiangular) a face or cell is. According to the definition
    of skewness, a value of 0 indicates an equilateral cell (best) and a value of 1 indicates a completely degenerate
    cell (worst). Degenerate cells (slivers) are characterized by nodes that are nearly coplanar (colinear in 2D).
    This metric is based on the deviation from a normalized equilateral angle. This method applies to all cell
    and face shapes, including pyramids and prisms. (extracted from "Ansys Meshing User's Guide 2021R2" p.141)

    """
    theta_e = {
        cfs_element_type.TRIA3: np.deg2rad(60),
        cfs_element_type.QUAD4: 0.5 * np.pi,
    }

    if element_type not in theta_e:
        raise NotImplementedError(
            f"{element_type} not supported. Element metric implemented for element types: {list(theta_e.keys())}"
        )

    angles = element_angle_2d(element_coordinates)
    skewness = max(
        (max(angles) - theta_e[element_type]) / (np.pi - theta_e[element_type]),
        (theta_e[element_type] - min(angles)) / theta_e[element_type],
    )

    return skewness


def element_quality_ansys(element_coordinates: np.ndarray, element_type: cfs_element_type) -> float:
    """
    Compute element quality based on ANSYS metric. Supported element types: TRIA3, QUAD4, TET4

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.
    element_type : pyCFS.data.cfs_types.cfs_element_type
        Element type

    Returns
    -------
    float
        Element quality. Unsupported elements return -1.

    Notes
    -----
    This metric is based on the ratio of the volume to the sum of the square of the edge lengths for 2D
    quad/tri elements, or the square root of the cube of the sum of the square of the edge lengths for
    3D elements. A value of 1 indicates a perfect cube or square while a value of 0 indicates that the
    element has a zero or negative volume. (extracted from "Ansys Meshing User's Guide 2021R2" p.130)

    References
    ----------
    "Ansys Meshing User's Guide 2021R2" p.130

    """
    # Factor extracted from "Ansys Meshing User's Guide 2021R2" p.130
    factor = {
        cfs_element_type.TRIA3: 6.92820323,
        cfs_element_type.QUAD4: 4.0,
        cfs_element_type.TET4: 124.70765802,
        cfs_element_type.HEXA8: 41.56921938,
        cfs_element_type.WEDGE6: 62.35382905,
        cfs_element_type.PYRA5: 96,
    }

    if element_type in (cfs_element_type.TRIA3, element_type.QUAD4):
        edge_length = np.linalg.norm(element_coordinates - np.roll(element_coordinates, 1, axis=0), axis=1)
        return factor[element_type] * element_area(element_coordinates, element_type) / sum(edge_length**2)
    elif element_type in (
        cfs_element_type.TET4,
        cfs_element_type.HEXA8,
        cfs_element_type.WEDGE6,
        cfs_element_type.PYRA5,
    ):
        # TODO implement HEXA8, WEDGE6, PYRA5
        match element_type:
            case cfs_element_type.TET4:
                edge_length = np.linalg.norm(element_coordinates - np.roll(element_coordinates, 1, axis=0), axis=1)
                return (
                    factor[element_type]
                    * element_volume(element_coordinates, element_type)
                    / np.sqrt(sum(edge_length**2) ** 3)
                )
            case cfs_element_type.HEXA8:
                edge_length = np.concatenate(
                    (
                        np.linalg.norm(
                            element_coordinates[:4, :] - np.roll(element_coordinates[:4, :], 1, axis=0), axis=1
                        ),
                        np.linalg.norm(
                            element_coordinates[4:, :] - np.roll(element_coordinates[4:, :], 1, axis=0), axis=1
                        ),
                        np.linalg.norm(element_coordinates[:4, :] - element_coordinates[4:, :], axis=1),
                    )
                )
                return (
                    factor[element_type]
                    * element_volume(element_coordinates, element_type)
                    / np.sqrt(sum(edge_length**2) ** 3)
                )
            case _:
                return -1
    else:
        raise NotImplementedError(
            f"{element_type} not supported. Element metric implemented for element types: {list(factor.keys())}"
        )


def element_quality(
    element_coordinates: np.ndarray,
    element_type: cfs_element_type,
    metric: str = "quality",
) -> float:
    """
    Compute element metric

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.
    element_type : pyCFS.data.cfs_types.cfs_element_type
        Element type
    metric : str
        Quality metric. Implemented metrics: Element Quality (Ansys), Skewness

    Returns
    -------
    float
        Element quality. Unsupported elements return -1.

    """
    if metric == "quality":
        return element_quality_ansys(element_coordinates, element_type)
    elif metric == "skewness":
        return element_skew(element_coordinates, element_type)
    else:
        raise NotImplementedError("Implemented element metrics: Element Quality (Ansys), Skewness")


def element_area(element_coordinates: np.ndarray, element_type: cfs_element_type) -> float:
    """
    Compute area of 2D element. Implemented element types: TRIA3, QUAD4

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.
    element_type : pyCFS.data.cfs_types.cfs_element_type
        Element type

    Returns
    -------
    float
        Element area

    """
    return element_volume(element_coordinates, element_type)


def element_volume(element_coordinates: np.ndarray, element_type: cfs_element_type | int) -> float:
    """
    Compute volume of 3D element or area of 2D element. Implemented element types: TET4, HEXA8, TRIA3, QUAD4

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.
    element_type : pyCFS.data.cfs_types.cfs_element_type
        Element type

    Returns
    -------
    float
        Element volume

    """
    match element_type:
        # Volume elements
        case cfs_element_type.TET4:
            v1 = element_coordinates[0, :] - element_coordinates[3, :]
            v2 = element_coordinates[1, :] - element_coordinates[3, :]
            v3 = element_coordinates[2, :] - element_coordinates[3, :]
            return float(1.0 / 6 * np.linalg.norm(np.dot(v1, np.cross(v2, v3))))
        case cfs_element_type.HEXA8:
            # Define the five tetrahedra by their node indices
            tetrahedra = [(0, 1, 2, 5), (2, 6, 7, 5), (0, 5, 7, 4), (0, 2, 3, 7), (0, 2, 5, 7)]
            return sum(
                [
                    element_volume(element_coordinates[list(tetrahedron), :], cfs_element_type.TET4)
                    for tetrahedron in tetrahedra
                ]
            )
        # Surface elements
        case cfs_element_type.TRIA3:
            v1 = element_coordinates[1, :] - element_coordinates[0, :]
            v2 = element_coordinates[2, :] - element_coordinates[0, :]
            return float(0.5 * np.linalg.norm(np.cross(v1, v2)))
        case cfs_element_type.QUAD4:
            return element_volume(element_coordinates[:3, :], cfs_element_type.TRIA3) + element_volume(
                element_coordinates[[0, 2, 3], :], cfs_element_type.TRIA3
            )
        case _:
            supported_element_types = [
                cfs_element_type.TET4,
                cfs_element_type.HEXA8,
                cfs_element_type.TRIA3,
                cfs_element_type.QUAD4,
            ]
            raise NotImplementedError(f"Implemented element types: {supported_element_types}")


def element_centroid(element_coordinates: np.ndarray) -> np.ndarray:
    """
    Compute geometric center of element

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of node Coordinates (Nx3) or Array of elements (MxNx3), where M is the number of elements and N is the
        number of nodes.

    Returns
    -------
    numpy.ndarray
        Geometric center of element

    """
    if element_coordinates.ndim == 2:
        return np.mean(element_coordinates, axis=0)
    elif element_coordinates.ndim == 3:
        return np.mean(element_coordinates, axis=1)
    else:
        raise ValueError(
            "Expect element coordinates to be of shape (MxNx3) or (Nx3), "
            "where M is the number of elements and N is the number of nodes."
        )


def vecnorm(v: np.ndarray, order: int | None = None, axis: int | None = None) -> np.ndarray:
    """
    Normalize vector

    Parameters
    ----------
    v : numpy.ndarray
        Vector / array of vectors to normalize
    order : {non-zero int, inf, -inf, 'fro', 'nuc'}, optional
        Order of the norm (see table under ``Notes``). inf means numpy's
        `inf` object. The default is None.
    axis : {None, int, 2-tuple of ints}, optional
        If `axis` is an integer, it specifies the axis of `x` along which to
        compute the vector norms.  If `axis` is a 2-tuple, it specifies the
        axes that hold 2-D matrices, and the matrix norms of these matrices
        are computed.  If `axis` is None then either a vector norm (when `x`
        is 1-D) or a matrix norm (when `x` is 2-D) is returned. The default
        is None.

    Returns
    -------
    numpy.ndarray
        Normalized vector / array of vectors

    """
    v_norm = np.linalg.norm(v, ord=order, axis=axis)
    if v_norm.ndim == 0:
        v_return = v / v_norm
    elif v_norm.ndim == 1 and v.ndim == 2:
        v_return = v / np.tile(v_norm, (v.shape[1], 1)).T
    else:
        raise NotImplementedError(
            f"Normalizing array of dimension {v.ndim} with norm array of dimension {v_norm.ndim} not implemented"
        )

    return v_return


def trilateration(
    c1: np.ndarray, c2: np.ndarray, c3: np.ndarray, r1: float, r2: float, r3: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find the intersection of three spheres with centers C1,C2,C3 and radii r1,r2,r3.
    Yields 2 feasible intersection points.

    Parameters
    ----------
    c1 : numpy.ndarray
        Center Coordinates of sphere 1.
    c2 : numpy.ndarray
        Center Coordinates of sphere 2.
    c3 : numpy.ndarray
        Center Coordinates of sphere 3.
    r1 : float
        Radius of sphere 1.
    r2 : float
        Radius of sphere 2.
    r3 : float
        Radius of sphere 3.

    Returns
    -------
    p1 : numpy.ndarray
        Coordinates of intersection point 1
    p2 : numpy.ndarray
        Coordinates of intersection point 2

    References
    -----
    Implementaton based on Wikipedia Trilateration article:
    https://en.wikipedia.org/wiki/True-range_multilateration#Three_Cartesian_dimensions,_three_measured_slant_ranges

    """

    # Define coordinate system with origin in C1, C2 on x-axis, and C3 in xy-plane
    v1 = c2 - c1
    v2 = c3 - c1

    e1 = vecnorm(v1)
    e3 = vecnorm(np.cross(v1, v2))
    e2 = np.cross(e3, e1)

    u = np.dot(e1, v1)
    vx = np.dot(e1, v2)
    vy = np.dot(e2, v2)

    x = ((r1**2) - (r2**2) + (u**2)) / (2 * u)
    y = ((r1**2) - (r3**2) + (vx**2) + (vy**2) - (2 * vx * x)) / (2 * vy)
    z = np.sqrt(r1**2 - x**2 - y**2)

    k1 = c1 + x * e1 + y * e2 + z * e3
    k2 = c1 + x * e1 + y * e2 - z * e3
    return k1, k2


def apply_dict_vectorized(data: np.ndarray, dictionary: Dict, val_no_key: Optional[Any] = None):
    """
    Apply dictionary to data array. Vectorized implementation. Fast approach for small number of unique elements,
    according to https://stackoverflow.com/questions/16992713/translate-every-element-in-numpy-array-according-to-key

    Parameters
    ----------
    data: np.ndarray
        Data array to apply dictionary to
    dictionary: Dict
        Dictionary to apply to data array
    val_no_key: Any, optional
        Value to apply if key is not in dictionary. Default is ``None``.

    Returns
    -------
    np.ndarray
        Data array with dictionary applied


    """
    u, inv = np.unique(data, return_inverse=True)
    if all([x in dictionary for x in u]):
        return np.array([dictionary[x] for x in u])[inv].reshape(data.shape)
    else:
        tmp = []
        for x in u:
            if x in dictionary:
                tmp.append(dictionary[x])
            else:
                tmp.append(val_no_key)

        return np.array(tmp)[inv].reshape(data.shape)


def merge_nested_dict(dict_target: Dict, dict_source: Dict, path: List[str] | None = None) -> Dict:
    """
    Merge nested dictionary ``dict_source`` into nested dictionary ``dict_target``.

    Parameters
    ----------
    dict_target : dict
        Target dictionary
    dict_source : dict
        Source dictionary
    path : list[str], optional
        Dynamic dictionary path for recursive call. Default is ``None``.

    Returns
    -------
    dict
        Merged nested dictionary

    """
    if path is None:
        path = []
    for key in dict_source:
        if key in dict_target:
            if isinstance(dict_target[key], dict) and isinstance(dict_source[key], dict):
                merge_nested_dict(dict_target[key], dict_source[key], path + [str(key)])
            elif dict_target[key] == dict_source[key]:
                pass  # same leaf value
            else:
                raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            dict_target[key] = dict_source[key]
    return dict_target


def vprint(*args, verbose=True, **kwargs) -> None:
    # noinspection PyArgumentEqualDefault,PyUnresolvedReferences
    """
    If verbose flag is ``True``, prints the values to a stream, or to sys.stdout by default.

    Parameters
    ----------
    args
        Value to print.
    verbose : bool, optional
        Flag whether to print
    file : , optional
        a file-like object (stream); defaults to the current sys.stdout.
    sep : str, optional
        string inserted between values, default a space.
    end : str, optional
        string appended after the last value, default a newline.
    flush : bool, optional
        whether to forcibly flush the stream.

    Examples
    --------
    >>> from pyCFS.data.util import vprint
    >>> vprint(value, verbose=True, sep=' ', end='\\n', file=sys.stdout, flush=False)

    """
    if verbose:
        print(*args, **kwargs)


def progressbar(it: Collection, prefix="", size=40, out=sys.stdout, max_update=1000, show_etc=True, verbose=True):
    """
    Shows and updates (overwrites) progressbar, updates every iteration

    Parameters
    ----------
    it
    prefix : str
        Prefix to the progress bar
    size : int, optional
        Number of characters used to print the progress bar. Default value is ``40``
    out : optional
        a file-like object (stream); defaults to the current sys.stdout.
    max_update : int, optional
        Maximum number of updates to show in the progress bar. Skippes iterations if ``it`` exceeds ``max_update``.
    show_etc : bool, optional
        Flag whether to show ETC (estimated time to completion); defaults to ``True``.
    verbose : bool, optional
        Flag whether to print the progress bar. Defaults to ``True``.

    Examples
    --------
    >>> for _ in progressbar(range(5),prefix='Looping: '):
    >>>    pass

    """
    count = len(it)
    if count == 0:
        return

    def show(j, etc: float | None = None):
        """Show progressbar"""
        x = int(size * j / count)
        if not show_etc or (etc is None):
            vprint(
                f"{prefix}[{u'█' * x}{('.' * (size - x))}] {j}/{count}",
                end="\r",
                file=out,
                flush=True,
                verbose=verbose,
            )
        else:
            vprint(
                f"{prefix}[{u'█' * x}{('.' * (size - x))}] {j}/{count} | ETA: {datetime.timedelta(seconds=etc)}",
                end="\r",
                file=out,
                flush=True,
                verbose=verbose,
            )

    time_start = time.time()
    show(0)
    time_iter_list = np.array([])
    movmean_window = int(count / 20)
    if count < max_update:
        for i, item in enumerate(it):
            time_iter_start = time.time()
            yield item
            time_iter = time.time() - time_iter_start
            time_iter_list = np.append(time_iter_list, time_iter)
            time_per_iter = np.mean(time_iter_list[max(0, i - movmean_window) :])
            time_etc = np.ceil((count - i) * time_per_iter)
            show(i + 1, etc=time_etc)
    else:
        step = int(count / max_update)
        time_etc = 0
        time_iter_start = time.time()
        for i, item in enumerate(it):
            yield item
            if i % step == 0:
                time_iter = time.time() - time_iter_start
                time_iter_list = np.append(time_iter_list, time_iter)
                time_per_iter = np.mean(time_iter_list[max(0, int((i - movmean_window) / step)) :])
                time_etc = np.ceil((count - i) * time_per_iter / step)
                show(i + 1, etc=time_etc)
                time_iter_start = time.time()
        show(count, etc=time_etc)
    vprint(
        f"\x1b[2K\r{prefix}[{u'█' * size}] {count}/{count} | Elapsed time: {datetime.timedelta(seconds=int(time.time() - time_start))}",
        file=out,
        flush=True,
        verbose=verbose,
    )


class TimeRecord:
    """
    Context manager for recording the elapsed time of a code block.

    Parameters
    ----------
    message : str, optional
        Message to display with the elapsed time. Default is an empty string.
    single_line : bool, optional
        Whether to display the elapsed time in a single line. Default is True.
        Set to False to display the elapsed time in a new line (in case the code block
        includes prints).
    out : file-like object, optional
        Stream to which the message will be printed. Default is sys.stdout.

    Attributes
    ----------
    TimeStart : float
        Time when the context block started.
    TimeElapsed : float
        Elapsed time in seconds since the context block started.

    Examples
    --------
    >>> with TimeRecord(message="Run function", single_line=False):
    >>>     print("do stuff")

    >>> with TimeRecord(message="Run function"):
    >>>     pass

    >>> with TimeRecord(message="Run function", single_line=False) as t_rec:
    >>>     print("do stuff")
    >>>     print(f"Time elapsed: {t_rec.TimeElapsed}")
    >>>     print("do more stuff")
    """

    def __init__(self, message="", single_line=True, out=sys.stdout, verbose=True) -> None:
        self.TimeStart = 0.0
        self.Message = message
        self.SingleLine = single_line
        self.Out = out
        self.Verbose = verbose

    def __enter__(self) -> TimeRecord:
        end = "\r" if self.SingleLine else "\n"
        vprint(f"{self.Message}", end=end, file=self.Out, flush=True, verbose=self.Verbose)
        self.TimeStart = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        vprint(
            f"{self.Message} | Elapsed time: {datetime.timedelta(seconds=floor(self.TimeElapsed))}",
            file=self.Out,
            flush=True,
            verbose=self.Verbose,
        )

    def __repr__(self):
        return f"TimeRecord (message={self.Message}, single_line={self.SingleLine}, out={self.Out})"

    def __str__(self) -> str:
        return f"{self.Message} | Elapsed time: {datetime.timedelta(seconds=floor(self.TimeElapsed))}"

    @property
    def TimeElapsed(self) -> float:
        """Elapsed time in seconds since the context block started."""
        return time.time() - self.TimeStart
