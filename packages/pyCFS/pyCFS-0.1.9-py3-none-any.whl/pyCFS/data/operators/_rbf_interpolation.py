"""
This module provides functions to interpolate data and compute gradients using radial basis functions (RBF).
"""

from typing import Optional, Sequence, List, Dict, Callable, Tuple

import numpy as np
from scipy.spatial import KDTree

from pyCFS.data import io, v_def
from pyCFS.data.io import cfs_types
from pyCFS.data.io.cfs_types import cfs_result_type
from pyCFS.data.util import progressbar, vprint, TimeRecord


def _gaussian_rbf(r: np.ndarray, epsilon=1.0) -> np.ndarray:
    r"""
    Gaussian radial basis function (RBF) kernel.

    Parameters
    ----------
    r : np.ndarray
        Pairwise distances between points.
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.

    Returns
    -------
    phi : np.ndarray
        Kernel values evaluated at the given distances.

    Notes
    -----
    The Gaussian RBF is defined as:
    .. math::
        \phi(r) = e^{-(\epsilon r)^2}

    where :math:`r` is the distance between points and :math:`\epsilon` is a shape parameter.
    """
    return np.exp(-((epsilon * r) ** 2))


def _gaussian_grad_rbf(x: np.ndarray, y: np.ndarray, epsilon=1.0) -> np.ndarray:
    r"""
    Gradient of the Gaussian RBF kernel with respect to x.

    Parameters
    ----------
    x : np.ndarray
        Target point(s), shape (N,) or (Q, N).
    y : np.ndarray
        Source point(s), shape (P, N).
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.

    Returns
    -------
    grad : np.ndarray
        Gradient of the kernel, shape (P, N).

    Notes
    -----
    The Gradient of the Gaussian RBF is defined as:
    .. math::
        \nabla \phi(x, y) = -2 \epsilon^2 \phi(r) (x - y)

    where :math:`\phi` is the gaussian rbf kernel, :math:`r` is the distance between points,
    :math:`x` is the target point, and :math:`y` is the source point.
    """
    diff = x[None, :] - y[:, None, :]  # shape (P, N)
    r = np.linalg.norm(diff, axis=-1)  # (P,)
    factor = -2 * epsilon**2 * _gaussian_rbf(r, epsilon)  # (P,)
    return factor[..., None] * diff  # (P, N)


def _multiquadratic_rbf(r: np.ndarray, epsilon=1.0) -> np.ndarray:
    r"""
    Multiquadratic radial basis function (RBF) kernel.

    Parameters
    ----------
    r : np.ndarray
        Pairwise distances between points.
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.

    Returns
    -------
    phi : np.ndarray
        Kernel values evaluated at the given distances.

    Notes
    -----
    The multiquadratic RBF is defined as:
    .. math::
        \phi(r) = \sqrt{1 + (\epsilon r)^2}

    where :math:`r` is the distance between points and :math:`\epsilon` is a shape parameter.
    """
    return np.sqrt(1.0 + (epsilon * r) ** 2)


def _multiquadratic_grad_rbf(x: np.ndarray, y: np.ndarray, epsilon=1.0) -> np.ndarray:
    r"""
    Gradient of the multiquadratic RBF kernel with respect to x.

    Parameters
    ----------
    x : np.ndarray
        Target point(s), shape (N,) or (Q, N).
    y : np.ndarray
        Source point(s), shape (P, N).
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.

    Returns
    -------
    grad : np.ndarray
        Gradient of the kernel, shape (P, N).

    Notes
    -----
    The gradient of the multiquadratic RBF is defined as:
    .. math::
        \nabla \phi(x, y) = \frac{\epsilon^2 (x - y)}{\sqrt{1 + (\epsilon r)^2}}

    where :math:`\phi` is the multiquadratic rbf kernel, :math:`r` is the distance between points,
    :math:`x` is the target point, and :math:`y` is the source point.
    """
    diff = x[None, :] - y[:, None, :]  # shape (P, N)
    r = np.linalg.norm(diff, axis=-1)  # (P,)
    denom = np.sqrt(1.0 + (epsilon * r) ** 2)  # (P,)
    return (epsilon**2 * diff) / denom[..., None]  # (P, N)


