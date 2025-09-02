"""
Module containing data processing utilities for reading EnSight Case Gold files

Notes
-----
Required dependencies are not included in the standard installation. Additional dependencies can be installed via pip:
```pip install -U pyCFS[vtk]```
"""

from __future__ import annotations

import os
import importlib
from typing import List, Dict, Tuple, Optional
import numpy as np

if importlib.util.find_spec("vtk") is None:
    raise ModuleNotFoundError(
        "Missing dependency for submodule pyCFS.data.extras.ensight_io. "
        "To install pyCFS with all required dependencies run 'pip install -U pyCFS[vtk]'."
    )

from vtkmodules.vtkIOEnSight import vtkEnSightGoldBinaryReader
from vtkmodules.util import numpy_support as vtk_numpy

from pyCFS.data import io, v_def
from pyCFS.data.io import cfs_types
from pyCFS.data.util import progressbar, connectivity_list_to_matrix, TimeRecord
from pyCFS.data.extras.vtk_types import vtk_to_cfs_elem_type


def ensightInitReader(file: str) -> vtkEnSightGoldBinaryReader:
    """
    Initializes an EnSight reader object with the specified filename and filepath.

    This function creates an instance of the class vtkEnSightGoldBinaryReader and sets the
    case file name and path for reading EnSight files. The reader object is then updated.

    Parameters
    ----------
    file : str
        Path to the EnSight case file.

    Returns
    -------
    vtk.vtkEnSightGoldBinaryReader
        The initialized EnSight reader object.

    """

    filepath, filename = os.path.split(file)
    if filepath == "":
        filepath = "../ensight/"
    reader = vtkEnSightGoldBinaryReader()
    reader.SetCaseFileName(filename)
    reader.SetFilePath(filepath)
    reader.Update()

    return reader


def ensightGetInfo(reader: vtkEnSightGoldBinaryReader) -> Dict:
    """
    Retrieves information about the EnSight file using the provided reader object.

    This function extracts the names and data types of cell and point arrays in the EnSight file.
    It also retrieves the number of time steps, the time range and generates an array with the time
    steps. Every time a Cell/Point Array is found, its name is printed. Finally, the function returns
    a dictionary with the following keys:
    - 'fieldNames' (list): List of field names (meaning cell and point arrays).
    - 'fieldDataTypes' (list): List of field data types (types: 'Cell' or 'Point').
    - 'numSteps' (int): Number of time steps.
    - 'timeRange' (tuple): start and end point of the time values.
    - 'timeSteps' (numpy array) : one-dimensional array of time steps.

    Parameters
    ----------
    reader : vtk.vtkEnSightGoldBinaryReader
        The EnSight reader object.

    Returns
    --------
    dict
        A dictionary containing the retrieved information.

    """

    field_name_list = []
    field_data_type_list = []

    # append names and types of all Cell/Point Arrays to field_name_list and field_data_type_list
    for j in range(reader.GetNumberOfCellArrays()):
        q = reader.GetCellArrayName(j)
        print(f"Found Cell array: {q}")
        field_name_list.append(q)
        field_data_type_list.append("Cell")
    for j in range(reader.GetNumberOfPointArrays()):
        q = reader.GetPointArrayName(j)
        print(f"Found Point array: {q}")
        field_name_list.append(q)
        field_data_type_list.append("Point")

    # retrieve information about the time steps and create an array time_steps
    time_numsteps = reader.GetTimeSets().GetItem(0).GetNumberOfValues()
    time_range = reader.GetTimeSets().GetItem(0).GetRange(0)
    time_steps = np.linspace(time_range[0], time_range[1], num=time_numsteps)

    return {
        "fieldNames": field_name_list,
        "fieldDataTypes": field_data_type_list,
        "numSteps": time_numsteps,
        "timeRange": time_range,
        "timeSteps": time_steps,
    }


