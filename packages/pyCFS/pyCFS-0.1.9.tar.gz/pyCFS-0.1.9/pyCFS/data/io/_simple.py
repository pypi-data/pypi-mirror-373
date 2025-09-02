"""
Top-level functions for reading and writing CFS files.

This module provides simple functions to read and write mesh and result data
in the CFS HDF5 file format.

Examples
--------
>>> from pyCFS.data import io
>>> mesh = io.read_mesh(file="example.cfs")
>>> result = io.read_data(file="example.cfs", multistep=1)
>>> mesh, results = io.read_file(file="example.cfs")
>>> io.write_file(file="output.cfs", mesh=mesh, result=results)
"""

from typing import Dict, Optional, Sequence, List

from pyCFS.data._v_def import v_def
from pyCFS.data.io._CFSReaderModule import CFSReader
from pyCFS.data.io._CFSWriterModule import CFSWriter
from pyCFS.data.io._CFSArrayModule import CFSResultArray
from pyCFS.data.io._CFSResultContainerModule import CFSResultContainer
from pyCFS.data.io._CFSMeshDataModule import CFSMeshData


def read_mesh(file: str, verbosity: int = v_def.release, **kwargs) -> CFSMeshData:
    """
    Read a mesh from a CFS file.

    Parameters
    ----------
    file : str
        Path to the CFS file.
    verbosity : int, optional
        Verbosity level for logging (default is v_def.release).

    Other Parameters
    ----------------
    processes : int, optional
        Number of processes to use for parallelized operations. The default is ``None``, in which case all available
        cores are used.
    h5driver : str, optional
        Driver used to read the hdf5 file (see h5py documentation). The default is ``None``, in which case the standard
        driver is used

    Returns
    -------
    tuple
        A tuple containing the mesh data and region data.

    Examples
    --------
    >>> from pyCFS.data.io import read_mesh
    >>> mesh = read_mesh(file="file.cfs")
    """
    with CFSReader(file, verbosity=verbosity, **kwargs) as f:
        return f.MeshData


def read_data(
    file: str,
    multistep: Optional[int] = 1,
    quantities: Optional[List[str]] = None,
    regions: Optional[List[str]] = None,
    verbosity: int = v_def.release,
    **kwargs,
) -> CFSResultContainer:
    """
    Read result data from a CFS file.

    Parameters
    ----------
    file : str
        Path to the CFS file.
    multistep : int, optional
        Multi-step ID to read (default is 1).
    quantities : list[str], optional
        List of quantities to read from the file. If None, all available quantities are read.
    regions : list[str], optional
        List of regions to read from the file. If None, all available regions are read.
    verbosity : int, optional
        Verbosity level for logging (default is v_def.release).

    Other Parameters
    ----------------
    processes : int, optional
        Number of processes to use for parallelized operations. The default is ``None``, in which case all available
        cores are used.
    h5driver : str, optional
        Driver used to read the hdf5 file (see h5py documentation). The default is ``None``, in which case the standard
        driver is used

    Returns
    -------
    CFSResultContainer
        Result data for the specified multi-step ID.

    Examples
    --------
    >>> from pyCFS.data.io import read_data
    >>> result = read_data(file="file.cfs", multistep=1, quantities=["quantity"], regions=["region"])
    """
    with CFSReader(file, verbosity=verbosity, **kwargs) as f:
        return f.get_multi_step_data(multi_step_id=multistep, quantities=quantities, regions=regions)


def read_file(file: str, verbosity: int = v_def.release, **kwargs) -> tuple[CFSMeshData, Dict[int, CFSResultContainer]]:
    """
    Read a CFS file and return the mesh and result data for all multi-steps.

    Parameters
    ----------
    file : str
        Path to the CFS file.
    verbosity : int, optional
        Verbosity level for logging (default is v_def.release).

    Other Parameters
    ----------------
    processes : int, optional
        Number of processes to use for parallelized operations. The default is ``None``, in which case all available
        cores are used.
    h5driver : str, optional
        Driver used to read the hdf5 file (see h5py documentation). The default is ``None``, in which case the standard
        driver is used

    Returns
    -------
    tuple[CFSMeshData, dict[int, CFSResultContainer]]
        A tuple containing the mesh data and a dictionary mapping multi-step IDs to result data.

    Examples
    --------
    >>> from pyCFS.data.io import read_file
    >>> mesh, result = read_file(file="file.cfs")
    """

    res_dict = {}
    with CFSReader(file, verbosity=verbosity, **kwargs) as f:
        mesh = f.MeshData
        for mid in f.MultiStepIDs:
            res_dict[mid] = f.get_multi_step_data(multi_step_id=mid)

    return mesh, res_dict


def write_file(
    file: str,
    mesh: Optional[CFSMeshData] = None,
    result: (
        Dict[int, CFSResultContainer]
        | Sequence[CFSResultContainer]
        | CFSResultContainer
        | Sequence[CFSResultArray]
        | None
    ) = None,
    verbosity: int = v_def.release,
    **kwargs,
):
    """
    Write mesh and result data to a CFS file.

    Parameters
    ----------
    file : str
        Path to the CFS file to write.
    mesh : CFSMeshData, optional
        Mesh data to write to the file. If None, only result data is written (if provided).
    result : dict[int, CFSResultContainer] or Sequence[CFSResultContainer] or CFSResultContainer or Sequence[CFSResultArray], optional
        Result data to write.
        Can be a dictionary mapping multi-step IDs to result containers, a list of result containers,
        a single result container, or a list of result arrays. If None, only mesh data is written (if provided).
    verbosity : int, optional
        Verbosity level for logging (default is v_def.release).

    Other Parameters
    ----------------
    h5driver : str, optional
        Driver used to read the hdf5 file (see h5py documentation). The default is ``None``, in which case the standard
        driver is used.
    compression_lvl : int, optional
        Defines the GZIP compression level used for writing all large datasets in the hdf5 file.
        The default level is ``6``.

    Examples
    --------
    >>> from pyCFS.data.io import write_file
    >>> write_file(file="file.cfs", mesh=mesh)
    >>> write_file(file="file.cfs", mesh=mesh, result=result)
    >>> write_file(file="file.cfs", mesh=mesh, result={1: result_1, 2: result_2})
    >>> write_file(file="file.cfs", mesh=mesh, result=[result_1, result_2])
    """
    with CFSWriter(file, verbosity=verbosity, **kwargs) as f:
        f.create_file(mesh=mesh, result=result)


def file_info(file: str) -> str:
    """
    Read information from a CFS file and return a summary string.

    Parameters
    ----------
    file : str
        Path to the CFS file.

    Returns
    -------
    str
        A string summarizing the contents of the CFS file, including mesh and result data.

    Examples
    --------
    >>> from pyCFS.data.io import file_info
    >>> print(file_info(file="example.cfs"))
    """
    with CFSReader(file) as f:
        return str(f)
