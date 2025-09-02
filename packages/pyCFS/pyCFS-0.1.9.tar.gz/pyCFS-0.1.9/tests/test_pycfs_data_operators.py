import importlib.util

import pytest
import numpy as np

from pyCFS.data import io, v_def
from pyCFS.data.io import cfs_types
from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
from pyCFS.data.operators import interpolators, transformation, sngr, modal_analysis, derivatives
from pyCFS.data.operators._rbf_interpolation import (
    jacobian_rbf_local,
    jacobian_rbf,
    interpolation_rbf_local,
    interpolation_rbf,
)
from pyCFS.data.operators.interpolators import interpolate_projection_based
from pyCFS.data.util import TimeRecord
from .pycfs_data_fixtures import dummy_CFSMeshData_obj


def test_transformation_fit_coordinates(working_directory="."):
    from pyCFS.data.operators.transformation import fit_coordinates

    filename_src = f"{working_directory}/tests/data/operators/transformation/fit_geometry/fit_geometry_src.cfs"
    filename_target = f"{working_directory}/tests/data/operators/transformation/fit_geometry/fit_geometry_target.cfs"
    filename_out = f"{working_directory}/tests/data_tmp/operators/transformation/fit_geometry/fit_geometry_out.cfs"

    regions_target = ["HULL_TARGET"]
    regions_fit = ["surface"]

    transform_param_init = [0.02, 0.1, 0.07, 0, 150, 0]

    while len(transform_param_init) < len(regions_fit) * 6:
        transform_param_init.extend([0, 0, 0, 0, 0, 0])

    fit_coordinates(
        filename_src,
        filename_out,
        filename_target,
        regions_target=regions_target,
        regions_fit=regions_fit,
        transform_param_init=transform_param_init,
        init_angle_degree=True,
    )


def test_transformation_transform_mesh_only(working_directory="."):
    from pyCFS.data.operators.transformation import transform_mesh

    filename_src = (
        f"{working_directory}/tests/data/operators/transformation/transform_mesh_only/transform_mesh_only_src.cfs"
    )
    filename_out = (
        f"{working_directory}/tests/data_tmp/operators/transformation/transform_mesh_only/transform_mesh_only_out.cfs"
    )

    transform_regions = ["domain2"]
    translate_coords = (0.05, 0.1, 0.2)
    rotate_angles = (45, 35, 75)
    rotate_origin = (1, 1.5, 1.9)

    transform_mesh(
        filename_src,
        filename_out,
        translate_coords=translate_coords,
        rotate_angles=rotate_angles,
        rotate_origin=rotate_origin,
        regions=transform_regions,
        transform_results=False,
    )


def test_transformation_transform_mesh_with_results(working_directory="."):
    from pyCFS.data.operators.transformation import transform_mesh

    filename_src = f"{working_directory}/tests/data/operators/transformation/transform_mesh_with_results/transform_mesh_with_results_src.cfs"
    filename_out = f"{working_directory}/tests/data_tmp/operators/transformation/transform_mesh_with_results/transform_mesh_with_results_out.cfs"

    transform_regions = ["domain2"]
    translate_coords = (0.05, 0.1, 0.2)
    rotate_angles = (45, 35, 75)
    rotate_origin = (0, 0, 0)

    transform_mesh(
        filename_src,
        filename_out,
        translate_coords=translate_coords,
        rotate_angles=rotate_angles,
        rotate_origin=rotate_origin,
        regions=transform_regions,
        transform_results=True,
    )


def test_interpolators_cell2node_node2cell(working_directory="."):
    file_in = f"{working_directory}/tests/data/operators/interpolators/interpolators.cfs"
    file_out = f"{working_directory}/tests/data_tmp/operators/interpolators/cell2node_node2cell.cfs"

    quantity = "quantity"
    reg_name = "Vol"
    with io.CFSReader(file_in) as h5r:
        mesh_data = h5r.MeshData
        result_data_read = h5r.ResultMeshData

        reg_coord = h5r.get_mesh_region_coordinates(reg_name)
        reg_conn = h5r.get_mesh_region_connectivity(reg_name)

    m_interp = interpolators.interpolation_matrix_node_to_cell(reg_coord, reg_conn)
    r_array = result_data_read.get_data_array(quantity, reg_name, cfs_result_type.NODE)
    r_array_N2C = interpolators.apply_interpolation(
        result_array=r_array,
        interpolation_matrix=m_interp,
        restype_out=cfs_result_type.ELEMENT,
        quantity_out="quantity_N2C",
    )

    m_interp = interpolators.interpolation_matrix_cell_to_node(reg_coord, reg_conn).tocsr()

    r_array_C2N = interpolators.apply_interpolation(
        result_array=r_array_N2C,
        interpolation_matrix=m_interp,
        restype_out=cfs_result_type.NODE,
        quantity_out="quantity_C2N",
    )

    result_data_write = io.CFSResultContainer(data=[r_array_C2N, r_array_N2C])

    with io.CFSWriter(file_out) as h5w:
        h5w.create_file(mesh_data, result_data_write)


def test_interpolators_nearest_neighbor_elem(working_directory="."):
    # TODO Unit test for Nearest Neighbor interpolation
    # NN Elem -> Elem example

    source_file = f"{working_directory}/tests/data/operators/interpolators/nn_elem.cfs"
    interpolated_sim = f"{working_directory}/tests/data_tmp/operators/interpolators/nn_elem_interp.cfs"

    quantity = "acouIntensity"
    region_src_target_dict = {"internal": ["internal"]}

    with io.CFSReader(source_file) as h5r:
        result_data_src = h5r.ResultMeshData
        mesh_data_src = h5r.MeshData

    with io.CFSReader(source_file) as h5r:
        mesh_data = h5r.MeshData

    result_array_lst_nn = []
    for src_region_name in region_src_target_dict:
        source_coord = mesh_data_src.get_region_centroids(src_region_name)

        target_coord = []
        for reg_name in region_src_target_dict[src_region_name]:
            target_coord.append(mesh_data.get_region_centroids(reg_name))

        for i, reg_name in enumerate(region_src_target_dict[src_region_name]):
            m_interp = interpolators.interpolation_matrix_nearest_neighbor(
                source_coord,
                target_coord[i],
                num_neighbors=1,
                interpolation_exp=1,
                max_distance=1e-6,
                formulation="forward",
            )
            m_interp = interpolators.interpolation_matrix_nearest_neighbor(
                source_coord, target_coord[i], num_neighbors=1, max_distance=1e-6, formulation="backward"
            )
            result_array_src = result_data_src.get_data_array(
                quantity=quantity, region=src_region_name, restype=cfs_result_type.ELEMENT
            )
            result_array_lst_nn.append(
                interpolators.apply_interpolation(
                    result_array=result_array_src,
                    interpolation_matrix=m_interp,
                    region_out=reg_name,
                    restype_out=cfs_result_type.ELEMENT,
                )
            )

    result_data_disp = io.CFSResultContainer(data=result_array_lst_nn, analysis_type=cfs_analysis_type.TRANSIENT)

    with io.CFSWriter(interpolated_sim) as h5w:
        h5w.create_file(mesh_data, result_data_disp)


