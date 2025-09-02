"""
Module containing data processing utilities for writing HDF5 files in openCFS format
"""

from __future__ import annotations

import datetime
import functools
import textwrap
import time
from multiprocessing import Pool

import h5py
import numpy as np
from scipy.spatial import KDTree
from typing import List, Tuple, Optional

from pyCFS.data.io import CFSResultArray, cfs_types, CFSRegData
from pyCFS.data.io._CFSMeshDataModule import CFSMeshData, CFSMeshInfo
from pyCFS.data.io._CFSResultContainerModule import CFSResultContainer, CFSResultInfo
from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type, cfs_result_definition

from pyCFS.data.util import vprint, progressbar

from pyCFS.data._v_def import v_def


def _catch_key_error(f):
    """
    Decorator to catch KeyError in reading HDF5 file
    """

    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            print(f"--- \nError: Could not find object in HDF5 file ({f.__name__})! \n---")
            raise e
        except Exception as e:
            raise e

    return func


class CFSReader:
    # noinspection PyUnresolvedReferences,LongLine
    """
    Base class for all reading operations

    Parameters
    ----------
    filename : str
        Path to the hdf5 file.
    multistep_id : int, optional
        MultiStepID to read result data from. The default is ``1``
    processes : int, optional
        Number of processes to use for parallelized operations. The default is ``None``, in which case all available
        cores are used.
    h5driver : str, optional
        Driver used to read the hdf5 file (see h5py documentation). The default is ``None``, in which case the standard
        driver is used
    verbosity : int, optional
        Verbosity level <=1000 ; see _v_def.py for predefined levels. Default is v_def.release.

    Attributes
    ----------
    MeshInfo: CFSMeshInfo
        Mesh attributes
    Coordinates: np.ndarray
        Mesh coordinates
    Connectivity: np.ndarray
        Mesh connectivity array
    ElementTypes: np.ndarray
        Mesh element types
    MeshData: CFSMeshData
        Mesh data structure
    MeshGroupsRegions: List[CFSRegData]
        List of group / region structures
    MeshGroups: List[CFSRegData]
        List of group structures
    MeshRegions: List[CFSRegData]
        List of region structures
    ResultInfo: List[CFSResultInfo]
        List of result attributes
    MultiStepIDs: List[int]
        List of available MultiStepIDs
    MultiStepData: CFSResultContainer
        Result data structure of the active MultiStep
    ResultMeshData: CFSResultContainer
        Result data structure of the active MultiStep containing mesh result data only
    HistoryData: CFSResultContainer
        Result data structure of the active MultiStep containing history result data only
    AnalysisType: cfs_analysis_type
        Analysis type of the active MultiStep
    ResultQuantities: List[str]
        List of result quantities of the active MultiStep

    Notes
    -----
    -  ``set_multi_step`` Sets the multiStepID

    -  ``check_group_region`` Checks whether a mesh entity is a group or a region instead.

    -  ``check_result_definition`` Checks whether the result definition exists in the file.

    -  ``get_mesh_region`` Reads mesh region or group.

    -  ``get_mesh_region_dimension`` Get the dimension of a mesh region or group.

    -  ``get_mesh_region_nodes`` Get the nodes of a mesh region or group.

    -  ``get_mesh_region_elements`` Get the elements of a mesh region or group.

    -  ``get_mesh_region_coordinates`` Reads node Coordinates of a region or group.

    -  ``get_mesh_region_connectivity`` Reads element Connectivity of a region or group.

    -  ``get_mesh_region_types`` Reads element types of a region or group.

    -  ``get_closest_node`` Return node ids of closest nodes to coordinate array.

    -  ``get_closest_element`` Return element ids of closest element centroids to coordinate array.

    -  ``get_multistep_result_info`` Get result information for all quantities and regions in a multi-step.

    -  ``get_result_info`` Get result information for a given quantity and region.

    -  ``get_multi_step_data`` Reads result data of specified multiStep

    -  ``get_analysis_type`` Get the analysis type for a specified multi-step.

    -  ``get_result_quantities`` Get the result quantities for a specified multi-step.

    -  ``get_result_regions`` Get the result regions for a specified quantity and multi-step.

    -  ``get_dim_names`` Get the dimension names for a given quantity and multi-step.

    -  ``get_restype`` Get the result regions for a specified quantity and multi-step.

    -  ``get_external_filenames`` Get the filenames of external files containing the result data.

    -  ``get_step_numbers`` Get the step numbers for a specified quantity and multi-step.

    -  ``get_step_values`` Get the step values for a specified quantity and multi-step.

    -  ``get_data_step`` Get the data for a specific step.

    -  ``get_data_steps`` Get data over all steps for a specified quantity and region.

    -  ``check_data_complex`` Checks if result contains real or complex data

    -  ``get_single_data_steps`` Get data over all steps of given element/node id (id starting from 0).

    -  ``get_result_mesh_data`` Reads result mesh data of a multiStep.

    -  ``get_history_data`` Reads all history data of a multi-step.

    -  ``get_history_data_array`` Reads history data of a quantity and region.

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader
    >>> with CFSReader('file.cfs') as f:
    >>>     mesh = f.MeshData
    >>>     results = f.MultiStepData

    """

    def __init__(
        self,
        filename: str,
        multistep_id=1,
        processes: Optional[int] = None,
        h5driver: Optional[str] = None,
        verbosity=v_def.release,
    ) -> None:
        """Initialize the reader"""
        self._filename = filename
        self.Processes = processes
        self._h5driver = h5driver
        self._multiStepID = multistep_id
        self._Verbosity = verbosity

    def __enter__(self):
        vprint(f"Opened {self._filename} (CFSReader)", verbose=self._Verbosity >= v_def.debug)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        vprint(f"Closed {self._filename} (CFSReader)", verbose=self._Verbosity >= v_def.debug)
        self._filename = ""
        return

    def __repr__(self) -> str:
        if self._filename:
            return f"CFSReader linked to file_src '{self._filename}', Verbosity {self._Verbosity}"
        else:
            return "Closed CFSReader"

    def __str__(self) -> str:
        if self._filename:
            try:
                reg_str_lst = [f"   - {reg}\n" for reg in self.MeshGroupsRegions]
                reg_str = str().join(reg_str_lst)
                return_str = textwrap.dedent(f"{self.MeshInfo}\n - Regions:   {len(reg_str_lst)}\n{reg_str}")

                for ms_id in self.MultiStepIDs:
                    info = self.get_multistep_result_info(multi_step_id=ms_id)
                    info_str = str().join([f" - {ri}\n" for ri in info])
                    return_str += textwrap.dedent(
                        f"MultiStep {ms_id}: {info[0].AnalysisType}, {info[0].StepValues.size} steps \n{info_str}"
                    )

                return return_str
            except OSError:
                return "Invalid file"
            except KeyError:
                return "Invalid HDF5 file structure"
            except Exception as e:
                raise e
        else:
            return "Closed CFSReader"

    def set_multi_step(self, multi_step_id: int) -> None:
        """Sets the multiStepID"""
        self._multiStepID = multi_step_id

    @property
    @_catch_key_error
    def MeshInfo(self) -> CFSMeshInfo:
        """
        Reads mesh attributes

        Returns
        -------
        pyCFS.data.io.CFSMeshInfo
            data structure containing mesh attributes.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     info = f.MeshInfo

        """
        vprint("Reading Mesh Attributes", verbose=self._Verbosity >= v_def.debug)
        mesh_info = CFSMeshInfo()
        with h5py.File(self._filename, driver=self._h5driver) as f:
            mesh_info.Dimension = f["Mesh"].attrs["Dimension"]
            mesh_info.Num1DElems = f["Mesh/Elements"].attrs["Num1DElems"]
            mesh_info.Num2DElems = f["Mesh/Elements"].attrs["Num2DElems"]
            mesh_info.Num3DElems = f["Mesh/Elements"].attrs["Num3DElems"]
            mesh_info.NumElems = f["Mesh/Elements"].attrs["NumElems"]
            mesh_info.Num_HEXA20 = f["Mesh/Elements"].attrs["Num_HEXA20"]
            mesh_info.Num_HEXA27 = f["Mesh/Elements"].attrs["Num_HEXA27"]
            mesh_info.Num_HEXA8 = f["Mesh/Elements"].attrs["Num_HEXA8"]
            mesh_info.Num_PYRA13 = f["Mesh/Elements"].attrs["Num_PYRA13"]
            mesh_info.Num_PYRA14 = f["Mesh/Elements"].attrs["Num_PYRA14"]
            mesh_info.Num_PYRA5 = f["Mesh/Elements"].attrs["Num_PYRA5"]
            mesh_info.Num_WEDGE15 = f["Mesh/Elements"].attrs["Num_WEDGE15"]
            mesh_info.Num_WEDGE18 = f["Mesh/Elements"].attrs["Num_WEDGE18"]
            mesh_info.Num_WEDGE6 = f["Mesh/Elements"].attrs["Num_WEDGE6"]
            mesh_info.Num_TET10 = f["Mesh/Elements"].attrs["Num_TET10"]
            mesh_info.Num_TET4 = f["Mesh/Elements"].attrs["Num_TET4"]
            mesh_info.Num_QUAD4 = f["Mesh/Elements"].attrs["Num_QUAD4"]
            mesh_info.Num_QUAD8 = f["Mesh/Elements"].attrs["Num_QUAD8"]
            mesh_info.Num_QUAD9 = f["Mesh/Elements"].attrs["Num_QUAD9"]
            mesh_info.Num_TRIA3 = f["Mesh/Elements"].attrs["Num_TRIA3"]
            mesh_info.Num_TRIA6 = f["Mesh/Elements"].attrs["Num_TRIA6"]
            mesh_info.Num_LINE2 = f["Mesh/Elements"].attrs["Num_LINE2"]
            mesh_info.Num_LINE3 = f["Mesh/Elements"].attrs["Num_LINE3"]
            mesh_info.Num_POINT = f["Mesh/Elements"].attrs["Num_POINT"]
            mesh_info.Num_POLYGON = f["Mesh/Elements"].attrs["Num_POLYGON"]
            mesh_info.Num_POLYHEDRON = f["Mesh/Elements"].attrs["Num_POLYHEDRON"]
            mesh_info.Num_UNDEF = f["Mesh/Elements"].attrs["Num_UNDEF"]
            mesh_info.QuadraticElems = f["Mesh/Elements"].attrs["QuadraticElems"]
            mesh_info.NumNodes = f["Mesh/Nodes"].attrs["NumNodes"]
        return mesh_info

    @property
    @_catch_key_error
    def Coordinates(self) -> np.ndarray:
        """
        Reads node coordinates

        Returns
        -------
        np.ndarray
            Coordinate array (Nx3) of the whole mesh (N number of nodes)

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     coordinates = f.Coordinates

        """
        with h5py.File(self._filename, driver=self._h5driver) as f:
            return _read_dataset(f["Mesh/Nodes/Coordinates"], dtype=float)

    @property
    @_catch_key_error
    def Connectivity(self) -> np.ndarray:
        """
        Reads element connectivity

        Returns
        -------
        np.ndarray
            Connectivity array (NxM) of the whole mesh (N number of elements, M maximum number of nodes per element).
            Includes zero entries in case of different element types.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     connectivity = f.Connectivity

        """
        with h5py.File(self._filename, driver=self._h5driver) as f:
            return _read_dataset(f["Mesh/Elements/Connectivity"], dtype=int)

    @property
    @_catch_key_error
    def ElementTypes(self) -> np.ndarray:
        """
        Reads element types

        Returns
        -------
        np.ndarray[cfs_element_type]
            Element type array (Nx1) of the whole mesh (N number of elements).
            Element definitions based on pyCFS.data.io.cfs_types.cfs_element_type

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     element_types = f.ElementTypes

        """
        with h5py.File(self._filename, driver=self._h5driver) as f:
            # noinspection PyTypeChecker
            return _read_dataset(f["Mesh/Elements/Types"], dtype=int)

    @property
    def MeshData(self) -> CFSMeshData:
        """
        Reads mesh

        Returns
        -------
        pyCFS.data.io.CFSMeshData
            data structure containing mesh data, region data and mesh attributes.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData

        """
        vprint("Reading Mesh Data", verbose=self._Verbosity >= v_def.more)
        mesh_data = CFSMeshData(
            coordinates=self.Coordinates,
            connectivity=self.Connectivity,
            types=self.ElementTypes,
            regions=self.MeshGroupsRegions,
            verbosity=self._Verbosity,
        )
        return mesh_data

    @property
    def MeshGroupsRegions(self) -> List[CFSRegData]:
        """
        Reads all mesh groups and regions

        Returns
        -------
        ListpyCFS.data.io.CFSRegData]
            list of data structures containing data about a group or region.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     groups_regions_data = f.MeshGroupsRegions

        """
        reg_data = []
        reg_data.extend(self.MeshGroups)
        reg_data.extend(self.MeshRegions)
        return reg_data

    @property
    @_catch_key_error
    def MeshGroups(self) -> List[CFSRegData]:
        """
        Reads all mesh groups

        Returns
        -------
        list[pyCFS.data.io.CFSRegData]
            list of data structures containing data about a group.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     groups_data = f.MeshGroups

        """
        grp_data = []
        with h5py.File(self._filename, driver=self._h5driver) as f:
            reg_names = list(f["Mesh/Groups"].keys())
        for region in reg_names:
            reg = self.get_mesh_region(region=region, is_group=True)
            grp_data.append(reg)
        return grp_data

    @property
    @_catch_key_error
    def MeshRegions(self) -> List[CFSRegData]:
        """
        Reads all mesh regions

        Returns
        -------
        list[pyCFS.data.io.CFSRegData]
            list of data structures containing data about a region.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     regions_data = f.MeshRegions

        """
        reg_data = []
        with h5py.File(self._filename, driver=self._h5driver) as f:
            reg_names = list(f["Mesh/Regions"].keys())
        for region in reg_names:
            reg = self.get_mesh_region(region=region, is_group=False)
            reg_data.append(reg)
        return reg_data

    @_catch_key_error
    def check_group_region(self, region: str) -> bool:
        """
        Checks whether a mesh entity is a group or a region instead.

        Parameters
        ----------
        region : str
            Name of the group/region

        Returns
        -------
        bool
            flag indicating if the entity is a group

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     if f.check_group_region('region_name'):
        >>>         pass

        """
        with h5py.File(self._filename, driver=self._h5driver) as f:
            group_names = list(f["Mesh/Groups"].keys())
        with h5py.File(self._filename, driver=self._h5driver) as f:
            reg_names = list(f["Mesh/Regions"].keys())
        if region in group_names:
            is_group = True
        elif region in reg_names:
            is_group = False
        else:
            raise IOError(f"Entitiy {region} is found in neither Group nor Region names!")
        return is_group

    @_catch_key_error
    def check_result_definition(
        self, res_def: Optional[str | cfs_result_definition] = cfs_result_definition.MESH
    ) -> bool:
        """
        Checks whether the result definition exists in the file.

        Parameters
        ----------
        region : str
            Result definition 'Mesh' or 'History'

        Returns
        -------
        bool
            flag indicating if the result definition exists in the file

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     if f.check_result_definition(res_def='History'):
        >>>         pass

        """
        with h5py.File(self._filename, driver=self._h5driver) as f:
            result_names = list(f["Results"].keys())
        if res_def in result_names:
            return True
        else:
            return False

    def get_mesh_region(self, region: str, is_group: bool | None = None) -> CFSRegData:
        """
        Reads mesh region or group.

        Parameters
        ----------
        region : str
            Name of the group/region
        is_group : bool, optional
            Flag if the mesh entity is a group or region instead. The default is ``None``, in which case the entity
            will be checked based on the provided name.
        Returns
        -------
        pyCFS.data.io.CFSRegData
            data structure containing the region/group data

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     region_data = f.get_mesh_region('region_name'):

        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        reg_data = []
        vprint(f"Reading Region {region}", verbose=self._Verbosity >= v_def.more)
        reg = CFSRegData(name=region, is_group=is_group, verbosity=self._Verbosity)
        reg.Dimension = self.get_mesh_region_dimension(region=region, is_group=is_group)
        reg.Nodes = self.get_mesh_region_nodes(region=region, is_group=is_group)
        reg.Elements = self.get_mesh_region_elements(region=region, is_group=is_group)
        reg_data.append(reg)
        return reg

    @_catch_key_error
    def get_mesh_region_dimension(self, region: str, is_group: bool | None = None):
        """
        Get the dimension of a mesh region or group. (AI-generated)

        Parameters
        ----------
        region : str
            Name of the region or group.
        is_group : bool, optional
            Whether the region is a group. The default is None.

        Returns
        -------
        int
            Dimension of the region or group.
        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        with h5py.File(self._filename, driver=self._h5driver) as f:
            if is_group:
                return f[f"Mesh/Groups/{region}"].attrs["Dimension"]
            else:
                return f[f"Mesh/Regions/{region}"].attrs["Dimension"]

    @_catch_key_error
    def get_mesh_region_nodes(self, region: str, is_group: bool | None = None) -> np.ndarray:
        """
        Get the nodes of a mesh region or group. (AI-generated)

        Parameters
        ----------
        region : str
            Name of the region or group.
        is_group : bool, optional
            Whether the region is a group. The default is None.

        Returns
        -------
        np.ndarray
            Array of node indices.
        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        if is_group:
            h5_path = f"Mesh/Groups/{region}/Nodes"
        else:
            h5_path = f"Mesh/Regions/{region}/Nodes"

        with h5py.File(self._filename, driver=self._h5driver) as f:
            if h5_path in f:
                return _read_dataset(f[h5_path], dtype=int)
            else:
                raise IOError(f"No Node IDs defined for Region {region}!")

    @_catch_key_error
    def get_mesh_region_elements(self, region: str, is_group: bool | None = None) -> np.ndarray | None:
        """
        Get the elements of a mesh region or group. (AI-generated)

        Parameters
        ----------
        region : str
            Name of the region or group.
        is_group : bool, optional
            Whether the region is a group. The default is None.

        Returns
        -------
        np.ndarray or None
            Array of element indices or None if not applicable.
        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        if is_group:
            h5_path = f"Mesh/Groups/{region}/Elements"
        else:
            h5_path = f"Mesh/Regions/{region}/Elements"

        with h5py.File(self._filename, driver=self._h5driver) as f:
            if h5_path in f:
                return _read_dataset(f[h5_path], dtype=int)
            else:
                vprint(f"Warning: No Node IDs defined for Region {region}!", verbose=self._Verbosity >= v_def.more)
                return np.empty(0, dtype=np.int32)

    def get_mesh_region_coordinates(self, region: str, is_group: bool | None = None) -> np.ndarray:
        """
        Reads node Coordinates of a region or group.

        Parameters
        ----------
        region : str
            Name of the group/region
        is_group : bool, optional
            Flag if the mesh entity is a group or region instead. The default is ``None``, in which case the entity
            will be checked based on the provided name.
        Returns
        -------
        np.ndarray
            Coordinate array (Nx3) (N number of nodes in the region)

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     region_coordinates = f.get_mesh_region_coordinates('region_name'):

        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        coordinates = self.Coordinates
        region_nodes = self.get_mesh_region_nodes(region=region, is_group=is_group)
        if region_nodes.ndim > 1:
            region_nodes = region_nodes.flatten()
        return coordinates[region_nodes - 1, :]

    def get_mesh_region_connectivity(self, region: str, is_group: bool | None = None) -> np.ndarray:
        """
        Reads element Connectivity of a region or group.

        Parameters
        ----------
        region : str
            Name of the group/region
        is_group : bool, optional
            Flag if the mesh entity is a group or region instead. The default is ``None``, in which case the entity
            will be checked based on the provided name.
        Returns
        -------
        np.ndarray
            Connectivity array (NxM) (N number of elements in the region, M maximum number of nodes per element).
            Includes zero entries in case of different element types.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     region_connectivity = f.get_mesh_region_connectivity('region_name'):

        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        connectivity = self.Connectivity
        region_elements = self.get_mesh_region_elements(region=region, is_group=is_group)
        return connectivity[region_elements - 1, :]

    def get_mesh_region_types(self, region: str, is_group: bool | None = None) -> np.ndarray:
        """
        Reads element types of a region or group.

        Parameters
        ----------
        region : str
            Name of the group/region
        is_group : bool, optional
            Flag if the mesh entity is a group or region instead. The default is ``None``, in which case the entity
            will be checked based on the provided name.
        Returns
        -------
        np.ndarray
            Connectivity array (Nx1) (N number of elements in the region).
            Element definitions based on pyCFS.data.io.cfs_types.cfs_element_type

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     region_element_types = f.get_mesh_region_types('region_name'):

        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        element_types = self.ElementTypes
        region_elements = self.get_mesh_region_elements(region=region, is_group=is_group)
        return element_types[region_elements - 1]

    def get_closest_node(self, coordinate: np.ndarray, region: str | None = None, eps: float = 1e-3) -> np.ndarray:
        """
        Return node ids of closest nodes to coordinate array.

        Parameters
        ----------

        coordinate: np.ndarray
            Coordinate array (Nx3, N is the number of query points)
        region : str, optional
            Name of the group/region. The default is ``None``, in which case the global mesh will be used instead.
        eps : float, optional
            Show warning if distance of closest node exceeds the specified value. The default value is ``1e-3``.
        Returns
        -------
        np.ndarray
            Array of node ids (starting from 0) of the closest node to the respective coordinate. If region is passed,
            return region node id, otherwise return global node id.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> search_coord = np.array([0,0,0])
        >>> with CFSReader('file.cfs') as f:
        >>>     node_indices = f.get_closest_node(search_coord):

        """
        if region is None:
            search_coord = self.Coordinates
        else:
            search_coord = self.get_mesh_region_coordinates(region=region)
        search_coord_kdtree = KDTree(search_coord)
        d, idx = search_coord_kdtree.query(coordinate)
        if np.any(d > eps):
            vprint(
                f"Warning: Nearest neighbor distance {np.max(d)} exceeds {eps}",
                verbose=self._Verbosity >= v_def.release,
            )
        return idx

    def get_closest_element(self, coordinate: np.ndarray, region: str | None = None, eps=1e-3):
        """
        Return element ids of closest element centroids to coordinate array.

        Parameters
        ----------

        coordinate: np.ndarray
            Coordinate array (Nx3, N is the number of query points)
        region : str, optional
            Name of the group/region. The default is ``None``, in which case the global mesh will be used instead.
        eps : float, optional
            Show warning if distance of closest node exceeds the specified value. The default value is ``1e-3``.
        Returns
        -------
        np.ndarray
            Array of element ids (starting from 0) of the closest element centroid to the respective coordinate.
            If region is passed, return region element id, otherwise return global element id.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> search_coord = np.array([0,0,0])
        >>> with CFSReader('file.cfs') as f:
        >>>     element_indices = f.get_closest_element(search_coord):

        """
        if region is None:
            search_coord = self.MeshData.get_mesh_centroids()
        else:
            search_coord = self.MeshData.get_region_centroids(region=region)

        search_coord_kdtree = KDTree(search_coord)
        d, idx = search_coord_kdtree.query(coordinate)
        if any(d > eps):
            vprint(
                f"Warning: Nearest neighbor distance {max(d)} exceeds {eps}",
                verbose=self._Verbosity >= v_def.release,
            )
        return idx

    @property
    def ResultInfo(self) -> List[CFSResultInfo]:
        return self.get_multistep_result_info()

    def get_multistep_result_info(self, multi_step_id: Optional[int] = None) -> List[CFSResultInfo]:
        # TODO Adapt to support multiple res_types for one quantity & region
        # Doesn't read DataShape Property

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        result_info_list = []
        quantities_mesh = self.get_result_quantities(is_history=False)
        for quantity in quantities_mesh:
            regions = self.get_result_regions(quantity, is_history=False)
            for reg in regions:
                result_info_list.append(self.get_result_info(quantity=quantity, region=reg, is_history=False))

        quantities_mesh = self.get_result_quantities(is_history=True)
        for quantity in quantities_mesh:
            regions = self.get_result_regions(quantity, is_history=True)
            for reg in regions:
                result_info_list.append(self.get_result_info(quantity=quantity, region=reg, is_history=True))

        return result_info_list

    def get_result_info(
        self, quantity: str, region: str, is_history=False, multi_step_id: Optional[int] = None
    ) -> CFSResultInfo:
        """
        Get result information for a given quantity and region. (AI-generated)

        Parameters
        ----------
        quantity : str
            Name of the quantity.
        region : str
            Name of the region.

        Returns
        -------
        CFSResultInfo
            Result information for the specified quantity and region.
        """
        result_def = cfs_types.is_history_dict[is_history]

        if not self.check_result_definition(res_def=result_def):
            raise IOError(f"Result Definition {result_def} not found in file!")

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        dim_names = self.get_dim_names(quantity=quantity, is_history=is_history)
        # step_numbers = self.get_step_numbers(quantity=quantity,is_history=is_history)
        step_values = self.get_step_values(quantity=quantity, is_history=is_history)
        restype = self.get_restype(quantity=quantity, is_history=is_history)
        is_complex = self.check_data_complex(quantity=quantity, region=region, restype=restype, is_history=is_history)
        return CFSResultInfo(
            quantity=quantity,
            region=region,
            res_type=restype,
            dim_names=dim_names,
            step_values=step_values,
            is_complex=is_complex,
            multi_step_id=self._multiStepID,
            analysis_type=self.AnalysisType,
        )

    @property
    @_catch_key_error
    def MultiStepIDs(self) -> List[int]:
        """
        Reads all available MultiStepIDs

        Returns
        -------
        list[int]
            List of available MultiStepIDs

        """
        with h5py.File(self._filename, driver=self._h5driver) as f:
            multi_step_names = []
            if "Mesh" in f["Results"]:
                multi_step_names.extend(list(f["Results/Mesh"].keys()))
            if "History" in f["Results"]:
                multi_step_names.extend(list(f["Results/History"].keys()))

        multi_step_names = list(set(multi_step_names))
        multi_step_ids = [int(line.replace("MultiStep_", "")) for line in multi_step_names]
        multi_step_ids.sort()
        return multi_step_ids

    @property
    def MultiStepData(self) -> CFSResultContainer:
        """
        Reads result data of the active multiStep

        Returns
        -------
        pyCFS.data.io.CFSResultContainer
            data structure containing result data and attributes of the active multiStep

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result = f.MultiStepData

        """
        return self.get_multi_step_data(multi_step_id=self._multiStepID)

    def get_multi_step_data(
        self,
        multi_step_id: Optional[int] = None,
        quantities: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        sort_steps: bool = True,
    ) -> CFSResultContainer:
        """
        Reads result data of specified multiStep

        Parameters
        ----------
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is ``None``, in which case the active multiStep is used.
        quantities : list of str, optional
            List of quantities to read. The default is ``None``, in which case all quantities are read.
        regions : list of str, optional
            List of regions to include in reading operation. The default is ``None``, in which case all regions are used.

        Returns
        -------
        pyCFS.data.io.CFSResultContainer
            data structure containing result data and attributes of the active multiStep

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result = f.get_multi_step_data(multi_step_id=1)

        """
        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        vprint(
            f"Reading MultiStep {self._multiStepID}",
            verbose=self._Verbosity >= v_def.more,
        )
        if quantities is None:
            quantities_mesh = self.get_result_quantities(is_history=False)
        else:
            quantities_mesh = list(set(quantities) & set(self.get_result_quantities(is_history=False)))

        regions_mesh_set: set[str] = set()
        for quantity in quantities_mesh:
            regions_mesh_set = regions_mesh_set | set(self.get_result_regions(quantity=quantity, is_history=False))
        if regions is None:
            regions_mesh = list(regions_mesh_set)
        else:
            regions_mesh = list(set(regions) & regions_mesh_set)

        if quantities is None:
            quantities_hist = self.get_result_quantities(is_history=True)
        else:
            quantities_hist = list(set(quantities) & set(self.get_result_quantities(is_history=True)))

        regions_hist_set: set[str] = set()
        for quantity in quantities_hist:
            regions_hist_set = regions_hist_set | set(self.get_result_regions(quantity=quantity, is_history=True))
        if regions is None:
            regions_hist = list(regions_hist_set)
        else:
            regions_hist = list(set(regions) & regions_hist_set)

        result_mesh = self.get_result_mesh_data(
            multi_step_id=multi_step_id, quantities=quantities_mesh, regions=regions_mesh, sort_steps=False
        )
        result_hist = self.get_history_data(
            multi_step_id=multi_step_id, quantities=quantities_hist, regions=regions_hist, sort_steps=False
        )

        result_mesh.combine_with(result_hist)

        if sort_steps:
            result_mesh.sort_steps()

        return result_mesh

    @property
    def AnalysisType(self) -> cfs_analysis_type:
        """
        Get the analysis type for the active multi-step. (AI-generated)

        Returns
        -------
        cfs_analysis_type
            Analysis type of the active multi-step.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     analysis_type = f.AnalysisType
        """
        return self.get_analysis_type()

    @_catch_key_error
    def get_analysis_type(self, is_history=False, multi_step_id: Optional[int] = None) -> cfs_analysis_type:
        """
        Get the analysis type for a specified multi-step. (AI-generated)

        Parameters
        ----------
        is_history : bool, optional
            Flag indicating if the result is defined as a history result. The default is ``False`` indicating the result
            is defined on a mesh.
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is None.

        Returns
        -------
        cfs_analysis_type
            Analysis type for the specified multi-step.
        """
        result_def = cfs_types.is_history_dict[is_history]

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        if not self.check_result_definition(res_def=result_def):
            return cfs_analysis_type.NO_ANALYSIS

        with h5py.File(self._filename, driver=self._h5driver) as f:
            try:
                analysis_type = f[f"Results/{result_def}/MultiStep_{self._multiStepID}"].attrs["AnalysisType"]
            except KeyError:
                analysis_type = "undefined"
        return cfs_analysis_type(analysis_type)

    @property
    def ResultQuantities(self) -> List[str]:
        """
        Get the result quantities for the active multi-step. (AI-generated)

        Returns
        -------
        List[str]
            Concatenated list of result quantities for both mesh and history data for the active multi-step.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     quantities = f.ResultQuantities
        """
        return self.get_result_quantities(is_history=False) + self.get_result_quantities(is_history=True)

    @_catch_key_error
    def get_result_quantities(self, is_history=False, multi_step_id: Optional[int] = None) -> List[str]:
        """
        Get the result quantities for a specified multi-step. (AI-generated)

        Parameters
        ----------
        is_history : bool, optional
            Flag indicating if the result is defined as a history result. The default is ``False`` indicating the result
            is defined on a mesh.
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is None.

        Returns
        -------
        List[str]
            List of result quantities for the specified multi-step.
        """
        result_def = cfs_types.is_history_dict[is_history]

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        if not self.check_result_definition(res_def=result_def):
            return []

        with h5py.File(self._filename, driver=self._h5driver) as f:
            hdf_path = f"Results/{result_def}/MultiStep_{self._multiStepID}/ResultDescription"
            if hdf_path not in f:
                return []
            else:
                return list(f[hdf_path].keys())

    @_catch_key_error
    def get_result_regions(self, quantity, is_history=False, multi_step_id: Optional[int] = None) -> List[str]:
        """
        Get the result regions for a specified quantity and multi-step. (AI-generated)

        Parameters
        ----------
        quantity : str
            Name of the quantity.
        is_history : bool, optional
            Flag indicating if the result is defined as a history result. The default is ``False`` indicating the result
            is defined on a mesh.
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is None.

        Returns
        -------
        List[str]
            List of result regions for the specified quantity and multi-step.
        """
        result_def = cfs_types.is_history_dict[is_history]

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        if not self.check_result_definition(res_def=result_def):
            return []

        with h5py.File(self._filename, driver=self._h5driver) as f:
            regions_array = (
                f[f"Results/{result_def}/MultiStep_{self._multiStepID}/ResultDescription/{quantity}/EntityNames"][()]
            ).flatten()
            regions = [reg.decode() for reg in regions_array]  # Convert b'' to str
        return regions

    @_catch_key_error
    def get_dim_names(self, quantity, is_history=False, multi_step_id: Optional[int] = None) -> List[str]:
        """
        Get the dimension names for a given quantity and multi-step. (AI-generated)

        Parameters
        ----------
        quantity : str
            Name of the quantity.
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is ``None``.

        Returns
        -------
        List[str]
            List of dimension names for the specified quantity.
        """
        result_def = cfs_types.is_history_dict[is_history]

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        if not self.check_result_definition(res_def=result_def):
            return []

        with h5py.File(self._filename, driver=self._h5driver) as f:
            dim_names_array = (
                f[f"Results/{result_def}/MultiStep_{self._multiStepID}/ResultDescription/{quantity}/DOFNames"][()]
            ).flatten()
            dim_names = [name.decode() for name in dim_names_array]  # Convert b'' to str
        return dim_names

    @_catch_key_error
    def get_restype(self, quantity, is_history=False, multi_step_id: Optional[int] = None) -> cfs_result_type:
        """
        Get the result regions for a specified quantity and multi-step. (AI-generated)

        Parameters
        ----------
        quantity : str
            Name of the quantity.
        is_history : bool, optional
            Flag indicating if the result is defined as a history result. The default is ``False`` indicating the result
            is defined on a mesh.
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is None.

        Returns
        -------
        cfs_result_type
            Result type for the specified quantity and multi-step.
        """
        # TODO support Quantity to be defined on multiple ResTypes
        result_def = cfs_types.is_history_dict[is_history]

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        if not self.check_result_definition(res_def=result_def):
            return cfs_result_type.UNDEFINED

        with h5py.File(self._filename, driver=self._h5driver) as f:
            restype = cfs_result_type(
                int(
                    (
                        f[f"Results/{result_def}/MultiStep_{self._multiStepID}/ResultDescription/{quantity}/DefinedOn"][
                            ()
                        ]
                    ).item()
                )
            )
        return restype

    @_catch_key_error
    def get_external_filenames(self, quantity, multi_step_id: Optional[int] = None) -> np.ndarray:
        """
        Get the filenames of external files containing the result data for all steps, a specified quantity, and a multi-step. (AI-generated)

        Parameters
        ----------
        quantity : str
            Name of the quantity.
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is None.

        Returns
        -------
        np.ndarray
            Array of strings containing the file paths of the external files for the specified quantity and multi-step.
        """
        result_def = cfs_types.cfs_result_definition.MESH

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        with h5py.File(self._filename, driver=self._h5driver) as f:
            pth = f"Results/{result_def}/MultiStep_{self._multiStepID}"
            step_numbers = self.get_step_numbers(quantity)
            filenames = []
            for it_step in step_numbers:
                try:
                    filenames.append(f[f"{pth}/Step_{it_step}"].attrs["ExtHDF5FileName"])
                except Exception as e:
                    print(f"Warning: External filename for step {it_step} not found. Assigning empty string.")
                    print(f"h5py error: {e}")
                    filenames.append("")
        return np.array(filenames, dtype=str).flatten()

    @_catch_key_error
    def get_step_numbers(self, quantity, is_history=False, multi_step_id: Optional[int] = None) -> np.ndarray:
        """
        Get the step numbers for a specified quantity and multi-step. (AI-generated)

        Parameters
        ----------
        quantity : str
            Name of the quantity.
        is_history : bool, optional
            Flag indicating if the result is defined as a history result. The default is ``False`` indicating the result
            is defined on a mesh.
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is None.

        Returns
        -------
        np.ndarray
            Array of step numbers for the specified quantity and multi-step.
        """
        result_def = cfs_types.is_history_dict[is_history]

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        if not self.check_result_definition(res_def=result_def):
            raise ValueError(f"Result definition {result_def} not found in file!")

        with h5py.File(self._filename, driver=self._h5driver) as f:
            step_numbers = np.array(
                f[f"Results/{result_def}/MultiStep_{self._multiStepID}/ResultDescription/{quantity}/StepNumbers"],
                dtype=int,
            ).flatten()
        return step_numbers

    @_catch_key_error
    def get_step_values(self, quantity, is_history=False, multi_step_id: Optional[int] = None) -> np.ndarray:
        """
        Get the step values for a specified quantity and multi-step. (AI-generated)

        Parameters
        ----------
        quantity : str
            Name of the quantity.
        is_history : bool, optional
            Flag indicating if the result is defined as a history result. The default is ``False`` indicating the result
            is defined on a mesh.
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is None.

        Returns
        -------
        np.ndarray
            Array of step values for the specified quantity and multi-step.
        """
        result_def = cfs_types.is_history_dict[is_history]
        if not self.check_result_definition(res_def=result_def):
            raise ValueError(f"Result definition {result_def} not found in file!")

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        with h5py.File(self._filename, driver=self._h5driver) as f:
            step_values = (
                _read_dataset(
                    f[f"Results/{result_def}/MultiStep_{self._multiStepID}/ResultDescription/{quantity}/StepValues"],
                    dtype=float,
                )
            ).flatten()
        return step_values

    @_catch_key_error
    def get_data_step(
        self,
        step_num: int,
        quantity: str,
        region: str,
        restype: cfs_result_type,
        ds_idx: tuple = (),
    ) -> Tuple[np.ndarray, bool]:
        """
        Get the data for a specific step. (AI-generated)

        Parameters
        ----------
        step_num : int
            The step number to retrieve data for.
        quantity : str
            Name of the quantity.
        region : str
            Name of the region.
        restype : cfs_result_type
            Result type.
        ds_idx : tuple, optional
            Data slice indices. The default is an empty tuple.

        Returns
        -------
        Tuple[np.ndarray, bool]
            A tuple containing the data array and a flag indicating if the data is complex.

        """
        return _get_data_step(
            step_num=step_num,
            filename=self._filename,
            multi_step_id=self._multiStepID,
            quantity=quantity,
            region=region,
            restype=restype,
            h5driver=self._h5driver,
            ds_idx=ds_idx,
        )

    def get_data_steps(self, quantity, region, ds_idx: tuple = ()) -> Tuple[np.ndarray, bool]:
        """
        Get data over all steps for a specified quantity and region. (AI-generated)

        Parameters
        ----------
        quantity : str
            Name of the quantity.
        region : str
            Name of the region.
        ds_idx : tuple, optional
            Data slice indices. The default is ().

        Returns
        -------
        Tuple[np.ndarray, bool]
            Data array and a flag indicating if the data is complex.
        """
        step_numbers = self.get_step_numbers(quantity)
        # Initialize with 1st step
        is_complex = False
        res_type = self.get_restype(quantity)
        data_step, flag_complex = self.get_data_step(
            int(step_numbers[0]),
            quantity,
            region,
            res_type,
            ds_idx=ds_idx,
        )
        is_complex = is_complex or flag_complex
        data_dtype: type[float] | type[complex]
        if is_complex:
            data_dtype = complex
        else:
            data_dtype = float

        data = np.zeros([step_numbers.size] + list(data_step.shape), dtype=data_dtype)
        data[0, ...] = data_step

        get_data_step_args = {
            "quantity": quantity,
            "region": region,
            "restype": res_type,
            "ds_idx": ds_idx,
        }

        if self.Processes == 1:
            # Implement without map for improved performance
            for step_idx, step_num in enumerate(
                progressbar(
                    step_numbers[1:],
                    prefix=f"Reading {quantity} on {region}: ",
                    verbose=self._Verbosity >= v_def.more,
                )
            ):
                data_step, flag_complex = self.get_data_step(step_num, **get_data_step_args)
                is_complex = is_complex or flag_complex
                data[step_idx + 1, ...] = data_step
        else:
            # Execute on multiprocessing pool
            vprint(f"Reading {quantity} on {region}", end="", verbose=self._Verbosity >= v_def.more)
            get_data_step_args["filename"] = self._filename
            get_data_step_args["multi_step_id"] = self._multiStepID
            get_data_step_args["h5driver"] = self._h5driver

            with Pool(processes=self.Processes) as pool:
                t_start = time.time()
                for step_idx, res in enumerate(
                    pool.map(
                        functools.partial(_get_data_step, **get_data_step_args),
                        step_numbers[1:],
                    )
                ):
                    data_step, flag_complex = res
                    is_complex = is_complex or flag_complex
                    data[step_idx + 1, ...] = data_step

            vprint(
                f" | Elapsed time: {datetime.timedelta(seconds=round(time.time() - t_start))}",
                verbose=self._Verbosity >= v_def.more,
            )

        return data, is_complex

    @_catch_key_error
    def check_data_complex(
        self,
        quantity: str,
        region: str,
        restype: cfs_result_type,
        is_history=False,
        multi_step_id: Optional[int] = None,
    ) -> bool:
        """
        Check if the result contains real or complex data. (AI-generated)

        Parameters
        ----------
        quantity : str
            Name of the quantity.
        region : str
            Name of the region.
        restype : cfs_result_type
            Result type.
        is_history : bool, optional
            Flag indicating if the result is defined as a history result. The default is ``False`` indicating the result
            is defined on a mesh.
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is ``None``.

        Returns
        -------
        bool
            True if the data is complex, False otherwise.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     is_complex = f.check_data_complex(quantity='quantity_name', region='region_name')
        """
        result_def = cfs_types.is_history_dict[is_history]
        if not self.check_result_definition(res_def=result_def):
            raise ValueError(f"Result definition {result_def} not found in file!")

        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        step_num = self.get_step_numbers(quantity, is_history=is_history)[0]

        with h5py.File(self._filename, driver=self._h5driver) as f:
            if is_history:
                if restype in [cfs_result_type.NODE, cfs_result_type.ELEMENT]:
                    # Select first available ID
                    id = list(f[f"Results/History/MultiStep_{self._multiStepID}/{quantity}/{restype}"].keys())[0]
                    h5_data_path = f"Results/History/MultiStep_{self._multiStepID}/{quantity}/{restype}/{id}"
                else:
                    h5_data_path = f"Results/{result_def}/MultiStep_{self._multiStepID}/{quantity}/{restype}/{region}"
            else:
                h5_data_path = (
                    f"Results/{result_def}/MultiStep_{self._multiStepID}/Step_{step_num}/{quantity}/{region}/{restype}"
                )

            data_names = list(f[h5_data_path].keys())
            if "Imag" in data_names:
                is_complex = True
            else:
                is_complex = False
        return is_complex

    def get_single_data_steps(self, quantity: str, region: str, entity_id: int) -> np.ndarray:
        """
        Get data over all steps of a given element/node id (id starting from 0).

        Parameters
        ----------
        quantity : str
            Name of the quantity.
        region : str
            Name of the region.
        entity_id : int
            ID of the element/node (starting from 0).

        Returns
        -------
        np.ndarray
            Data array over all steps for the specified element/node.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     data = f.get_single_data_steps(quantity='quantity_name', region='region_name', entity_id=0)
        """

        dim = len(self.get_dim_names(quantity=quantity))
        ds_idx = (entity_id, range(dim))
        data, _ = self.get_data_steps(quantity, region, ds_idx)

        return np.array(data)

    @property
    def ResultMeshData(self) -> CFSResultContainer:
        """
        Reads mesh result data of the active multiStep

        Returns
        -------
        CFSResultContainer
            data structure containing result data and attributes of the active multiStep

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result = f.ResultMeshData

        """
        return self.get_result_mesh_data(multi_step_id=self._multiStepID)

    def get_result_mesh_data(
        self,
        multi_step_id: Optional[int] = None,
        quantities: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        sort_steps: bool = True,
    ) -> CFSResultContainer:
        """
        Reads result mesh data of specified multiStep

        Parameters
        ----------
        multi_step_id : int, optional
            MultiStepID to read result data from. The default is ``None``, in which case the active multiStep is used.
        quantities : list of str, optional
            List of quantities to read. The default is ``None``, in which case all quantities are read.
        regions : list of str, optional
            List of regions to include in reading operation. The default is ``None``, in which case all regions are used.

        Returns
        -------
        pyCFS.data.io.CFSResultContainer
            data structure containing result data and attributes of the active multiStep

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result = f.get_multi_step_data(multi_step_id=1)

        """
        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        vprint(
            f"Reading Mesh Data for MultiStep {self._multiStepID}",
            verbose=self._Verbosity >= v_def.more,
        )
        result = CFSResultContainer(
            analysis_type=self.AnalysisType, multi_step_id=self._multiStepID, verbosity=self._Verbosity
        )
        if quantities is None:
            quantities = self.get_result_quantities(is_history=False)
        else:
            for q in quantities:
                if q not in self.get_result_quantities(is_history=False):
                    raise ValueError(
                        f"Quantity {q} not available in the result data. Available quantities: {self.get_result_quantities(is_history=False)}"
                    )
        for quantity in quantities:
            regions_quantitiy = self.get_result_regions(quantity)
            if regions is None:
                regions_read = regions_quantitiy
            else:
                regions_read = [reg for reg in regions_quantitiy if reg in regions]
            for region in regions_read:
                dim_names = self.get_dim_names(quantity)
                # step_numbers = self.get_step_numbers(quantity)
                step_values = self.get_step_values(quantity)
                restype = self.get_restype(quantity)
                data, is_complex = self.get_data_steps(quantity, region)
                result.add_data(
                    data=data,
                    step_values=step_values,
                    quantity=quantity,
                    region=region,
                    restype=restype,
                    dim_names=dim_names,
                    is_complex=is_complex,
                )
        if sort_steps:
            result.sort_steps()

        return result

    @property
    def HistoryData(self) -> CFSResultContainer:
        """
        Reads history result data of the active multiStep

        Returns
        -------
        CFSResultContainer
            data structure containing result data and attributes of the active multiStep

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result = f.HistoryData

        """
        return self.get_history_data(multi_step_id=self._multiStepID)

    def get_history_data(
        self,
        multi_step_id: Optional[int] = None,
        quantities: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        sort_steps: bool = True,
    ) -> CFSResultContainer:
        """
        Reads all history data of a multi-step.

        Parameters
        ----------
        multi_step_id: int, optional
            MultiStepID to read result data from. The default is ``None``, in which case the active multiStep is used.

        Returns
        -------
        CFSResultContainer
            data structure containing result data and attributes of the active multiStep
        """
        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        vprint(
            f"Reading History Data for MultiStep {self._multiStepID}",
            verbose=self._Verbosity >= v_def.more,
        )

        data = []
        if quantities is None:
            quantities = self.get_result_quantities(is_history=True)
        for quantity in quantities:
            regions_quantitiy = self.get_result_regions(quantity, is_history=True)
            if regions is None:
                regions_read = regions_quantitiy
            else:
                regions_read = [reg for reg in regions_quantitiy if reg in regions]
            for region in regions_read:
                data.append(self.get_history_data_array(quantity=quantity, region=region))

        result = CFSResultContainer(data=data, verbosity=self._Verbosity)

        if sort_steps:
            result.sort_steps()

        return result

    @_catch_key_error
    def get_history_data_array(self, quantity: str, region: str, multi_step_id: Optional[int] = None) -> CFSResultArray:
        """
        Reads history data of a quantity and region.

        Parameters
        ----------
        quantity: str
            quantity name to read
        region: str
            region name to read
        multi_step_id: int, optional
            MultiStepID to read result data from. The default is ``None``, in which case the active multiStep is used.

        Returns
        -------
        pyCFS.data.io.CFSResultArray
            History data array for the specified quantity and region.
        """
        if multi_step_id is not None:
            self.set_multi_step(multi_step_id)

        analysis_type = self.get_analysis_type(is_history=True)
        step_values = self.get_step_values(quantity=quantity, is_history=True)
        restype = self.get_restype(quantity=quantity, is_history=True)
        dim_names = self.get_dim_names(quantity=quantity, is_history=True)

        # Consider different folder structure for node and element history results
        if restype in [cfs_result_type.NODE, cfs_result_type.ELEMENT]:
            match restype:
                case cfs_result_type.NODE:
                    entity_ids = self.get_mesh_region_nodes(region=region)
                case cfs_result_type.ELEMENT:
                    entity_ids = self.get_mesh_region_elements(region=region)
            tmp = []
            is_complex = False
            for id in entity_ids:
                h5_data_path = f"Results/History/MultiStep_{self._multiStepID}/{quantity}/{restype}/{id}"

                data_array, is_complex = _get_data_from_hdf5(
                    filename=self._filename, h5_data_path=h5_data_path, h5driver=self._h5driver
                )
                tmp.append(data_array)
            data_array = np.stack(tmp, axis=1)
        else:
            h5_data_path = f"Results/History/MultiStep_{self._multiStepID}/{quantity}/{restype}/{region}"

            data_array, is_complex = _get_data_from_hdf5(
                filename=self._filename, h5_data_path=h5_data_path, h5driver=self._h5driver
            )

        return CFSResultArray(
            data_array,
            quantity=quantity,
            region=region,
            step_values=step_values,
            dim_names=dim_names,
            res_type=restype,
            is_complex=is_complex,
            multi_step_id=self._multiStepID,
            analysis_type=analysis_type,
        )


def _get_data_step(
    step_num: int,
    filename: str,
    multi_step_id: int,
    quantity: str,
    region: str,
    restype: cfs_result_type,
    h5driver: str | None = None,
    ds_idx: tuple = (),
) -> Tuple[np.ndarray, bool]:
    """
    Get the data for a specific step. (AI-generated)

    Parameters
    ----------
    step_num : int
        The step number to retrieve data for.
    filename : str
        Path to the HDF5 file.
    multi_step_id : int
        MultiStepID to read result data from.
    quantity : str
        Name of the quantity.
    region : str
        Name of the region.
    restype : cfs_result_type
        Result type.
    h5driver : str, optional
        Driver used to read the HDF5 file (see h5py documentation). The default is ``None``.
    ds_idx : tuple, optional
        Data slice indices. The default is an empty tuple.

    Returns
    -------
    Tuple[np.ndarray, bool]
        A tuple containing the data array and a flag indicating if the data is complex.
    """
    h5_data_path = f"Results/Mesh/MultiStep_{multi_step_id}/Step_{step_num}/{quantity}/{region}/{restype}"

    return _get_data_from_hdf5(filename=filename, h5_data_path=h5_data_path, h5driver=h5driver, ds_idx=ds_idx)


def _get_data_from_hdf5(filename: str, h5_data_path: str, h5driver: str | None = None, ds_idx: tuple = ()):
    """
    Get dataset for a specific path in the hdf5 file. (AI-generated)

    Parameters
    ----------
    filename : str
        Path to the HDF5 file.
    h5_data_path : str
        HDF5 path to the dataset.
    h5driver : str, optional
        Driver used to read the HDF5 file (see h5py documentation). The default is ``None``.
    ds_idx : tuple, optional
        Data slice indices. The default is an empty tuple.

    Returns
    -------
    Tuple[np.ndarray, bool]
        A tuple containing the data array and a flag indicating if the data is complex.
    """
    with h5py.File(filename, driver=h5driver) as f:
        data_names = list(f[h5_data_path].keys())
        if "Imag" in data_names:
            # data_step = f[f"{h5_data_path}/Real"][ds_idx] + f[f"{h5_data_path}/Imag"][ds_idx] * 1j
            data_step = (
                _read_dataset(f[f"{h5_data_path}/Real"], dtype=float, ds_idx=ds_idx)
                + _read_dataset(f[f"{h5_data_path}/Imag"], dtype=float, ds_idx=ds_idx) * 1j
            )
            is_complex = True
        else:
            data_step = _read_dataset(f[f"{h5_data_path}/Real"], dtype=float, ds_idx=ds_idx)
            is_complex = False

    if data_step.ndim == 1:
        data_step = data_step.reshape((data_step.shape[0], 1))

    return data_step, is_complex


def _read_dataset(dset: h5py.Dataset, dtype=None, ds_idx: tuple = ()) -> np.ndarray:
    """
    Read dataset of active HDF5 file

    Parameters
    ----------
    dset : h5py.Dataset
        dataset object of opened HDF5 file
    dtype: type, optional
        array data type
    ds_idx: slice, optional
        slice indices to read from dataset. The default is ``()``, which reads the entire dataset.

    Examples
    --------
    >>> import h5py
    >>> from pyCFS.data.io import CFSReader
    >>> with h5py.File('file.cfs', 'r') as f:
    >>>     ds_idx = np.s_[0:10, 3]
    >>>     dset = f['Mesh/Connectivity']
    >>>     data = _read_dataset(dset, dtype=int, ds_idx=ds_idx)

    """
    # TODO investigate performance gain of read_direct vs. slicing
    # if dtype is None:
    #     dtype = dset.dtype
    #
    # if not ds_idx:
    #     arr = np.empty(dset.shape, dtype=dtype)
    #     dset.read_direct(arr)
    # else:
    #     arr = dset[ds_idx].astype(dtype)
    #
    # return arr

    if dtype is None:
        return dset[ds_idx]
    else:
        return dset[ds_idx].astype(dtype)
