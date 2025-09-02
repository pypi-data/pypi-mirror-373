"""
pyCFS.data.extras
=================

Library of modules to read from, convert to, and write in various formats.

This subpackage provides:

- Readers and writers for various mesh and result file formats.
- Conversion utilities to and from the CFS format.

Modules
-------
- ansys_io, ansys_to_cfs_element_types
- cgns_io, cgns_types
- ensight_io, vtk_types
- exodus_io, exodus_to_cfs_element_types
- nihu_io, nihu_types
- psv_io
- stl_io

Examples
--------
>>> from pyCFS.data import extras
>>> mesh = extras.cgns_io.read_mesh("example.cgns")
>>> mesh = extras.exodus_io.read_exodus("example.e")
>>> mesh, result = extras.ensight_io.convert_to_cfs("example.case", quantities=['quantity1'], region_dict={'region1': 'Region_1'})
>>> mesh = extras.stl_io.read_mesh("example.stl")
"""

import importlib.util

flag_vtk = False
flag_opengl = True
if importlib.util.find_spec("vtk") is not None:
    # Check if OpenGL is available by trying to import a VTK module that requires it.
    try:
        import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
    except ImportError:
        flag_opengl = False
        print("Warning: VTK is available but OpenGL support is not enabled. Some features may not work.")
    except Exception as e:
        raise e
    else:
        flag_vtk = True
        from . import ensight_io
        from . import vtk_types

flag_ansys = False
if importlib.util.find_spec("ansys") is not None and flag_opengl:
    flag_ansys = True
    from . import ansys_io
    from . import ansys_to_cfs_element_types

from . import cgns_io  # noqa: E402
from . import cgns_types  # noqa: E402
from . import exodus_io  # noqa: E402
from . import exodus_to_cfs_element_types  # noqa: E402
from . import nihu_io  # noqa: E402
from . import nihu_types  # noqa: E402
from . import psv_io  # noqa: E402
from . import stl_io  # noqa: E402

__all__ = [
    "cgns_io",
    "cgns_types",
    "exodus_io",
    "exodus_to_cfs_element_types",
    "nihu_io",
    "nihu_types",
    "psv_io",
    "stl_io",
]

if flag_ansys:
    __all__ += [
        "ansys_io",
        "ansys_to_cfs_element_types",
    ]
if flag_vtk:
    __all__ += [
        "ensight_io",
        "vtk_types",
    ]
