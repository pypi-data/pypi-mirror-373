import numpy as np
from numba import jit
from pyCFS.util.lib_types import pyCFSparamVec

# p* to mat functions (material switching) :


def switch_fun_onoff(xp: pyCFSparamVec, v_on: float, v_off: float, p: float = 5.0) -> pyCFSparamVec:
    return xp * (v_on - v_off) + v_off  # type: ignore[operator]


def switch_fun_onoff_deriv(xp_deriv: pyCFSparamVec, v_on: float, v_off: float, p: float = 5.0) -> pyCFSparamVec:
    return xp_deriv * (v_on - v_off)  # type: ignore[operator]


# p to p* functions (thresholding) :
def bypass(x: pyCFSparamVec) -> pyCFSparamVec:
    return x


def bypass_deriv(x: pyCFSparamVec) -> pyCFSparamVec:
    return np.ones_like(x)


simp_init_args = {"p": 5.0}


def simp_penalization(x, p: float = 5.0):
    return x**p


def simp_penalization_deriv(x, p: float = 5.0):
    return p * x ** (p - 1)


sigmoid_init_args = {"a": 50, "b": 0.5}


def sigmoid_penalization(x: pyCFSparamVec, a: float = 100, b: float = 0.5) -> pyCFSparamVec:
    return 1 / (1 + np.exp(-a * (x - b)))  # type: ignore[operator]


def sigmoid_penalization_deriv(x: pyCFSparamVec, a: float = 100, b: float = 0.5) -> pyCFSparamVec:
    return a * np.exp(-a * (x - b)) * 1 / (1 + np.exp(-a * (x - b))) ** 2  # type: ignore[operator]


# Filter functions :


@jit(nopython=True)
def filter_weights(d, r):
    return np.maximum(0.0, r - d)


@jit(nopython=True)
def compute_l2_distance(x, c):
    return np.sqrt(np.sum((x - c) ** 2, axis=1))


@jit(nopython=True)
def filter_densities(x, centroids, r_filter=1e-2):
    x_bar = np.zeros_like(x)

    for i_elem in range(len(x)):
        # Compute distances to current element
        distances = compute_l2_distance(centroids, centroids[i_elem, :])
        # Construct set Ne : Get elements inside filter radius rmin
        elems_inside = distances <= r_filter
        # Compute filter weights for current element
        w_filter = filter_weights(distances[elems_inside], r_filter)

        x_bar[i_elem] = 1 / np.sum(w_filter) * np.sum(w_filter * x[elems_inside])

    return x_bar


@jit(nopython=True)
def filter_densities_deriv_chain(dg_dpbar, centroids, r_filter=1e-2):

    x_bar_deriv = np.zeros_like(dg_dpbar)

    for i_elem in range(len(dg_dpbar)):
        # Compute distances to current element
        distances = compute_l2_distance(centroids, centroids[i_elem, :])
        # Construct set Ne : Get elements inside filter radius rmin
        elems_inside = distances <= r_filter
        # Compute filter weights for current element
        w_filter = filter_weights(distances[elems_inside], r_filter)

        x_bar_deriv[i_elem] = 1 / np.sum(w_filter) * np.sum(w_filter * dg_dpbar[elems_inside])

    return x_bar_deriv


param_init_funcs = {
    "ones": np.ones,
    "zeros": np.zeros,
}

mat_switch_funcs = {
    "modified-simp": (switch_fun_onoff, switch_fun_onoff_deriv),
}

penalization_funcs = {
    "bypass": (bypass, bypass_deriv, {}),
    "simp": (simp_penalization, simp_penalization_deriv, simp_init_args),
    "sigmoid": (sigmoid_penalization, sigmoid_penalization_deriv, sigmoid_init_args),
}

filter_funcs = {
    "density": filter_densities,
}
