"""
Module containing methods for fast fourier transforms (FFT) of possibly vector valued (field) data.
"""

from __future__ import annotations

from typing import Optional, Callable

from pyCFS.data.io import CFSResultArray

import numpy as np
import scipy.fft


def field_fft(
    data: CFSResultArray | np.ndarray,
    fft_func: Callable = scipy.fft.fft,
    axis: int = 0,
    window: Optional[np.ndarray] = None,
    norm: Optional[str] = None,
) -> np.ndarray:
    """
    Apply FFT to the field data along a specified axis.

    Parameters
    ----------
    data : CFSResultArray | np.ndarray
        A (n,m,d) CFSResultArray or a ND array representing
        the field data to be transformed.
    fft_func : Callable, optional
        The FFT function to use, by default scipy.fft.fft.
        This can be replaced with other FFT implementations if needed.
    axis : int, optional
        The axis along which to apply the FFT, by default 0 (first axis).
    window : Optional[np.ndarray], optional
        Window function to apply before the FFT, by default None.
        If provided, it should be a 1D array or an array with the same
        shape as `data`.
    norm : Optional[str], optional
        Normalization mode for the FFT, by default None.

    Returns
    -------
    np.ndarray
        The fourier transformed field data.


    Examples
    --------
    >>> from pyCFS.data.operators.field_fft import field_fft
    >>> data = np.random.rand(100, 20, 3)  # Example data
    >>> transformed_data = field_fft(data)

    """

    if not (isinstance(data, CFSResultArray) or isinstance(data, np.ndarray)):
        raise TypeError("Input data must be of type CFSResultArray or numpy ndarray.")

    if isinstance(data, np.ndarray) and data.ndim < 1:
        raise ValueError("Numpy input data must have at least one dimension.")

    if isinstance(data, CFSResultArray) and data.ndim != 3:
        raise ValueError("CFSResultArray input data must have exactly three dimensions (n, m, d).")

    if window is not None:
        if not isinstance(window, np.ndarray):
            raise TypeError("Window must be a numpy ndarray.")

        if window.ndim == 1:
            if window.size != data.shape[axis]:
                raise ValueError("Window is a 1D array, it has to have the same size as the specified axis of data.")
            reshape_dims = [1] * data.ndim
            reshape_dims[axis] = -1
            window = window.reshape(reshape_dims)
            data = data * window
        elif window.ndim == data.ndim:
            if window.shape != data.shape:
                raise ValueError("Window must be a 1D array or an array with the same shape as data.")
            data = data * window
        else:
            raise ValueError("Window must be a 1D array or an array with the same shape as data.")

    return fft_func(data, axis=axis, norm=norm)