def test_interpolators_nearest_neighbor_node(working_directory="."):
    # NN Example
    source_file = f"{working_directory}/tests/data/operators/interpolators/nn_source.cfs"
    target_file = f"{working_directory}/tests/data/operators/interpolators/nn_target.cfs"
    out_file = f"{working_directory}/tests/data_tmp/operators/interpolators/nn_interpolated.cfs"

    quantity = "function"
    reg_name_source = "S_source"
    reg_name_target = ["S_target"]

    with io.CFSReader(source_file) as h5r:
        result_data_src = h5r.ResultMeshData
        source_coord = h5r.get_mesh_region_coordinates(reg_name_source)

    with io.CFSReader(target_file) as h5r:
        mesh_data = h5r.MeshData
        target_coord = []
        for reg_name in reg_name_target:
            target_coord.append(h5r.get_mesh_region_coordinates(reg_name))

    result_array_lst_nn = []
    result_array_lst_nn_inverse = []
    for i, reg_name in enumerate(reg_name_target):
        m_interp = interpolators.interpolation_matrix_nearest_neighbor(
            source_coord, target_coord[i], num_neighbors=10, interpolation_exp=2
        )
        m_interp_inverse = interpolators.interpolation_matrix_nearest_neighbor(
            source_coord, target_coord[i], num_neighbors=10, interpolation_exp=2, formulation="backward"
        )
        result_array_src = result_data_src.get_data_array(
            quantity=quantity, region=reg_name_source, restype=cfs_result_type.NODE
        )
        result_array_lst_nn.append(
            interpolators.apply_interpolation(
                result_array=result_array_src,
                interpolation_matrix=m_interp,
                quantity_out=f"{quantity}_interpolated",
                region_out=reg_name,
                restype_out=cfs_result_type.NODE,
            )
        )
        result_array_lst_nn_inverse.append(
            interpolators.apply_interpolation(
                result_array=result_array_src,
                interpolation_matrix=m_interp_inverse,
                quantity_out=f"{quantity}_interpolated_inverse",
                region_out=reg_name,
                restype_out=cfs_result_type.NODE,
            )
        )

    result_data_write = io.CFSResultContainer(
        data=result_array_lst_nn + result_array_lst_nn_inverse, analysis_type=cfs_analysis_type.TRANSIENT
    )

    with io.CFSWriter(out_file) as h5w:
        h5w.create_file(mesh=mesh_data, result=result_data_write)


def test_interpolators_interpolate_nearest_neighbor(working_directory="."):
    source_file = f"{working_directory}/tests/data/operators/interpolators/nn_source.cfs"
    target_file = f"{working_directory}/tests/data/operators/interpolators/nn_target.cfs"
    out_file = f"{working_directory}/tests/data_tmp/operators/interpolators/nn_interpolated.cfs"

    quantities = ["function"]

    region_src_target = [
        {"source": ["S_source"], "target": ["S_target"]},
    ]

    with io.CFSReader(source_file) as h5r:
        src_mesh = h5r.MeshData
        src_data = h5r.ResultMeshData
    with io.CFSReader(target_file) as h5r:
        target_mesh = h5r.MeshData

    result_data_write = interpolators.interpolate_nearest_neighbor(
        mesh_src=src_mesh,
        result_src=src_data,
        mesh_target=target_mesh,
        region_src_target=region_src_target,
        quantity_names=quantities,
        element_centroid_data_target=True,
    )

    with io.CFSReader(target_file) as h5r:
        mesh_data = h5r.MeshData

    with io.CFSWriter(out_file) as h5w:
        h5w.create_file(mesh=mesh_data, result=result_data_write)


def test_interpolators_interpolate_distinct_nodes_nearest_neighbor(working_directory="."):
    """
    Interpolates nodes on a straight line in the center of a plate.
    """
    source_file = f"{working_directory}/tests/data/operators/interpolators/nn_source.cfs"
    ref_file = f"{working_directory}/tests/data/operators/interpolators/nn_distinct_interpolated.cfs"
    quantity = "function"
    regions = ["S_source"]
    interpolate_node_ids = list(np.arange(start=211, stop=232, step=1))
    # load source file
    with io.CFSReader(source_file) as h5r:
        src_mesh = h5r.MeshData
        src_data = h5r.ResultMeshData
    # interpolate
    result_data_write = interpolators.interpolate_distinct_nodes(
        mesh=src_mesh,
        result=src_data,
        quantity_name=quantity,
        interpolate_node_ids=interpolate_node_ids,
        regions=regions,
        num_neighbors=400,
        interpolation_exp=0.0001,
        max_distance=None,
    )
    # load reference file and compare
    with io.CFSReader(ref_file) as h5r:
        ref_data = h5r.ResultMeshData
    np.testing.assert_array_almost_equal(ref_data.Data, result_data_write.Data, decimal=15)


