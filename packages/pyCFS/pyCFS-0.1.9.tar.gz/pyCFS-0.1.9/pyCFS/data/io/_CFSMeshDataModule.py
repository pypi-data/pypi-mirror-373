"""
Module defining data structures describing the computational grid.

.. figure:: ../../../docs/source/resources/data_structures_overview.png

"""

from __future__ import annotations

import copy
import textwrap
import datetime
import time
from functools import partial
from multiprocessing import Pool

import numpy as np
from scipy.spatial import Delaunay, KDTree
from typing import Iterable, Any, List, Dict, Optional, Sequence
from collections import defaultdict, deque

from pyCFS.data.io import CFSRegData, CFSResultContainer, CFSResultArray, cfs_types

from pyCFS.data.io.cfs_types import cfs_element_type, cfs_result_type
from pyCFS.data.util import (
    vprint,
    progressbar,
    element_quality,
    list_search,
    element_centroid,
    element_normal_2d,
    node_normal_2d,
    renumber_connectivity,
    reshape_connectivity,
    apply_dict_vectorized,
    TimeRecord,
    element_volume,
    connectivity_structured_grid,
)
from pyCFS.data._v_def import v_def


class CFSMeshInfo:
    """
    Data structure containing mesh information

    Notes
    -----
    -  ``update_by_coord_types`` Update structure based on coordinate and element types as defined in CFSMeshData

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader, CFSMeshInfo
    >>> with CFSReader('file.cfs') as f:
    >>>     coordinates = f.Coordinates
    >>>     element_types = f.ElementTypes
    >>> MeshInfo = CFSMeshInfo()
    >>> MeshInfo.update_by_coord_types(coordinates=coordinates,element_types=element_types)

    """

    def __init__(self, coordinates: Optional[np.ndarray] = None, types: Optional[np.ndarray] = None) -> None:
        self._initilize()

        if coordinates is not None and types is not None:
            self.update_by_coord_types(coordinates=coordinates, types=types)

    def __repr__(self) -> str:
        return f"""Mesh Info ({self.Dimension}D, {self.NumNodes} Nodes, {self.NumElems} Elements)"""

    def __str__(self) -> str:
        return textwrap.dedent(
            f"""
        Mesh
         - Dimension: {self.Dimension}
         - Nodes:     {self.NumNodes}
         - Elements:  {self.NumElems}"""
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, CFSMeshInfo):
            return False
        return all(
            [
                self.Dimension == other.Dimension,
                self.Num1DElems == other.Num1DElems,
                self.Num2DElems == other.Num2DElems,
                self.Num3DElems == other.Num3DElems,
                self.NumElems == other.NumElems,
                self.Num_HEXA20 == other.Num_HEXA20,
                self.Num_HEXA27 == other.Num_HEXA27,
                self.Num_HEXA8 == other.Num_HEXA8,
                self.Num_PYRA13 == other.Num_PYRA13,
                self.Num_PYRA14 == other.Num_PYRA14,
                self.Num_PYRA5 == other.Num_PYRA5,
                self.Num_WEDGE15 == other.Num_WEDGE15,
                self.Num_WEDGE18 == other.Num_WEDGE18,
                self.Num_WEDGE6 == other.Num_WEDGE6,
                self.Num_TET10 == other.Num_TET10,
                self.Num_TET4 == other.Num_TET4,
                self.Num_QUAD4 == other.Num_QUAD4,
                self.Num_QUAD8 == other.Num_QUAD8,
                self.Num_QUAD9 == other.Num_QUAD9,
                self.Num_TRIA3 == other.Num_TRIA3,
                self.Num_TRIA6 == other.Num_TRIA6,
                self.Num_LINE2 == other.Num_LINE2,
                self.Num_LINE3 == other.Num_LINE3,
                self.Num_POINT == other.Num_POINT,
                self.Num_POLYGON == other.Num_POLYGON,
                self.Num_POLYHEDRON == other.Num_POLYHEDRON,
                self.Num_UNDEF == other.Num_UNDEF,
                self.QuadraticElems == other.QuadraticElems,
                self.NumNodes == other.NumNodes,
            ]
        )

    def _initilize(self) -> None:
        self.Dimension = -1
        self.Num1DElems = 0
        self.Num2DElems = 0
        self.Num3DElems = 0
        self.NumElems = 0
        self.Num_HEXA20 = 0
        self.Num_HEXA27 = 0
        self.Num_HEXA8 = 0
        self.Num_PYRA13 = 0
        self.Num_PYRA14 = 0
        self.Num_PYRA5 = 0
        self.Num_WEDGE15 = 0
        self.Num_WEDGE18 = 0
        self.Num_WEDGE6 = 0
        self.Num_TET10 = 0
        self.Num_TET4 = 0
        self.Num_QUAD4 = 0
        self.Num_QUAD8 = 0
        self.Num_QUAD9 = 0
        self.Num_TRIA3 = 0
        self.Num_TRIA6 = 0
        self.Num_LINE2 = 0
        self.Num_LINE3 = 0
        self.Num_POINT = 0
        self.Num_POLYGON = 0
        self.Num_POLYHEDRON = 0
        self.Num_UNDEF = 0
        self.QuadraticElems = False
        self.NumNodes = 0

    def update_by_coord_types(self, coordinates: np.ndarray, types: np.ndarray) -> None:
        """
        Update structure based on coordinate and element types as defined in CFSMeshData

        Parameters
        ----------
        coordinates : numpy.ndarray
            Coordinate array (Nx3) of the whole mesh (N number of nodes)

        types : numpy.ndarray[cfs_element_type]
            Element type array (Nx1) of the whole mesh (N number of elements).
            Element definitions based on pyCFS.data.io.cfs_types.cfs_element_type

        """
        # Reinitialize structure for empty input arrays
        if coordinates.size == 0 or types.size == 0:
            self._initilize()
            return

        self.NumNodes = coordinates.shape[0]
        self.NumElems = types.shape[0]

        self.Num_HEXA20 = np.count_nonzero(types == cfs_element_type.HEXA20)
        self.Num_HEXA27 = np.count_nonzero(types == cfs_element_type.HEXA27)
        self.Num_HEXA8 = np.count_nonzero(types == cfs_element_type.HEXA8)
        self.Num_PYRA13 = np.count_nonzero(types == cfs_element_type.PYRA13)
        self.Num_PYRA14 = np.count_nonzero(types == cfs_element_type.PYRA14)
        self.Num_PYRA5 = np.count_nonzero(types == cfs_element_type.PYRA5)
        self.Num_WEDGE15 = np.count_nonzero(types == cfs_element_type.WEDGE15)
        self.Num_WEDGE18 = np.count_nonzero(types == cfs_element_type.WEDGE18)
        self.Num_WEDGE6 = np.count_nonzero(types == cfs_element_type.WEDGE6)
        self.Num_TET10 = np.count_nonzero(types == cfs_element_type.TET10)
        self.Num_TET4 = np.count_nonzero(types == cfs_element_type.TET4)
        self.Num_QUAD4 = np.count_nonzero(types == cfs_element_type.QUAD4)
        self.Num_QUAD8 = np.count_nonzero(types == cfs_element_type.QUAD8)
        self.Num_QUAD9 = np.count_nonzero(types == cfs_element_type.QUAD9)
        self.Num_TRIA3 = np.count_nonzero(types == cfs_element_type.TRIA3)
        self.Num_TRIA6 = np.count_nonzero(types == cfs_element_type.TRIA6)
        self.Num_LINE2 = np.count_nonzero(types == cfs_element_type.LINE2)
        self.Num_LINE3 = np.count_nonzero(types == cfs_element_type.LINE3)
        self.Num_POINT = np.count_nonzero(types == cfs_element_type.POINT)
        self.Num_POLYGON = np.count_nonzero(types == cfs_element_type.POLYGON)
        self.Num_POLYHEDRON = np.count_nonzero(types == cfs_element_type.POLYHEDRON)
        self.Num_UNDEF = np.count_nonzero(types == cfs_element_type.UNDEF)

        self.QuadraticElems = (
            self.Num_HEXA20
            + self.Num_HEXA27
            + self.Num_PYRA13
            + self.Num_PYRA14
            + self.Num_WEDGE15
            + self.Num_WEDGE18
            + self.Num_TET10
            + self.Num_QUAD8
            + self.Num_QUAD9
            + self.Num_TRIA6
            + self.Num_LINE3
        ) > 0

        self.Num1DElems = self.Num_LINE2 + self.Num_LINE3
        self.Num2DElems = (
            self.Num_QUAD4 + self.Num_QUAD8 + self.Num_QUAD9 + self.Num_TRIA3 + self.Num_TRIA6 + self.Num_POLYGON
        )
        self.Num3DElems = (
            self.Num_HEXA20
            + self.Num_HEXA27
            + self.Num_HEXA8
            + self.Num_PYRA13
            + self.Num_PYRA14
            + self.Num_PYRA5
            + self.Num_WEDGE15
            + self.Num_WEDGE18
            + self.Num_WEDGE6
            + self.Num_TET10
            + self.Num_TET4
            + self.Num_POLYHEDRON
        )

        if self.Num3DElems > 0:
            self.Dimension = 3
        elif self.Num2DElems > 0:
            self.Dimension = 2
        elif self.Num1DElems > 0:
            self.Dimension = 1
        elif self.Num_POINT > 0:
            self.Dimension = 0
        else:
            self.Dimension = -1


