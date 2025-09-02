"""
pyCFS.data.operators
====================

Libraries to perform various operations on pyCFS.data objects.

Modules
-------
- derivatives
- interpolators
- modal_analysis
- sngr
- dynamic_mode_decomposition
- fieldfft
- transformation

"""

import importlib.util

from . import derivatives  # noqa
from . import interpolators  # noqa
from . import modal_analysis  # noqa
from . import sngr  # noqa
from . import field_fft  # noqa
from . import transformation  # noqa
from . import _projection_interpolation  # noqa
from . import _rbf_interpolation  # noqa
from . import _nearest_neighbor_interpolation  # noqa

flag_dmd = False

if importlib.util.find_spec("pydmd") is not None:
    from . import dynamic_mode_decomposition  # noqa

    flag_dmd = True

__all__ = [
    "derivatives",
    "interpolators",
    "modal_analysis",
    "sngr",
    "field_fft",
    "transformation",
]

if flag_dmd:
    __all__ += [
        "dynamic_mode_decomposition",
    ]