def test_interpolators_interpolation_rbf(interpolation_tolerance=1e-3, seed=42):
    rng = np.random.default_rng(seed)

    coord = rng.random((500, 3))
    coord_trg = rng.random((20, 3))

    fun_3d = np.sin(coord[:, 0]) * np.cos(coord[:, 1]) * np.exp(coord[:, 2])
    fun_3d = io.CFSResultArray(
        fun_3d,
        quantity="function",
        region="src",
        step_values=np.array([1.0]),
        res_type=cfs_types.cfs_result_type.NODE,
        analysis_type=cfs_types.cfs_analysis_type.STATIC,
    )

    with TimeRecord(verbose=False) as rec:
        fun_3d_rbf = interpolation_rbf(
            coord, coord_trg, fun_3d[:, None], kernel="gaussian", epsilon=2.0, smoothing=1e-10
        )
        print(f"RBF interpolation: {rec.TimeElapsed:.2f} seconds")

    fun_3d_ref = np.sin(coord_trg[:, 0]) * np.cos(coord_trg[:, 1]) * np.exp(coord_trg[:, 2])

    print(f"Interpolated Function Error: {np.linalg.norm(fun_3d_rbf[:,0] - fun_3d_ref)/np.linalg.norm(fun_3d_ref):.2g}")

    assert (np.linalg.norm(fun_3d_rbf[:, 0] - fun_3d_ref) / np.linalg.norm(fun_3d_ref)) < interpolation_tolerance


def test_interpolators_interpolation_rbf_local(interpolation_tolerance=5e-3, seed=42):
    rng = np.random.default_rng(seed)

    coord = rng.random((500, 3))
    coord_trg = rng.random((20, 3))

    fun_3d = np.sin(coord[:, 0]) * np.cos(coord[:, 1]) * np.exp(coord[:, 2])
    fun_3d = io.CFSResultArray(
        fun_3d,
        quantity="function",
        region="src",
        step_values=np.array([1.0]),
        res_type=cfs_types.cfs_result_type.NODE,
        analysis_type=cfs_types.cfs_analysis_type.STATIC,
    )

    with TimeRecord(verbose=False) as rec:
        fun_3d_rbf_local = interpolation_rbf_local(
            coord,
            coord_trg,
            fun_3d[:, None],
            kernel="gaussian",
            epsilon=2.0,
            smoothing=1e-10,
            # neighbors=40,
            min_neighbors=10,
            # radius_factor=1.5,
        )
        print(f"Local RBF interpolation: {rec.TimeElapsed:.2f} seconds")

    fun_3d_ref = np.sin(coord_trg[:, 0]) * np.cos(coord_trg[:, 1]) * np.exp(coord_trg[:, 2])

    print(
        f"Interpolated Function Error: {np.linalg.norm(fun_3d_rbf_local[:,0] - fun_3d_ref)/np.linalg.norm(fun_3d_ref):.2g}"
    )

    assert (np.linalg.norm(fun_3d_rbf_local[:, 0] - fun_3d_ref) / np.linalg.norm(fun_3d_ref)) < interpolation_tolerance


def test_derivatives_jacobian_rbf(interpolation_tolerance=5e-3, seed=42):
    rng = np.random.default_rng(seed)

    coord = rng.random((600, 3))
    coord_trg = rng.random((20, 3))

    fun_3d = np.sin(coord[:, 0]) * np.cos(coord[:, 1]) * np.exp(coord[:, 2])
    fun_3d = io.CFSResultArray(
        fun_3d,
        quantity="function",
        region="src",
        step_values=np.array([1.0]),
        res_type=cfs_types.cfs_result_type.NODE,
        analysis_type=cfs_types.cfs_analysis_type.STATIC,
    )

    with TimeRecord(verbose=False) as rec:
        grad_3d_rbf = jacobian_rbf(coord, coord_trg, fun_3d[:, None], kernel="gaussian", epsilon=2.0, smoothing=1e-10)
        print(f"RBF gradient: {rec.TimeElapsed:.2f} seconds")
    grad_3d_rbf = grad_3d_rbf.reshape(grad_3d_rbf.shape[0], grad_3d_rbf.shape[1] * grad_3d_rbf.shape[2])

    grad_3d_ref = np.array(
        [
            np.cos(coord_trg[:, 0]) * np.cos(coord_trg[:, 1]) * np.exp(coord_trg[:, 2]),
            -np.sin(coord_trg[:, 0]) * np.sin(coord_trg[:, 1]) * np.exp(coord_trg[:, 2]),
            np.sin(coord_trg[:, 0]) * np.cos(coord_trg[:, 1]) * np.exp(coord_trg[:, 2]),
        ]
    ).swapaxes(0, 1)

    print(f"Interpolated Gradient Error: {np.linalg.norm(grad_3d_rbf - grad_3d_ref)/np.linalg.norm(grad_3d_ref):.2g}")

    assert (np.linalg.norm(grad_3d_rbf - grad_3d_ref) / np.linalg.norm(grad_3d_ref)) < interpolation_tolerance


def test_derivatives_jacobian_rbf_local(interpolation_tolerance=1e-2, seed=42):
    rng = np.random.default_rng(seed)

    coord = rng.random((600, 3))
    coord_trg = rng.random((20, 3))

    fun_3d = np.sin(coord[:, 0]) * np.cos(coord[:, 1]) * np.exp(coord[:, 2])
    fun_3d = io.CFSResultArray(
        fun_3d,
        quantity="function",
        region="src",
        step_values=np.array([1.0]),
        res_type=cfs_types.cfs_result_type.NODE,
        analysis_type=cfs_types.cfs_analysis_type.STATIC,
    )

    with TimeRecord(verbose=False) as rec:
        grad_3d_rbf_local = jacobian_rbf_local(
            coord,
            coord_trg,
            fun_3d[:, None],
            kernel="gaussian",
            epsilon=2.0,
            smoothing=1e-10,
            # neighbors=200,
            min_neighbors=50,
            # radius_factor=3.0,
        )
        print(f"Local RBF gradient: {rec.TimeElapsed:.2f} seconds")
    grad_3d_rbf_local = grad_3d_rbf_local.reshape(
        grad_3d_rbf_local.shape[0], grad_3d_rbf_local.shape[1] * grad_3d_rbf_local.shape[2]
    )

    grad_3d_ref = np.array(
        [
            np.cos(coord_trg[:, 0]) * np.cos(coord_trg[:, 1]) * np.exp(coord_trg[:, 2]),
            -np.sin(coord_trg[:, 0]) * np.sin(coord_trg[:, 1]) * np.exp(coord_trg[:, 2]),
            np.sin(coord_trg[:, 0]) * np.cos(coord_trg[:, 1]) * np.exp(coord_trg[:, 2]),
        ]
    ).swapaxes(0, 1)

    print(
        f"Interpolated Gradient Error: {np.linalg.norm(grad_3d_rbf_local - grad_3d_ref)/np.linalg.norm(grad_3d_ref):.2g}"
    )

    assert (np.linalg.norm(grad_3d_rbf_local - grad_3d_ref) / np.linalg.norm(grad_3d_ref)) < interpolation_tolerance


