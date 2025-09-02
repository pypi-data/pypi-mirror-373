from enum import IntEnum

import numpy as np

from pyCFS.data.io.cfs_types import cfs_element_type
from pyCFS.data.util import apply_dict_vectorized


# noinspection PyPep8Naming
class cgns_element_type(IntEnum):
    """
    Extracted from cgnslib.h
    """

    NODE = 2
    BAR_2 = 3
    BAR_3 = 4
    TRI_3 = 5
    TRI_6 = 6
    QUAD_4 = 7
    QUAD_8 = 8
    QUAD_9 = 9
    TETRA_4 = 10
    TETRA_10 = 11
    PYRA_5 = 12
    PYRA_14 = 13
    PENTA_6 = 14
    PENTA_15 = 15
    PENTA_18 = 16
    HEXA_8 = 17
    HEXA_20 = 18
    HEXA_27 = 19
    MIXED = 20
    PYRA_13 = 21
    NGON_n = 22
    NFACE_n = 23
    BAR_4 = 24
    TRI_9 = 25
    TRI_10 = 26
    QUAD_12 = 27
    QUAD_16 = 28
    TETRA_16 = 29
    TETRA_20 = 30
    PYRA_21 = 31
    PYRA_29 = 32
    PYRA_30 = 33
    PENTA_24 = 34
    PENTA_38 = 35
    PENTA_40 = 36
    HEXA_32 = 37
    HEXA_56 = 38
    HEXA_64 = 39
    BAR_5 = 40
    TRI_12 = 41
    TRI_15 = 42
    QUAD_P4_16 = 43
    QUAD_25 = 44
    TETRA_22 = 45
    TETRA_34 = 46
    TETRA_35 = 47
    PYRA_P4_29 = 48
    PYRA_50 = 49
    PYRA_55 = 50
    PENTA_33 = 51
    PENTA_66 = 52
    PENTA_75 = 53
    HEXA_44 = 54
    HEXA_98 = 55
    HEXA_125 = 56


cgns_element_node_num = {
    cgns_element_type.NODE: 1,
    cgns_element_type.BAR_2: 2,
    cgns_element_type.BAR_3: 3,
    cgns_element_type.TRI_3: 3,
    cgns_element_type.TRI_6: 6,
    cgns_element_type.QUAD_4: 4,
    cgns_element_type.QUAD_8: 8,
    cgns_element_type.QUAD_9: 9,
    cgns_element_type.TETRA_4: 4,
    cgns_element_type.TETRA_10: 10,
    cgns_element_type.PYRA_5: 5,
    cgns_element_type.PYRA_14: 14,
    cgns_element_type.PENTA_6: 6,
    cgns_element_type.PENTA_15: 15,
    cgns_element_type.PENTA_18: 18,
    cgns_element_type.HEXA_8: 8,
    cgns_element_type.HEXA_20: 20,
    cgns_element_type.HEXA_27: 27,
    # cgns_element_type.MIXED : -1,
    cgns_element_type.PYRA_13: 13,
    # cgns_element_type.NGON_n : -1,
    # cgns_element_type.NFACE_n : -1,
    cgns_element_type.BAR_4: 4,
    cgns_element_type.TRI_9: 9,
    cgns_element_type.TRI_10: 10,
    cgns_element_type.QUAD_12: 12,
    cgns_element_type.QUAD_16: 16,
    cgns_element_type.TETRA_16: 16,
    cgns_element_type.TETRA_20: 20,
    cgns_element_type.PYRA_21: 21,
    cgns_element_type.PYRA_29: 29,
    cgns_element_type.PYRA_30: 30,
    cgns_element_type.PENTA_24: 24,
    cgns_element_type.PENTA_38: 38,
    cgns_element_type.PENTA_40: 40,
    cgns_element_type.HEXA_32: 32,
    cgns_element_type.HEXA_56: 56,
    cgns_element_type.HEXA_64: 64,
    cgns_element_type.BAR_5: 5,
    cgns_element_type.TRI_12: 12,
    cgns_element_type.TRI_15: 15,
    # cgns_element_type.QUAD_P4_16 : 16,
    cgns_element_type.QUAD_25: 25,
    cgns_element_type.TETRA_22: 22,
    cgns_element_type.TETRA_34: 34,
    cgns_element_type.TETRA_35: 35,
    # cgns_element_type.PYRA_P4_29 : 29,
    cgns_element_type.PYRA_50: 50,
    cgns_element_type.PYRA_55: 55,
    cgns_element_type.PENTA_33: 33,
    cgns_element_type.PENTA_66: 66,
    cgns_element_type.PENTA_75: 75,
    cgns_element_type.HEXA_44: 44,
    cgns_element_type.HEXA_98: 98,
    cgns_element_type.HEXA_125: 125,
}

