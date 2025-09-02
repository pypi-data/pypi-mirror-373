import numpy as np

from netCDF4 import Dataset
from pyCFS.data import v_def
from pyCFS.data.io import CFSMeshData, CFSRegData
from pyCFS.data.io.cfs_types import cfs_element_type, cfs_element_dimension
from pyCFS.data.extras.exodus_to_cfs_element_types import exodus_to_cfs_elem_type


def reorder_nodes(connectivity: np.ndarray, elem_types_exodus: np.ndarray) -> np.ndarray:
    """
    Reorder the nodes in the connectivity array for element types that have different node ordering in cfs than exodus.

    Parameters
    ----------
    connectivity : np.ndarray
        The connectivity array where each row contains the node indices of a certain element in exodus ordering.
    elem_types_exodus : np.ndarray
        The array of exodus element types corresponding to each element in the connectivity array.

    Returns
    -------
    np.ndarray
        The reordered connectivity array with cfs node ordering.
    """
    # elements that have different node ordering in exodus and cfs
    reorder_map = {
        "WEDGE15": [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 9, 10, 11],
        "WEDGE18": [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 9, 10, 11, 15, 16, 17],
        "HEX20": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 19, 12, 13, 14, 15],
        "HEX27": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 19, 12, 13, 14, 15, 25, 24, 26, 23, 21, 22, 20],
    }

    reordered_connectivity = np.copy(connectivity)

    # reorder the connectivity for the elements in reorder_map
    for elem_type, reorder in reorder_map.items():
        matching_elem_types = elem_types_exodus == elem_type
        if np.any(matching_elem_types):
            reordered_connectivity[matching_elem_types, : len(reorder)] = connectivity[matching_elem_types][:, reorder]

    return reordered_connectivity


