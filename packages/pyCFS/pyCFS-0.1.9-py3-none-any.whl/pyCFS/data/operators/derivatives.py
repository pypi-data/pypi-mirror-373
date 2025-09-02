from typing import Sequence, List, Dict, Optional

from pyCFS.data import io, v_def
from pyCFS.data.operators import _rbf_interpolation


def gradient_rbf(
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
    Interpolate the gradient (Jacobian) of field values from a source mesh to a target mesh using global RBF interpolation.

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

    Returns
    -------
    results : io.CFSResultContainer
        Interpolated gradients on the target mesh.
    """
    return _rbf_interpolation._process_rbf(
        flag_grad=True,
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


def gradient_rbf_local(
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
    Interpolate the gradient (Jacobian) of field values from a source mesh to a target mesh using local RBF interpolation.

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
        Interpolated gradients on the target mesh.
    """
    return _rbf_interpolation._process_rbf(
        flag_grad=True,
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