def test_interpolators_interpolate_rbf(tolerance=1e-5):

    X = np.linspace(0, 1, 10)
    Y = np.linspace(0, 1, 10)

    mesh_src = io.CFSMeshData.struct_mesh(X, Y, region_name="S_source")
    mesh_trg = io.CFSMeshData.struct_mesh(X * 0.9 + 0.05, Y * 0.9 + 0.05, region_name="S_target")

    coord_src = mesh_src.get_region_coordinates("S_source")
    coord_trg = mesh_trg.get_region_coordinates("S_target")

    data_src = io.CFSResultArray(
        np.array([np.sin(np.pi * coord_src[:, 0]) * np.cos(np.pi * coord_src[:, 1])]),
        quantity="function",
        region="S_source",
        step_values=np.array([1.0]),
        res_type=cfs_result_type.NODE,
        analysis_type=cfs_analysis_type.TRANSIENT,
    ).require_shape()
    data_ref = io.CFSResultArray(
        np.array([np.sin(np.pi * coord_trg[:, 0]) * np.cos(np.pi * coord_trg[:, 1])]),
        quantity="function_ref",
        region="S_target",
        step_values=np.array([1.0]),
        res_type=cfs_result_type.NODE,
        analysis_type=cfs_analysis_type.TRANSIENT,
    ).require_shape()

    result_data_rbf = interpolators.interpolate_rbf(
        mesh_src=mesh_src,
        result_src=[data_src],
        mesh_target=mesh_trg,
        region_src_target=[{"source": ["S_source"], "target": ["S_target"]}],
        quantity_names={"function": "function_rbf"},
        kernel="gaussian",
        verbosity=v_def.debug,
    )

    data_rbf = result_data_rbf.get_data_array(quantity="function_rbf", region="S_target")

    error_norm = np.linalg.norm(data_ref - data_rbf) / np.linalg.norm(data_ref)
    print(f"RBF Interpolation Error: {error_norm:.2g}")
    assert error_norm < tolerance, f"RBF interpolation error exceeds tolerance {error_norm:.2g}>{tolerance:.2g}"


def test_interpolators_interpolate_rbf_local(tolerance=1e-4):

    X = np.linspace(0, 1, 10)
    Y = np.linspace(0, 1, 10)

    mesh_src = io.CFSMeshData.struct_mesh(X, Y, region_name="S_source")
    mesh_trg = io.CFSMeshData.struct_mesh(X * 0.9 + 0.05, Y * 0.9 + 0.05, region_name="S_target")

    coord_src = mesh_src.get_region_coordinates("S_source")
    coord_trg = mesh_trg.get_region_coordinates("S_target")

    data_src = io.CFSResultArray(
        np.array([np.sin(np.pi * coord_src[:, 0]) * np.cos(np.pi * coord_src[:, 1])]),
        quantity="function",
        region="S_source",
        step_values=np.array([1.0]),
        res_type=cfs_result_type.NODE,
        analysis_type=cfs_analysis_type.TRANSIENT,
    ).require_shape()
    data_ref = io.CFSResultArray(
        np.array([np.sin(np.pi * coord_trg[:, 0]) * np.cos(np.pi * coord_trg[:, 1])]),
        quantity="function_ref",
        region="S_target",
        step_values=np.array([1.0]),
        res_type=cfs_result_type.NODE,
        analysis_type=cfs_analysis_type.TRANSIENT,
    ).require_shape()

    result_data_rbf = interpolators.interpolate_rbf_local(
        mesh_src=mesh_src,
        result_src=[data_src],
        mesh_target=mesh_trg,
        region_src_target=[{"source": ["S_source"], "target": ["S_target"]}],
        quantity_names={"function": "function_rbf"},
        verbosity=v_def.debug,
    )

    data_rbf = result_data_rbf.get_data_array(quantity="function_rbf", region="S_target")

    error_norm = np.linalg.norm(data_ref - data_rbf) / np.linalg.norm(data_ref)
    print(f"RBF Interpolation Error: {error_norm:.2g}")
    assert error_norm < tolerance, f"RBF interpolation error exceeds tolerance {error_norm:.2g}>{tolerance:.2g}"


def test_derivatives_gradient_rbf(tolerance=1e-5):

    X = np.linspace(0, 1, 10)
    Y = np.linspace(0, 1, 10)

    mesh_src = io.CFSMeshData.struct_mesh(X, Y, region_name="S_source")
    mesh_trg = io.CFSMeshData.struct_mesh(X * 0.9 + 0.05, Y * 0.9 + 0.05, region_name="S_target")

    coord_src = mesh_src.get_region_coordinates("S_source")
    coord_trg = mesh_trg.get_region_coordinates("S_target")

    data_src = io.CFSResultArray(
        np.array([np.sin(np.pi * coord_src[:, 0]) * np.cos(np.pi * coord_src[:, 1])]),
        quantity="function",
        region="S_source",
        step_values=np.array([1.0]),
        res_type=cfs_result_type.NODE,
        analysis_type=cfs_analysis_type.TRANSIENT,
    ).require_shape()
    data_ref = io.CFSResultArray(
        np.array(
            [
                np.pi * np.cos(np.pi * coord_trg[:, 0]) * np.cos(np.pi * coord_trg[:, 1]),
                -np.pi * np.sin(np.pi * coord_trg[:, 0]) * np.sin(np.pi * coord_trg[:, 1]),
                np.zeros_like(coord_trg[:, 0]),
            ]
        ).T,
        quantity="function_ref",
        region="S_target",
        step_values=np.array([1.0]),
        res_type=cfs_result_type.NODE,
        analysis_type=cfs_analysis_type.TRANSIENT,
    ).require_shape()

    result_data_rbf = derivatives.gradient_rbf(
        mesh_src=mesh_src,
        result_src=[data_src],
        mesh_target=mesh_trg,
        region_src_target=[{"source": ["S_source"], "target": ["S_target"]}],
        quantity_names={"function": "function_rbf"},
        kernel="gaussian",
        verbosity=v_def.debug,
    )

    data_rbf = result_data_rbf.get_data_array(quantity="function_rbf", region="S_target")

    error_norm = np.linalg.norm(data_ref - data_rbf) / np.linalg.norm(data_ref)
    print(f"RBF Interpolation Error: {error_norm:.2g}")
    assert error_norm < tolerance, f"RBF interpolation error exceeds tolerance {error_norm:.2g}>{tolerance:.2g}"


