import numpy as np
from typing import Dict, List, Tuple
from pyCFS.util.lib_types import pyCFSparamVec, resultVec
from ._param_functions import (
    param_init_funcs,
    mat_switch_funcs,
    penalization_funcs,
    filter_funcs,
)

GRAD_TOKEN = "gradParam"
P = "p"
PSTAR = "pstar"
DPSTAR_DPBAR = "dpstar_dpbar"
PBAR = "pbar"
DPBAR_DP = "dpbar_dp"

DENSITY_FILTER = "density"
SENSITIVITY_FILTER = "sensitivity"


class Topt:
    def __init__(
        self,
        sim,
        geometry_type: str,
        design_domain: str,
        param_data: Dict[str, Dict[str, float]],
        param_to_grad_map: Dict[str, int] = {},
        param_init_strategy: str = "ones",
        void_material: str = "V_air",
        mat_switch_method: str = "modified-simp",
        penalization_method: str = "sigmoid",
        filter_method: str = "density",
        r_filter: float = 1e-2,
    ) -> None:
        self.sim = sim
        self.geometry_type = geometry_type
        self.design_domain = design_domain
        self.param_data = param_data
        self.void_material = void_material

        if param_init_strategy not in param_init_funcs.keys():
            raise KeyError(f"[pyCFS.topt] {param_init_strategy} not defined!")

        if mat_switch_method not in mat_switch_funcs.keys():
            raise KeyError(f"[pyCFS.topt] {mat_switch_method} not defined!")

        if penalization_method not in penalization_funcs.keys():
            raise KeyError(f"[pyCFS.topt] {penalization_method} not defined!")

        if filter_method not in filter_funcs.keys():
            raise KeyError(f"[pyCFS.topt] {filter_method} not defined!")

        self.param_init_strategy = param_init_strategy
        self.mat_switch_method = mat_switch_method
        self.penalization_method = penalization_method
        self.filter_method = filter_method
        self.r_filter = r_filter

        self.regions_element_parameters: Dict[str, Dict[str, pyCFSparamVec]] = {}
        self.n_design_elems = 0
        self.p_vector = np.array([])
        self.param_history: List[Dict[str, pyCFSparamVec]] = []
        self.iter = 0  # iteration number
        self.history_dump_path = "./data_dump/topt_history.npy"
        self.param_to_grad_map = param_to_grad_map

        # run initializers :
        self._init_functions()
        self._init_topt_setup()
        self._init_element_parameters()
        self._init_topt_globals()

    def _init_functions(self) -> None:
        self.param_init_fun = param_init_funcs[self.param_init_strategy]
        self._mat_switch_fun, self._mat_switch_fun_deriv = mat_switch_funcs[self.mat_switch_method]
        self.penalization_fun, self.penalization_fun_deriv, self.penalization_args = penalization_funcs[
            self.penalization_method
        ]
        self.density_filter_fun = filter_funcs[DENSITY_FILTER]

    def _init_topt_setup(self) -> None:
        self.sim.init_topopt_setup(geom_type=self.geometry_type, design_domain=self.design_domain)

    def _init_topt_globals(self) -> None:
        self.V0 = np.sum(self.sim.topopt_design_volumes)

    def _init_element_parameters(self) -> None:
        """Initializes a dictionary containing for each passed region in regions_data
        an array filled with the values given in param_data.

        """
        regions_data = self.sim._get_topt_regions(list(self.param_data.keys()))

        for region in regions_data:
            self.regions_element_parameters[region.Name] = {}
            n_elems = len(region.Elements)

            p_vector = self.param_init_fun((n_elems,))

            # initialize parameter state dict :
            param_state = self._init_param_state(p_vector)

            # perform density filtering step :
            self._do_density_filtering(param_state, region)

            # perform thresholding step :
            self._do_penalization(param_state)

            if region.Name not in self.param_data.keys():
                raise KeyError(f"[pyCFS.topt] {region.Name} not found in param_data!")

            for param, v_on in self.param_data[region.Name].items():
                # perform mat switch and update element parameters :
                self.regions_element_parameters[region.Name][param] = self._do_mat_switch(param, v_on, param_state)

            # update history state only if design domain
            # only tracking parameters from design domain
            if region == self.design_domain:
                # set number of elements in design domain
                self.n_design_elems = n_elems

                # update history state :
                self._update_hist_state(param_state)

        # write parameter file for cfs :
        self.sim.set_topopt_params(self.regions_element_parameters)

    @staticmethod
    def _construct_param_keys(param: str) -> Tuple[str, str]:
        key = f"{param}"
        deriv_key = f"d{param}_dpstar"
        return key, deriv_key

    @staticmethod
    def _init_param_state(p_vector: pyCFSparamVec) -> Dict[str, pyCFSparamVec]:
        return {P: p_vector}

    def _do_penalization(self, param_state: Dict[str, pyCFSparamVec]) -> None:
        # p to p* (thresholding step) :
        param_state[PSTAR] = self.penalization_fun(param_state[PBAR], **self.penalization_args)  # type: ignore[operator]
        param_state[DPSTAR_DPBAR] = self.penalization_fun_deriv(param_state[PBAR], **self.penalization_args)  # type: ignore[operator]

    def update_penalization_args(self, penalization_args: Dict[str, float]) -> None:
        self.penalization_args = penalization_args

    def _do_density_filtering(self, param_state: Dict[str, pyCFSparamVec], region: str) -> None:
        # p to pbar (density filtering step) :
        if region == self.design_domain:
            param_state[PBAR] = self.density_filter_fun(
                param_state[P], self.sim.topopt_design_centroids, r_filter=self.r_filter
            )
        else:
            param_state[PBAR] = param_state[P]

    def _do_mat_switch(self, param_name: str, param_val: float, param_state: Dict[str, pyCFSparamVec]) -> pyCFSparamVec:
        # get key names :
        param_key, param_deriv_key = self._construct_param_keys(param_name)
        v_off = self.param_data[self.void_material][param_name]

        # p* to material_param (mat switch function) :
        param_state[param_key] = self._mat_switch_fun(param_state[PSTAR], param_val, v_off)
        param_state[param_deriv_key] = self._mat_switch_fun_deriv(param_state[DPSTAR_DPBAR], param_val, v_off)

        return param_state[param_key]

    def _update_hist_state(self, state: Dict[str, pyCFSparamVec]) -> None:
        self.param_history.append(state)
        self.iter += 1

    def update_design_parameters(self, p_vector: pyCFSparamVec) -> None:

        # initialize parameter state dict :
        param_state = self._init_param_state(p_vector)

        # perform density filtering step :
        self._do_density_filtering(param_state, self.design_domain)

        # perform penalization step :
        self._do_penalization(param_state)

        for param, v_on in self.param_data[self.design_domain].items():

            # perform mat switch and update element parameters :
            self.regions_element_parameters[self.design_domain][param] = self._do_mat_switch(param, v_on, param_state)

        # update history state :
        self._update_hist_state(param_state)

        # write parameter file for cfs :
        self.sim.set_topopt_params(self.regions_element_parameters)

    def compute_volume_for(self, p: pyCFSparamVec) -> float:

        pbar = self.density_filter_fun(p, self.sim.topopt_design_centroids, r_filter=self.r_filter)
        pstar = self.penalization_fun(pbar, **self.penalization_args)  # type: ignore[operator]

        return np.sum(pstar * self.sim.topopt_design_volumes)

    def compute_volume(self) -> float:
        return np.sum(self.param_history[-1][PSTAR] * self.sim.topopt_design_volumes)

    def compute_volume_constraint(self, p=None) -> float:
        # V(xe) / V0 = xe * Ve / V0
        if p is None:
            return self.compute_volume() / self.V0
        else:
            return self.compute_volume_for(p) / self.V0

    def compute_volume_constraint_deriv(self) -> resultVec:

        # dV/dxe = Ve * dxstar/dxbar * dxbar/dx
        dV_dpbar = self.sim.topopt_design_volumes * self.param_history[-1][DPSTAR_DPBAR]

        dV_dp = self.density_filter_fun(dV_dpbar, self.sim.topopt_design_centroids, r_filter=self.r_filter)

        return dV_dp

    @staticmethod
    def filter_grad_keys(keys_list: List[str]) -> List[str]:
        grad_keys = []
        for key in keys_list:
            if GRAD_TOKEN in key:
                grad_keys.append(key)

        return grad_keys

    def _extract_mat_gradients(self, domain: str) -> resultVec:

        results = self.sim.results[0][1]
        grad_keys = Topt.filter_grad_keys(results.keys())
        n_elems = results[grad_keys[0]][domain].shape[1]

        gradients = np.zeros((n_elems, len(grad_keys)))

        for ind, grad_key in enumerate(grad_keys):
            # take only real parts of the computed gradients
            gradients[:, ind] = np.real(results[grad_key][domain][0, :, 0])

        return gradients

    def compute_gradient(self, normalize: bool = False) -> resultVec:
        grads = self._extract_mat_gradients(self.design_domain)

        for p_name, grad_ind in self.param_to_grad_map.items():
            _, grad_key = self._construct_param_keys(p_name)

            # dg_dmat * dmat_dpstar
            grads[:, grad_ind] *= self.param_history[-1][grad_key]  # type: ignore[operator]

        # apply chain rule for thresholding :
        dg_dpbar = grads.sum(axis=1) * self.param_history[-1][DPSTAR_DPBAR]
        # dg_dpbar = grads.sum(axis=1)

        #   dg_dpbar = (derivatives of the individual material parameters summed)
        # Apply chain rule of filter :
        # dg_dp = dg_dpbar * dpbar_dp -> is the same as applying the density filter
        # over the dg_dpbar derivatives
        dg_dp = self.density_filter_fun(dg_dpbar, self.sim.topopt_design_centroids, r_filter=self.r_filter)

        if normalize:
            dg_dp *= 1 / np.abs(dg_dp).max()
            dg_dp = np.clip(dg_dp * 1 / dg_dp.mean(), -1, 1)

        return dg_dp

    def dump_history(self) -> None:
        np.save(self.history_dump_path, self.param_history, allow_pickle=True)  # type: ignore[arg-type]
