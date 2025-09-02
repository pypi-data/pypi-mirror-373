"""
Module containing methods for dynamic mode decomposition (DMD) of vector valued (field) data.
"""

from __future__ import annotations

import importlib.util

from typing import Optional, Callable

from pyCFS.data.io import CFSResultArray

import numpy as np

if importlib.util.find_spec("pydmd") is None:
    raise ModuleNotFoundError(
        "Missing dependency for submodule pyCFS.data.operators.dynamic_mode_decomposition. "
        "To install pyCFS with all required dependencies run 'pip install -U pyCFS[dmd]'."
    )

from pydmd import DMD


def dmd(
    data: CFSResultArray | np.ndarray,
    dmd_func: Callable = DMD,
    svd_rank: Optional[int] = -1,
    exact: bool = False,
    tikhonov_regularisation: Optional[float] = None,
    dt: float = 1.0,
    **kwargs,
) -> DMD:
    """
    Apply Dynamic Mode Decomposition (DMD) to the field data.

    Parameters
    ----------
    data : CFSResultArray or np.ndarray
        Input data representing the field data to be decomposed.
        The first dimension is expected to be time, and the remaining dimensions are spatial.
    dmd_func : Callable, optional
        The DMD function to use, by default pyDMD.DMD.
        lookup pyDMD documentation for other available DMD methods.
    svd_rank : Optional[int], optional
        Rank for SVD truncation, by default -1 (no truncation).
        When set to 0, it internally calculates optimal rank truncation.
    exact : bool, optional
        Whether to use exact DMD, by default False, which uses projected DMD.
    tikhonov_regularisation : Optional[float], optional
        Tikhonov regularisation parameter, by default None (no regularisation).
    dt : float, optional
        Time step between snapshots, by default 1.0.

    Returns
    -------
    pyDMD.DMD
        The DMD object containing the decomposition results.
        The object will have attributes such as `amplitudes`, `frequency`, `modes`, `eigs`,
        and `dynamics` that can be used for further analysis. For more details,
        refer to the pyDMD documentation.

    Examples
    --------
    >>> from pyCFS.data.operators.dynamic_mode_decomposition import dmd
    >>> data = np.random.rand(100, 20, 3)  # Example data
    >>> dmd_instance = dmd(data, svd_rank=10, exact=True)
    >>> modes = dmd_instance.modes  # Access the DMD modes
    >>> frequencies = dmd_instance.frequency  # Access the DMD frequencies
    >>> dynamics = dmd_instance.dynamics  # Access the DMD dynamics
    >>> amplitudes = dmd_instance.amplitudes  # Access the DMD amplitudes
    >>> eigs = dmd_instance.eigs  # Access the DMD eigenvalues

    """

    if not (isinstance(data, np.ndarray) or isinstance(data, CFSResultArray)):
        raise TypeError("Input data must be a numpy ndarray or a CFSResultArray.")

    if isinstance(data, np.ndarray) and data.ndim < 2:
        raise ValueError("Numpy array input data must have at least two dimensions (time and spatial dimensions).")

    if isinstance(data, CFSResultArray) and data.ndim != 3:
        raise ValueError("CFSResultArray input data must have exactly three dimensions (n,m,d).")

    if isinstance(data, CFSResultArray):
        data = np.transpose(data, (1, 2, 0))
    elif isinstance(data, np.ndarray) and data.ndim == 2:
        data = data.T
    elif isinstance(data, np.ndarray) and data.ndim == 3:
        data = np.transpose(data, (1, 2, 0))
    else:
        raise ValueError("Input data must be a 2D or 3D numpy array or a CFSResultArray.")

    dmd_instance = dmd_func(svd_rank=svd_rank, exact=exact, tikhonov_regularization=tikhonov_regularisation, **kwargs)
    dmd_instance.fit(data)

    return dmd_instance


def reshape_3d_dmd_modes(modes: np.ndarray, n_points: int, n_dim: int, r_trunc: int) -> np.ndarray:
    """
    Reshape the DMD modes to their original representation.

    Parameters
    ----------
    modes : np.ndarray
        The DMD modes to be reshaped. Expected shape is (n_points * n_dim, r_trunc).
        If the input data is vector valued, it will be reshaped to (n_points, n_dim, r_trunc).
    n_points : int
        The number of spatial points in the original data.
    n_dim : int
        The number of dimensions in the original data.
    r_trunc : int
        The rank truncation to apply to the DMD modes. If -1, no truncation is applied.

    Returns
    -------
    np.ndarray
        The reshaped DMD modes with shape (n_points, n_dim, r_trunc).

    Examples
    --------
    >>> data = np.random.rand(100, 20, 3)  # Example data
    >>> dmd_instance = dmd(data, svd_rank=10)
    >>> modes = dmd_instance.modes  # Get the DMD modes
    >>> reshaped_modes = reshape_3d_dmd_modes(modes, n_points=20, n_dim=3, r_trunc=10)
    >>> print(reshaped_modes.shape)  # Should print (20, 3, 10)

    """

    if n_dim == 1 or n_points == 1:
        raise ValueError("The original input data is not vector valued and does not have to be reshaped.")

    if r_trunc == -1:
        r_trunc = modes.shape[0]

    if modes.shape != (n_points * n_dim, r_trunc):
        raise ValueError(f"Modes shape {modes.shape} does not match expected shape {(n_points * n_dim, r_trunc)}.")

    modes = modes.reshape((n_points, n_dim, r_trunc))

    return modes
