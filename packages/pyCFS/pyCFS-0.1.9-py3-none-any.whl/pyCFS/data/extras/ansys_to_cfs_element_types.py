import importlib.util
import numpy as np

from pyCFS.data.util import apply_dict_vectorized

if importlib.util.find_spec("ansys") is None:
    raise ModuleNotFoundError(
        "Missing dependency for submodule pyCFS.data.extras.ansys_to_cfs_element_types . "
        "To install pyCFS with all required dependencies run 'pip install -U pyCFS[data]'"
    )

from ansys.dpf import core as dpf
from pyCFS.data.io.cfs_types import cfs_element_type

type_link_ansys_cfs = {
    dpf.element_types.Tet10.value: cfs_element_type.TET10,
    dpf.element_types.Hex20.value: cfs_element_type.HEXA20,
    dpf.element_types.Wedge15.value: cfs_element_type.WEDGE15,
    dpf.element_types.Pyramid13.value: cfs_element_type.PYRA13,
    dpf.element_types.Tri6.value: cfs_element_type.TRIA6,
    dpf.element_types.Quad8.value: cfs_element_type.QUAD8,
    dpf.element_types.Tet4.value: cfs_element_type.TET4,
    dpf.element_types.Hex8.value: cfs_element_type.HEXA8,
    dpf.element_types.Wedge6.value: cfs_element_type.WEDGE6,
    dpf.element_types.Pyramid5.value: cfs_element_type.PYRA5,
    dpf.element_types.Tri3.value: cfs_element_type.TRIA3,
    dpf.element_types.Quad4.value: cfs_element_type.QUAD4,
    dpf.element_types.Line2.value: cfs_element_type.LINE2,
    dpf.element_types.Point1.value: cfs_element_type.POINT,
}


# mapping ansys dpf element types array to cfs element types array
def dpf_to_cfs_elem_type(elem_types: np.ndarray):
    return apply_dict_vectorized(dictionary=type_link_ansys_cfs, data=elem_types, val_no_key=cfs_element_type.UNDEF)
