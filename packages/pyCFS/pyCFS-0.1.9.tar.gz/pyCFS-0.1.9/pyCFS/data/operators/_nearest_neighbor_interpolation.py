"""
This module provides functions to compute interpolation matrices using nearest neighbor search with inverse distance weighting.
"""

import numpy as np
import scipy
from scipy.spatial import KDTree

from pyCFS.data import v_def
from pyCFS.data.util import TimeRecord, progressbar


def _interpolation_matrix_nearest_neighbor_backward(
    source_coord: np.ndarray,
    target_coord: np.ndarray,
    num_neighbors=20,
    interpolation_exp=2.0,
    max_distance: float | None = None,
    workers=-1,
    verbosity=v_def.release,
) -> scipy.sparse.csr_array:
    """
    Computes interpolation matrix based on nearest neighbor search with inverse distance weighting (Shepard's method)
    (see https://opencfs.gitlab.io/userdocu/DataExplanations/NN/). Nearest neighbors are searched for each point on the
    (coarser) target grid. Leads to checkerboard if the target grid is finer than the source grid.
    """
    # Calculate weights
    with TimeRecord("KDTree search", verbose=verbosity >= v_def.debug):
        source_coord_kdtree = KDTree(source_coord)
        d, idx_list = source_coord_kdtree.query(target_coord, num_neighbors, workers=workers)

    matrix_shape = (target_coord.shape[0], source_coord.shape[0])

    with TimeRecord("Compute weights", verbose=verbosity >= v_def.debug):
        col_ind = []
        row_ptr = []
        counter = 0

        if num_neighbors == 1:
            val = np.ones((target_coord.shape[0]))
            idx_list = np.expand_dims(idx_list, axis=1)
        else:
            # Prevent zero division
            d[d == 0] += np.finfo(d.dtype).eps
            # Compute weights
            dmax = np.tile(1.01 * d.max(axis=1), (num_neighbors, 1)).T
            w = ((dmax - d) / (dmax * d)) ** interpolation_exp
            a = np.tile(np.sum(w, axis=1), (num_neighbors, 1)).T
            w /= a
            val = w.flatten()

    if max_distance is not None:
        with TimeRecord("Apply max distance", verbose=verbosity >= v_def.debug):
            # Set weights for neighbors that exceed max_distance to zero
            # TODO normalize weights again (currently sum(w) can be < 1)
            # TODO remove zero values from sparse matrix
            idx_zero = d > max_distance
            val[idx_zero.flatten()] = 0

    for idx_el in progressbar(
        list(idx_list), prefix="Creating interpolation matrix: ", verbose=verbosity >= v_def.release
    ):
        for idx_source in idx_el:
            col_ind.append(idx_source)
        row_ptr.append(counter)
        counter += num_neighbors
    row_ptr.append(counter)
    interpolation_matrix = scipy.sparse.csr_array(
        (val, np.array(col_ind).flatten(), np.array(row_ptr)), matrix_shape, dtype=float
    )

    return interpolation_matrix


def _interpolation_matrix_nearest_neighbor_forward(
    source_coord: np.ndarray,
    target_coord: np.ndarray,
    num_neighbors=20,
    interpolation_exp=2.0,
    max_distance: float | None = None,
    workers=-1,
    verbosity=v_def.release,
) -> scipy.sparse.csc_array:
    """
    Computes interpolation matrix based on nearest neighbor search with inverse distance weighting (Shepard's method)
    (see https://opencfs.gitlab.io/userdocu/DataExplanations/NN/). Nearest neighbors are searched for each point on the
    (coarser) source grid. Leads to overprediction if the source grid is finer than the target grid.
    """
    # Calculate weights
    with TimeRecord("KDTree search", verbose=verbosity >= v_def.debug):
        target_coord_kdtree = KDTree(target_coord)
        d, idx_list = target_coord_kdtree.query(source_coord, num_neighbors, workers=workers)

    matrix_shape = (target_coord.shape[0], source_coord.shape[0])

    with TimeRecord("Compute weights", verbose=verbosity >= v_def.debug):
        row_ind = []
        col_ptr = []
        counter = 0

        if num_neighbors == 1:
            val = np.ones((source_coord.shape[0]))
            idx_list = np.expand_dims(idx_list, axis=1)
        else:
            # Compute weights
            d += np.finfo(float).eps  # Offset to prevent division by zero
            dmax = np.tile(1.01 * d.max(axis=1), reps=(num_neighbors, 1)).T
            w = ((dmax - d) / (dmax * d)) ** interpolation_exp
            a = np.tile(np.sum(w, axis=1), reps=(num_neighbors, 1)).T
            w /= a
            val = w.flatten()

    if max_distance is not None:
        with TimeRecord("Apply max distance", verbose=verbosity >= v_def.debug):
            # Set weights for neighbors that exceed max_distance to zero
            # TODO normalize weights again (currently sum(w) can be < 1)
            # TODO remove zero values from sparse matrix
            idx_zero = d > max_distance
            val[idx_zero.flatten()] = 0

    for idx_el in progressbar(
        list(idx_list), prefix="Creating interpolation matrix: ", verbose=verbosity >= v_def.release
    ):
        for idx_target in idx_el:
            row_ind.append(idx_target)
        col_ptr.append(counter)
        counter += num_neighbors
    col_ptr.append(counter)

    interpolation_matrix = scipy.sparse.csc_array(
        (val, np.array(row_ind).flatten(), np.array(col_ptr)), matrix_shape, dtype=float
    )

    return interpolation_matrix
