"""
pyCFS.data.io
=============

This subpackage provides classes and functions for reading and writing data in the CFS HDF5 file format.

Contents
--------
- Data structures for mesh and result data
- Utilities for reading and writing CFS files
- Simple high-level functions for common I/O operations

Modules
-------
- CFSReader, CFSWriter
- CFSResultArray, CFSResultContainer, CFSResultInfo
- CFSMeshData, CFSMeshInfo
- CFSRegData
- cfs_types

Functions
---------
- read_mesh : Read mesh data from a CFS file.
- read_data : Read result data from a CFS file.
- read_file : Read mesh and result data from a CFS file.
- write_file : Write mesh and result data to a CFS file.

Examples
--------
>>> from pyCFS.data import io
>>> mesh = io.read_mesh(file="example.cfs")
>>> result = io.read_data(file="example.cfs", multistep=1)
>>> mesh, results = io.read_file(file="example.cfs")
>>> io.write_file(file="output.cfs", mesh=mesh, result=results)
"""

# flake8: noqa : F401

from ._CFSArrayModule import CFSResultArray
from ._CFSRegDataModule import CFSRegData
from ._CFSResultContainerModule import CFSResultContainer, CFSResultInfo
from ._CFSMeshDataModule import CFSMeshData, CFSMeshInfo
from ._CFSReaderModule import CFSReader
from ._CFSWriterModule import CFSWriter
from . import cfs_types
from ._simple import read_mesh, read_data, read_file, write_file, file_info

__all__ = [
    "CFSResultArray",
    "CFSResultContainer",
    "CFSResultInfo",
    "CFSMeshData",
    "CFSMeshInfo",
    "CFSRegData",
    "CFSReader",
    "CFSWriter",
    "cfs_types",
    # Simple functions
    "read_mesh",
    "read_data",
    "read_file",
    "write_file",
    "file_info",
]
