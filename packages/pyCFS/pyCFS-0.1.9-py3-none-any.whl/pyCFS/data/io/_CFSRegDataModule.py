import textwrap
from typing import Optional, Tuple

import numpy as np

from pyCFS.data._v_def import v_def
from pyCFS.data.util import vprint


class CFSRegData:
    """
    Data structure containing mesh region definition

    .. figure:: ../../../docs/source/resources/data_structures_CFSRegData.png

    Parameters
    ----------
    name : str, optional
        Group/Region name
    elements : numpy.ndarray, optional
        array of element ids (Nx1) of the group/region (N number of elements in the group/region).
    nodes : numpy.ndarray, optional
        array of node ids (Nx1) of the group/region (N number of nodes in the group/region).
    dimension : int, optional
        Group/Region dimension
    is_group : bool, optional
        flag indicating if the entity is a group.
    verbosity : int, optional
        Verbosity level <=1000 ; see _v_def.py for predefined levels. Default is v_def.release.

    Attributes
    ----------
    Name : str
        Group/Region name
    Elements : numpy.ndarray
        array of element ids, starting from 1, (Nx1) of the group/region (N number of elements in the group/region).
    Nodes : numpy.ndarray
        array of node ids, starting from 1, (Nx1) of the group/region (N number of nodes in the group/region).
    Dimension : int
        Group/Region dimension
    IsGroup : bool
        flag indicating if the entity is a group.

    Notes
    -----
    -  ``merge`` Merges region with other region removing duplicate node/element indices

    -  ``update_nodes_from_connectivity`` Update region nodes based on element ids.

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

    """

    def __init__(
        self,
        name: str,
        elements=np.empty(0),
        nodes=np.empty(0),
        dimension=-1,
        is_group=False,
        verbosity=v_def.release,
    ):
        self._Elements = np.empty(0)
        self._Nodes = np.empty(0)

        self.Name = name
        self.Elements = elements
        self.Nodes = nodes
        self.Dimension: int = dimension
        self.IsGroup: bool = is_group
        self.Verbosity = verbosity

    @property
    def Nodes(self):
        return self._Nodes

    @Nodes.setter
    def Nodes(self, nodes: np.ndarray):
        self._Nodes = np.array(nodes, dtype=np.uint32).flatten()  # type: ignore[assignment]

    @property
    def Elements(self):
        return self._Elements

    @Elements.setter
    def Elements(self, elements: np.ndarray):
        self._Elements = np.array(elements, dtype=np.int32).flatten()  # type: ignore[assignment]

    def __repr__(self) -> str:
        if self.IsGroup:
            reg_type = "Group"
        else:
            reg_type = "Region"
        return f"{reg_type}: {self.Name}"

    def __str__(self) -> str:
        if self.IsGroup:
            reg_type = "Group "
        else:
            reg_type = "Region"
        return textwrap.dedent(
            f"{reg_type}: {self.Name} ({self.Dimension}D, {self.Nodes.size} nodes, {self.Elements.size} elements)"
        )

    def __eq__(self, other: object | str):
        if not isinstance(other, CFSRegData):
            if type(other) is str:
                return self.Name == other
            else:
                raise NotImplementedError("Object comparison implemented for CFSRegData and str only!")
        return all(
            [
                self.Name == other.Name,
                np.array_equal(self.Elements, other.Elements),
                np.array_equal(self.Nodes, other.Nodes),
                self.Dimension == other.Dimension,
            ]
        )

    def __lt__(self, other):
        if not isinstance(other, CFSRegData):
            raise NotImplementedError("Object comparison implemented for CFSRegData and str only!")
        else:
            return self.Name < other.Name

    def __add__(self, other: "CFSRegData"):
        return_data, _, _ = self.merge(other)
        return return_data

    def merge(self, other: "CFSRegData"):
        """
        Merges region with other region removing duplicate node/element indices
        """
        # TODO add method to manipulate data after region merge
        if type(other) is not CFSRegData:
            raise NotImplementedError("Addition of CFSRegData only implemented with other object of type CFSRegData!")
        merged_region = CFSRegData(self.Name, verbosity=self.Verbosity)
        merged_region.Dimension = max(self.Dimension, other.Dimension)
        merged_region.IsGroup = self.IsGroup
        if other.IsGroup != self.IsGroup:
            p_dict = {False: "region", True: "group"}
            vprint(
                f"Merging {p_dict[self.IsGroup]} with {p_dict[other.IsGroup]} into {p_dict[merged_region.IsGroup]}",
                verbose=self.Verbosity > v_def.release,
            )
        merged_region.Nodes, idx_node = np.unique(np.append(self.Nodes, other.Nodes), return_index=True)
        merged_region.Elements, idx_elem = np.unique(np.append(self.Elements, other.Elements), return_index=True)

        return merged_region, idx_node, idx_elem

    def update_nodes_from_connectivity(
        self, connectivity: np.ndarray, elems: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray | None, np.ndarray | None]:
        """
        Update region nodes based on element ids.

        Parameters
        ----------
        connectivity: numpy.ndarray
        elems : numpy.ndarray, optional

        Returns
        -------
        node_idx : numpy.ndarray
            Updated node indices (starting from 0)
        elem_idx : numpy.ndarray
            Updated element indices (starting from 0)

        """
        if elems is None:
            elems = self.Elements

        reg_conn = connectivity[elems - 1, :]
        nodes = np.unique(reg_conn)
        # Remove zero entry
        nodes = np.delete(nodes, np.where(nodes == 0)[0])

        node_idx = None
        if np.all(np.isin(nodes, self.Nodes)):
            _, idx_intersect, node_idx = np.intersect1d(nodes, self.Nodes, return_indices=True)
            nodes = nodes[idx_intersect]

        elem_idx = None
        if np.all(np.isin(elems, self.Elements)):
            _, idx_intersect, elem_idx = np.intersect1d(elems, self.Elements, return_indices=True)
            elems = elems[idx_intersect]

        self.Nodes = nodes
        self.Elements = elems

        return node_idx, elem_idx