def test_derivatives_gradient_rbf_local(tolerance=1e-3):

    X = np.linspace(0, 1, 10)
    Y = np.linspace(0, 1, 10)

    mesh_src = io.CFSMeshData.struct_mesh(X, Y, region_name="S_source")
    mesh_trg = io.CFSMeshData.struct_mesh(X * 0.9 + 0.05, Y * 0.9 + 0.05, region_name="S_target")

    coord_src = mesh_src.get_region_coordinates("S_source")
    coord_trg = mesh_trg.get_region_coordinates("S_target")

    data_src = io.CFSResultArray(
        np.array([np.sin(np.pi * coord_src[:, 0]) * np.cos(np.pi * coord_src[:, 1])]),
        quantity="function",
        region="S_source",
        step_values=np.array([1.0]),
        res_type=cfs_result_type.NODE,
        analysis_type=cfs_analysis_type.TRANSIENT,
    ).require_shape()
    data_ref = io.CFSResultArray(
        np.array(
            [
                np.pi * np.cos(np.pi * coord_trg[:, 0]) * np.cos(np.pi * coord_trg[:, 1]),
                -np.pi * np.sin(np.pi * coord_trg[:, 0]) * np.sin(np.pi * coord_trg[:, 1]),
                np.zeros_like(coord_trg[:, 0]),
            ]
        ).T,
        quantity="function_ref",
        region="S_target",
        step_values=np.array([1.0]),
        res_type=cfs_result_type.NODE,
        analysis_type=cfs_analysis_type.TRANSIENT,
    ).require_shape()

    result_data_rbf = derivatives.gradient_rbf_local(
        mesh_src=mesh_src,
        result_src=[data_src],
        mesh_target=mesh_trg,
        region_src_target=[{"source": ["S_source"], "target": ["S_target"]}],
        quantity_names={"function": "function_rbf"},
        verbosity=v_def.debug,
    )

    data_rbf = result_data_rbf.get_data_array(quantity="function_rbf", region="S_target")

    error_norm = np.linalg.norm(data_ref - data_rbf) / np.linalg.norm(data_ref)
    print(f"RBF Interpolation Error: {error_norm:.2g}")
    assert error_norm < tolerance, f"RBF interpolation error exceeds tolerance {error_norm:.2g}>{tolerance:.2g}"


def test_modal_analysis_mac():
    mode_matrix = np.array(
        [
            [1, 0],  # Orthogonal 1
            [0, 1],  # Orthogonal 2
            [1, 1],  # Linear combination of 1 and 2
        ]
    )

    automac = modal_analysis.modal_assurance_criterion(mode_matrix)
    mac = modal_analysis.modal_assurance_criterion(mode_matrix, mode_matrix + 0.5)

    automac_ref = np.array(
        [
            [1.0, 0.0, 0.5],
            [0.0, 1.0, 0.5],
            [0.5, 0.5, 1.0],
        ]
    )

    mac_ref = np.array(
        [
            [0.9, 0.1, 0.5],
            [0.1, 0.9, 0.5],
            [0.8, 0.8, 1.0],
        ]
    )

    np.testing.assert_array_equal(automac, automac_ref)
    np.testing.assert_array_equal(mac, mac_ref)


def test_projection_interpolation(working_directory="."):
    from pyCFS.data.operators._projection_interpolation import interpolate_region

    file_src = f"{working_directory}/tests/data/operators/projection_interpolation/source.cfs"
    file_target = f"{working_directory}/tests/data/operators/projection_interpolation/target.cfs"
    region_src_target_dict = {
        "IFs_mount_inlet": ["IFs_mount_inlet"],
        "IF_pipe_outer": ["IF_pipe_outer"],
    }

    quantity_name = "mechVelocity"

    file_out = f"{working_directory}/tests/data_tmp/operators/projection_interpolation/data_interpolated.cfs"

    return_data = interpolate_region(
        file_src=file_src,
        file_target=file_target,
        region_src_target_dict=region_src_target_dict,
        quantity_name=quantity_name,
        dim_names=["x", "y", "z"],
        is_complex=True,
        projection_direction=None,
        max_projection_distance=5e-3,
        search_radius=5e-2,
    )

    with io.CFSReader(file_target) as h5reader:
        target_mesh = h5reader.MeshData

    # Create output and write interpolated data
    with io.CFSWriter(file_out) as h5writer:
        h5writer.create_file(mesh=target_mesh, result=return_data)


def test_interpolate_projection_based(working_directory="."):
    file_src = f"{working_directory}/tests/data/operators/projection_interpolation/source.cfs"
    file_target = f"{working_directory}/tests/data/operators/projection_interpolation/target.cfs"
    region_src_target_dict = {
        "IFs_mount_inlet": ["IFs_mount_inlet"],
        "IF_pipe_outer": ["IF_pipe_outer"],
    }

    quantity_name = "mechVelocity"

    mesh_src = io.read_mesh(file_src)
    result_src = io.read_data(file_src)
    mesh_target = io.read_mesh(file_target)

    result_interp = interpolate_projection_based(
        mesh_src=mesh_src,
        result_src=result_src,
        mesh_target=mesh_target,
        region_src_target_dict=region_src_target_dict,
        quantity_name=quantity_name,
        projection_direction=None,
        max_projection_distance=5e-3,
        search_radius=5e-2,
    )

    result_ref = io.read_data(file_target)

    data_interp = result_interp.Data[0]
    data_ref = result_ref.Data[0]

    np.testing.assert_array_almost_equal(
        data_interp, data_ref, decimal=9, err_msg="Interpolated data does not match reference data."
    )