def _wendland_c2_rbf(r: np.ndarray, epsilon=1.0) -> np.ndarray:
    r"""
    Wendland C2 compactly supported RBF kernel.

    Parameters
    ----------
    r : np.ndarray
        Pairwise distances between points.
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.

    Returns
    -------
    phi : np.ndarray
        Kernel values evaluated at the given distances.

    Notes
    -----
    The Wendland C2 RBF is defined as:
    .. math::
        \phi(r) = (1 - \frac{r}{\epsilon})^4 (4 \frac{r}{\epsilon} + 1) for r < \epsilon, 0 otherwise

    where :math:`r` is the distance between points and :math:`\epsilon` is a shape parameter.
    """
    s = np.clip(1 - (r / epsilon), 0, None)
    return s**4 * (4 * (r / epsilon) + 1)


def _wendland_c2_grad_rbf(x: np.ndarray, y: np.ndarray, epsilon=1.0) -> np.ndarray:
    r"""
    Gradient of the Wendland C2 RBF kernel with respect to x.

    Parameters
    ----------
    x : np.ndarray
        Target point(s), shape (N,) or (Q, N).
    y : np.ndarray
        Source point(s), shape (P, N).
    epsilon : float
        Shape parameter for the RBF kernel.

    Returns
    -------
    grad : np.ndarray
        Gradient of the kernel, shape (P, N).

    Notes
    -----
    The gradient of the Wendland C2 RBF is defined as:
    .. math::
        \nabla \phi(x, y) = -20 \frac{(r / \epsilon)^3}{\epsilon^2} (1 - \frac{r}{\epsilon})^3 (x - y) for r < \epsilon, 0 otherwise

    where :math:`\phi` is the Wendland C2 rbf kernel, :math:`r` is the distance between points,
    :math:`x` is the target point, and :math:`y` is the source point.
    """
    diff = x[None, :] - y[:, None, :]  # (P, N)
    r = np.linalg.norm(diff, axis=-1)  # (P,)
    s = np.clip(1 - (r / epsilon), 0, None)
    mask = r < epsilon
    # Derivative w.r.t. r
    dphi_dr = -20 * (r / epsilon**2) * s**3
    dphi_dr[~mask] = 0.0
    # Chain rule: dphi/dx = dphi/dr * dr/dx
    grad = dphi_dr[..., None] * (diff / (r[..., None] + 1e-12))
    grad[~mask] = 0.0
    return grad


_kernel_dict = {
    "gaussian": _gaussian_rbf,
    "multiquadratic": _multiquadratic_rbf,
    "wendland_c2": _wendland_c2_rbf,
}
_kernel_grad_dict = {
    "gaussian": _gaussian_grad_rbf,
    "multiquadratic": _multiquadratic_grad_rbf,
    "wendland_c2": _wendland_c2_grad_rbf,
}


def _build_rbf_system(
    coord: np.ndarray, vals: np.ndarray, kernel_func: Callable, epsilon=1.0, smoothing=0.0
) -> np.ndarray:
    """
    Construct and solve the RBF linear system for interpolation coefficients.

    Parameters
    ----------
    coord : np.ndarray
        Source coordinates of shape (P, N), where P is the number of points and N is the spatial dimension.
    vals : np.ndarray
        Source data values of shape (P, S), where S is the number of data components.
    kernel_func : Callable
        Kernel function of the form `kernel_func(r, epsilon)` returning kernel values for pairwise distances.
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.
    smoothing : float, optional
        Smoothing parameter added to the diagonal of the kernel matrix. Default is 0.0.

    Returns
    -------
    coeffs : np.ndarray
        RBF interpolation coefficients, shape (P, S).
    """

    P, N = coord.shape
    vals = np.atleast_2d(vals)
    if vals.shape[0] != P:
        vals = vals.T  # ensure shape (P, S)

    # Build kernel matrix
    dists = np.linalg.norm(coord[:, None, :] - coord[None, :, :], axis=-1)
    K = kernel_func(dists, epsilon)

    # Add smoothing term to the diagonal
    K.flat[:: P + 1] += smoothing

    # Solve
    sol = np.linalg.solve(K, vals)
    coeffs = sol[:P]  # RBF weights

    return coeffs


