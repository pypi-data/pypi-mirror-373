"""
Module containing Enums extracted from vtk source code (https://vtk.org/doc/nightly/html/vtkCellType_8h_source.html)
"""

from enum import IntEnum

import numpy as np

from pyCFS.data.io.cfs_types import cfs_element_type
from pyCFS.data.util import apply_dict_vectorized


class vtk_element_type(IntEnum):
    # Linear cells
    VTK_EMPTY_CELL = (0,)
    VTK_VERTEX = (1,)
    VTK_POLY_VERTEX = (2,)
    VTK_LINE = (3,)
    VTK_POLY_LINE = (4,)
    VTK_TRIANGLE = (5,)
    VTK_TRIANGLE_STRIP = (6,)
    VTK_POLYGON = (7,)
    VTK_PIXEL = (8,)
    VTK_QUAD = (9,)
    VTK_TETRA = (10,)
    VTK_VOXEL = (11,)
    VTK_HEXAHEDRON = (12,)
    VTK_WEDGE = (13,)
    VTK_PYRAMID = (14,)
    VTK_PENTAGONAL_PRISM = (15,)
    VTK_HEXAGONAL_PRISM = (16,)

    # Quadratic, isoparametric cells
    VTK_QUADRATIC_EDGE = (21,)
    VTK_QUADRATIC_TRIANGLE = (22,)
    VTK_QUADRATIC_QUAD = (23,)
    VTK_QUADRATIC_POLYGON = (36,)
    VTK_QUADRATIC_TETRA = (24,)
    VTK_QUADRATIC_HEXAHEDRON = (25,)
    VTK_QUADRATIC_WEDGE = (26,)
    VTK_QUADRATIC_PYRAMID = (27,)
    VTK_BIQUADRATIC_QUAD = (28,)
    VTK_TRIQUADRATIC_HEXAHEDRON = (29,)
    VTK_TRIQUADRATIC_PYRAMID = (37,)
    VTK_QUADRATIC_LINEAR_QUAD = (30,)
    VTK_QUADRATIC_LINEAR_WEDGE = (31,)
    VTK_BIQUADRATIC_QUADRATIC_WEDGE = (32,)
    VTK_BIQUADRATIC_QUADRATIC_HEXAHEDRON = (33,)
    VTK_BIQUADRATIC_TRIANGLE = (34,)

    # Cubic, isoparametric cell
    VTK_CUBIC_LINE = (35,)

    # Special class of cells formed by convex group of points
    VTK_CONVEX_POINT_SET = (41,)

    # Polyhedron cell(consisting of polygonal faces)
    VTK_POLYHEDRON = (42,)

    # Higher order cells in parametric form
    VTK_PARAMETRIC_CURVE = (51,)
    VTK_PARAMETRIC_SURFACE = (52,)
    VTK_PARAMETRIC_TRI_SURFACE = (53,)
    VTK_PARAMETRIC_QUAD_SURFACE = (54,)
    VTK_PARAMETRIC_TETRA_REGION = (55,)
    VTK_PARAMETRIC_HEX_REGION = (56,)

    # Higher order cells
    VTK_HIGHER_ORDER_EDGE = (60,)
    VTK_HIGHER_ORDER_TRIANGLE = (61,)
    VTK_HIGHER_ORDER_QUAD = (62,)
    VTK_HIGHER_ORDER_POLYGON = (63,)
    VTK_HIGHER_ORDER_TETRAHEDRON = (64,)
    VTK_HIGHER_ORDER_WEDGE = (65,)
    VTK_HIGHER_ORDER_PYRAMID = (66,)
    VTK_HIGHER_ORDER_HEXAHEDRON = (67,)

    # Arbitrary order Lagrange elements(formulated separated from generic higher order cells)
    VTK_LAGRANGE_CURVE = (68,)
    VTK_LAGRANGE_TRIANGLE = (69,)
    VTK_LAGRANGE_QUADRILATERAL = (70,)
    VTK_LAGRANGE_TETRAHEDRON = (71,)
    VTK_LAGRANGE_HEXAHEDRON = (72,)
    VTK_LAGRANGE_WEDGE = (73,)
    VTK_LAGRANGE_PYRAMID = (74,)

    # Arbitrary order Bezier elements(formulated separated from generic higher order cells)
    VTK_BEZIER_CURVE = (75,)
    VTK_BEZIER_TRIANGLE = (76,)
    VTK_BEZIER_QUADRILATERAL = (77,)
    VTK_BEZIER_TETRAHEDRON = (78,)
    VTK_BEZIER_HEXAHEDRON = (79,)
    VTK_BEZIER_WEDGE = (80,)
    VTK_BEZIER_PYRAMID = 81

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