def test_sngr_velocity(working_directory="."):
    # Constants
    C_mu = 0.09  # (2.46)
    vkp_scaling_const = 1.452762113  # (2.62)

    # Parameters
    eps_orthogonal = 1e-9  # orthogonality check

    delta_t = 1e-4  # Dt
    num_steps = 10  # I
    num_modes = 20  # N
    length_scale_factor = 1.0  # fL
    kin_viscosity = 1.48e-5  # nu
    crit_tke_percentage = 0.5  # beta_k_crit
    max_wave_number_percentage = 100  # beta_K_max
    min_wave_number_percentage = 0.01  # beta_K_min

    file_rans = f"{working_directory}/tests/data/operators/sngr/orifice.cfs"
    mesh_data = io.read_mesh(file=file_rans)
    result_data = io.read_data(file=file_rans)

    file_reference = f"{working_directory}/tests/data/operators/sngr/orifice_sngr.cfs"
    result_reference = io.read_data(file=file_reference)

    region_list = [
        "fluid",
    ]

    data_on_elems = True

    for reg_name in region_list:
        print(f" - Process region: {reg_name}")

        if data_on_elems:
            coords = mesh_data.get_region_centroids(region=reg_name)
        else:
            coords = mesh_data.get_region_coordinates(region=reg_name)

        mean_velocity = result_data.get_data_array(quantity="U", region=reg_name).squeeze()
        tke = result_data.get_data_array(quantity="k", region=reg_name).squeeze()
        tdr = result_data.get_data_array(quantity="epsilon", region=reg_name).squeeze()

        u_prime, timesteps = sngr.compute_stochastic_velocity_fluctuations(
            coords,
            mean_velocity=mean_velocity,
            tke=tke,
            tdr=tdr,
            C_mu=C_mu,
            vkp_scaling_const=vkp_scaling_const,
            length_scale_factor=length_scale_factor,
            kin_viscosity=kin_viscosity,
            crit_tke_percentage=crit_tke_percentage,
            max_wave_number_percentage=max_wave_number_percentage,
            min_wave_number_percentage=min_wave_number_percentage,
            num_modes=num_modes,
            num_steps=num_steps,
            delta_t=delta_t,
            eps_orthogonal=eps_orthogonal,
            rn_gen=np.random.Generator(np.random.PCG64(seed=1)),
        )

        u_prime_reference = result_reference.get_data_array(quantity="fluctFluidMechVelocity", region=reg_name)

        np.testing.assert_allclose(u_prime, u_prime_reference, rtol=1e-9, err_msg="SNRG velocity fluctuation not equal")


def test_sngr_lighthill(working_directory="."):
    # Constants
    C_mu = 0.09  # (2.46)
    vkp_scaling_const = 1.452762113  # (2.62)

    # Parameters
    eps_orthogonal = 1e-9  # orthogonality check

    f_min = 1
    f_max = 1000
    num_steps = 10  # I
    num_modes = 20  # N
    length_scale_factor = 1.0  # fL
    kin_viscosity = 1.48e-5  # nu
    density = 1.225  # rho
    crit_tke_percentage = 0.5  # beta_k_crit
    max_wave_number_percentage = 100  # beta_K_max
    min_wave_number_percentage = 0.01  # beta_K_min

    file_rans = f"{working_directory}/tests/data/operators/sngr/orifice.cfs"
    mesh_data = io.read_mesh(file=file_rans)
    result_data = io.read_data(file=file_rans)

    file_reference = f"{working_directory}/tests/data/operators/sngr/orifice_sngr_lighthill.cfs"
    result_reference = io.read_data(file=file_reference)

    region_list = [
        "fluid",
    ]

    data_on_elems = True

    for reg_name in region_list:
        print(f" - Process region: {reg_name}")

        if data_on_elems:
            coords = mesh_data.get_region_centroids(region=reg_name)
        else:
            coords = mesh_data.get_region_coordinates(region=reg_name)

        mean_velocity = result_data.get_data_array(quantity="U", region=reg_name).squeeze()
        tke = result_data.get_data_array(quantity="k", region=reg_name).squeeze()
        tdr = result_data.get_data_array(quantity="epsilon", region=reg_name).squeeze()

        lighthill_rhs_reference = result_reference.get_data_array(quantity="acouRhsDensity", region=reg_name)

        lighthill_rhs, f_steps = sngr.compute_stochastic_harmonic_lighthill_rhs(
            coords=coords,
            mean_velocity=mean_velocity,
            tke=tke,
            tdr=tdr,
            C_mu=C_mu,
            vkp_scaling_const=vkp_scaling_const,
            length_scale_factor=length_scale_factor,
            kin_viscosity=kin_viscosity,
            density=density,
            crit_tke_percentage=crit_tke_percentage,
            max_wave_number_percentage=max_wave_number_percentage,
            min_wave_number_percentage=min_wave_number_percentage,
            num_modes=num_modes,
            num_steps=num_steps,
            f_min=f_min,
            f_max=f_max,
            eps_orthogonal=eps_orthogonal,
            rn_gen=np.random.Generator(np.random.PCG64(seed=1)),
            max_memory_usage=0.005,
        )

        np.testing.assert_allclose(
            lighthill_rhs[..., np.newaxis],
            lighthill_rhs_reference,
            rtol=1e-9,
            err_msg="SNRG Lighthill source density not equal",
        )


def test_transformation_extrude_mesh_region(dummy_CFSMeshData_obj):
    mesh_extrude, _ = transformation.extrude_mesh_region(
        mesh=dummy_CFSMeshData_obj,
        region="Surf1",
        created_region="Surf1_extrude",
        extrude_vector=np.array([0.5, 0, 0]),
        num_layers=2,
    )

    coord_ref = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 1.0],
            [0.25, 0.0, 0.0],
            [0.25, 0.0, 1.0],
            [0.25, 1.0, 0.0],
            [0.25, 1.0, 1.0],
            [0.5, 0.0, 0.0],
            [0.5, 0.0, 1.0],
            [0.5, 1.0, 0.0],
            [0.5, 1.0, 1.0],
        ]
    )

    conn_ref = np.array(
        [
            [1, 2, 3, 5, 6, 7],
            [2, 4, 3, 6, 8, 7],
            [5, 6, 7, 9, 10, 11],
            [6, 8, 7, 10, 12, 11],
        ]
    )

    np.testing.assert_array_equal(mesh_extrude.Coordinates, coord_ref)
    np.testing.assert_array_equal(mesh_extrude.Connectivity, conn_ref)