def _evaluate_rbf(
    coord_trg: np.ndarray, coord_rbf: np.ndarray, coeffs: np.ndarray, kernel_func: Callable, epsilon=1.0
) -> np.ndarray:
    """
    Evaluate the RBF interpolant at target points.

    Parameters
    ----------
    coord_trg : np.ndarray
        Target coordinates of shape (Q, N), where Q is the number of target points and N is the spatial dimension.
    coord_rbf : np.ndarray
        Source coordinates used for the RBF system, shape (P, N), where P is the number of source points.
    coeffs : np.ndarray
        RBF interpolation coefficients, shape (P, S), where S is the number of data components.
    kernel_func : Callable
        Kernel function of the form `kernel_func(r, epsilon)` returning kernel values for pairwise distances.
    epsilon : float, optional
        Shape parameter for the RBF kernel.

    Returns
    -------
    data_trg : np.ndarray
        Interpolated values at the target points, shape (Q, S).
    """
    coord_trg = np.atleast_2d(coord_trg)

    dists = np.linalg.norm(coord_trg[:, None, :] - coord_rbf[None, :, :], axis=-1)  # (Q, P)
    phi = kernel_func(dists, epsilon)  # (Q, P)

    return phi @ coeffs  # (Q, S)


def _evaluate_rbf_gradient(
    coord_trg: np.ndarray, coord_rbf: np.ndarray, coeffs: np.ndarray, grad_kernel_func: Callable, epsilon=1.0
) -> np.ndarray:
    """
    Evaluate the gradient (Jacobian) of the RBF interpolant at a target point.

    Parameters
    ----------
    coord_trg : np.ndarray
        Target point coordinates, shape (Q, N), where N is the spatial dimension and Q is the number of target points.
    coord_rbf : np.ndarray
        Source coordinates used for the RBF system, shape (P, N), where P is the number of source points.
    coeffs : np.ndarray
        RBF interpolation coefficients, shape (P, S), where S is the number of data components.
    grad_kernel_func : Callable
        Gradient of the kernel function of the form `grad_kernel_func(x, y, epsilon)` returning gradients for each pair of points.
    epsilon : float
        Shape parameter for the RBF kernel.

    Returns
    -------
    grad_trg : np.ndarray
        Gradient of the RBF interpolant at the target point(s), shape (S, N).
    """
    coord_trg = np.asarray(coord_trg)
    coord_rbf = np.asarray(coord_rbf)

    grad_rbf = grad_kernel_func(coord_trg, coord_rbf, epsilon)  # shape (P, N)
    grad_rbf_term = np.sum(grad_rbf * coeffs[..., None], axis=0)  # shape (N, S)

    return grad_rbf_term


_supported_res_types = (
    cfs_result_type.UNDEFINED,
    cfs_result_type.NODE,
    cfs_result_type.EDGE,
    cfs_result_type.FACE,
    cfs_result_type.ELEMENT,
    cfs_result_type.SURF_ELEM,
    # cfs_result_type.REGION,
    # cfs_result_type.REGION_AVERAGE,
    # cfs_result_type.SURF_REGION,
    # cfs_result_type.NODELIST,
    # cfs_result_type.COIL,
    # cfs_result_type.FREE,
)


def interpolation_rbf(
    coord_src: np.ndarray,
    coord_trg: np.ndarray,
    data_src: np.ndarray | io.CFSResultArray,
    kernel="gaussian",
    epsilon=1.0,
    smoothing=1e-12,
) -> np.ndarray:
    """
    Interpolate values at target points using Radial Basis Function (RBF) interpolation.

    Parameters
    ----------
    coord_src : np.ndarray
        Source coordinates of shape (P, N), where P is the number of source points and N is the spatial dimension.
    coord_trg : np.ndarray
        Target coordinates of shape (Q, N), where Q is the number of target points.
    data_src : np.ndarray or io.CFSResultArray
        Source data values of shape (P, S), where S is the number of data components.
    kernel : str, optional
        Type of RBF kernel to use. Available kernels: "gaussian", "multiquadratic", "wendland_c2".
        Default is "gaussian".
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.
    smoothing : float, optional
        Smoothing parameter added to the diagonal of the kernel matrix. Default is 1e-12.
    verbosity : int, optional
        Verbosity level. Default is `v_def.release`.

    Returns
    -------
    data_trg : np.ndarray
        Interpolated values at the target points, shape (Q, S).
    """
    kernel_func = _kernel_dict[kernel]

    # Build RBF system
    coeffs = _build_rbf_system(coord_src, data_src, kernel_func, epsilon=epsilon, smoothing=smoothing)

    # Evaluate RBF system at target coordinates
    return _evaluate_rbf(coord_trg, coord_src, coeffs, kernel_func, epsilon=epsilon)