# define mapping between vtk and cfs element types
type_link = {
    # Linear cells
    vtk_element_type.VTK_EMPTY_CELL: cfs_element_type.UNDEF,
    vtk_element_type.VTK_VERTEX: cfs_element_type.POINT,
    vtk_element_type.VTK_POLY_VERTEX: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LINE: cfs_element_type.LINE2,
    vtk_element_type.VTK_POLY_LINE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_TRIANGLE: cfs_element_type.TRIA3,
    vtk_element_type.VTK_TRIANGLE_STRIP: cfs_element_type.UNDEF,
    vtk_element_type.VTK_POLYGON: cfs_element_type.POLYGON,
    vtk_element_type.VTK_PIXEL: cfs_element_type.UNDEF,
    vtk_element_type.VTK_QUAD: cfs_element_type.QUAD4,
    vtk_element_type.VTK_TETRA: cfs_element_type.TET4,
    vtk_element_type.VTK_VOXEL: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HEXAHEDRON: cfs_element_type.HEXA8,
    vtk_element_type.VTK_WEDGE: cfs_element_type.WEDGE6,
    vtk_element_type.VTK_PYRAMID: cfs_element_type.PYRA5,
    vtk_element_type.VTK_PENTAGONAL_PRISM: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HEXAGONAL_PRISM: cfs_element_type.UNDEF,
    # Quadratic, isoparametric cells
    vtk_element_type.VTK_QUADRATIC_EDGE: cfs_element_type.LINE3,
    vtk_element_type.VTK_QUADRATIC_TRIANGLE: cfs_element_type.TRIA6,
    vtk_element_type.VTK_QUADRATIC_QUAD: cfs_element_type.QUAD8,
    vtk_element_type.VTK_QUADRATIC_POLYGON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_QUADRATIC_TETRA: cfs_element_type.TET10,
    vtk_element_type.VTK_QUADRATIC_HEXAHEDRON: cfs_element_type.HEXA20,
    vtk_element_type.VTK_QUADRATIC_WEDGE: cfs_element_type.WEDGE15,
    vtk_element_type.VTK_QUADRATIC_PYRAMID: cfs_element_type.PYRA13,
    vtk_element_type.VTK_BIQUADRATIC_QUAD: cfs_element_type.QUAD9,
    vtk_element_type.VTK_TRIQUADRATIC_HEXAHEDRON: cfs_element_type.HEXA27,
    vtk_element_type.VTK_TRIQUADRATIC_PYRAMID: cfs_element_type.UNDEF,
    vtk_element_type.VTK_QUADRATIC_LINEAR_QUAD: cfs_element_type.UNDEF,
    vtk_element_type.VTK_QUADRATIC_LINEAR_WEDGE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BIQUADRATIC_QUADRATIC_WEDGE: cfs_element_type.WEDGE18,
    vtk_element_type.VTK_BIQUADRATIC_QUADRATIC_HEXAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BIQUADRATIC_TRIANGLE: cfs_element_type.UNDEF,
    # Cubic, isoparametric cell
    vtk_element_type.VTK_CUBIC_LINE: cfs_element_type.UNDEF,
    # Special class of cells formed by convex group of points
    vtk_element_type.VTK_CONVEX_POINT_SET: cfs_element_type.UNDEF,
    # Polyhedron cell(consisting of polygonal faces)
    vtk_element_type.VTK_POLYHEDRON: cfs_element_type.POLYHEDRON,
    # Higher order cells in parametric form
    vtk_element_type.VTK_PARAMETRIC_CURVE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_PARAMETRIC_SURFACE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_PARAMETRIC_TRI_SURFACE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_PARAMETRIC_QUAD_SURFACE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_PARAMETRIC_TETRA_REGION: cfs_element_type.UNDEF,
    vtk_element_type.VTK_PARAMETRIC_HEX_REGION: cfs_element_type.UNDEF,
    # Higher order cells
    vtk_element_type.VTK_HIGHER_ORDER_EDGE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_TRIANGLE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_QUAD: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_POLYGON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_TETRAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_WEDGE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_PYRAMID: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_HEXAHEDRON: cfs_element_type.UNDEF,
    # Arbitrary order Lagrange elements(formulated separated from generic higher order cells)
    vtk_element_type.VTK_LAGRANGE_CURVE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_TRIANGLE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_QUADRILATERAL: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_TETRAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_HEXAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_WEDGE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_PYRAMID: cfs_element_type.UNDEF,
    # Arbitrary order Bezier elements(formulated separated from generic higher order cells)
    vtk_element_type.VTK_BEZIER_CURVE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_TRIANGLE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_QUADRILATERAL: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_TETRAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_HEXAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_WEDGE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_PYRAMID: cfs_element_type.UNDEF,
}


# mapping vtk element types array to cfs element types array
def vtk_to_cfs_elem_type(vtk_elem_types: np.ndarray) -> np.ndarray:
    """
    Convert VTK element types to CFS element types.

    Parameters
    ----------
    vtk_elem_types: np.ndarray
        Array of VTK element types.

    Returns
    -------
    np.ndarray
        Array of CFS element types corresponding to the VTK element types.

    """
    return apply_dict_vectorized(dictionary=type_link, data=vtk_elem_types)