def ensightReadMesh(
    reader: vtkEnSightGoldBinaryReader,
    block: int = 0,
    processes: int | None = None,
    verbosity=v_def.release,
) -> Dict:
    """
    Retrieves mesh data from an EnSight reader for the specified block.

    This function retrieves information about the mesh, including node Coordinates, Connectivity,
    element types, the number of certain element types and the number of nodes.

    It returns a dictionary with the following keys:
     - 'Coordinates' (numpy array): An array with the node Coordinates.
     - 'Connectivity' (numpy array): A 2D array containing the Connectivity information, where
        each row corresponds to a cell and the columns represent the nodes connected to that cell.
     - 'types' (numpy array): A 1D array containing the element types of the field.
     - 'num_grid' (dict): A dictionary containing information about the number of certain element
        types and the number of nodes.

    Parameters
    ----------
    reader : vtk.vtkEnSightGoldBinaryReader
        The EnSight reader object.
    block : int, optional
        The index of the block to read from the EnSight file. Defaults to 0.
    processes : int, optional
        Number of parallel processes for Connectivity build up.
    verbosity : int, optional
        Verbosity level

    Returns
    -------
    dict
        A dictionary containing the retrieved information.

    """

    data = reader.GetOutput()

    bdata = data.GetBlock(block)

    points = bdata.GetPoints()
    cells = bdata.GetCells()

    coord = points.GetData()
    connectivity = cells.GetConnectivityArray()
    offsets = cells.GetOffsetsArray()

    # convert vtk data objects to numpy arrays
    numpy_coord = vtk_numpy.vtk_to_numpy(coord)  # type: ignore[no-untyped-call]
    numpy_connectivity_list = vtk_numpy.vtk_to_numpy(connectivity)  # type: ignore[no-untyped-call]
    numpy_offsets = vtk_numpy.vtk_to_numpy(offsets)  # type: ignore[no-untyped-call]

    # put Connectivity data into a 2D numpy array where each row contains the Connectivity data of one cell

    numpy_connectivity = connectivity_list_to_matrix(
        connectivity_list=numpy_connectivity_list,
        offsets=numpy_offsets,
    )

    # correct indexing in CFS starts with 1
    numpy_connectivity += 1

    # list of vtk element types
    numpy_elem_type = vtk_numpy.vtk_to_numpy(data.GetBlock(block).GetCellTypesArray())  # type: ignore[no-untyped-call]

    # convert vtk element types codes to a common format for cfs indexing
    numpy_elem_type_cfs = vtk_to_cfs_elem_type(numpy_elem_type)

    # count number of each element type in class cfs_element_type and add number to dictionary
    num_grid = {}
    for elemType in cfs_types.cfs_element_type:
        num_grid["Num_" + elemType.name] = np.count_nonzero(numpy_elem_type_cfs == elemType.value)

    # add number of elements (of different dimensions) and total number of nodes to the dictionary
    num_grid["NumElems"] = len(numpy_elem_type_cfs)
    num_grid["Num1DElems"] = num_grid["Num_LINE2"] + num_grid["Num_LINE3"]
    num_grid["Num2DElems"] = (
        num_grid["Num_TRIA3"]
        + num_grid["Num_TRIA6"]
        + num_grid["Num_QUAD4"]
        + num_grid["Num_QUAD8"]
        + num_grid["Num_QUAD9"]
        + num_grid["Num_POLYGON"]
    )
    num_grid["Num3DElems"] = (
        num_grid["Num_TET4"]
        + num_grid["Num_TET10"]
        + num_grid["Num_HEXA8"]
        + num_grid["Num_HEXA20"]
        + num_grid["Num_HEXA27"]
        + num_grid["Num_PYRA5"]
        + num_grid["Num_PYRA13"]
        + num_grid["Num_PYRA14"]
        + num_grid["Num_WEDGE6"]
        + num_grid["Num_WEDGE15"]
        + num_grid["Num_WEDGE18"]
        + num_grid["Num_POLYHEDRON"]
    )
    num_grid["NumNodes"] = numpy_coord.shape[0]

    return {
        "Coordinates": numpy_coord,
        "Connectivity": numpy_connectivity,
        "types": numpy_elem_type_cfs,
        "num_grid": num_grid,
    }


def ensightReadTimeStep(
    reader: vtkEnSightGoldBinaryReader,
    quantity: str,
    step=0,
    block: int = 0,
    idata: Dict | None = None,
) -> np.ndarray:
    if idata is None:
        idata = ensightGetInfo(reader)

    reader.UpdateTimeStep(idata["timeSteps"][step])
    reader.Update()

    idx_array = idata["fieldNames"].index(quantity)

    data = reader.GetOutput()

    # Get field data
    # fdata = data.GetFieldData()

    # Get block data
    bdata = data.GetBlock(block)

    if idata["fieldDataTypes"][idx_array] == "Cell":
        # Get cell data
        cpdata = bdata.GetCellData()
    elif idata["fieldDataTypes"][idx_array] == "Point":
        # Get point data
        cpdata = bdata.GetPointData()
    else:
        raise (IOError("No readable data found"))

    # Get vtk array
    adata = cpdata.GetArray(idx_array)

    # Convert vtkArray to numpy array:
    numpy_data = vtk_numpy.vtk_to_numpy(adata)  # type: ignore[no-untyped-call]

    # Reshape scalar array (scalar arrays are 2D with 1 column in CFS)
    if len(numpy_data.shape) == 1:
        numpy_data = numpy_data.reshape(-1, 1)

    return numpy_data