def jacobian_rbf(
    coord_src: np.ndarray,
    coord_trg: np.ndarray,
    data_src: np.ndarray | io.CFSResultArray,
    kernel="gaussian",
    epsilon=1.0,
    smoothing=1e-12,
) -> np.ndarray:
    """
    Compute the gradient (Jacobian) of the RBF interpolant at target points.

    Parameters
    ----------
    coord_src : np.ndarray
        Source coordinates of shape (P, N), where P is the number of source points and N is the spatial dimension.
    coord_trg : np.ndarray
        Target coordinates of shape (Q, N), where Q is the number of target points.
    data_src : np.ndarray or io.CFSResultArray
        Source data values of shape (P, S), where S is the number of data components.
    kernel : str, optional
        Type of RBF kernel to use. Available kernels: "gaussian", "multiquadratic", "wendland_c2".
        Default is "gaussian".
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.
    smoothing : float, optional
        Smoothing parameter added to the diagonal of the kernel matrix. Default is 1e-12.

    Returns
    -------
    grad_trg : np.ndarray
        Gradient of the RBF interpolant at the target points, shape (Q, S, N).
    """
    kernel_func = _kernel_dict[kernel]
    kernel_grad_func = _kernel_grad_dict[kernel]

    # Build RBF system
    coeffs = _build_rbf_system(coord_src, data_src, kernel_func, epsilon=epsilon, smoothing=smoothing)

    # Evaluate Jacobian at target coordinates
    grad_trg = np.full((coord_trg.shape[0], data_src.shape[1], coord_trg.shape[1]), fill_value=np.nan)
    for didx in range(data_src.shape[1]):
        grad_trg[:, didx, :] = _evaluate_rbf_gradient(coord_trg, coord_src, coeffs, kernel_grad_func, epsilon=epsilon)

    return grad_trg


def interpolation_rbf_local(
    coord_src: np.ndarray,
    coord_trg: np.ndarray,
    data_src: np.ndarray | io.CFSResultArray,
    kernel="gaussian",
    epsilon=1.0,
    smoothing=1e-12,
    neighbors=100,
    min_neighbors: Optional[int] = None,
    radius_factor: float = 2.0,
    verbosity: int = v_def.release,
) -> np.ndarray:
    """
    Interpolate values at target points using local RBF interpolation.

    Parameters
    ----------
    coord_src : np.ndarray
        Source coordinates of shape (P, N).
    coord_trg : np.ndarray
        Target coordinates of shape (Q, N).
    data_src : np.ndarray or io.CFSResultArray
        Source data values of shape (P, S).
    kernel : str, optional
        Type of RBF kernel to use. Available kernels: "gaussian", "multiquadratic", "wendland_c2".
        Default is "gaussian".
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.
    smoothing : float, optional
        Smoothing parameter for the kernel matrix. Default is 1e-12.
    neighbors : int, optional
        Number of nearest neighbors to use for local interpolation. Default is 100.
    min_neighbors : int or None, optional
        Minimum number of neighbors to use. Default is None.
    radius_factor : float, optional
        Factor to determine the local neighborhood radius. Default is 2.0.
    verbosity : int, optional
        Verbosity level. Default is `v_def.release`.

    Returns
    -------
    data_trg : np.ndarray
        Interpolated values at the target points, shape (Q, S).
    """
    kernel_func = _kernel_dict[kernel]

    tree = KDTree(coord_src)

    data_trg = np.zeros((coord_trg.shape[0], data_src.shape[1]), dtype=data_src.dtype)

    for cidx in progressbar(
        range(coord_trg.shape[0]), prefix="Perform RBF interpolation: ", verbose=verbosity >= v_def.debug
    ):
        dists, nidx_max = tree.query(coord_trg[cidx, :], k=neighbors)

        if min_neighbors is None:
            nidx = nidx_max
        else:
            # Compute adaptive radius from first k_min neighbors
            k_eff = min(min_neighbors, len(dists))
            local_radius = radius_factor * np.mean(dists[:k_eff])

            mask = dists <= local_radius
            if np.sum(mask) < min_neighbors:
                # Ensure at least k_min neighbors
                mask[:min_neighbors] = True

            vprint(
                f"Target {cidx + 1}/{coord_trg.shape[0]}: Using {np.sum(mask)} neighbors",
                verbose=verbosity >= v_def.debug,
            )

            nidx = nidx_max[mask]

        # Build RBF system
        coeffs_local = _build_rbf_system(
            coord_src[nidx, :], data_src[nidx, ...], kernel_func, epsilon=epsilon, smoothing=smoothing
        )

        # Evaluate RBF system at target coordinates
        data_trg_local = _evaluate_rbf(
            coord_trg[cidx, :], coord_src[nidx, :], coeffs_local, kernel_func, epsilon=epsilon
        )

        data_trg[cidx, :] = data_trg_local

    return data_trg


