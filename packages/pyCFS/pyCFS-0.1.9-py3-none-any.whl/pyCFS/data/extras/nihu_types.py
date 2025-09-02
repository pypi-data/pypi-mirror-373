"""
Module containing Enums extracted from NiHu source code (TODO code reference)
"""

from enum import IntEnum

import numpy as np

from pyCFS.data.io.cfs_types import cfs_element_type
from pyCFS.data.util import apply_dict_vectorized


# noinspection PyPep8Naming
class nihu_element_type(IntEnum):
    """
    Extracted from NiHu repo (TODO code reference)
    """

    UNDEF = 0
    ConstantPoint = 1
    LinearLine = 10212
    LinearTria = 10323
    LinearQuad = 10424
    QuadraticLine = 20312
    QuadraticTria = 20623
    QuadraticQuad = 20824
    QuadraticQuadMid = 20924
    LinearTetra = 10434
    LinearHexa = 10838


type_link_nihu_cfs = {
    nihu_element_type.UNDEF: cfs_element_type.UNDEF,
    nihu_element_type.ConstantPoint: cfs_element_type.POINT,
    nihu_element_type.LinearLine: cfs_element_type.LINE2,
    nihu_element_type.LinearTria: cfs_element_type.TRIA3,
    nihu_element_type.LinearQuad: cfs_element_type.QUAD4,
    nihu_element_type.QuadraticLine: cfs_element_type.LINE3,
    nihu_element_type.QuadraticTria: cfs_element_type.TRIA6,
    nihu_element_type.QuadraticQuad: cfs_element_type.QUAD8,
    nihu_element_type.QuadraticQuadMid: cfs_element_type.QUAD9,
    nihu_element_type.LinearTetra: cfs_element_type.TET4,
    nihu_element_type.LinearHexa: cfs_element_type.HEXA8,
}


# mapping nihu element types array to cfs element types array
def nihu_to_cfs_elem_type(nihu_elem_types: np.ndarray) -> np.ndarray:
    """
    Convert NiHu element types to CFS element types.

    Parameters
    ----------
    nihu_elem_types: np.ndarray
        Array of NiHu element types.

    Returns
    -------
    np.ndarray
        Array of CFS element types corresponding to the NiHu element types.

    """
    return apply_dict_vectorized(dictionary=type_link_nihu_cfs, data=nihu_elem_types)