def test_transformation_revolve_mesh_region(dummy_CFSMeshData_obj):
    dummy_CFSMeshData_obj.Coordinates = transformation.transform_coord(
        arg=np.array([0, 1.0, 0, 0, 0, 0]), coord=dummy_CFSMeshData_obj.Coordinates
    )

    mesh_revolve, _ = transformation.revolve_mesh_region(
        mesh=dummy_CFSMeshData_obj,
        region="Surf1",
        created_region="Surf1_revolve",
        revolve_axis=np.array([0, 0, 1.0]),
        revolve_angle=2 * np.pi,
        num_layers=4,
    )

    coord_ref = np.array(
        [
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 1.0],
            [0.0, 2.0, 0.0],
            [0.0, 2.0, 1.0],
            [-1.0, 0, 0.0],
            [-1.0, 0.0, 1.0],
            [-2.0, 0.0, 0.0],
            [-2.0, 0.0, 1.0],
            [0.0, -1.0, 0.0],
            [0.0, -1.0, 1.0],
            [0.0, -2.0, 0.0],
            [0.0, -2.0, 1.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 1.0],
            [2.0, 0.0, 0.0],
            [2.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 1.0],
            [0.0, 2.0, 0.0],
            [0.0, 2.0, 1.0],
        ]
    )
    conn_ref = np.array(
        [
            [1, 2, 3, 5, 6, 7],
            [2, 4, 3, 6, 8, 7],
            [5, 6, 7, 9, 10, 11],
            [6, 8, 7, 10, 12, 11],
            [9, 10, 11, 13, 14, 15],
            [10, 12, 11, 14, 16, 15],
            [13, 14, 15, 1, 2, 3],
            [14, 16, 15, 2, 4, 3],
        ]
    )

    np.testing.assert_array_almost_equal(mesh_revolve.Coordinates, coord_ref, decimal=15)
    np.testing.assert_array_equal(mesh_revolve.Connectivity, conn_ref)


def test_field_fft_cfs_result_array():
    from pyCFS.data.operators.field_fft import field_fft
    from pyCFS.data.io import CFSResultArray
    import scipy.fft

    # Create a dummy CFSResultArray
    data = np.random.rand(100, 20, 3)  # Example data
    cfs_result_array = CFSResultArray(data)

    # Apply FFT along the first axis
    transformed_cfs_result_array = field_fft(cfs_result_array)
    transformed_data = scipy.fft.fft(cfs_result_array.data, axis=0)

    # Check the shape of the transformed data
    assert transformed_data.shape == (100, 20, 3), "Transformed data shape mismatch"
    # Check if the transformation is correct
    np.testing.assert_array_almost_equal(
        transformed_data, transformed_cfs_result_array.data, decimal=6, err_msg="FFT transformation mismatch"
    )


def test_field_fft_numpy_array():
    from pyCFS.data.operators.field_fft import field_fft
    import scipy.fft

    data = np.random.rand(100, 20, 3)  # Example data
    transformed_data = scipy.fft.fft(data, axis=0)
    transformed_numpy_array = field_fft(data)

    # Check the shape of the transformed data
    assert transformed_data.shape == (100, 20, 3), "Transformed data shape mismatch"
    assert transformed_numpy_array.shape == (100, 20, 3), "Transformed numpy array shape mismatch"
    # Check if the transformation is correct
    np.testing.assert_array_almost_equal(
        transformed_data, transformed_numpy_array, decimal=6, err_msg="FFT transformation mismatch"
    )


def test_field_fft_invalid_input():
    from pyCFS.data.operators.field_fft import field_fft
    from pyCFS.data.io import CFSResultArray
    import numpy as np

    # Test with invalid input type
    with np.testing.assert_raises(TypeError):
        field_fft([[0, 0], [0, 0]])

    # Test with empty numpy array
    with np.testing.assert_raises(ValueError):
        field_fft(np.array([]))

    # Test with CFSResultArray with incorrect dimensions
    cfs_result_array_invalid = CFSResultArray(np.random.rand(10, 10))  # 2D array instead of 3D
    with np.testing.assert_raises(ValueError):
        field_fft(cfs_result_array_invalid)


def test_field_fft_1D_window():
    from pyCFS.data.operators.field_fft import field_fft
    from pyCFS.data.io import CFSResultArray
    import numpy as np
    import scipy.fft

    data = CFSResultArray(np.random.rand(100, 20, 3))  # Example data
    window = np.hanning(data.shape[0])  # Create a Hanning window

    transformed_data = scipy.fft.fft(data * window[:, np.newaxis, np.newaxis], axis=0)
    transformed_with_window = field_fft(data, window=window)

    # Check the shape of the transformed data
    assert transformed_data.shape == (100, 20, 3), "Transformed data shape mismatch"
    assert transformed_with_window.shape == (100, 20, 3), "Transformed data with window shape mismatch"
    # Check if the transformation is correct
    np.testing.assert_array_almost_equal(
        transformed_data, transformed_with_window.data, decimal=6, err_msg="FFT transformation with window mismatch"
    )


def test_field_fft_3D_window():
    from pyCFS.data.operators.field_fft import field_fft
    from pyCFS.data.io import CFSResultArray
    import numpy as np
    import scipy.fft

    data = CFSResultArray(np.random.rand(100, 20, 3))  # Example data
    window = np.random.rand(100, 20, 3)  # Create a random 3D window

    transformed_data = scipy.fft.fft(data * window, axis=0)
    transformed_with_window = field_fft(data, window=window)

    # Check the shape of the transformed data
    assert transformed_data.shape == (100, 20, 3), "Transformed data shape mismatch"
    assert transformed_with_window.shape == (100, 20, 3), "Transformed data with window shape mismatch"
    # Check if the transformation is correct
    np.testing.assert_array_almost_equal(
        transformed_data, transformed_with_window.data, decimal=6, err_msg="FFT transformation with 3D window mismatch"
    )