def jacobian_rbf_local(
    coord_src: np.ndarray,
    coord_trg: np.ndarray,
    data_src: np.ndarray | io.CFSResultArray,
    kernel="gaussian",
    epsilon=1.0,
    smoothing=1e-12,
    neighbors=200,
    min_neighbors: Optional[int] = None,
    radius_factor: float = 2.0,
    verbosity: int = v_def.release,
) -> np.ndarray:
    """
    Compute the gradient (Jacobian) of the local RBF interpolant at target points.

    Parameters
    ----------
    coord_src : np.ndarray
        Source coordinates of shape (P, N).
    coord_trg : np.ndarray
        Target coordinates of shape (Q, N).
    data_src : np.ndarray or io.CFSResultArray
        Source data values of shape (P, S).
    kernel : str, optional
        Type of RBF kernel to use. Available kernels: "gaussian", "multiquadratic", "wendland_c2".
        Default is "gaussian".
    epsilon : float, optional
        Shape parameter for the RBF kernel. Default is 1.0.
    smoothing : float, optional
        Smoothing parameter for the kernel matrix. Default is 1e-12.
    neighbors : int, optional
        Number of nearest neighbors to use for local interpolation. Default is 200.
    min_neighbors : int or None, optional
        Minimum number of neighbors to use. Default is None.
    radius_factor : float, optional
        Factor to determine the local neighborhood radius. Default is 2.0.
    verbosity : int, optional
        Verbosity level. Default is `v_def.release`.

    Returns
    -------
    grad_trg : np.ndarray
        Gradient of the RBF interpolant at the target points, shape (Q, S, N).
    """
    kernel_func = _kernel_dict[kernel]
    kernel_grad_func = _kernel_grad_dict[kernel]

    tree = KDTree(coord_src)

    grad_trg = np.zeros(
        (
            coord_trg.shape[0],
            data_src.shape[1],
            coord_src.shape[1],
        ),
        dtype=data_src.dtype,
    )

    for cidx in progressbar(
        range(coord_trg.shape[0]), prefix="Compute RBF gradient: ", verbose=verbosity >= v_def.debug
    ):
        dists, nidx_max = tree.query(coord_trg[cidx, :], k=neighbors)

        if min_neighbors is None:
            nidx = nidx_max
        else:
            # Compute adaptive radius from first k_min neighbors
            k_eff = min(min_neighbors, len(dists))
            local_radius = radius_factor * np.mean(dists[:k_eff])

            mask = dists <= local_radius
            if np.sum(mask) < min_neighbors:
                # Ensure at least k_min neighbors
                mask[:min_neighbors] = True

            vprint(
                f"Target {cidx + 1}/{coord_trg.shape[0]}: Using {np.sum(mask)} neighbors",
                verbose=verbosity >= v_def.debug,
            )

            nidx = nidx_max[mask]

        # Build RBF system
        coeffs_local = _build_rbf_system(
            coord_src[nidx, :], data_src[nidx, ...], kernel_func, epsilon=epsilon, smoothing=smoothing
        )

        # Evaluate Jacobian at target coordinates
        grad_trg_local = _evaluate_rbf_gradient(
            coord_trg[cidx, :], coord_src[nidx, :], coeffs_local, kernel_grad_func, epsilon=epsilon
        )

        grad_trg[cidx, :, :] = grad_trg_local

    return grad_trg


