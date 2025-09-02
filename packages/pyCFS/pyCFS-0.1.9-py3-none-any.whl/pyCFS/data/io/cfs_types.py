"""
Module containing Enums extracted from openCFS source code (https://gitlab.com/openCFS/cfs)
"""

from enum import IntEnum, Enum


class cfs_result_definition(str, Enum):
    """
    Definition of result storage on Mesh or History.
    """

    MESH = "Mesh"
    HISTORY = "History"

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.value

    @classmethod
    def _missing_(cls, value):
        return cls.MESH


is_history_dict = {False: cfs_result_definition.MESH, True: cfs_result_definition.HISTORY}


# noinspection PyPep8Naming
class cfs_result_type(IntEnum):
    """
    Extracted from openCFS repo (Domain/Results/ResultInfo.hh)
    """

    UNDEFINED = 0
    NODE = 1
    EDGE = 2
    FACE = 3
    ELEMENT = 4
    SURF_ELEM = 5
    REGION = 6
    REGION_AVERAGE = 7
    SURF_REGION = 8
    NODELIST = 9
    COIL = 10
    FREE = 11

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        # Extracted from openCFS repo (source/DataInOut/SimInOut/hdf5/hdf5io.cc::1786)
        str_dict = {
            "NODE": "Nodes",
            "EDGE": "Edges",
            "FACE": "Faces",
            "ELEMENT": "Elements",
            "SURF_ELEM": "Elements",
            "REGION": "Regions",
            "REGION_AVERAGE": "Regions",
            "SURF_REGION": "ElementGroup",
            "NODELIST": "NodeGroup",
            "COIL": "Coils",
            "FREE": "Unknowns",
        }

        if self.name in str_dict:
            return str_dict[self.name]
        else:
            return f"{self.name.title()}"

    @classmethod
    def _missing_(cls, value):
        return cls.UNDEFINED


# TODO check for commented result types
cfs_history_types = {
    # cfs_result_type.UNDEFINED:cfs_result_definition.MESH
    cfs_result_type.NODE: cfs_result_definition.MESH,
    cfs_result_type.EDGE: cfs_result_definition.MESH,
    cfs_result_type.FACE: cfs_result_definition.MESH,
    cfs_result_type.ELEMENT: cfs_result_definition.MESH,
    cfs_result_type.SURF_ELEM: cfs_result_definition.MESH,
    cfs_result_type.REGION: cfs_result_definition.HISTORY,
    cfs_result_type.REGION_AVERAGE: cfs_result_definition.HISTORY,
    cfs_result_type.SURF_REGION: cfs_result_definition.HISTORY,
    cfs_result_type.NODELIST: cfs_result_definition.HISTORY,
    # cfs_result_type.COIL:cfs_result_definition.HISTORY,
    # cfs_result_type.FREE:cfs_result_definition.HISTORY,
}


def check_history(result_type: cfs_result_type) -> bool:
    """
    Check if the result type is a history type.
    """
    if result_type in cfs_history_types:
        if cfs_history_types[result_type] == cfs_result_definition.HISTORY:
            return True
        else:
            return False
    else:
        raise NotImplementedError(f"Result type '{result_type}' declared as neither history result nor mesh result.")


# noinspection PyPep8Naming
class cfs_element_type(IntEnum):
    """
    Extracted from openCFS repo (Domain/ElemMapping/Elem.hh)
    """

    UNDEF = 0
    POINT = 1
    LINE2 = 2
    LINE3 = 3
    TRIA3 = 4
    TRIA6 = 5
    QUAD4 = 6
    QUAD8 = 7
    QUAD9 = 8
    TET4 = 9
    TET10 = 10
    HEXA8 = 11
    HEXA20 = 12
    HEXA27 = 13
    PYRA5 = 14
    PYRA13 = 15
    PYRA14 = 19
    WEDGE6 = 16
    WEDGE15 = 17
    WEDGE18 = 18
    POLYGON = 20
    POLYHEDRON = 21

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    @classmethod
    def _missing_(cls, value):
        return cls.UNDEF


cfs_element_dimension = {
    cfs_element_type.UNDEF: -1,
    cfs_element_type.POINT: 0,
    cfs_element_type.LINE2: 1,
    cfs_element_type.LINE3: 1,
    cfs_element_type.TRIA3: 2,
    cfs_element_type.TRIA6: 2,
    cfs_element_type.QUAD4: 2,
    cfs_element_type.QUAD8: 2,
    cfs_element_type.QUAD9: 2,
    cfs_element_type.TET4: 3,
    cfs_element_type.TET10: 3,
    cfs_element_type.HEXA8: 3,
    cfs_element_type.HEXA20: 3,
    cfs_element_type.HEXA27: 3,
    cfs_element_type.PYRA5: 3,
    cfs_element_type.PYRA13: 3,
    cfs_element_type.PYRA14: 3,
    cfs_element_type.WEDGE6: 3,
    cfs_element_type.WEDGE15: 3,
    cfs_element_type.WEDGE18: 3,
    cfs_element_type.POLYGON: 2,
    cfs_element_type.POLYHEDRON: 3,
}

cfs_element_node_num = {
    cfs_element_type.UNDEF: -1,
    cfs_element_type.POINT: 1,
    cfs_element_type.LINE2: 2,
    cfs_element_type.LINE3: 3,
    cfs_element_type.TRIA3: 3,
    cfs_element_type.TRIA6: 6,
    cfs_element_type.QUAD4: 4,
    cfs_element_type.QUAD8: 8,
    cfs_element_type.QUAD9: 9,
    cfs_element_type.TET4: 4,
    cfs_element_type.TET10: 10,
    cfs_element_type.HEXA8: 8,
    cfs_element_type.HEXA20: 20,
    cfs_element_type.HEXA27: 27,
    cfs_element_type.PYRA5: 5,
    cfs_element_type.PYRA13: 13,
    cfs_element_type.PYRA14: 14,
    cfs_element_type.WEDGE6: 6,
    cfs_element_type.WEDGE15: 15,
    cfs_element_type.WEDGE18: 18,
    cfs_element_type.POLYGON: -1,
    cfs_element_type.POLYHEDRON: -1,
}


class cfs_entry_type(IntEnum):
    """
    Extracted from openCFS repo (DataInOut/SimInOut/hdf5/hdf5io.cc::1877)
    """

    UNKNOWN = 0
    SCALAR = 1
    VECTOR = 3
    TENSOR = 6
    STRING = 32

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


class cfs_analysis_type(str, Enum):
    """
    Extracted from openCFS repo (PDE/BasePDE.cc::42)
    """

    NO_ANALYSIS = "undefined"
    STATIC = "static"
    TRANSIENT = "transient"
    HARMONIC = "harmonic"
    MULTIHARMONIC = "multiharmonic"
    # HARMONIC = "paramIdent" // the value is not unique
    EIGENFREQUENCY = "eigenFrequency"
    INVERSESOURCE = "inverseSource"
    MULTI_SEQUENCE = "multiSequence"
    BUCKLING = "buckling"
    EIGENVALUE = "eigenValue"

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.value

    @classmethod
    def _missing_(cls, value):
        return cls.NO_ANALYSIS
