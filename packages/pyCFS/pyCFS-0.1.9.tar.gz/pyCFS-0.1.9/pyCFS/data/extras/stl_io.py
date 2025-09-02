import numpy as np
import stl_reader

from pyCFS.data.io import CFSMeshData
from pyCFS.data.io.cfs_types import cfs_element_type


def read_mesh(file: str, region_name="Region"):
    """
    Read STL file and convert to CFSMeshData object.

    Parameters
    ----------
    file: str
        Path to the STL file.
    region_name: str, optional
        Name of the region in the mesh data object. Default is "Region".

    Returns
    -------
    CFSMeshData
        Mesh data object.
    """
    vertices, indices = stl_reader.read(file)

    return CFSMeshData.from_coordinates_connectivity(
        coordinates=vertices,
        connectivity=indices + 1,
        element_types=np.array([cfs_element_type.TRIA3 for _ in range(indices.shape[0])]),
        region_name=region_name,
    )