def get_connectivity_and_elem_types(
    variables: dict, nr_elems: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Extract and process connectivity and element type information from Exodus data.

    Parameters
    ----------
    variables : dict
        A dictionary containing the variables from the Exodus file, including connectivity and element type data.
    nr_elems : int
        The total number of elements in the mesh.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        A tuple containing:
        - connectivity_exodus : np.ndarray
            The connectivity array in Exodus node ordering.
        - elem_types_exodus : np.ndarray
            The Exodus element types corresponding to the Exodus connectivity.
        - connectivity_cfs : np.ndarray
            The connectivity array reordered to match CFS node ordering.
        - elem_types_cfs : np.ndarray
            The element types converted to CFS element types.
    """
    # extract connectivity variables
    connectivities = [variables[var] for var in variables if "connect" in var]

    # determine the maximum number of nodes per element
    max_nodes_per_elem = max(var.shape[1] for var in connectivities)

    # initialize the connectivity array
    connectivity_exodus = np.zeros((nr_elems, max_nodes_per_elem), dtype=np.int64)

    idx = 0
    elem_types_exodus_list = []

    # iterate over all connectivity blocks
    for conn in connectivities:
        nr_elems_in_block, nr_nodes_per_elem = conn.shape

        # fill the connectivity array with the current block's data
        connectivity_exodus[idx : idx + nr_elems_in_block, :nr_nodes_per_elem] = conn[:]
        idx += nr_elems_in_block

        # append the element type for each element in the block
        elem_types_exodus_list.extend([conn.elem_type] * nr_elems_in_block)

    # convert exodus element types to numpy array
    elem_types_exodus = np.array(elem_types_exodus_list)

    # convert exodus connectivity to cfs connectivity (node reordering)
    connectivity_cfs = reorder_nodes(connectivity_exodus, elem_types_exodus)

    # convert exodus element types to cfs element types
    elem_types_cfs = exodus_to_cfs_elem_type(elem_types_exodus)

    return connectivity_exodus, elem_types_exodus, connectivity_cfs, elem_types_cfs


def get_region_names(variables: dict, region_type: str, default_name: str) -> list[str]:
    """
    Extract and decode region names from Exodus file variables.

    Parameters
    ----------
    variables : dict
        A dictionary containing the variables from the Exodus file.
    region_type : str
        The type of region to extract ("ns" for nodesets, "eb" for element blocks, "ss" for sidesets).
    default_name : str
        The default name to assign to regions if no valid name is found.

    Returns
    -------
    list[str]
        A list of region names, with default names assigned where necessary.
    """
    region_names = variables[f"{region_type}_names"][:]
    decoded_region_names = []

    for region_idx, region_id in enumerate(variables[f"{region_type}_prop1"]):
        # get region name
        valid_name = region_names[region_idx].compressed()  # extract unmasked values
        if valid_name.size > 0:
            name = b"".join(valid_name).decode("utf-8")  # convert bytes to joint string
        else:
            name = f"{default_name}{region_id}"  # default name
        decoded_region_names.append(name)
    return decoded_region_names


def append_nodesets_to_regions(variables: dict, verbosity: int, regions: list[CFSRegData]) -> None:
    """
    Append nodesets from the Exodus file to the list of CFS regions.

    Parameters
    ----------
    variables : dict
        A dictionary containing the variables from the Exodus file, including nodeset data.
    verbosity : int
        The verbosity level.
    regions : list[CFSRegData]
        A list of CFSRegData objects representing the regions in the mesh.

    Returns
    -------
    None
        This function modifies the `regions` list in place by appending nodeset regions.
    """
    nodeset_names = get_region_names(variables, "ns", "nodeset")

    for nodeset_id, name in zip(variables["ns_prop1"], nodeset_names):
        # get nodes of the nodeset
        node_ids = variables[f"node_ns{nodeset_id}"]

        # turn nodeset into CFSRegion
        region = CFSRegData(
            name=name,
            nodes=np.array(node_ids),
            elements=np.array([]),  # nodesets don't have elements
            dimension=0,
            is_group=True,
            verbosity=verbosity,
        )
        regions.append(region)


def append_element_blocks_to_regions(
    variables: dict, regions: list[CFSRegData], elem_types_cfs: np.ndarray, verbosity: int
) -> None:
    """
    Append element blocks from the Exodus file to the list of CFS regions.

    Parameters
    ----------
    variables : dict
        A dictionary containing the variables from the Exodus file, including element block data.
    regions : list[CFSRegData]
        A list of CFSRegData objects representing the regions in the mesh.
    elem_types_cfs : np.ndarray
        An array of element types in CFS format.
    verbosity : int
        The verbosity level.

    Returns
    -------
    None
        This function modifies the `regions` list in place by appending element block regions.
    """
    block_names = get_region_names(variables, "eb", "element_block")

    # extract connectivity variables
    connectivities = [variables[var] for var in variables if "connect" in var]

    idx = 0
    # iterate over element block connectivities
    for conn, name in zip(connectivities, block_names):
        nr_elems_in_block, nr_nodes_per_elem = conn.shape
        node_ids = np.unique(conn[:])
        elem_ids = np.arange(idx + 1, idx + 1 + nr_elems_in_block)
        dimension = cfs_element_dimension[elem_types_cfs[idx]]
        idx += nr_elems_in_block

        # turn sideset into CFSRegion
        region = CFSRegData(
            name=name,
            nodes=np.array(node_ids),
            elements=elem_ids,
            dimension=dimension,
            is_group=False,
            verbosity=verbosity,
        )
        regions.append(region)


def get_nodes_for_side(
    current_elem_connectivity_exodus: np.ndarray, side: int, current_elem_type_exodus: str
) -> tuple[list[int], cfs_element_type]:
    """
    Get the node ids and element type for a specific side of an element.

    The association between element types, their sides, and the corresponding node IDs is based on the Exodus II documentation
    (https://sandialabs.github.io/seacas-docs/exodusII-new.pdf, page 31, Table 4.2). Only those Exodus element types
    that have a corresponding CFS element type are included.

    Parameters
    ----------
    current_elem_connectivity_exodus : np.ndarray
        The connectivity of the element in Exodus node ordering.
    side : int
        The side number of the element for which the nodes are to be retrieved.
    current_elem_type_exodus : str
        The Exodus element type of the element.

    Returns
    -------
    tuple[list[int], cfs_element_type]
        A tuple containing:
        - A list of node IDs corresponding to the specified side of the element.
        - The CFS element type of the specified side.

    Raises
    ------
    ValueError
        If the element type is not defined in the side mapping or if the side number is invalid for the given element type.
    """
    side_mapping = {
        # 2D elements
        "QUAD": {
            1: ([0, 1], cfs_element_type.LINE2),
            2: ([1, 2], cfs_element_type.LINE2),
            3: ([2, 3], cfs_element_type.LINE2),
            4: ([3, 0], cfs_element_type.LINE2),
        },
        "QUAD4": {
            1: ([0, 1], cfs_element_type.LINE2),
            2: ([1, 2], cfs_element_type.LINE2),
            3: ([2, 3], cfs_element_type.LINE2),
            4: ([3, 0], cfs_element_type.LINE2),
        },
        "QUAD8": {
            1: ([0, 1, 4], cfs_element_type.LINE3),
            2: ([1, 2, 5], cfs_element_type.LINE3),
            3: ([2, 3, 6], cfs_element_type.LINE3),
            4: ([3, 0, 7], cfs_element_type.LINE3),
        },
        "QUAD9": {
            1: ([0, 1, 4], cfs_element_type.LINE3),
            2: ([1, 2, 5], cfs_element_type.LINE3),
            3: ([2, 3, 6], cfs_element_type.LINE3),
            4: ([3, 0, 7], cfs_element_type.LINE3),
        },
        "TRI": {
            1: ([0, 1], cfs_element_type.LINE2),
            2: ([1, 2], cfs_element_type.LINE2),
            3: ([2, 0], cfs_element_type.LINE2),
        },
        "TRI3": {
            1: ([0, 1], cfs_element_type.LINE2),
            2: ([1, 2], cfs_element_type.LINE2),
            3: ([2, 0], cfs_element_type.LINE2),
        },
        "TRI6": {
            1: ([0, 1, 3], cfs_element_type.LINE3),
            2: ([1, 2, 4], cfs_element_type.LINE3),
            3: ([2, 0, 5], cfs_element_type.LINE3),
        },
        # 3D elements – tetrahedra
        "TETRA": {
            1: ([0, 1, 3], cfs_element_type.TRIA3),
            2: ([1, 2, 3], cfs_element_type.TRIA3),
            3: ([0, 3, 2], cfs_element_type.TRIA3),
            4: ([0, 2, 1], cfs_element_type.TRIA3),
        },
        "TETRA4": {
            1: ([0, 1, 3], cfs_element_type.TRIA3),
            2: ([1, 2, 3], cfs_element_type.TRIA3),
            3: ([0, 3, 2], cfs_element_type.TRIA3),
            4: ([0, 2, 1], cfs_element_type.TRIA3),
        },
        "TETRA10": {
            1: ([0, 1, 3, 4, 8, 7], cfs_element_type.TRIA6),
            2: ([1, 2, 3, 5, 9, 8], cfs_element_type.TRIA6),
            3: ([0, 3, 2, 7, 9, 6], cfs_element_type.TRIA6),
            4: ([0, 2, 1, 6, 5, 4], cfs_element_type.TRIA6),
        },
        # 3D elements - hexahedra
        "HEX": {
            1: ([0, 1, 5, 4], cfs_element_type.QUAD4),
            2: ([1, 2, 6, 5], cfs_element_type.QUAD4),
            3: ([2, 3, 7, 6], cfs_element_type.QUAD4),
            4: ([0, 4, 7, 3], cfs_element_type.QUAD4),
            5: ([0, 3, 2, 1], cfs_element_type.QUAD4),
            6: ([4, 5, 6, 7], cfs_element_type.QUAD4),
        },
        "HEX8": {
            1: ([0, 1, 5, 4], cfs_element_type.QUAD4),
            2: ([1, 2, 6, 5], cfs_element_type.QUAD4),
            3: ([2, 3, 7, 6], cfs_element_type.QUAD4),
            4: ([0, 4, 7, 3], cfs_element_type.QUAD4),
            5: ([0, 3, 2, 1], cfs_element_type.QUAD4),
            6: ([4, 5, 6, 7], cfs_element_type.QUAD4),
        },
        "HEX20": {
            1: ([0, 1, 5, 4, 8, 13, 16, 12], cfs_element_type.QUAD8),
            2: ([1, 2, 6, 5, 9, 14, 17, 13], cfs_element_type.QUAD8),
            3: ([2, 3, 7, 6, 10, 15, 18, 14], cfs_element_type.QUAD8),
            4: ([0, 4, 7, 3, 12, 19, 15, 11], cfs_element_type.QUAD8),
            5: ([0, 3, 2, 1, 11, 10, 9, 8], cfs_element_type.QUAD8),
            6: ([4, 5, 6, 7, 16, 17, 18, 19], cfs_element_type.QUAD8),
        },
        "HEX27": {
            1: ([0, 1, 5, 4, 8, 13, 16, 12, 25], cfs_element_type.QUAD9),
            2: ([1, 2, 6, 5, 9, 14, 17, 13, 24], cfs_element_type.QUAD9),
            3: ([2, 3, 7, 6, 10, 15, 18, 14, 26], cfs_element_type.QUAD9),
            4: ([0, 4, 7, 3, 12, 19, 15, 11, 23], cfs_element_type.QUAD9),
            5: ([0, 3, 2, 1, 11, 10, 9, 8, 21], cfs_element_type.QUAD9),
            6: ([4, 5, 6, 7, 16, 17, 18, 19, 22], cfs_element_type.QUAD9),
        },
        # 3D elements - pyramids
        "PYRAMID": {
            1: ([0, 1, 4], cfs_element_type.TRIA3),
            2: ([1, 2, 4], cfs_element_type.TRIA3),
            3: ([2, 3, 4], cfs_element_type.TRIA3),
            4: ([3, 0, 4], cfs_element_type.TRIA3),
            5: ([0, 3, 2, 1], cfs_element_type.QUAD4),
        },
        "PYRAMID5": {
            1: ([0, 1, 4], cfs_element_type.TRIA3),
            2: ([1, 2, 4], cfs_element_type.TRIA3),
            3: ([2, 3, 4], cfs_element_type.TRIA3),
            4: ([3, 0, 4], cfs_element_type.TRIA3),
            5: ([0, 3, 2, 1], cfs_element_type.QUAD4),
        },
        "PYRAMID13": {
            1: ([0, 1, 4, 5, 10, 9], cfs_element_type.TRIA6),
            2: ([1, 2, 4, 6, 11, 10], cfs_element_type.TRIA6),
            3: ([2, 3, 4, 7, 12, 11], cfs_element_type.TRIA6),
            4: ([3, 0, 4, 8, 9, 12], cfs_element_type.TRIA6),
            5: ([0, 3, 2, 1, 8, 7, 6, 5], cfs_element_type.QUAD8),
        },
        "PYRAMID14": {
            1: ([0, 1, 4, 5, 10, 9], cfs_element_type.TRIA6),
            2: ([1, 2, 4, 6, 11, 10], cfs_element_type.TRIA6),
            3: ([2, 3, 4, 7, 12, 11], cfs_element_type.TRIA6),
            4: ([3, 0, 4, 8, 9, 12], cfs_element_type.TRIA6),
            5: ([0, 3, 2, 1, 8, 7, 6, 5, 13], cfs_element_type.QUAD9),
        },
        # 3D elements - wedges
        "WEDGE": {
            1: ([0, 1, 4, 3], cfs_element_type.QUAD4),
            2: ([1, 2, 5, 4], cfs_element_type.QUAD4),
            3: ([0, 3, 5, 2], cfs_element_type.QUAD4),
            4: ([0, 2, 1], cfs_element_type.TRIA3),
            5: ([3, 4, 5], cfs_element_type.TRIA3),
        },
        "WEDGE6": {
            1: ([0, 1, 4, 3], cfs_element_type.QUAD4),
            2: ([1, 2, 5, 4], cfs_element_type.QUAD4),
            3: ([0, 3, 5, 2], cfs_element_type.QUAD4),
            4: ([0, 2, 1], cfs_element_type.TRIA3),
            5: ([3, 4, 5], cfs_element_type.TRIA3),
        },
        "WEDGE15": {
            1: ([0, 1, 4, 3, 6, 10, 12, 9], cfs_element_type.QUAD8),
            2: ([1, 2, 5, 4, 7, 11, 13, 10], cfs_element_type.QUAD8),
            3: ([0, 3, 5, 2, 9, 14, 11, 8], cfs_element_type.QUAD8),
            4: ([0, 2, 1, 8, 7, 6], cfs_element_type.TRIA6),
            5: ([3, 4, 5, 12, 13, 14], cfs_element_type.TRIA6),
        },
    }

    if current_elem_type_exodus not in side_mapping:
        raise ValueError(f"Sideset node ordering is not defined for element type {current_elem_type_exodus}.")
    if side not in side_mapping[current_elem_type_exodus]:
        raise ValueError(f"Side number {side} does not exist for element type {current_elem_type_exodus}.")

    # get the node IDs according to the mapping
    side_node_ids = [
        int(current_elem_connectivity_exodus[node_idx]) for node_idx in side_mapping[current_elem_type_exodus][side][0]
    ]
    side_elem_type = side_mapping[current_elem_type_exodus][side][1]

    return side_node_ids, side_elem_type


def append_sidesets_to_regions(
    variables: dict,
    elem_types_exodus: np.ndarray,
    elem_types_cfs: np.ndarray,
    connectivity_exodus: np.ndarray,
    connectivity_cfs: np.ndarray,
    verbosity: int,
    regions: list[CFSRegData],
):
    """
    Append sidesets from the Exodus file to the list of CFS regions and expand connectivity and element types.


    This function updates the `connectivity_cfs` and `elem_types_cfs` arrays by appending the connectivity and element
    types of the sides of each sideset. Additionally, it creates and appends new regions for the sidesets to the
    `regions` list.

    Parameters
    ----------
    variables : dict
        A dictionary containing the variables from the Exodus file, including sideset data.
    elem_types_exodus : np.ndarray
        The array of element types in Exodus format.
    elem_types_cfs : np.ndarray
        The array of element types in CFS format.
    connectivity_exodus : np.ndarray
        The connectivity array in Exodus node ordering.
    connectivity_cfs : np.ndarray
        The connectivity array in CFS node ordering.
    verbosity : int
        The verbosity level.
    regions : list[CFSRegData]
        A list of CFSRegData objects representing the regions in the mesh.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        A tuple containing:
        - Updated `connectivity_cfs` : np.ndarray
            The updated connectivity array in CFS node ordering, with the connectivity of the sides of the sidesets appended.
        - Updated `elem_types_cfs` : np.ndarray
            The updated array of element types in CFS format, with the element types of the sides of the sidesets appended.

    Raises
    ------
    ValueError
        If the sideset node ordering is not defined for an element type or if the side number is invalid.
    """
    sideset_names = get_region_names(variables, "ss", "sideset")

    # iterate over sidesets
    for sideset_id, name in zip(variables["ss_prop1"], sideset_names):

        # get sideset data
        sideset_elem_ids = variables[f"elem_ss{sideset_id}"][:]
        sideset_side_ids = variables[f"side_ss{sideset_id}"][:]

        sideset_node_ids = []
        sideset_elem_types = set()

        original_connectivity_length = len(connectivity_cfs)

        # iterate over elements and sides of the current sideset
        for elem, side in zip(sideset_elem_ids, sideset_side_ids):
            current_elem_type_exodus = str(elem_types_exodus[elem - 1])

            # get the nodes of the element
            current_elem_connectivity_exodus = connectivity_exodus[elem - 1]

            # get the nodes of the side
            side_node_ids, side_elem_type = get_nodes_for_side(
                current_elem_connectivity_exodus, side, current_elem_type_exodus
            )
            sideset_node_ids.extend(side_node_ids)
            sideset_elem_types.add(side_elem_type)

            # add side elements and their connectivity to global element types and connectivity
            zero_padded_side_node_ids = np.pad(
                side_node_ids, (0, connectivity_cfs.shape[1] - len(side_node_ids)), mode="constant"
            )
            connectivity_cfs = np.append(connectivity_cfs, [zero_padded_side_node_ids], axis=0)
            elem_types_cfs = np.append(elem_types_cfs, side_elem_type)

        # remove duplicate nodes and reshape
        unique_sideset_node_ids = np.unique(sideset_node_ids).reshape(-1, 1)

        # get highest dimension of sideset
        dimension = max(cfs_element_dimension[elem_type] for elem_type in sideset_elem_types)

        # get element ids of the sides of the sideset
        sideset_side_elem_ids = np.arange(
            original_connectivity_length + 1, original_connectivity_length + len(sideset_elem_ids) + 1
        )

        # turn sideset into CFSRegion
        region = CFSRegData(
            name=name,
            nodes=np.array(unique_sideset_node_ids),
            elements=sideset_side_elem_ids,
            dimension=dimension,
            is_group=False,
            verbosity=verbosity,
        )
        regions.append(region)

    return connectivity_cfs, elem_types_cfs


def read_exodus(filepath: str, verbosity: int = v_def.release) -> CFSMeshData:
    """
    Read an Exodus file and convert its data into a CFSMeshData object.

    Parameters
    ----------
    filepath : str
        Path to the Exodus file to be read.
    verbosity : int, optional
        Verbosity level <=1000 ; see _v_def.py for predefined levels. Default is v_def.release.

    Returns
    -------
    CFSMeshData
        A CFSMeshData object containing the mesh data extracted from the Exodus file.

    Examples
    --------
    >>> from pyCFS.data.extras.exodus_io import read_exodus
    >>> cfs_mesh = read_exodus(filepath="exodus_mesh.e")

    References
    -----
    .. Usage Tutorial:
           https://opencfs.gitlab.io/pycfs/examples/data_tutorial/exodus_io_tutorial/exodus_io_tutorial.html

    """
    with Dataset(filepath, "r") as dataset:
        # extract variables and dimensions from the Exodus dataset
        variables = dataset.variables
        dimensions = dataset.dimensions
        nr_elems = dimensions["num_elem"].size

        # get coordinates
        x_coord = variables["coordx"][:]
        y_coord = variables["coordy"][:]
        z_coord = variables.get("coordz", np.zeros_like(x_coord))[:]  # handles 2D and 3D coordinates
        coordinates = np.vstack((x_coord, y_coord, z_coord)).T

        # get connectivity and element type arrays
        connectivity_exodus, elem_types_exodus, connectivity_cfs, elem_types_cfs = get_connectivity_and_elem_types(
            variables, nr_elems
        )

        # get regions (nodesets, sidesets and element blocks)
        regions: list[CFSRegData] = []

        # add nodesets to regions
        if "ns_prop1" in variables.keys():
            append_nodesets_to_regions(variables, verbosity, regions)

        # add element blocks to regions
        append_element_blocks_to_regions(variables, regions, elem_types_cfs, verbosity)

        # add sidesets to regions and add side elements and their connectivity to global element types and connectivity
        if "ss_prop1" in variables:
            connectivity_cfs, elem_types_cfs = append_sidesets_to_regions(
                variables, elem_types_exodus, elem_types_cfs, connectivity_exodus, connectivity_cfs, verbosity, regions
            )

        # create CFS mesh data object
        mesh = CFSMeshData(
            coordinates=coordinates,
            connectivity=connectivity_cfs,
            types=elem_types_cfs,
            regions=regions,
            verbosity=verbosity,
        )

        # create point elements for nodesets
        mesh.check_add_point_elements()

        return mesh