type_link_cgns_cfs = {
    cgns_element_type.NODE: cfs_element_type.POINT,
    cgns_element_type.BAR_2: cfs_element_type.LINE2,
    cgns_element_type.BAR_3: cfs_element_type.LINE3,
    cgns_element_type.TRI_3: cfs_element_type.TRIA3,
    cgns_element_type.TRI_6: cfs_element_type.TRIA6,
    cgns_element_type.QUAD_4: cfs_element_type.QUAD4,
    cgns_element_type.QUAD_8: cfs_element_type.QUAD8,
    cgns_element_type.QUAD_9: cfs_element_type.QUAD9,
    cgns_element_type.TETRA_4: cfs_element_type.TET4,
    cgns_element_type.TETRA_10: cfs_element_type.TET10,
    cgns_element_type.PYRA_5: cfs_element_type.PYRA5,
    cgns_element_type.PYRA_14: cfs_element_type.PYRA14,
    cgns_element_type.PENTA_6: cfs_element_type.WEDGE6,
    cgns_element_type.PENTA_15: cfs_element_type.WEDGE15,
    cgns_element_type.PENTA_18: cfs_element_type.WEDGE18,
    cgns_element_type.HEXA_8: cfs_element_type.HEXA8,
    cgns_element_type.HEXA_20: cfs_element_type.HEXA20,
    cgns_element_type.HEXA_27: cfs_element_type.HEXA27,
    # cgns_element_type.MIXED : cfs_element_type.MIXED,
    cgns_element_type.PYRA_13: cfs_element_type.PYRA13,
    # cgns_element_type.NGON_n : cfs_element_type.NGONn,
    # cgns_element_type.NFACE_n : cfs_element_type.NFACEn,
    # cgns_element_type.BAR_4: cfs_element_type.LINE4,
    # cgns_element_type.TRI_9: cfs_element_type.TRIA9,
    # cgns_element_type.TRI_10: cfs_element_type.TRIA10,
    # cgns_element_type.QUAD_12: cfs_element_type.QUAD12,
    # cgns_element_type.QUAD_16: cfs_element_type.QUAD16,
    # cgns_element_type.TETRA_16: cfs_element_type.TET16,
    # cgns_element_type.TETRA_20: cfs_element_type.TET20,
    # cgns_element_type.PYRA_21: cfs_element_type.PYRA21,
    # cgns_element_type.PYRA_29: cfs_element_type.PYRA29,
    # cgns_element_type.PYRA_30: cfs_element_type.PYRA30,
    # cgns_element_type.PENTA_24: cfs_element_type.WEDGE24,
    # cgns_element_type.PENTA_38: cfs_element_type.WEDGE38,
    # cgns_element_type.PENTA_40: cfs_element_type.WEDGE40,
    # cgns_element_type.HEXA_32: cfs_element_type.HEXA32,
    # cgns_element_type.HEXA_56: cfs_element_type.HEXA56,
    # cgns_element_type.HEXA_64: cfs_element_type.HEXA64,
    # cgns_element_type.BAR_5: cfs_element_type.LINE5,
    # cgns_element_type.TRI_12: cfs_element_type.TRIA12,
    # cgns_element_type.TRI_15: cfs_element_type.TRIA15,
    # cgns_element_type.QUAD_P4_16 : cfs_element_type.QUAD_P4_16,
    # cgns_element_type.QUAD_25: cfs_element_type.QUAD25,
    # cgns_element_type.TETRA_22: cfs_element_type.TET22,
    # cgns_element_type.TETRA_34: cfs_element_type.TET34,
    # cgns_element_type.TETRA_35: cfs_element_type.TET35,
    # cgns_element_type.PYRA_P4_29 : cfs_element_type.PYRA_P4_29,
    # cgns_element_type.PYRA_50: cfs_element_type.PYRA50,
    # cgns_element_type.PYRA_55: cfs_element_type.PYRA55,
    # cgns_element_type.PENTA_33: cfs_element_type.WEDGE33,
    # cgns_element_type.PENTA_66: cfs_element_type.WEDGE66,
    # cgns_element_type.PENTA_75: cfs_element_type.WEDGE75,
    # cgns_element_type.HEXA_44: cfs_element_type.HEXA44,
    # cgns_element_type.HEXA_98: cfs_element_type.HEXA98,
    # cgns_element_type.HEXA_125: cfs_element_type.HEXA125,
}


# mapping cgns element types array to cfs element types array
def cgns_to_cfs_elem_type(cgns_elem_types: np.ndarray) -> np.ndarray:
    """
    Maps CGNS element types to CFS element types.

    Parameters
    ----------
    cgns_elem_types: np.ndarray
        An array of CGNS element types.

    Returns
    -------
    np.ndarray
        An array of CFS element types corresponding to the input CGNS element types.

    """
    return apply_dict_vectorized(dictionary=type_link_cgns_cfs, data=cgns_elem_types, val_no_key=cfs_element_type.UNDEF)