@pytest.mark.skipif(importlib.util.find_spec("pydmd") is None, reason="requires pyDMD>=2025.6.1")
def test_dmd_truncation():
    from pyCFS.data.operators.dynamic_mode_decomposition import dmd

    # creat dummy data
    dt = 0.1  # time step
    n_steps = 100
    n_points = 30
    t = np.linspace(0, dt * (n_steps - 1), n_steps)  # time vector
    x = np.linspace(0, np.pi, n_points)
    X, T = np.meshgrid(x, t)
    noise = np.random.normal(0, 0.1, X.shape)  # Add some noise

    data = np.sin(X) * np.cos(T) + noise
    # Apply DMD
    dmd_instance = dmd(data, svd_rank=5, exact=False, dt=dt)
    # Check if the DMD instance has the expected attributes
    ampl = dmd_instance.amplitudes
    freq = dmd_instance.frequency
    modes = dmd_instance.modes
    dynamics = dmd_instance.dynamics

    # Check the shape of the attributes
    assert modes.shape == (n_points, 5), "Modes shape mismatch"
    assert dynamics.shape == (5, n_steps), "Dynamics shape mismatch"
    assert ampl.shape == (5,), "Amplitudes shape mismatch"
    assert freq.shape == (5,), "Frequencies shape mismatch"


@pytest.mark.skipif(importlib.util.find_spec("pydmd") is None, reason="requires pyDMD>=2025.6.1")
def test_dmd_no_truncation():
    from pyCFS.data.operators.dynamic_mode_decomposition import dmd

    # Create dummy data
    dt = 0.1  # time step
    n_steps = 100
    n_points = 30
    t = np.linspace(0, dt * (n_steps - 1), n_steps)  # time vector
    x = np.linspace(0, np.pi, n_points)
    X, T = np.meshgrid(x, t)
    noise = np.random.normal(0, 0.1, X.shape)  # Add some noise
    data = np.sin(X) * np.cos(T) + noise

    # Apply DMD without truncation
    dmd_instance = dmd(data, exact=False, svd_rank=-1, dt=dt)

    # Check if the DMD instance has the expected attributes
    modes = dmd_instance.modes
    dynamics = dmd_instance.dynamics
    ampl = dmd_instance.amplitudes
    freq = dmd_instance.frequency

    # Check the shape of the modes
    assert modes.shape == (n_points, n_points), "Modes shape mismatch without truncation"
    assert dynamics.shape == (n_points, n_steps), "Dynamics shape mismatch without truncation"
    assert ampl.shape == (n_points,), "Amplitudes shape mismatch without truncation"
    assert freq.shape == (n_points,), "Frequencies shape mismatch without truncation"


@pytest.mark.skipif(importlib.util.find_spec("pydmd") is None, reason="requires pyDMD>=2025.6.1")
def test_dmd_numpy_3d():
    from pyCFS.data.operators.dynamic_mode_decomposition import dmd

    # Create dummy 3D data
    dt = 0.1  # time step
    n_steps = 100
    n_points = 30
    n_d = 3

    data = np.random.rand(n_steps, n_points, n_d)  # Example 3D data

    # Apply DMD to the 3D numpy array while ignoring warnings for invalid operations
    with np.errstate(divide="ignore", invalid="ignore"):
        dmd_instance = dmd(data, svd_rank=5, exact=False, dt=dt)

    # Check the shape of the modes and dynamics
    assert dmd_instance.modes.shape == (n_points * n_d, 5), "Modes shape mismatch for 3D numpy array"
    assert dmd_instance.dynamics.shape == (5, n_steps), "Dynamics shape mismatch for 3D numpy array"
    assert dmd_instance.amplitudes.shape == (5,), "Amplitudes shape mismatch for 3D numpy array"


@pytest.mark.skipif(importlib.util.find_spec("pydmd") is None, reason="requires pyDMD>=2025.6.1")
def test_dmd_cfs_result_array():
    from pyCFS.data.operators.dynamic_mode_decomposition import dmd
    from pyCFS.data.io import CFSResultArray

    # Create a dummy CFSResultArray
    data = np.random.rand(100, 20, 3)  # Example data
    cfs_result_array = CFSResultArray(data)

    # Apply DMD while ignoring warnings for divide by zero and invalid operations
    with np.errstate(divide="ignore", invalid="ignore"):
        dmd_instance = dmd(cfs_result_array, svd_rank=5, exact=False)

    # Check the shape of the modes
    assert dmd_instance.modes.shape == (60, 5), "Modes shape mismatch for CFSResultArray"
    assert dmd_instance.dynamics.shape == (5, 100), "Dynamics shape mismatch for CFSResultArray"
    assert dmd_instance.amplitudes.shape == (5,), "Amplitudes shape mismatch for CFSResultArray"
    assert dmd_instance.frequency.shape == (5,), "Frequencies shape mismatch for CFSResultArray"


@pytest.mark.skipif(importlib.util.find_spec("pydmd") is None, reason="requires pyDMD>=2025.6.1")
def test_dmd_reshape_vec_valued_modes():
    from pyCFS.data.operators.dynamic_mode_decomposition import reshape_3d_dmd_modes
    from pyCFS.data.operators.dynamic_mode_decomposition import dmd

    # Create dummy data
    dt = 0.1  # time step
    n_steps = 100
    n_points = 30
    n_dim = 3
    data = np.random.rand(n_steps, n_points, n_dim)  # Example 3D data

    # Apply DMD while ignoring warnings for divide by zero and invalid operations
    with np.errstate(divide="ignore", invalid="ignore"):
        dmd_instance = dmd(data, svd_rank=5, exact=False, dt=dt)

    # Reshape the modes
    reshaped_modes = reshape_3d_dmd_modes(dmd_instance.modes, n_points=n_points, n_dim=n_dim, r_trunc=5)

    # Check the shape of the reshaped modes
    assert reshaped_modes.shape == (n_points, n_dim, 5), "Reshaped modes shape mismatch"