class CFSMeshData:
    """
    Data structure containing mesh definition

    .. figure:: ../../../docs/source/resources/data_structures_CFSMeshData.png

    Parameters
    ----------
    coordinates : numpy.ndarray, optional
        Coordinate array (Nx3) of the whole mesh (N number of nodes)
    connectivity : numpy.ndarray, optional
        Connectivity array (NxM) of the whole mesh (N number of elements, M maximum number of nodes per element).
        Includes zero entries in case of different element types.
    types : numpy.ndarray[cfs_element_type], optional
        Element type array (Nx1) of the whole mesh (N number of elements).
        Element definitions based on pyCFS.data.io.cfs_types.cfs_element_type
    regions : list[pyCFS.data.io.CFSRegData], optional
        list of data structures containing data about a group or region.
    verbosity : int, optional
        Verbosity level <=1000 ; see _v_def.py for predefined levels. Default is v_def.release.

    Attributes
    ----------
    Coordinates : np.ndarray
        Coordinate array (Nx3) of the whole mesh (N number of nodes)
    Connectivity : np.ndarray
        Connectivity array (NxM) of the whole mesh (N number of elements, M maximum number of nodes per element).
        Includes zero entries in case of different element types.
    Types : np.ndarray
        Element type array (N) of the whole mesh (N number of elements).
        Element definitions based on pyCFS.data.io.cfs_types.cfs_element_type
    MeshInfo : CFSMeshInfo
        Data structure containing mesh information. All attributes are also directly accessible e.g. `meshdata_obj.NumNodes`.
    Regions : list[CFSRegData]
        List of data structures containing mesh region definition
    ElementCentroids : np.ndarray
        Centroids of mesh elements
    Quality : np.ndarray
        Quality metric of mesh elements

    Notes
    -----
    -  ``update_mesh_centroids`` Compute element centroids.

    -  ``get_mesh_centroids`` Compute geometric centers of mesh elements.

    -  ``get_mesh_surface_normals`` Compute surface normal vectors of surface mesh.

    -  ``update_mesh_quality`` Compute mesh metric based on ‘metric’.

    -  ``get_mesh_quality`` Compute mesh metric based on the specified metric.

    -  ``merge`` Merges mesh with other mesh removing duplicate coordinates and elements

    -  ``update_info`` Update structure based on coordinate and element types

    -  ``check_add_point_elements`` Check groups/regions for not defined Elements (Nodes only) and create POINT elements

    -  ``extract_regions`` Extract regions from the mesh data structure.

    -  ``extract_nodes_elements`` Extract nodes and elements from the mesh data structure.

    -  ``drop_nodes_elements`` Drop nodes and elements from the mesh data structure.

    -  ``drop_unused_nodes_elements`` Drop nodes and elements that are not used in the given list of groups/regions.

    -  ``merge_duplicate_nodes`` Merge duplicate nodes in the coordinate array and update regions.

    -  ``renumber_nodes`` Renumber nodes in the connectivity array and update regions.

    -  ``convert_to_simplex`` Convert arbitrary 3D elements into simplexes (tetrahedra), by applying Delaunay triangulation.

    -  ``convert_quad2tria`` Convert QUAD4 elements into TRIA3 elements. If ‘idx_convert’ is unspecified all QUAD4 in the mesh are converted.

    -  ``get_region`` Get region data structure by name.

    -  ``get_region_nodes`` Get node indices of a region.

    -  ``get_region_elements`` Get element indices of a region.

    -  ``get_region_coordinates`` Get coordinates of a region.

    -  ``get_region_connectivity`` Get connectivity of a region.

    -  ``get_region_element_types`` Get element types of a region.

    -  ``get_region_centroids`` Get element centroids of a region.

    -  ``get_closest_node`` Get the closest node to a given coordinate.

    -  ``get_closest_element`` Get the closest element to a given coordinate.

    -  ``reorient_region`` Reorient elements of a region based on the element centroid.

    -  ``reorient_elements`` Reorient elements based on the element centroid.

    -  ``split_regions_by_connectivity`` Split regions by connectivity.

    -  ``from_coordinates_connectivity`` (Classmethod)
        Generates data objects to create cfs mesh with one single region containing all elements.
        Detects element type from number of nodes. Therefore, all elements must have same dimension.

    - ``struct_mesh`` (Classmethod) Create a structured 2D quadrilateral mesh from coordinate arrays.


    Examples
    --------
    >>> from pyCFS.data.io import CFSReader, CFSMeshInfo
    >>> with CFSReader('file.cfs') as f:
    >>>     coordinates = f.Coordinates
    >>>     connectivity = f.Connectivity
    >>>     ElementTypes = f.ElementTypes
    >>>     region_data = f.MeshGroupsRegions
    >>> mesh = CFSMeshData(coordinates=coordinates, connectivity=connectivity, ElementTypes=ElementTypes,
    >>>                    regions=region_data)

    """  # noqa : E501

    def __init__(
        self,
        coordinates=np.empty((0, 3)),
        connectivity=np.empty((0, 1)),
        types=np.empty(0),
        regions: List[CFSRegData] | None = None,
        verbosity=v_def.release,
    ) -> None:
        """Initializes a CFSMeshData object. If both Coordinates and types are provided,
        also updates mesh attributes."""
        if regions is None:
            regions = []
        self._Verbosity = verbosity
        self.Coordinates = coordinates
        self.Connectivity = connectivity
        self.Types: np.ndarray = types
        self.Regions: List[CFSRegData] = regions
        self.check_add_point_elements()
        self._flag_warn_element_centroid = True
        self._flag_warn_element_quality = True
        self._ElementCentroids: np.ndarray | None = None
        self._Quality: np.ndarray | None = None

    def __getattr__(self, name):
        return getattr(self.MeshInfo, name)

    def __deepcopy__(self, memodict={}):
        # Create a new instance of CFSMeshData
        new_instance = self.__class__()
        memodict[id(self)] = new_instance

        # Copy attributes
        for k, v in self.__dict__.items():
            setattr(new_instance, k, copy.deepcopy(v, memodict))

        return new_instance

    # noinspection LongLine
    def __repr__(self) -> str:
        return f"""Mesh ({self.MeshInfo.Dimension}D, {self.MeshInfo.NumNodes} Nodes, {self.MeshInfo.NumElems} Elements, {len(self.Regions)} Regions)"""

    def __str__(self) -> str:
        reg_str = str().join([f"   - {reg}\n" for reg in self.Regions])
        return textwrap.dedent(f"{self.MeshInfo}\n - Regions:   {len(self.Regions)}\n{reg_str}")

    def __eq__(self, other) -> bool:
        if not isinstance(other, CFSMeshData):
            return False
        return all(
            [
                np.array_equal(self.Coordinates, other.Coordinates),
                np.array_equal(self.Connectivity, other.Connectivity),
                np.array_equal(self.Types, other.Types),
                self.MeshInfo == other.MeshInfo,
                sorted(self.Regions) == sorted(other.Regions),
            ]
        )

    def __add__(self, other: CFSMeshData):
        return self.merge(other)

    @property
    def MeshInfo(self) -> CFSMeshInfo:
        """Mesh information data structure"""
        return CFSMeshInfo(coordinates=self.Coordinates, types=self.Types)

    @property
    def Coordinates(self):
        """Node coordinate array"""
        return self._Coordinates

    @Coordinates.setter
    def Coordinates(self, node_coord: np.ndarray | Sequence[Sequence[float]] | Sequence[np.ndarray]):
        coordinates = np.array(node_coord, dtype=float)
        if coordinates.ndim == 1:
            coordinates = coordinates[:, np.newaxis]
        self._Coordinates = coordinates

    @property
    def Connectivity(self):
        """Element Connectivity array"""
        return self._Connectivity

    @Connectivity.setter
    def Connectivity(self, nodes: np.ndarray | Sequence[Sequence[int]] | Sequence[np.ndarray]):
        conn = np.array(nodes, dtype=np.uint32)
        if conn.ndim == 1:
            conn = conn[:, np.newaxis]
        self._Connectivity = conn

    @property
    def Types(self):
        """Element type array"""
        return self._Types

    @Types.setter
    def Types(self, types: np.ndarray | Sequence[int | cfs_element_type]):
        self._Types = np.array(types).flatten()

    def get_mesh_centroids(self, el_idx: np.ndarray | None = None) -> np.ndarray:
        """
        Compute geometric centers of mesh elements.

        Parameters
        ----------
        el_idx : numpy.ndarray, optional
            Array of (global) element ids (starting from 0) for which to compute centroids. The default is ``None``,
            in which case all elements are processed.

        Returns
        -------
        np.ndarray
            Array of element centroids.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>> element_indices = np.array([0,1,2,3])
        >>> centroids = mesh.get_mesh_centroids(el_idx=element_indices,processes=1)

        """
        if el_idx is None:
            el_idx_it: Iterable[Any] = range(self.Connectivity.shape[0])
        elif isinstance(el_idx, np.ndarray):
            el_idx_it = el_idx
        else:
            raise TypeError("el_idx must be of type numpy.ndarray, or None")

        mesh_centroids = np.zeros((self.Connectivity[el_idx_it, :].shape[0], 3), dtype=float)

        t_start = time.time()
        el_idx_it_done: List = []
        for cidx in progressbar(
            range(self.Connectivity.shape[1]),
            prefix="Computing mesh centroids: ",
            verbose=self._Verbosity >= v_def.debug,
        ):
            if cidx == 0:
                conn = self.Connectivity
            else:
                conn = self.Connectivity[:, 0:-cidx]

            el_idx_it_type = np.argwhere(np.all(conn, axis=1))
            el_idx_it_cur, sort_el_idx_it_cur, _ = np.intersect1d(el_idx_it, el_idx_it_type, return_indices=True)  # type: ignore[call-overload]
            # Elements are sorted by increasing element id, so we need to unsort them
            unsort_el_idx_it_cur = np.argsort(sort_el_idx_it_cur)
            el_idx_it_cur = el_idx_it_cur[unsort_el_idx_it_cur]

            el_idx_it_cur = el_idx_it_cur[np.isin(el_idx_it_cur, el_idx_it_done, invert=True)]
            if el_idx_it_cur.size == 0:
                continue
            element_connectivity = conn[el_idx_it_cur, :]
            element_coordinates = self.Coordinates[element_connectivity - 1, :]
            mesh_centroids[np.isin(el_idx_it, el_idx_it_cur), :] = element_centroid(element_coordinates)  # type: ignore[arg-type]

            el_idx_it_done += list(el_idx_it_cur)
            if el_idx_it_cur.size > 0 and np.all(conn[el_idx_it, 0:-cidx]) and np.all(conn[el_idx_it, :]):
                vprint(
                    f"Computing mesh centroids | Elapsed time: {datetime.timedelta(seconds=int(time.time() - t_start))}",
                    verbose=self._Verbosity >= v_def.debug,
                )
                break

        return mesh_centroids

    def get_mesh_surface_normals(
        self,
        restype=cfs_result_type.ELEMENT,
        node_idx_include: Optional[np.ndarray] = None,
        el_idx_include: Optional[np.ndarray] = None,
        processes: Optional[int] = None,
    ) -> np.ndarray:
        """
        Compute surface normal vectors of surface mesh.

        Parameters
        ----------
        restype: cfs_result_type, optional
        node_idx_include: numpy.ndarray, optional
        el_idx_include: numpy.ndarray, optional
        processes: int, optional

        Returns
        -------
        numpy.ndarray

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>> mesh_normal_vectors = mesh.get_mesh_surface_normals()
        """
        _supported_types = [cfs_element_type.TRIA3, cfs_element_type.QUAD4, cfs_element_type.POLYGON]

        if node_idx_include is None:
            node_idx_include = np.arange(self.Coordinates.shape[0])
        if el_idx_include is None:
            el_idx_include = np.arange(self.Connectivity.shape[0])

        # Get supported elements
        el_idx_supported = np.argwhere(np.isin(self.Types[el_idx_include].flatten(), _supported_types)).flatten()

        if restype == cfs_result_type.ELEMENT:
            surface_normals = np.zeros((el_idx_include.shape[0], 3))
            surface_normals.fill(np.nan)
            # Extract element coordinates for supported elements
            el_coord = self.Coordinates[self.Connectivity[el_idx_include[el_idx_supported], 0:3] - 1]
            # Compute element surface normal vecotors
            surface_normals[el_idx_supported, :] = element_normal_2d(element_coordinates=el_coord)

        elif restype == cfs_result_type.NODE:
            # raise NotImplementedError("Evaluating surface normal on nodes currently not implemented.")
            coord = self.Coordinates[node_idx_include, :]
            conn = self.Connectivity[el_idx_include, :][el_idx_supported, :]

            surface_normals = np.zeros((coord.shape[0], 3))
            surface_normals.fill(np.nan)

            with TimeRecord(message="Computing node normals", verbose=self._Verbosity >= v_def.debug):
                with Pool(processes=processes) as pool:
                    for idx, res in enumerate(
                        pool.map(
                            partial(
                                _compute_mesh_node_normal,
                                connectivity=conn,
                                coordinates=coord,
                            ),
                            node_idx_include,
                        )
                    ):
                        surface_normals[node_idx_include[idx], :] = res
        else:
            raise NotImplementedError(
                f"Evaluating surface normal on {restype} not implemented. Supported on NODE and ELEMENT, only!"
            )

        return surface_normals

    def get_mesh_quality(
        self, metric="quality", el_idx: np.ndarray | None = None, processes: int | None = None
    ) -> np.ndarray:
        """
        Compute mesh metric based on the specified metric.

        Parameters
        ----------
        metric : str, optional
            Metric type to compute. The default is ``quality``.
        processes : int, optional
            Number of processes to use in parallel. The default is ``None``, in which case all cores are used.

        Returns
        -------
        np.ndarray
            Array of mesh metric values. Returns -1 for unsupported element types.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>> metric = mesh.get_mesh_quality(metric='skewness', processes=1)
        """
        supported_types = {
            "quality": (
                cfs_element_type.TRIA3,
                cfs_element_type.QUAD4,
                cfs_element_type.TET4,
                cfs_element_type.HEXA8,
                cfs_element_type.WEDGE6,
                cfs_element_type.PYRA5,
            ),
            "skewness": (cfs_element_type.TRIA3, cfs_element_type.QUAD4),
        }

        if metric not in supported_types:
            raise NotImplementedError(f"Implemented mesh quality metrics: {list(supported_types.keys())}.")

        # Extract supported element types
        idx_support_lst = []
        for el_type in supported_types[metric]:
            idx_support_lst.append(np.where(self.Types == el_type)[0])
        idx_support = np.hstack(idx_support_lst)

        if el_idx is None:
            mesh_quality = np.ones(self.Types.size, dtype=float) * -1
            idx_process = idx_support
        else:
            mesh_quality = np.ones(el_idx.size, dtype=float) * -1
            idx_process = np.intersect1d(el_idx, idx_support)

        with TimeRecord(message="Computing mesh quality", verbose=self._Verbosity >= v_def.debug):
            with Pool(processes=processes) as pool:
                for i, res in enumerate(
                    pool.map(
                        partial(
                            _compute_mesh_quality,
                            connectivity=self.Connectivity,
                            coordinates=self.Coordinates,
                            el_types=self.Types,
                            metric=metric,
                        ),
                        idx_process,
                    )
                ):
                    mesh_quality[i] = res

        return mesh_quality

    def merge(self, other: CFSMeshData) -> CFSMeshData:
        """
        Merges mesh with other mesh removing duplicate Coordinates and elements

        Parameters
        ----------
        other : CFSMeshData
            Mesh data object that is merged with.

        Returns
        -------
        CFSMeshData
            Merged mesh data structure.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file1.cfs') as f:
        >>>     mesh1 = f.MeshData
        >>> with CFSReader('file2.cfs') as f:
        >>>     mesh2 = f.MeshData
        >>> mesh_merged = mesh1.merge(mesh2)

        """
        if type(other) is not CFSMeshData:
            raise NotImplementedError("Addition of CFSMeshData only implemented with other object of type CFSMeshData!")

        # Merge Coordinates
        coord_merge, idx_coord_inv = np.unique(
            np.append(self.Coordinates, other.Coordinates, axis=0),
            axis=0,
            return_inverse=True,
        )

        idx_coord_self = idx_coord_inv[: self.Coordinates.shape[0]]
        idx_coord_other = idx_coord_inv[self.Coordinates.shape[0] :]

        # Take starting index 1 for Connectivity into account (keep in mind there are 0 entries for unused columns)
        idx_coord_self = np.insert(idx_coord_self, 0, values=-1)
        idx_coord_other = np.insert(idx_coord_other, 0, values=-1)

        # Merge Connectivity
        conn_self = idx_coord_self[self.Connectivity] + 1
        conn_other = idx_coord_other[other.Connectivity] + 1

        num_rows = max(conn_self.shape[1], conn_other.shape[1])
        while conn_self.shape[1] < num_rows:
            conn_self = np.c_[conn_self, np.zeros(conn_self.shape[0])]

        while conn_other.shape[1] < num_rows:
            conn_other = np.c_[conn_other, np.zeros(conn_other.shape[0])]

        conn_merge, idx_conn, idx_conn_inv = np.unique(
            np.append(conn_self, conn_other, axis=0),
            axis=0,
            return_index=True,
            return_inverse=True,
        )

        idx_conn_self = idx_conn_inv[: conn_self.shape[0]]
        idx_conn_other = idx_conn_inv[conn_self.shape[0] :]

        # Merge types
        types_merge = np.append(self.Types, other.Types)[idx_conn]

        # Create merged mesh object
        return_mesh = CFSMeshData(
            coordinates=coord_merge,
            connectivity=conn_merge,
            types=types_merge,
            verbosity=self._Verbosity,
        )

        if self.Regions or other.Regions:
            # Merge and update regions
            for reg in self.Regions:
                return_reg = CFSRegData(
                    name=reg.Name,
                    dimension=reg.Dimension,
                    is_group=reg.IsGroup,
                    verbosity=self._Verbosity,
                )
                return_reg.Nodes = idx_coord_self[reg.Nodes] + 1
                return_reg.Elements = idx_conn_self[reg.Elements - 1] + 1
                return_mesh.Regions.append(return_reg)
            for reg in other.Regions:
                return_reg = CFSRegData(
                    name=reg.Name,
                    dimension=reg.Dimension,
                    is_group=reg.IsGroup,
                    verbosity=self._Verbosity,
                )
                return_reg.Nodes = idx_coord_other[reg.Nodes] + 1
                return_reg.Elements = idx_conn_other[reg.Elements - 1] + 1
                return_mesh.Regions.append(return_reg)

        return return_mesh

    def update_info(self) -> None:
        """
        Update the mesh information structure based on the current coordinates and element types. (AI-generated)

        This method recalculates the mesh information attributes such as the number of nodes, elements,
        and element types based on the current state of the `Coordinates` and `Types` attributes.

        Examples
        --------
        >>> mesh_data = CFSMeshData(coordinates=coordinates, connectivity=connectivity, types=types)
        >>> mesh_data.update_info()
        """
        self.MeshInfo.update_by_coord_types(coordinates=self.Coordinates, types=self.Types)

    def check_add_point_elements(self) -> None:
        """Check groups/regions for not defined Elements (Nodes only) and create POINT elements"""
        for reg in self.Regions:
            if reg.Elements.size == 0:
                vprint(
                    f"Missing point elements detected in group/region {reg.Name}. Adding point elements.",
                    verbose=self._Verbosity >= v_def.release,
                )
                # Define Element IDs
                reg.Elements = np.arange(reg.Nodes.size, dtype=np.int32) + self.Connectivity.shape[0] + 1
                # Add elements to connectivity and types
                conn_add = np.zeros((reg.Nodes.size, self.Connectivity.shape[1]))
                conn_add[:, 0] = reg.Nodes
                el_types_add = np.full(shape=reg.Nodes.size, fill_value=cfs_element_type.POINT, dtype=np.int32)

                self.Connectivity = np.vstack((self.Connectivity, conn_add))
                self.Types = np.concatenate((self.Types, el_types_add), axis=0)

    def check_mesh(self) -> bool:
        """
        Check mesh data for consistency and validity.

        Returns
        -------
        bool
            True if mesh data is valid, raises AssertionError otherwise.

        """
        vprint("Checking mesh", verbose=self._Verbosity >= v_def.debug)
        # Check connectivity
        assert (
            np.max(self.Connectivity) <= self.MeshInfo.NumNodes
        ), f"Connectivity idx {np.max(self.Connectivity)} exceeds number of nodes {self.MeshInfo.NumNodes}."
        assert (
            self.Connectivity.shape[0] == self.MeshInfo.NumElems
        ), f"Connectivity element count ({self.Connectivity.shape[0]}) mismatch with element types array ({self.MeshInfo.NumElems})."

        # Check element types
        possible_types = [etype.value for etype in cfs_element_type]

        assert np.all(np.isin(self.Types, possible_types)), "Invalid element type found in Types array."

        np.testing.assert_array_equal(
            np.sum(self.Connectivity > 0, axis=1),
            apply_dict_vectorized(data=self.Types, dictionary=cfs_types.cfs_element_node_num),
            err_msg="Connectivity node count mismatch with element types.",
        )

        # Check regions
        for reg in self.Regions:
            assert (
                np.max(reg.Nodes) <= self.MeshInfo.NumNodes
            ), f"Region {reg.Name} has invalid node index {np.max(reg.Nodes)}."
            assert (
                np.max(reg.Elements) <= self.MeshInfo.NumElems
            ), f"Region {reg.Name} has invalid element index {np.max(reg.Elements)}."

            reg_con = self.get_region_connectivity(reg)

            assert np.all(
                np.isin(reg_con[reg_con != 0].flatten(), reg.Nodes)
            ), f"Region {reg.Name} has incomplete Node id definition."
            assert np.all(
                np.isin(reg.Nodes, reg_con)
            ), f"Region {reg.Name} has Node ids defined that are not contained in any region element."

        return True

    def extract_regions(
        self,
        regions: List[str | CFSRegData],
        result_data: CFSResultContainer | None = None,
    ) -> CFSResultContainer | None:
        """
        Extract regions from the mesh data structure. (AI-generated)

        Parameters
        ----------
        regions : List[str | CFSRegData]
            List of regions that should be extracted.
        result_data : CFSResultContainer or None, optional
            Result data associated with the mesh, by default None.

        Returns
        -------
        CFSResultContainer or None
            Updated result data after extracting nodes and elements, or None if no result data is provided.
        """
        region_list: List[CFSRegData] = []
        for reg in regions:
            if type(reg) is CFSRegData:
                region_list.append(reg)
            else:
                region_list.append(self.get_region(region=reg))

        node_idx = np.unique(np.concatenate([reg.Nodes - 1 for reg in region_list]))
        elem_idx = np.unique(np.concatenate([reg.Elements - 1 for reg in region_list]))

        result_extract = self.extract_nodes_elements(node_idx=node_idx, el_idx=elem_idx, result_data=result_data)

        return self.drop_unused_nodes_elements(reg_data_list=region_list, result_data=result_extract)

    def extract_nodes_elements(
        self,
        node_idx: np.ndarray | None = None,
        el_idx: np.ndarray | None = None,
        result_data: CFSResultContainer | None = None,
    ) -> CFSResultContainer | None:
        """
        Extract nodes and elements from the mesh data structure. (AI-generated)

        Parameters
        ----------
        node_idx : np.ndarray or None, optional
            Array of node indices to keep, by default None.
        el_idx : np.ndarray or None, optional
            Array of element indices to keep, by default None.
        result_data : CFSResultContainer or None, optional
            Result data associated with the mesh, by default None.

        Returns
        -------
        CFSResultContainer or None
            Updated result data after extracting nodes and elements, or None if no result data is provided.
        """
        el_idx_extract: Optional[List[int] | np.ndarray] = None
        if node_idx is not None:
            vprint(f"Extracting {len(node_idx)} nodes", verbose=self._Verbosity >= v_def.debug)
            # Drop Elements from connectivity
            # Vectorized selection of elements containing any of the specified nodes
            mask = ~np.any(np.isin(self.Connectivity, node_idx[:, None] + 1), axis=1)

            vprint(
                f"Selected {np.sum(~mask)} elements containing nodes to extract",
                verbose=self._Verbosity >= v_def.debug,
            )
            el_idx_extract = np.where(~mask)[0]

        if el_idx_extract is None or len(el_idx_extract) == 0:
            el_idx_extract = el_idx
        elif el_idx is not None:
            el_idx_extract = np.union1d(el_idx, el_idx_extract)

        el_idx_drop = np.setdiff1d(np.arange(self.Connectivity.shape[0]), el_idx_extract)  # type: ignore[arg-type]

        result_data = self.drop_nodes_elements(el_idx=el_idx_drop, result_data=result_data)

        return result_data

    def drop_nodes_elements(
        self,
        node_idx: np.ndarray | None = None,
        el_idx: np.ndarray | None = None,
        result_data: CFSResultContainer | None = None,
    ) -> CFSResultContainer | None:
        """
        Drop nodes and elements from the mesh data structure. (AI-generated)

        Parameters
        ----------
        node_idx : np.ndarray or None, optional
            Array of node indices to drop, by default None.
        el_idx : np.ndarray or None, optional
            Array of element indices to drop, by default None.
        result_data : CFSResultContainer or None, optional
            Result data associated with the mesh, by default None.

        Returns
        -------
        CFSResultContainer or None
            Updated result data after dropping nodes and elements, or None if no result data is provided.
        """
        el_idx_drop: Optional[List[int] | np.ndarray] = None
        if node_idx is not None:
            vprint(f"Dropping {len(node_idx)} nodes", verbose=self._Verbosity >= v_def.debug)
            # Drop Elements from connectivity
            # Vectorized selection of elements containing any of the specified nodes
            mask = ~np.any(np.isin(self.Connectivity, node_idx[:, None] + 1), axis=1)

            vprint(
                f"Selected {np.sum(~mask)} elements containing dropped nodes to be removed",
                verbose=self._Verbosity >= v_def.debug,
            )
            el_idx_drop = np.where(~mask)[0]

        if el_idx_drop is None or len(el_idx_drop) == 0:
            el_idx_drop = el_idx
        elif el_idx is not None:
            el_idx_drop = np.union1d(el_idx, el_idx_drop)

        if el_idx_drop is not None:
            vprint(f"Dropping {len(el_idx_drop)} elements", verbose=self._Verbosity >= v_def.release)
            result_data = self._drop_elements(el_idx=el_idx_drop, result_data=result_data)

        return result_data

    def _drop_elements(
        self,
        el_idx: List[int] | np.ndarray,
        result_data: CFSResultContainer | None = None,
    ) -> CFSResultContainer | None:
        """
        Drop elements from the mesh data structure. (AI-generated)

        Parameters
        ----------
        el_idx : list of int or np.ndarray
            List or array of element indices to drop.
        result_data : CFSResultContainer or None, optional
            Result data associated with the mesh, by default None.

        Returns
        -------
        CFSResultContainer or None
            Updated result data after dropping elements, or None if no result data is provided.
        """
        self.Types = np.delete(self.Types, el_idx, axis=0)

        nodes = np.unique(self.Connectivity)
        conn_new = np.delete(self.Connectivity, el_idx, axis=0)
        nodes_new = np.unique(conn_new)
        # Remove zero entry
        nodes = np.delete(nodes, np.where(nodes == 0)[0])
        nodes_new = np.delete(nodes_new, np.where(nodes_new == 0)[0])

        # Extract Coordinates
        _, idx_intersect, node_idx_keep = np.intersect1d(nodes_new, nodes, return_indices=True)
        self.Coordinates = self.Coordinates[node_idx_keep, :]

        # Element renumbering
        el_idx_keep = np.delete(np.arange(self.Connectivity.shape[0]), el_idx)
        renumber_element_dict = {el_idx_keep[idx] + 1: idx + 1 for idx in range(el_idx_keep.size)}

        # Node renumbering
        renumber_node_dict = {node_idx_keep[idx] + 1: idx + 1 for idx in range(node_idx_keep.size)}
        renumber_node_dict[0] = 0

        # Update regions
        result_data_node_dict = dict()
        result_data_el_dict = dict()

        idx_pop = []
        for idx, reg in enumerate(self.Regions):
            reg_el_idx = np.where(np.isin(reg.Elements, el_idx_keep + 1))[0]
            if reg_el_idx.size == 0:
                idx_pop.append(idx)
                continue
            reg.Elements = reg.Elements[reg_el_idx]

            reg_nodes = np.unique(self.get_region_connectivity(region=reg))
            reg_nodes = np.delete(reg_nodes, np.where(reg_nodes == 0)[0])
            _, _, reg_node_idx = np.intersect1d(reg_nodes, reg.Nodes, return_indices=True)
            reg.Nodes = reg_nodes

            # ID Renumbering
            reg.Nodes = apply_dict_vectorized(dictionary=renumber_node_dict, data=reg.Nodes)
            reg.Elements = apply_dict_vectorized(dictionary=renumber_element_dict, data=reg.Elements)

            result_data_node_dict[reg.Name] = reg_node_idx
            result_data_el_dict[reg.Name] = reg_el_idx

        idx_pop.sort(reverse=True)
        for idx in idx_pop:
            self.Regions.pop(idx)

        # Renumber Connectivity
        self.Connectivity = apply_dict_vectorized(dictionary=renumber_node_dict, data=conn_new)
        self.Connectivity = reshape_connectivity(self.Connectivity)

        if result_data is not None:
            idx_pop = []
            for idx, item in enumerate(result_data.Data):
                result_data_dict = {
                    cfs_result_type.NODE: result_data_node_dict,
                    cfs_result_type.ELEMENT: result_data_el_dict,
                }
                if item.Region in result_data_dict[item.ResType]:
                    result_data.Data[idx] = item[:, result_data_dict[item.ResType][item.Region], ...]  # type: ignore[call-overload]
                else:
                    idx_pop.append(idx)
                    continue
            idx_pop.sort(reverse=True)
            for idx in idx_pop:
                result_data.Data.pop(idx)

        return result_data

    def drop_unused_nodes_elements(
        self, reg_data_list: Optional[List[CFSRegData]] = None, result_data: Optional[CFSResultContainer] = None
    ) -> CFSResultContainer | None:
        """
        Drop nodes and elements that are not used in the given list of groups/regions.

        Parameters
        ----------
        reg_data_list : list[CFSRegData], optional
            List of groups/regions
        result_data : CFSResultContainer or None, optional
            Result data associated with the mesh, by default None.

        Returns
        -------
        CFSResultContainer or None
            Updated result data after dropping entities, or None if no result data is provided.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> from pyCFS.data.util import list_search
        >>> with CFSReader('file1.cfs') as f:
        >>>     mesh = f.MeshData
        >>>     regions_data = f.MeshGroupsRegions
        >>> regions_data_keep = [list_search(regions_data, 'region_name')]
        >>> mesh.drop_unused_nodes_elements(reg_data_list=regions_data_keep)

        """
        if reg_data_list is None:
            reg_data_list = self.Regions
        self._drop_unused_elements(reg_data_list)
        self._drop_unused_nodes(reg_data_list)
        self.Regions = reg_data_list

        if result_data is None:
            return result_data
        else:
            return result_data.extract_quantity_region(region=reg_data_list)

    # noinspection PyTypeChecker,LongLine
    def _drop_unused_elements(self, reg_data_list: List[CFSRegData]) -> bool:
        """
        Drop elements that are not used in the given list of groups/regions.

        Parameters
        ----------
        reg_data_list

        Returns
        -------
        bool

        """
        # TODO optimize (see for CFSRegData.update_nodes_from_elements)
        used_elements = set()
        for reg_data in reg_data_list:
            used_elements.update(reg_data.Elements.tolist())
        if self.Types.size == len(used_elements):
            vprint("No elements dropped", verbose=self._Verbosity > v_def.release)
            return False
        conn = []
        el_type = []
        counter = 1
        el_id_dict = {}
        for el_id in progressbar(
            range(self.Connectivity.shape[0]),
            prefix=f"{self.Types.size - len(used_elements)} elements dropped. Renumbering elments: ",
            size=24,
            verbose=self._Verbosity >= v_def.release,
        ):
            if el_id + 1 in used_elements:
                el_id_dict[el_id + 1] = counter
                counter += 1
                conn.append(self.Connectivity[el_id, :])
                el_type.append(self.Types[el_id])

        self.Connectivity = np.array(conn)

        # Remove columns containing zeros only
        self.Connectivity = reshape_connectivity(self.Connectivity)

        self.Types = np.array(el_type)
        self.MeshInfo.update_by_coord_types(self.Coordinates, self.Types)

        for reg_data in reg_data_list:
            reg_data.Elements = np.array([el_id_dict[el_id] for el_id in reg_data.Elements])
        return True

    # noinspection PyTypeChecker,LongLine
    def _drop_unused_nodes(self, reg_data_list: List[CFSRegData]):
        """
        Drop nodes that are not used in the given list of groups/regions.

        Parameters
        ----------
        reg_data_list

        Returns
        -------
        bool

        """
        # TODO optimize (see for CFSRegData.update_nodes_from_elements)
        # TODO optimize (see for CFSMeshData.renumber_nodes)
        used_nodes = set()
        for reg_data in reg_data_list:
            used_nodes.update(reg_data.Nodes.tolist())
        if self.Coordinates.shape[0] == len(used_nodes):
            vprint("No nodes dropped", verbose=self._Verbosity > v_def.release)
            return False
        coord = []
        counter = 1
        node_id_dict = {0: 0}
        for node_id in progressbar(
            range(self.Coordinates.shape[0]),
            prefix=f"{self.Coordinates.shape[0] - len(used_nodes)} nodes dropped. Renumbering nodes: ",
            size=26,
            verbose=self._Verbosity >= v_def.release,
        ):
            if node_id + 1 in used_nodes:
                node_id_dict[node_id + 1] = counter
                counter += 1
                coord.append(self.Coordinates[node_id, :])

        self.Coordinates = np.array(coord)
        self.MeshInfo.update_by_coord_types(self.Coordinates, self.Types)

        for c in range(self.Connectivity.shape[1]):
            self.Connectivity[:, c] = apply_dict_vectorized(data=self.Connectivity[:, c], dictionary=node_id_dict)

        for reg_data in reg_data_list:
            reg_data.Nodes = apply_dict_vectorized(data=reg_data.Nodes, dictionary=node_id_dict)

        return True

    def merge_duplicate_nodes(self, precision=10):
        """
        Merge duplicate nodes in the coordinate array and update regions. (AI-generated)

        This method identifies and merges duplicate nodes in the `Coordinates` array based on the specified precision.
        It updates the `Connectivity` and `Regions` attributes accordingly.

        Parameters
        ----------
        precision : int, optional
            Number of decimal places to consider when identifying duplicate nodes. Default is 10.

        Examples
        --------
        >>> mesh_data = CFSMeshData(coordinates=coordinates, connectivity=connectivity, types=types)
        >>> mesh_data.merge_duplicate_nodes(precision=5)
        """
        # TODO merge_duplicate_elements
        coord_rounded = np.round(self.Coordinates, decimals=precision)

        _, unique_indices, inverse_indices, counts = np.unique(
            coord_rounded, axis=0, return_index=True, return_inverse=True, return_counts=True
        )

        node_id_dict = {nidx + 1: inverse_indices[nidx] + 1 for nidx in range(self.Coordinates.shape[0])}
        node_id_dict[0] = 0

        self.Coordinates = self.Coordinates[unique_indices]
        self.Connectivity = apply_dict_vectorized(data=self.Connectivity, dictionary=node_id_dict)

        # TODO for duplicate connectivity entries and change element type accordingly
        # for elidx in range(self.Connectivity.shape[0]):
        #     elconn, ridx, rinv = np.unique(self.Connectivity[elidx, :], return_index=True, return_inverse=True)

        for reg in self.Regions:
            reg.Nodes = np.unique(apply_dict_vectorized(data=reg.Nodes, dictionary=node_id_dict))

    def renumber_nodes(self):
        """
        Renumber nodes in the connectivity array and update regions. (AI-generated)

        This method updates the node numbering in the `Connectivity` array to ensure a continuous and sequential numbering.
        It also updates the node indices in the `Regions` attribute accordingly.

        Examples
        --------
        >>> mesh_data = CFSMeshData(coordinates=coordinates, connectivity=connectivity, types=types)
        >>> mesh_data.renumber_nodes()
        """
        self.Connectivity, eid_dict = renumber_connectivity(self.Connectivity)
        for reg in self.Regions:
            reg.Nodes = apply_dict_vectorized(data=reg.Nodes, dictionary=eid_dict)

    def sort_region_nodes_elements(self, result_data: Optional[CFSResultContainer] = None) -> CFSResultContainer | None:
        """
        Sort nodes and elements in each region and adapt result data accordingly.

        Parameters
        ----------
        result_data : CFSResultContainer, optional
            Result data to adapt based on sorted nodes and elements. Default is `None`.

        Returns
        -------
        CFSResultContainer or None
            Updated result data after sorting nodes and elements, or `None` if no result data is provided.

        Examples
        --------
        >>> mesh_data.sort_region_nodes_elements(result_data=result_data)

        """
        res_arr_lst = []
        for reg in self.Regions:
            # Sort region nodes
            n_idx = np.argsort(reg.Nodes)
            e_idx = np.argsort(reg.Elements)

            reg.Nodes = reg.Nodes[n_idx]
            reg.Elements = reg.Elements[e_idx]

            if result_data is not None:
                # Apply sorting to result data
                for idx, item in enumerate(result_data.Data):
                    if item.Region == reg:
                        if item.ResType == cfs_result_type.NODE:
                            item = item[:, n_idx, ...]  # type: ignore[assignment]
                        elif item.ResType == cfs_result_type.ELEMENT:
                            item = item[:, e_idx, ...]  # type: ignore[assignment]
                        res_arr_lst.append(item)

        if result_data is not None:
            return CFSResultContainer(data=res_arr_lst, verbosity=result_data._Verbosity)
        else:
            return None

    def convert_to_simplex(self, idx_convert: np.ndarray | None = None, result_data: CFSResultContainer | None = None):
        """
        Convert arbitrary 3D elements into simplices (tetrahedra) by applying Delaunay triangulation. (AI-generated)

        This method converts specified 3D elements in the mesh to tetrahedra using Delaunay triangulation.
        It supports various 3D element types and updates the mesh connectivity and types accordingly.

        Parameters
        ----------
        idx_convert : np.ndarray, optional
            Array of element indices to convert. If None, all supported 3D elements are converted. Default is None.
        result_data : CFSResultContainer, optional
            Result data associated with the mesh. If provided, it will be updated to reflect the changes in the mesh. Default is None.

        Examples
        --------
        >>> mesh_data = CFSMeshData(coordinates=coordinates, connectivity=connectivity, types=types)
        >>> mesh_data.convert_to_simplex()
        >>> mesh_data.convert_to_simplex(idx_convert=np.array([0, 1, 2]))
        >>> mesh_data.convert_to_simplex(result_data=result_data)
        """
        # TODO Check algorithm to prevent holes inside the volume domain
        # TODO Add support for 2D elements
        supported_types = {
            # cfs_element_type.QUAD4, cfs_element_type.QUAD8, cfs_element_type.QUAD9,
            cfs_element_type.TET10,
            cfs_element_type.HEXA8,
            cfs_element_type.HEXA20,
            cfs_element_type.HEXA27,
            cfs_element_type.PYRA5,
            cfs_element_type.PYRA13,
            cfs_element_type.PYRA14,
            cfs_element_type.WEDGE6,
            cfs_element_type.WEDGE15,
            cfs_element_type.WEDGE18,
            cfs_element_type.POLYHEDRON,
        }

        if idx_convert is None:
            idx_convert = np.array([i for i in range(self.Connectivity.shape[0])])

        num_el = self.Connectivity.shape[0]
        idx_convert_dict = {}
        reg_idx_convert_dict: Dict = {reg.Name: {} for reg in self.Regions}

        conn_add = []
        types_add = []

        for idx in progressbar(
            idx_convert,
            prefix="Converting elements into simplexes: ",
            verbose=self._Verbosity >= v_def.release,
        ):
            if cfs_element_type(self.Types[idx]) not in supported_types:
                if cfs_element_type(self.Types[idx]) == cfs_element_type.UNDEF:
                    vprint(
                        f"Warning: Element of type {cfs_element_type.UNDEF} can lead to unexpected result!",
                        verbose=self._Verbosity >= v_def.more,
                    )
                else:
                    vprint(
                        f"Skipped unsupported element ({cfs_element_type(self.Types[idx])})!",
                        verbose=self._Verbosity >= v_def.more,
                    )
                    continue
            conn_complex = self.Connectivity[idx, :]
            # Remove columns containing zeros only
            idx_zero = np.argwhere(conn_complex == 0).flatten()
            conn_complex = np.delete(conn_complex, idx_zero)
            coord_complex = self.Coordinates[conn_complex - 1, :]
            tri = Delaunay(coord_complex)

            complex_simplex_link = {i: conn_complex[i] for i in range(conn_complex.shape[0])}
            conn_simplex = apply_dict_vectorized(data=tri.simplices, dictionary=complex_simplex_link)
            conn_simplex = np.hstack(
                (
                    conn_simplex,
                    np.zeros(
                        (
                            conn_simplex.shape[0],
                            self.Connectivity.shape[1] - conn_simplex.shape[1],
                        ),
                        dtype=int,
                    ),
                )
            )

            vprint(
                f"Converted element ({cfs_element_type(self.Types[idx])}) into {conn_simplex.shape[0]} elements ({cfs_element_type.TET4})",
                verbose=self._Verbosity >= v_def.debug,
            )

            self.Connectivity[idx, :] = conn_simplex[0, :]  # Replace element
            self.Types[idx] = cfs_element_type.TET4

            conn_add.append(conn_simplex[1:, :])
            types_add.append(np.full(shape=conn_simplex.shape[0] - 1, fill_value=cfs_element_type.TET4))

            idx_convert_dict[idx] = np.array([idx] + [i + num_el for i in range(conn_simplex.shape[0] - 1)])
            num_el += conn_simplex.shape[0] - 1  # Update number of elements

            for reg in self.Regions:
                if idx + 1 in reg.Elements.flatten():
                    reg_el_idx = int(np.where(idx + 1 == reg.Elements.flatten())[0].item())
                    reg_idx_convert_dict[reg.Name][reg_el_idx] = np.array(
                        [reg_el_idx] + [i + reg.Elements.size for i in range(conn_simplex.shape[0] - 1)]
                    )

                    reg.Elements = np.vstack(
                        (
                            np.expand_dims(reg.Elements.flatten(), 1),
                            np.expand_dims(idx_convert_dict[idx][1:] + 1, 1),
                        )
                    ).flatten()

        # Add additional elements
        self.Connectivity = np.vstack([self.Connectivity] + conn_add)
        self.Types = np.concatenate((self.Types, np.concatenate(types_add, axis=0)), axis=0)

        self.update_info()

        # Remove columns containing zeros only
        self.Connectivity = reshape_connectivity(self.Connectivity)

        # Adapt element result data
        if result_data is not None:
            for res_idx, res_data in enumerate(result_data.Data):
                if res_data.ResType == cfs_result_type.ELEMENT:
                    res_data.require_shape(verbose=self._Verbosity >= v_def.debug)
                    data_list = []
                    for k in progressbar(
                        range(res_data.StepValues.size),
                        prefix=f"Converting result {res_data.Quantity}: ",
                        verbose=self._Verbosity >= v_def.more,
                    ):
                        data = res_data[k, ...]
                        for idx in reg_idx_convert_dict[res_data.Region]:
                            val = data[idx, :]
                            data = np.vstack(
                                (
                                    data,
                                    np.ones(
                                        (
                                            reg_idx_convert_dict[res_data.Region][idx].size - 1,
                                            res_data.shape[2],
                                        )
                                    )
                                    * val,
                                )
                            )
                        data_list.append(data)
                    res_data_new = CFSResultArray(np.array(data_list))
                    res_data_new.MetaData = res_data.MetaData
                    result_data.Data[res_idx] = res_data_new

            return result_data

        return None

    def convert_quad2tria(
        self,
        idx_convert: np.ndarray | None = None,
        result_data: CFSResultContainer | Sequence[CFSResultArray] | None = None,
    ):
        """
        Convert QUAD4 elements into TRIA3 elements. (AI-generated)

        This method converts QUAD4 elements in the mesh to TRIA3 elements. If `idx_convert` is unspecified, all QUAD4 elements in the mesh are converted.

        Parameters
        ----------
        idx_convert : np.ndarray, optional
            Array of element indices to convert. If None, all QUAD4 elements are converted. Default is None.
        result_data : CFSResultContainer or Sequence[CFSResultArray], optional
            Result data associated with the mesh. If provided, it will be updated to reflect the changes in the mesh. Default is None.

        Returns
        -------
        None

        Examples
        --------
        >>> mesh_data = CFSMeshData(coordinates=coordinates, connectivity=connectivity, types=types)
        >>> mesh_data.convert_quad2tria()
        >>> mesh_data.convert_quad2tria(idx_convert=np.array([0, 1, 2]))
        >>> mesh_data.convert_quad2tria(result_data=result_data)
        """
        if result_data is not None:
            result_data = CFSResultContainer.require_container(result=result_data, verbosity=self._Verbosity)

        conn = self.Connectivity
        # Get indices of quad4 elements
        idx_quad = np.where(self.Types == cfs_element_type.QUAD4)[0]
        if idx_convert is not None:
            # Check if all specified indices are quad4 elements
            idx_quad_convert = np.intersect1d(idx_quad, idx_convert)
            if idx_quad_convert.size < idx_convert.size:
                vprint(
                    "Warning: Some element indices are ignored because the element is not of type QUAD4!",
                    verbose=self._Verbosity >= v_def.debug,
                )
        else:
            idx_quad_convert = idx_quad

        if idx_quad_convert.size == 0:
            vprint("No QUAD4 elements found!", verbose=self._Verbosity >= v_def.debug)
            return

        conn_quad = conn[idx_quad_convert, :]
        conn_quad_tria = np.hstack(
            (
                conn_quad[:, (0, 1, 2)],
                np.zeros((conn_quad.shape[0], self.Connectivity.shape[1] - 3), dtype=int),
            )
        )
        conn_tria_add = np.hstack(
            (
                conn_quad[:, (0, 2, 3)],
                np.zeros((conn_quad.shape[0], self.Connectivity.shape[1] - 3), dtype=int),
            )
        )
        idx_tria_add = np.array([i for i in range(conn.shape[0], conn.shape[0] + conn_tria_add.shape[0])])

        self.Connectivity = np.vstack((conn, conn_tria_add))
        self.Connectivity[idx_quad_convert, :] = conn_quad_tria
        self.Types = np.append(self.Types, np.array([cfs_element_type.TRIA3 for i in range(conn_tria_add.shape[0])]))
        self.Types[idx_quad_convert] = cfs_element_type.TRIA3
        self.update_info()

        for reg in self.Regions:
            idx_reg_quad = np.where(np.isin(reg.Elements.flatten(), idx_quad_convert + 1))[0]
            idx_reg_tria_add = np.where(np.isin(idx_quad_convert, reg.Elements[idx_reg_quad] - 1))
            reg.Elements = np.vstack(
                (
                    np.expand_dims(reg.Elements.flatten(), 1),
                    np.expand_dims(idx_tria_add[idx_reg_tria_add] + 1, 1),
                )
            ).flatten()

        # Remove columns containing zeros only
        self.Connectivity = reshape_connectivity(self.Connectivity)

        if result_data is not None:
            # TODO: Adapt element result data
            raise NotImplementedError("Adapting result data not implemented!")
            return result_data

        return None

    def get_region(self, region: str | CFSRegData) -> CFSRegData:
        """
        Get region data structure by name. (AI-generated)

        Parameters
        ----------
        region : str or CFSRegData
            Name of the region or the region data structure.

        Returns
        -------
        CFSRegData
            The region data structure.

        Examples
        --------
        >>> from pyCFS.data.io import CFSMeshData
        >>> mesh = CFSMeshData()
        >>> region_data = mesh.get_region('region_name')
        """
        return list_search(self.Regions, region)

    def get_region_nodes(self, region: str | CFSRegData) -> np.ndarray:
        """
        Get node indices of a region. (AI-generated)

        Parameters
        ----------
        region : str or CFSRegData
            Name of the region or the region data structure.

        Returns
        -------
        np.ndarray
            Array of node indices (starting from 1).

        Examples
        --------
        >>> from pyCFS.data.io import CFSMeshData
        >>> mesh = CFSMeshData()
        >>> node_indices = mesh.get_region_nodes('region_name')
        """
        reg_obj = self.get_region(region=region)
        return reg_obj.Nodes

    def get_region_elements(self, region: str | CFSRegData) -> np.ndarray:
        """
        Get element indices of a region. (AI-generated)

        Parameters
        ----------
        region : str or CFSRegData
            Name of the region or the region data structure.

        Returns
        -------
        np.ndarray
            Array of element indices (starting from 1).

        Examples
        --------
        >>> from pyCFS.data.io import CFSMeshData
        >>> mesh = CFSMeshData()
        >>> element_indices = mesh.get_region_elements('region_name')
        """
        reg_obj = self.get_region(region=region)
        return reg_obj.Elements

    def get_region_element_volumes(self, region: str | CFSRegData) -> np.ndarray:
        """
        Get volume (or area in case of 2D elements) for each element of a given region.

        Parameters
        ----------
        region : str or CFSRegData
            Name of the region or the region data structure.

        Returns
        -------
        np.ndarray
            Array of element volumes.

        Examples
        --------
        >>> from pyCFS.data.io import CFSMeshData
        >>> mesh = CFSMeshData()
        >>> element_volumes = mesh.get_region_element_volumes('region_name')
        """

        reg_obj = self.get_region(region=region)

        elem_types = self.get_region_element_types(region=region)
        elem_nodes = self.Connectivity[reg_obj.Elements - 1, :]

        region_element_volumes = np.zeros((elem_types.size,))
        for el_idx, el_type in enumerate(
            progressbar(elem_types, prefix="Calculating element volumes: ", verbose=self._Verbosity >= v_def.debug)
        ):
            el_node = elem_nodes[el_idx, ...]
            el_coord = self.Coordinates[el_node[el_node != 0] - 1, :]
            region_element_volumes[el_idx] = element_volume(element_coordinates=el_coord, element_type=el_type)

        return region_element_volumes

    def get_region_coordinates(self, region: str | CFSRegData) -> np.ndarray:
        """
        Get coordinates of a region. (AI-generated)

        Parameters
        ----------
        region : str or CFSRegData
            Name of the region or the region data structure.

        Returns
        -------
        np.ndarray
            Array of coordinates.

        Examples
        --------
        >>> from pyCFS.data.io import CFSMeshData
        >>> mesh = CFSMeshData()
        >>> coordinates = mesh.get_region_coordinates('region_name')
        """
        reg_obj = self.get_region(region=region)
        return self.Coordinates[reg_obj.Nodes - 1, :]

    def get_region_connectivity(self, region: str | CFSRegData, renumber_nodes=False) -> np.ndarray:
        """
        Get connectivity of a region.

        Parameters
        ----------
        region : str or CFSRegData
            Name of the region or the region data structure.
        renumber_nodes: bool, optional
            Renumber node ids in the connectivity such that it fits with the region coordinates.

        Returns
        -------
        np.ndarray
            Array of connectivity.

        Examples
        --------
        >>> from pyCFS.data.io import CFSMeshData
        >>> mesh = CFSMeshData()
        >>> connectivity = mesh.get_region_connectivity('region_name')
        """
        reg_obj = self.get_region(region=region)

        reg_conn = self.Connectivity[reg_obj.Elements - 1, :]

        if renumber_nodes:
            # Renumber connectivity
            nidx_dict = {reg_obj.Nodes[i]: i + 1 for i in range(reg_obj.Nodes.size)}
            reg_conn = apply_dict_vectorized(reg_conn, dictionary=nidx_dict, val_no_key=0)

        return reg_conn

    def get_region_element_types(self, region: str | CFSRegData) -> np.ndarray:
        """
        Get element types of a region. (AI-generated)

        Parameters
        ----------
        region : str or CFSRegData
            Name of the region or the region data structure.

        Returns
        -------
        np.ndarray
            Array of element types.

        Examples
        --------
        >>> from pyCFS.data.io import CFSMeshData
        >>> mesh = CFSMeshData()
        >>> element_types = mesh.get_region_element_types('region_name')
        """
        reg_obj = self.get_region(region=region)
        return self.Types[reg_obj.Elements - 1]

    def get_region_centroids(self, region: str | CFSRegData) -> np.ndarray:
        """
        get_region_centroids (AI-generated)

        Get element centroids of a region.

        Parameters
        ----------
        region : str or CFSRegData
            Name of the region or the region data structure.

        Returns
        -------
        np.ndarray
            Array of element centroids.

        Examples
        --------
        >>> from pyCFS.data.io import CFSMeshData
        >>> mesh = CFSMeshData()
        >>> centroids = mesh.get_region_centroids('region_name')
        """
        reg_obj = self.get_region(region=region)
        return self.get_mesh_centroids(el_idx=reg_obj.Elements - 1)

    def get_region_element_quality(
        self, region: str | CFSRegData, metric="quality", processes: int | None = None
    ) -> np.ndarray:
        """
        Get element quality of a region. (AI-generated)

        Parameters
        ----------
        region : str or CFSRegData
            Name of the region or the region data structure.
        processes : int, optional
            Number of processes to use in parallel. Default is None.

        Returns
        -------
        np.ndarray
            Array of element quality values.

        Examples
        --------
        >>> from pyCFS.data.io import CFSMeshData
        >>> mesh = CFSMeshData()
        >>> quality = mesh.get_region_element_quality('region_name')
        """
        reg_obj = self.get_region(region=region)
        return self.get_mesh_quality(el_idx=reg_obj.Elements - 1, metric=metric, processes=processes)

    def get_closest_node(
        self, coordinate: np.ndarray, region: str | CFSRegData | None = None, eps: float = 1e-3
    ) -> np.ndarray:
        """
        Return node ids of closest nodes to coordinate array.

        Parameters
        ----------

        coordinate: np.ndarray
            Coordinate array (Nx3, N is the number of query points)
        region : str or CFSRegData, optional
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
        >>>     mesh = f.MeshData
        >>>     node_indices = mesh.get_closest_node(search_coord):

        """
        if region is None:
            search_coord = self.Coordinates
        else:
            search_coord = self.get_region_coordinates(region=region)
        search_coord_kdtree = KDTree(search_coord)
        d, idx = search_coord_kdtree.query(coordinate)
        if np.any(d > eps):
            vprint(
                f"Warning: Nearest neighbor distance {np.max(d)} exceeds {eps}",
                verbose=self._Verbosity >= v_def.release,
            )
        return idx

    def get_closest_element(self, coordinate: np.ndarray, region: str | None = None, eps=1e-3) -> np.ndarray:
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
        >>>     mesh = f.MeshData
        >>>     element_indices = mesh.get_closest_element(search_coord):

        """
        if region is None:
            search_coord = self.get_mesh_centroids()
        else:
            search_coord = self.get_region_centroids(region=region)

        search_coord_kdtree = KDTree(search_coord)
        d, idx = search_coord_kdtree.query(coordinate)
        if any(d > eps):
            vprint(
                f"Warning: Nearest neighbor distance {max(d)} exceeds {eps}",
                verbose=self._Verbosity >= v_def.release,
            )
        return idx

    def reorient_region(self, region: str | CFSRegData) -> None:
        """
        Reorient elements in a specified region. (AI-generated)

        Parameters
        ----------
        region : str
            Name of the region whose elements need to be reoriented.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>> mesh.reorient_region('region_name')
        """
        if type(region) is str:
            region_obj = list_search(self.Regions, region)
        else:
            region_obj = region
        vprint(
            f"Reorienting elements in region {region_obj.Name}",
            verbose=self._Verbosity >= v_def.more,
        )
        self.reorient_elements(idx_reorient=region_obj.Elements - 1)

    def reorient_elements(self, idx_reorient: List | np.ndarray) -> None:
        """
        Reorient elements based on the element centroid. (AI-generated)

        Parameters
        ----------
        idx_reorient : np.ndarray
            Indices of the elements that need to be reoriented.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>> mesh.reorient_elements(idx_reorient=[0, 1, 2])
        """
        for el_idx in progressbar(
            list(idx_reorient),
            prefix="Reorienting elements: ",
            verbose=self._Verbosity >= v_def.debug,
        ):
            if self.Types[el_idx] == cfs_element_type.LINE2:
                self.Connectivity[el_idx, [0, 1]] = self.Connectivity[el_idx, [1, 0]]
            elif self.Types[el_idx] == cfs_element_type.TRIA3:
                self.Connectivity[el_idx, [0, 1]] = self.Connectivity[el_idx, [1, 0]]
            elif self.Types[el_idx] == cfs_element_type.QUAD4:
                self.Connectivity[el_idx, [1, 3]] = self.Connectivity[el_idx, [3, 1]]
            else:
                raise NotImplementedError(f"Reorienting of element type {self.Types[el_idx]} not implemented!")

    def split_regions_by_connectivity(
        self,
        result_data: CFSResultContainer | Sequence[CFSResultArray] | None = None,
        regions: list[CFSRegData | str] | None = None,
    ):
        """
        Split regions by connectivity.

        This method splits the regions in the mesh data structure based on their connectivity. It clusters input regions
        into subregions in which all elements are connected.

        Parameters
        ----------
        result_data : CFSResultContainer or Sequence[CFSResultArray], optional
            Result data object. Default is ``None``.
        regions : list[CFSRegData | str], optional
            List of regions to be split. Default is ``None`` in which case all regions are considered.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>>     result = f.ResultMeshData
        >>> mesh.split_regions_by_connectivity(result_data = result)
        """
        if result_data is not None:
            result_data = CFSResultContainer.require_container(result=result_data, verbosity=self._Verbosity)
        # Find clusters in the connectivity array
        with TimeRecord("Finding clusters in connectivity", single_line=False, verbose=self._Verbosity >= v_def.debug):
            clusters = CFSMeshData._find_clusters(
                connectivity=self.Connectivity, verbose=self._Verbosity >= v_def.debug
            )

        # create new result data arrays
        new_result_data_arrays = []

        if regions is None or len(regions) == 0:
            region_lst = self.Regions
        else:
            region_lst = [self.get_region(reg) for reg in regions]

        # iterate over all source regions
        for i_regions in range(len(region_lst)):
            vprint("Processing region:", region_lst[i_regions].Name, verbose=self._Verbosity > v_def.debug)
            # iterate over all clusters
            full_region_node_ids = region_lst[i_regions].Nodes
            full_region_elem_ids = region_lst[i_regions].Elements
            for i_cluster in range(len(clusters)):
                vprint("Processing cluster:", i_cluster, verbose=self._Verbosity > v_def.debug)
                # new region name
                num_digits = len(str(len(clusters)))
                curr_reg_name = f"{region_lst[i_regions].Name}_{i_cluster:0{num_digits}d}"

                # create new region
                curr_reg_data = CFSRegData(
                    name=curr_reg_name,
                    dimension=region_lst[i_regions].Dimension,
                    is_group=region_lst[i_regions].IsGroup,
                    verbosity=self._Verbosity,
                )
                # set clustered elements
                curr_reg_data.Elements = clusters[i_cluster]
                # retrieve nodes from connectivity list
                reg_node_ids = np.unique(self.Connectivity[clusters[i_cluster] - 1])
                _, _, reg_node_idx = np.intersect1d(reg_node_ids, region_lst[i_regions].Nodes, return_indices=True)
                reg_node_idx.sort()
                curr_reg_data.Nodes = region_lst[i_regions].Nodes[reg_node_idx]
                # add region to mesh data
                self.Regions.append(curr_reg_data)

                if result_data is not None:
                    result_info = result_data.ResultInfo
                    # loop over result quantities
                    for i_quantity in range(len(result_info)):
                        quant = str(result_info[i_quantity].Quantity)
                        # get the result data array
                        vprint("Processing quantity:", quant, verbose=self._Verbosity > v_def.debug)
                        curr_result_data_array = result_data.get_data_array(
                            region=region_lst[i_regions].Name, quantity=quant
                        )
                        # remove all data not contained in the region
                        if curr_result_data_array.ResType == cfs_result_type.ELEMENT:
                            el_indices = np.where(np.isin(full_region_elem_ids, curr_reg_data.Elements))[0]
                            new_result_data_array = CFSResultArray(curr_result_data_array[:, el_indices, :])
                        elif curr_result_data_array.ResType == cfs_result_type.NODE:
                            # remove all data not contained in the current cluster region..
                            node_indices = np.where(np.isin(full_region_node_ids, curr_reg_data.Nodes))[0]
                            new_result_data_array = CFSResultArray(curr_result_data_array[:, node_indices, :])
                        else:
                            raise NotImplementedError(
                                f"Processing of result type {curr_result_data_array.ResType} not implemented!"
                            )
                        new_result_data_array.MetaData = curr_result_data_array.MetaData
                        # assign the curr region name
                        new_result_data_array.Region = curr_reg_data.Name
                        # collect
                        new_result_data_arrays.append(new_result_data_array)
        for region in region_lst:
            # clear the old regions
            self.Regions.remove(region)
        if result_data is not None:
            # combine all results into one result data object
            all_new_result_data = CFSResultContainer(
                data=new_result_data_arrays,
                analysis_type=new_result_data_arrays[0].AnalysisType,
                verbosity=self._Verbosity,
            )
        else:
            all_new_result_data = None
        return all_new_result_data

    @staticmethod
    def _find_clusters(connectivity: np.ndarray, perform_sanity_check: bool = True, verbose=False) -> List[np.ndarray]:
        """
        Find clusters in the connectivity array to separate non-connected regions using a breadth-first search (BFS) algorithm.

        Parameters
        ----------
        connectivity : np.ndarray
            The connectivity array with shape (n, m), where n is the number of elements and m is the maximum number of nodes for each element.
        perform_sanity_check : bool, optional
            Perform a sanity check to ensure that no element id is contained in multiple regions. Default is ``True``.
        verbose: bool, optional
            Print progress information. Default is ``False``.

        Returns
        -------
        list of np.ndarray
            The clusters containing the element ids
        """

        def bfs(start, visited, adjacency_list) -> np.ndarray:
            queue = deque([start])
            cluster = []
            while queue:
                node = queue.popleft()
                if node not in visited:
                    visited.add(node)
                    cluster.append(node)
                    queue.extend(adjacency_list[node])
            return np.array(cluster)

        # Create adjacency list
        adjacency_list = defaultdict(list)
        for element_id, element in enumerate(
            progressbar(connectivity, prefix="Creating adjacency list: ", verbose=verbose)
        ):
            for i in range(len(element)):
                if element[i] <= 0:  # Skip padding elements and node number 0
                    continue
                for j in range(i + 1, len(element)):
                    if element[j] <= 0:  # Skip padding elements and node number 0
                        continue
                    adjacency_list[element[i]].append(element[j])
                    adjacency_list[element[j]].append(element[i])

        # Find clusters using BFS
        visited: set[int] = set()
        clusters = []
        for node in adjacency_list:
            if node not in visited:
                cluster = bfs(node, visited, adjacency_list)
                clusters.append(cluster)

        # Map nodes back to element ids
        element_clusters = []
        for cluster in progressbar(clusters, prefix="Map nodes to element ids: ", verbose=verbose):
            element_cluster = set()
            element_indices = np.arange(connectivity.shape[0]) + 1  # element ids start from 1
            for node in cluster:
                mask = np.any(connectivity == node, axis=1)
                element_cluster.update(element_indices[mask])
            element_clusters.append(np.array(list(element_cluster)))

        # Sanity check: Ensure no element id is contained in multiple regions
        if perform_sanity_check:
            element_id_set = set()
            for cluster in progressbar(element_clusters, prefix="Performing sanity check: ", verbose=verbose):
                for element_id in cluster:
                    if element_id in element_id_set:
                        raise ValueError(f"Clustering Error: Element ID {element_id} is contained in multiple regions")
                    element_id_set.add(element_id)

        vprint(f"{len(element_clusters)} clusters found in the connectivity list.", verbose=verbose)

        return element_clusters

    @staticmethod
    def from_coordinates_connectivity(
        coordinates: np.ndarray,
        connectivity: Optional[np.ndarray] = None,
        element_types: Optional[np.ndarray] = None,
        element_dimension: Optional[int] = None,
        region_name="Region",
        verbosity=v_def.release,
    ) -> CFSMeshData:
        """
        Generates data objects to create cfs mesh with one single region containing all elements. Detects element type from
        number of nodes. Therefore, all elements must have same dimension.

        Parameters
        ----------
        coordinates : numpy.ndarray, optional
            Coordinate array (NxD) of the whole mesh (N number of nodes, D space dimension)
        connectivity : numpy.ndarray, optional
            Connectivity array (NxM) of the whole mesh (N number of elements, M maximum number of nodes per element).
            Includes zero entries in case of different element types.
        element_types : numpy.ndarray, optional
            Array of element types (Nx1) of the whole mesh (N number of elements). Default is ``None`` in which case the
            element type is identified based on the number of nodes.
        element_dimension : int, optional
            Dimension of all elements. Default is ``None`` in which case the dimension is chosen based on the coordinates
            parameter
        region_name : str, optional
            Name of the region to be created. Default is "Region".
        verbosity : int, optional
            Verbosity level <=1000 ; see _v_def.py for predefined levels. Default is v_def.release.

        Returns
        -------
        pyCFS.data.io.CFSMeshData
            Mesh data structure.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     coordinates = f.Coordinates
        >>>     connectivity = f.Connectivity
        >>>     ElementTypes = f.ElementTypes
        >>>     region_data = f.MeshGroupsRegions
        >>> mesh = CFSMeshData.from_coordinates_connectivity(coordinates=coordinates, connectivity=connectivity,
        >>>                                           element_dimension=3, region_name='region')

        """
        if element_dimension is None:
            element_dimension = coordinates.shape[1]

        if connectivity is None:
            connectivity = np.reshape(np.arange(coordinates.shape[0]) + 1, (coordinates.shape[0], 1))
            type_array = np.array([cfs_element_type.POINT for _ in range(connectivity.shape[0])])

        else:
            connectivity = reshape_connectivity(connectivity)

            if element_types is None:
                type_link = {
                    0: {1: cfs_element_type.POINT},
                    1: {2: cfs_element_type.LINE2, 3: cfs_element_type.LINE3},
                    2: {
                        3: cfs_element_type.TRIA3,
                        6: cfs_element_type.TRIA6,
                        4: cfs_element_type.QUAD4,
                        8: cfs_element_type.QUAD8,
                        9: cfs_element_type.QUAD9,
                    },
                    3: {
                        4: cfs_element_type.TET4,
                        10: cfs_element_type.TET10,
                        8: cfs_element_type.HEXA8,
                        20: cfs_element_type.HEXA20,
                        27: cfs_element_type.HEXA27,
                        5: cfs_element_type.PYRA5,
                        13: cfs_element_type.PYRA13,
                        14: cfs_element_type.PYRA14,
                        6: cfs_element_type.WEDGE6,
                        15: cfs_element_type.WEDGE15,
                        18: cfs_element_type.WEDGE18,
                    },
                }

                type_array = apply_dict_vectorized(
                    data=(connectivity != 0).sum(axis=1),
                    dictionary=type_link[element_dimension],
                    val_no_key=cfs_element_type.UNDEF,
                )
            else:
                type_array = element_types

            connectivity, _ = renumber_connectivity(connectivity)

        reg_node = np.array([i + 1 for i in range(coordinates.shape[0])])
        reg_el = np.array([i + 1 for i in range(connectivity.shape[0])])
        reg_data = [
            CFSRegData(
                name=region_name,
                elements=reg_el,
                nodes=reg_node,
                dimension=np.max(apply_dict_vectorized(dictionary=cfs_types.cfs_element_dimension, data=type_array)),
                verbosity=verbosity,
            )
        ]

        mesh_data = CFSMeshData(
            coordinates=coordinates,
            connectivity=connectivity,
            types=type_array,
            regions=reg_data,
            verbosity=verbosity,
        )

        return mesh_data

    @staticmethod
    def struct_mesh(
        x_coord: np.ndarray,
        y_coord: np.ndarray,
        z_coord: Optional[np.ndarray] = None,
        region_name="Region",
        verbosity=v_def.release,
    ) -> CFSMeshData:
        """
        Create a structured 2D quadrilateral mesh from coordinate arrays.

        Parameters
        ----------
        x_coord : np.ndarray
            1D array of x-coordinates defining the grid points in the x-direction.
        y_coord : np.ndarray
            1D array of y-coordinates defining the grid points in the y-direction.
        z_coord : np.ndarray, optional
            1D array of z-coordinates defining the grid points in the z-direction.
            If provided, creates a 3D hexahedral mesh. Default is None.
        region_name : str, optional
            Name of the region to be created. Default is "Region".
        verbosity : int, optional
            Verbosity level <=1000 ; see _v_def.py for predefined levels. Default is v_def.release.

        Returns
        -------
        CFSMeshData
            Mesh data structure containing the structured 2D quadrilateral mesh with a single region.

        Examples
        --------
        >>> import numpy as np
        >>> from pyCFS.data.io import CFSMeshData
        >>> x_coords = np.array([0, 0.2, 0.7, 1.0])
        >>> y_coords = np.array([0, 0.3, 1.0])
        >>> mesh = CFSMeshData.struct_mesh(x_coords, y_coords, region_name="StructuredMesh")
        >>> z_coords = np.array([0, 0.5, 1.0])
        >>> mesh_3d = CFSMeshData.struct_mesh(x_coords, y_coords, z_coords, region_name="StructuredMesh3D")

        Notes
        -----
        - For 2D: The resulting mesh consists of QUAD4 elements arranged in a regular grid pattern.
          Total nodes: `len(x_coord) * len(y_coord)`, elements: `(len(x_coord) - 1) * (len(y_coord) - 1)`.
        - For 3D: The resulting mesh consists of HEXA8 elements arranged in a regular grid pattern.
          Total nodes: `len(x_coord) * len(y_coord) * len(z_coord)`,
          elements: `(len(x_coord) - 1) * (len(y_coord) - 1) * (len(z_coord) - 1)`.

        """

        if z_coord is None:
            # 2D mesh
            xv, yv = np.meshgrid(x_coord, y_coord)
            zv = np.zeros_like(xv)
            element_dimension = 2
            conn = connectivity_structured_grid(x_coord.size, y_coord.size)
        else:
            # 3D mesh
            yv, zv, xv = np.meshgrid(y_coord, z_coord, x_coord)
            element_dimension = 3
            conn = connectivity_structured_grid(x_coord.size, y_coord.size, z_coord.size)

        coord = np.stack(
            (
                xv.flatten(),
                yv.flatten(),
                zv.flatten(),
            ),
            axis=1,
        )

        return CFSMeshData.from_coordinates_connectivity(
            coordinates=coord,
            connectivity=conn,
            element_dimension=element_dimension,
            region_name=region_name,
            verbosity=verbosity,
        )


# Usability functions
def _compute_mesh_node_normal(node_idx: int, connectivity: np.ndarray, coordinates: np.ndarray) -> np.ndarray:
    """
    Helper function for CFSMeshData.get_surface_normals. Computes node surface normal for single node in mesh.

    Parameters
    ----------
    node_idx : int
    connectivity : np.ndarray
    coordinates : np.ndarray

    Returns
    -------
    np.ndarray

    """
    el_idx = np.argwhere(np.any(connectivity == node_idx + 1, axis=1)).flatten()
    node_close_ids = connectivity[el_idx, :]
    # Put center node id in 1st position
    node_neighbor_ids = np.empty_like(node_close_ids, dtype=int)
    for row in range(node_neighbor_ids.shape[0]):
        neighbor_n_idx = np.argwhere(node_close_ids[row, :] != node_idx + 1).flatten()
        # Ensure consistent node sequence (23,13->31,12), when common node is 2nd node in connectivity
        if (node_close_ids[row, :] == node_idx + 1)[1]:
            neighbor_n_idx[:2] = np.array([2, 0])
        node_neighbor_ids[row, 1:] = node_close_ids[row, neighbor_n_idx]
        node_neighbor_ids[row, 0] = node_idx + 1
    neighbor_coord = coordinates[node_neighbor_ids - 1, 0:3]
    return node_normal_2d(neighbor_coord)


def _compute_mesh_quality(
    idx: int, connectivity: np.ndarray, coordinates: np.ndarray, el_types: np.ndarray, metric: str
):
    """Helper function for CFSMeshData._get_mesh_quality. Computes element quality for single element in mesh"""
    element_connectivity = reshape_connectivity(connectivity[[idx], :])
    element_coordinates = coordinates[element_connectivity.flatten() - 1, :]
    return element_quality(element_coordinates, cfs_element_type(el_types[idx]), metric=metric)
