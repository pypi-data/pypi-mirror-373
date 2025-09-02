"""
Modal analysis operators for mode shape comparison and evaluation.

This module provides functions for modal analysis, including:
- Modal Assurance Criterion (MAC)
- Complex Modal Assurance Criterion (MACX)
- Modal Scale Factor (MSF)
- Modal Complexity Factor (MCF)

These functions operate on mode shape matrices, supporting both `CFSResultArray` and `numpy.ndarray` types.

Functions
---------
modal_assurance_criterion
    Compute the Modal Assurance Criterion (MAC) between two mode shape matrices.
modal_assurance_criterion_complex
    Compute the Complex Modal Assurance Criterion (MACX) for complex mode shapes.
modal_scale_factor
    Compute the Modal Scale Factor (MSF) between two mode shape matrices.
modal_complexity_factor
    Compute the Modal Complexity Factor (MCF) for a mode shape matrix.
"""

import numpy as np
from typing import Optional
from pyCFS.data.io import CFSResultArray


def modal_assurance_criterion(
    phi_X: CFSResultArray | np.ndarray, phi_A: Optional[CFSResultArray | np.ndarray] = None
) -> np.ndarray:
    """Modal Assurance Criterion.

    Parameters
    ----------
    phi_X : CFSResultArray or np.ndarray
        Mode shape matrix X, shape (`n_modes`, `n_locations`).
    phi_A : CFSResultArray, or np.ndarray, optional
        Mode shape matrix A, shape (`n_modes`, `n_locations`).

    Returns
    -------
    np.ndarray
        MAC matrix.

    Notes
    -----
    The number of locations (axis 1) must be the same for `phi_X` and `phi_A`. The number of modes (axis 0) is arbitrary.

    References
    ----------
    [1] Maia, N. M. M., and J. M. M. Silva. "Modal analysis identification techniques."
    Philosophical Transactions of the Royal Society of London.
    Series A: Mathematical, Physical and Engineering Sciences 359.1778 (2001): 29-40.

    Examples
    --------
    >>> import numpy as np
    >>> from pyCFS.data.operators.modal_analysis import modal_assurance_criterion
    >>> phi_X = np.array([[1., 0.], [0., 1.], [1., 1.]])
    >>> phi_A = np.array([[0., 1.], [1., 0.], [0.5, 0.5]])
    >>> mac = modal_assurance_criterion(phi_X, phi_A)
    >>> mac_auto = modal_assurance_criterion(phi_X)
    """

    if phi_A is None:
        # Compute Auto MAC
        phi_A = phi_X

    if phi_X.shape[1] != phi_A.shape[1]:
        raise ValueError(
            f"Mode shapes must have the same number of locations (phi_X: {phi_X.shape[1]}, phi_A: {phi_A.shape[1]})"
        )

    if phi_X.ndim < 2 or phi_A.ndim < 2:
        raise ValueError(
            f"Mode shapes must be defined by (n_modes, n_locations). (phi_X:{phi_X.shape} and phi_A:{phi_A.shape})"
        )
    if phi_X.ndim > 2:
        if phi_X.shape[2] != 1:
            raise ValueError(f"Mode shapes must have 1 dimension only (phi_X: {phi_X.shape[2]})")
        phi_X = phi_X.squeeze(axis=2)
    if phi_A.ndim > 2:
        if phi_A.shape[2] != 1:
            raise ValueError(f"Mode shapes must have 1 dimension only (phi_A: {phi_A.shape[2]})")
        phi_A = phi_A.squeeze(axis=2)

    return np.abs(np.conj(phi_X) @ phi_A.T) ** 2 / np.real(
        np.outer(np.sum(np.abs(phi_X) ** 2, axis=1), np.sum(np.abs(phi_A) ** 2, axis=1))
    )


def modal_assurance_criterion_complex(
    phi_1: CFSResultArray | np.ndarray, phi_2: Optional[CFSResultArray | np.ndarray] = None
) -> np.ndarray:
    """
    Complex Modal Assurance Criterion (MACX).

    Parameters
    ----------
    phi_1 : CFSResultArray
        First mode shape matrix, shape (`n_modes`, `n_locations`).
    phi_2 : CFSResultArray, optional
        Second mode shape matrix, shape (`n_modes`, `n_locations`). If None, computes Auto MACX.

    Returns
    -------
    np.ndarray
        MACX matrix.

    Notes
    -----
    The number of locations (axis 1) must be the same for `phi_1` and `phi_2`. The number of modes (axis 0) is arbitrary.

    References
    ----------
    [1] Vacher, P., Jacquier, B. and Bucharles, A., 2010, September. Extensions of the MAC criterion to complex modes.
    In Proceedings of the international conference on noise and vibration engineering (pp. 2713-2726). ISMA Leuven, Belgium.
    """
    # TODO Implement tests

    if phi_2 is None:
        # Compute Auto MAC
        phi_2 = phi_1

    if phi_1.shape[1] != phi_2.shape[1]:
        raise ValueError(
            f"Mode shapes must have the same number of locations (phi_X: {phi_1.shape[1]}, phi_A: {phi_2.shape[1]})"
        )

    if phi_1.ndim < 2 or phi_2.ndim < 2:
        raise ValueError(
            f"Mode shapes must be defined by (n_modes, n_locations). (phi_X:{phi_1.shape} and phi_A:{phi_2.shape})"
        )
    if phi_1.ndim > 2:
        if phi_1.shape[2] != 1:
            raise ValueError(f"Mode shapes must have 1 dimension only (phi_X: {phi_1.shape[2]})")
        phi_1 = phi_1.squeeze(axis=2)
    if phi_2.ndim > 2:
        if phi_2.shape[2] != 1:
            raise ValueError(f"Mode shapes must have 1 dimension only (phi_A: {phi_2.shape[2]})")
        phi_2 = phi_2.squeeze(axis=2)

    num = (np.abs(np.conj(phi_1) @ phi_2.T) + np.abs(phi_1 @ phi_2.T)) ** 2

    den = np.real(
        (np.sum(np.abs(phi_1) ** 2, axis=1) + np.abs(np.sum(phi_1 * phi_1, axis=1)))[:, None]
        * (np.sum(np.abs(phi_2) ** 2, axis=1) + np.abs(np.sum(phi_2 * phi_2, axis=1)))[None, :]
    )

    return num / den