def ensightReadTimeSeries(
    reader: vtkEnSightGoldBinaryReader,
    quantity: str,
    block: int = 0,
    idata: Dict | None = None,
    verbosity=v_def.release,
) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Read time series. Currently only works for data defined on cells (not on nodes).

    Parameters
    ----------
    reader : vtk.vtkEnSightGoldBinaryReader
        The EnSight reader object.
    quantity : str
        The name of the quantity to read from the EnSight file.
    block : int, optional
        The index of the block to read from the EnSight file. Defaults to 0.
    idata: Dict, optional
        Information about the EnSight file. If not provided, it will be retrieved using `ensightGetInfo`.
    verbosity : int, optional
        Verbosity level for logging. Default is `v_def.release`.

    Returns
    -------
    data : list[np.ndarray]
        List of time data arrays
    time_steps : np.ndarray
        Array to time step values

    """
    if idata is None:
        idata = ensightGetInfo(reader)

    data = []

    for i in progressbar(
        range(idata["numSteps"]),
        prefix=f"Reading time series {quantity}, Step: ",
        size=30,
        verbose=verbosity >= v_def.debug,
    ):
        data.append(ensightReadTimeStep(reader, quantity, i, block, idata))

    return data, idata["timeSteps"]


def convert_to_cfs(
    file: str, quantities: List[str], region_dict: Dict, dim_names_dict: Optional[Dict] = None, verbosity=v_def.release
):
    reader = ensightInitReader(file=file)
    idata = ensightGetInfo(reader)
    mesh_list = []
    for region in region_dict:
        with TimeRecord(f"Reading region {region}", verbose=verbosity >= v_def.release):
            data_geo = ensightReadMesh(reader, block=region_dict[region], verbosity=verbosity)
            mesh_list.append(
                io.CFSMeshData.from_coordinates_connectivity(
                    coordinates=data_geo["Coordinates"],
                    connectivity=data_geo["Connectivity"],
                    element_dimension=3,
                    region_name=region,
                    verbosity=verbosity,
                )
            )

    mesh = mesh_list[0]
    for i in range(1, len(mesh_list)):
        mesh += mesh_list[i]

    result = io.CFSResultContainer(analysis_type=cfs_types.cfs_analysis_type.TRANSIENT)
    for quantity in quantities:
        for region in progressbar(region_dict, prefix=f"Reading {quantity}", verbose=verbosity >= v_def.release):
            if dim_names_dict is not None and quantity in dim_names_dict:
                dim_names = dim_names_dict[quantity]
            else:
                dim_names = None

            data, step_values = ensightReadTimeSeries(reader, quantity, block=region_dict[region], idata=idata)
            result.add_data(
                data=np.array(data),
                step_values=step_values,
                quantity=quantity,
                region=region,
                restype=cfs_types.cfs_result_type.ELEMENT,
                dim_names=dim_names,
                multi_step_id=1,
            )

    return mesh, result


def convert_encas_to_case(file: str, file_out: Optional[str] = None):
    """
    Convert an Encas file to a Case file.

    Parameters
    ----------
    file: str
        Path to the Encas file to be converted.
    file_out: str, optional
        Path to the output Case file. If not provided, the output file will have the same name as the input file
        but with a .case extension.

    Examples
    --------
    >>> convert_encas_to_case(file="example.encas")

    """
    # Read the encas file
    with open(file, "r") as f:
        lines = f.readlines()

    # Remove all " characters
    lines = [line.replace('"', "") for line in lines]

    # Check if "TIME" is in lines
    if "TIME\n" not in lines:
        if "SCRIPTS\n" in lines:
            # If "SCRIPTS" is in lines, add "TIME" before it
            index = lines.index("SCRIPTS\n")
        else:
            # If "SCRIPTS" is not in lines, add "TIME" at the end
            index = len(lines)

        lines.insert(index, "TIME\n")
        lines.insert(index + 1, "time set:                      1\n")
        lines.insert(index + 2, "number of steps:               1\n")
        lines.insert(index + 3, "filename start number:         0\n")
        lines.insert(index + 4, "filename increment:            1\n")
        lines.insert(index + 5, "time values:\n")
        lines.insert(index + 6, "0.00000e+00\n")

    if file_out is None:
        # Write the modified lines to a new file with .case extension
        file_out = file.replace(".encas", ".case")

    os.makedirs(os.path.dirname(file_out), exist_ok=True)
    with open(file_out, "w") as f:
        f.writelines(lines)