def _process_rbf(
    flag_grad: bool,
    flag_local: bool,
    mesh_src: io.CFSMeshData,
    result_src: io.CFSResultContainer | Sequence[io.CFSResultArray],
    mesh_target: io.CFSMeshData,
    region_src_target: List[Dict],
    quantity_names: List[str] | Dict[str, str] | None = None,
    element_centroid_data_src=False,
    element_centroid_data_target=False,
    verbosity=v_def.release,
    *kwargs,
    kernel="gaussian",
    epsilon=1.0,
    smoothing=1e-12,
    neighbors=20,
    min_neighbors: Optional[int] = None,
    radius_factor: float = 2.0,
) -> io.CFSResultContainer:
    """
    Internal function to perform RBF-based interpolation or gradient computation between source and target meshes.

    Parameters
    ----------
    flag_grad : bool
        If True, compute gradients (Jacobian) instead of interpolated values.
    flag_local : bool
        If True, use local RBF interpolation; otherwise, use global RBF interpolation.
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
        Type of RBF kernel to use. Available kernels: "gaussian", "multiquadratic", "wendland_c2".
        Default is "gaussian".
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
        Interpolated values or gradients on the target mesh.
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

                # Check result type
                assert src_array_reg.ResType in _supported_res_types, (
                    f"Unsupported result type '{src_array_reg.ResType}' for RBF interpolation. "
                    f"Supported types: {_supported_res_types}"
                )
                # TODO add support for history data
                if src_array_reg.IsHistory:
                    raise NotImplementedError(
                        f"History data {src_array_reg.ResultInfo} is not supported for interpolation yet."
                    )
                src_array_list.append(src_array_reg)

            src_array = io.CFSResultArray(np.concatenate(src_array_list, axis=1))
            src_array.MetaData = src_array_reg.MetaData
            src_array = src_array.require_shape(verbose=verbosity >= v_def.debug)

            if flag_grad:
                trg_shape: Tuple = (
                    src_array.shape[0],
                    target_coord.shape[0],
                    src_array.shape[2],
                    target_coord.shape[1],
                )
                process_func = jacobian_rbf_local if flag_local else jacobian_rbf
            else:
                trg_shape = (src_array.shape[0], target_coord.shape[0], src_array.shape[2])
                process_func = interpolation_rbf_local if flag_local else interpolation_rbf

            process_args = {
                "coord_src": src_coord,
                "coord_trg": target_coord,
                # "data_src": src_array,
                "kernel": kernel,
                "epsilon": epsilon,
                "smoothing": smoothing,
            }
            if flag_local:
                process_args.update(
                    {
                        "neighbors": neighbors,
                        "min_neighbors": min_neighbors,
                        "radius_factor": radius_factor,
                        "verbosity": verbosity,
                    }
                )

            trg_array = np.full(
                trg_shape,
                fill_value=np.nan,
                dtype=src_array.dtype,
            )
            for i in progressbar(
                range(len(src_array.StepValues)), prefix="Perform interpolation:", verbose=verbosity >= v_def.release
            ):
                trg_array[i, ...] = process_func(data_src=src_array[i, ...], **process_args)  # type: ignore[operator]

            for target_idx, target_region_name in enumerate(region_src_target_dict["target"]):
                vprint(
                    f'Finalize interpolation ({quantity}): "{src_region_name}" -> "{target_region_name}"',
                    verbose=verbosity >= v_def.debug,
                )

                target_lb = target_region_counter[target_idx]
                target_ub = target_region_counter[target_idx + 1]

                if element_centroid_data_target:
                    target_type = cfs_types.cfs_result_type.ELEMENT
                else:
                    target_type = cfs_types.cfs_result_type.NODE

                if quantity_out is None:
                    quantity_out = src_array.Quantity
                if target_region_name is None:
                    target_region_name = src_array.Region
                if target_type is None:
                    target_type = src_array.ResType

                trg_reg_array = io.CFSResultArray(trg_array[:, target_lb:target_ub, ...], meta_data=src_array.MetaData)
                if flag_grad:
                    # Voigt notation for gradients
                    trg_reg_array = trg_reg_array.reshape(
                        trg_reg_array.shape[0], trg_reg_array.shape[1], trg_reg_array.shape[2] * trg_reg_array.shape[3]
                    )  # type: ignore[assignment]
                    # Dimension labels
                    trg_reg_array.DimNames = None  # type: ignore[assignment]
                trg_reg_array.Quantity = quantity_out
                trg_reg_array.Region = target_region_name
                trg_reg_array.ResType = target_type

                # perform sanity checks
                trg_reg_array.check_result_array()

                result_array_list.append(trg_reg_array)

    return io.CFSResultContainer(
        data=result_array_list,
        analysis_type=data_src.AnalysisType,
        multi_step_id=data_src.MultiStepID,
        verbosity=verbosity,
    )