def modal_scale_factor(phi_X: CFSResultArray | np.ndarray, phi_A: CFSResultArray | np.ndarray) -> np.ndarray:
    """
    Modal Scale Factor.

    If ``phi_X`` and ``phi_A`` are matrices, multiple MSF values are returned.

    The MSF scales ``phi_X`` to ``phi_A`` when multiplying: ``msf * phi_X``.
    Also takes care of 180 deg phase difference.

    Parameters
    ----------
    phi_X : CFSResultArray or np.ndarray
        Mode shape matrix X, shape (`n_modes`, `n_locations`).
    phi_A : CFSResultArray or np.ndarray
        Mode shape matrix A, shape (`n_modes`, `n_locations`).

    Returns
    -------
    np.ndarray
        MSF values.

    Raises
    ------
    ValueError
        If input arrays do not have at least 2 dimensions or have more than 1 dimension in axis 2.
    Exception
        If input arrays do not have the same shape after swapping axes.
    """
    # TODO Implement tests
    # TODO Vectorize the implementation

    if phi_X.ndim < 2 or phi_A.ndim < 2:
        raise ValueError(
            f"Mode shapes must be defined by (n_modes, n_dofs). (phi_X:{phi_X.shape} and phi_A:{phi_A.shape})"
        )
    if phi_X.ndim > 2:
        if phi_X.shape[2] != 1:
            raise ValueError(f"Mode shapes must have 1 dimension only (phi_X: {phi_X.shape[2]})")
        phi_X = phi_X.squeeze(axis=2)
    if phi_A.ndim > 2:
        if phi_A.shape[2] != 1:
            raise ValueError(f"Mode shapes must have 1 dimension only (phi_X: {phi_A.shape[2]})")
        phi_A = phi_X.squeeze(axis=2)

    phi_X = phi_X.swapaxes(0, 1)
    phi_A = phi_A.swapaxes(0, 1)

    if phi_X.shape[0] != phi_A.shape[0] or phi_X.shape[1] != phi_A.shape[1]:
        raise Exception(f"`phi_X` and `phi_A` must have the same shape: {phi_X.shape} and {phi_A.shape}")

    # Implementation based on ``sdypy.EMA.tools.MSF(phi_X, phi_A)``
    n_modes = phi_X.shape[1]
    msf = []
    for i in range(n_modes):
        _msf = (phi_A[:, i].T @ phi_X[:, i]) / (phi_X[:, i].T @ phi_X[:, i])

        msf.append(_msf)

    return np.array(msf).real


def modal_complexity_factor(phi: CFSResultArray | np.ndarray) -> np.ndarray:
    """
    Modal complexity factor.

    The MCF ranges from 0 to 1. It returns 0 for real modes and 1 for complex modes.
    When ``dtype`` of ``phi`` is ``complex``, the modes can still be real if the angles
    of all components are the same.

    Additional information on MCF:
    http://www.svibs.com/resources/ARTeMIS_Modal_Help/Generic%20Complexity%20Plot.html

    Parameters
    ----------
    phi : CFSResultArray or np.ndarray
        Complex mode shape matrix, shape (`n_modes`, `n_locations`).

    Returns
    -------
    np.ndarray
        MCF (a value between 0 and 1).

    Raises
    ------
    ValueError
        If input array does not have at least 2 dimensions or has more than 1 dimension in axis 2.
    """
    # TODO Implement tests
    # TODO Vectorize the implementation

    if phi.ndim < 2:
        raise ValueError(f"Mode shapes must be defined by (n_modes, n_dofs). (phi:{phi.shape}")
    if phi.ndim > 2:
        if phi.shape[2] != 1:
            raise ValueError(f"Mode shapes must have 1 dimension only (phi_X: {phi.shape[2]})")
        phi = phi.squeeze(axis=2)

    phi = phi.swapaxes(0, 1)

    # Implementation based on ``sdypy.EMA.tools.MCF(phi)``
    n_modes = phi.shape[1]
    mcf = []
    for i in range(n_modes):
        S_xx = np.dot(phi[:, i].real, phi[:, i].real)
        S_yy = np.dot(phi[:, i].imag, phi[:, i].imag)
        S_xy = np.dot(phi[:, i].real, phi[:, i].imag)

        _mcf = 1 - ((S_xx - S_yy) ** 2 + 4 * S_xy**2) / (S_xx + S_yy) ** 2

        mcf.append(_mcf)
    return np.array(mcf)
