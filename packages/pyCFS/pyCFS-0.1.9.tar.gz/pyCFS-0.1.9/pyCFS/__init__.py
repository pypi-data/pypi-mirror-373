"""
pyCFS
==========

Python library for automating and data handling tasks for openCFS.

pyCFS.data
----------
Data processing framework for openCFS. This submodule
contains Python libraries to easily create and manipulate data stored in
openCFS type HDF5 file format (``*.cfs``).

"""

__name__ = "pyCFS"
__author__ = ["IGTE", "Eniz Mušeljić", "Andreas Wurzinger", "Patrick Heidegger"]
__version__ = "0.1.9"
__all__ = ["pyCFS", "application", "data", "topt", "util"]

from .pyCFS import pyCFS  # noqa
from . import application  # noqa
from . import data  # noqa
from . import topt  # noqa
from . import util  # noqa
