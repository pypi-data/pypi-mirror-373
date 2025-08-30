import numpy as np
import h5py
import pytest
from vtkio.writer.vtkhdf import (
    VTKHDFUnstructuredGridWriter,
    VTKHDFImageDataWriter,
    VTKHDFPolyDataWriter,
    VTKHDFMultiBlockWriter,
)

def test_unstructured_grid(tmp_path):
    nodes = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], dtype=np.float32)
    cell_types = np.array([10], dtype=np.uint8)  # VTK_TETRA
    connectivity = np.array([0,1,2,3], dtype=np.int64)
    offsets = np.array([4], dtype=np.int64)
    point_data = {"Temperature": np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)}
    cell_data = {"Pressure": np.array([100.0], dtype=np.float32)}
    field_data = {"Meta": np.array([42], dtype=np.int32)}
    filename = tmp_path / "unstructured"
    writer = VTKHDFUnstructuredGridWriter(
        filename=str(filename),
        nodes=nodes,
        cell_types=cell_types,
        connectivity=connectivity,
        offsets=offsets,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data
    )
    writer.write_vtkhdf_file()
    with h5py.File(str(filename) + ".vtkhdf", "r") as f:
        root = f["VTKHDF"]
        np.testing.assert_array_equal(root["Points"][:], nodes)
        np.testing.assert_array_equal(root["Connectivity"][:], connectivity)
        np.testing.assert_array_equal(root["Offsets"][:], np.array([0,4]))
        np.testing.assert_array_equal(root["Types"][:], cell_types)
        np.testing.assert_array_equal(root["PointData/Temperature"][:], point_data["Temperature"])
        np.testing.assert_array_equal(root["CellData/Pressure"][:], cell_data["Pressure"])
        np.testing.assert_array_equal(root["FieldData/Meta"][:], field_data["Meta"])

def test_image_data(tmp_path):
    whole_extent = np.array([0, 1, 0, 1, 0, 1])
    origin = np.array([0.0, 0.0, 0.0])
    spacing = np.array([1.0, 1.0, 1.0])
    point_data = {"Density": np.ones((8,1), dtype=np.float32)}
    cell_data = {"Pressure": np.ones((1,1), dtype=np.float32)}
    field_data = {"Meta": np.array([7], dtype=np.int32)}
    filename = tmp_path / "image"
    writer = VTKHDFImageDataWriter(
        filename=str(filename),
        whole_extent=whole_extent,
        origin=origin,
        spacing=spacing,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data
    )
    writer.write_vtkhdf_file()
    with h5py.File(str(filename) + ".vtkhdf", "r") as f:
        root = f["VTKHDF"]
        np.testing.assert_array_equal(root.attrs["WholeExtent"], whole_extent)
        np.testing.assert_array_equal(root.attrs["Origin"], origin)
        np.testing.assert_array_equal(root.attrs["Spacing"], spacing)
        np.testing.assert_array_equal(root["PointData/Density"][:].flatten(), np.ones(8))
        np.testing.assert_array_equal(root["CellData/Pressure"][:].flatten(), np.ones(1))
        np.testing.assert_array_equal(root["FieldData/Meta"][:], field_data["Meta"])

def test_polydata(tmp_path):
    points = np.array([[0,0,0],[1,0,0],[0,1,0]], dtype=np.float32)
    verts = (np.array([0,1,2], dtype=np.int64), np.array([3], dtype=np.int64))
    lines = (np.array([0,1], dtype=np.int64), np.array([2], dtype=np.int64))
    polys = (np.array([0,1,2], dtype=np.int64), np.array([3], dtype=np.int64))
    strips = None
    point_data = {"V": np.arange(3, dtype=np.float32)}
    cell_data = {"C": np.arange(1, dtype=np.float32)}
    field_data = {"F": np.arange(1, dtype=np.float32)}
    filename = tmp_path / "poly"
    writer = VTKHDFPolyDataWriter(
        filename=str(filename),
        points=points,
        verts=verts,
        lines=lines,
        polys=polys,
        strips=strips,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data
    )
    writer.write_vtkhdf_file()
    with h5py.File(str(filename) + ".vtkhdf", "r") as f:
        root = f["VTKHDF"]
        np.testing.assert_array_equal(root["Points"][:], points)
        np.testing.assert_array_equal(root["Vertices/Connectivity"][:], verts[0])
        np.testing.assert_array_equal(root["Vertices/Offsets"][:], np.array([0,3]))
        np.testing.assert_array_equal(root["Lines/Connectivity"][:], lines[0])
        np.testing.assert_array_equal(root["Lines/Offsets"][:], np.array([0,2]))
        np.testing.assert_array_equal(root["Polygons/Connectivity"][:], polys[0])
        np.testing.assert_array_equal(root["Polygons/Offsets"][:], np.array([0,3]))
        np.testing.assert_array_equal(root["PointData/V"][:], point_data["V"])
        np.testing.assert_array_equal(root["CellData/C"][:], cell_data["C"])
        np.testing.assert_array_equal(root["FieldData/F"][:], field_data["F"])

def test_multiblock(tmp_path):
    # Block 1: UnstructuredGrid
    nodes = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], dtype=np.float32)
    cell_types = np.array([10], dtype=np.uint8)
    from vtkio.writer.vtkhdf import (
        VTKHDFUnstructuredGridWriter,
        VTKHDFImageDataWriter,
        VTKHDFPolyDataWriter,
        VTKHDFMultiBlockWriter,
    )

    def test_unstructured_grid(tmp_path):
        nodes = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], dtype=np.float32)
        cell_types = np.array([10], dtype=np.uint8)  # VTK_TETRA
        connectivity = np.array([0,1,2,3], dtype=np.int64)
        offsets = np.array([4], dtype=np.int64)
        point_data = {"Temperature": np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)}
        cell_data = {"Pressure": np.array([100.0], dtype=np.float32)}
        field_data = {"Meta": np.array([42], dtype=np.int32)}
        filename = tmp_path / "unstructured"
        writer = VTKHDFUnstructuredGridWriter(
            filename=str(filename),
            nodes=nodes,
            cell_types=cell_types,
            connectivity=connectivity,
            offsets=offsets,
            point_data=point_data,
            cell_data=cell_data,
            field_data=field_data
        )
        writer.write_vtkhdf_file()
        with h5py.File(str(filename) + ".vtkhdf", "r") as f:
            root = f["VTKHDF"]
            np.testing.assert_array_equal(root["Points"][:], nodes)
            np.testing.assert_array_equal(root["Connectivity"][:], connectivity)
            np.testing.assert_array_equal(root["Offsets"][:], np.array([0,4]))
            np.testing.assert_array_equal(root["Types"][:], cell_types)
            np.testing.assert_array_equal(root["PointData/Temperature"][:], point_data["Temperature"])
            np.testing.assert_array_equal(root["CellData/Pressure"][:], cell_data["Pressure"])
            np.testing.assert_array_equal(root["FieldData/Meta"][:], field_data["Meta"])

    def test_image_data(tmp_path):
        whole_extent = np.array([0, 1, 0, 1, 0, 1])
        origin = np.array([0.0, 0.0, 0.0])
        spacing = np.array([1.0, 1.0, 1.0])
        point_data = {"Density": np.ones((8,1), dtype=np.float32)}
        cell_data = {"Pressure": np.ones((1,1), dtype=np.float32)}
        field_data = {"Meta": np.array([7], dtype=np.int32)}
        filename = tmp_path / "image"
        writer = VTKHDFImageDataWriter(
            filename=str(filename),
            whole_extent=whole_extent,
            origin=origin,
            spacing=spacing,
            point_data=point_data,
            cell_data=cell_data,
            field_data=field_data
        )
        writer.write_vtkhdf_file()
        with h5py.File(str(filename) + ".vtkhdf", "r") as f:
            root = f["VTKHDF"]
            np.testing.assert_array_equal(root.attrs["WholeExtent"], whole_extent)
            np.testing.assert_array_equal(root.attrs["Origin"], origin)
            np.testing.assert_array_equal(root.attrs["Spacing"], spacing)
            np.testing.assert_array_equal(root["PointData/Density"][:].flatten(), np.ones(8))
            np.testing.assert_array_equal(root["CellData/Pressure"][:].flatten(), np.ones(1))
            np.testing.assert_array_equal(root["FieldData/Meta"][:], field_data["Meta"])

    def test_polydata(tmp_path):
        points = np.array([[0,0,0],[1,0,0],[0,1,0]], dtype=np.float32)
        verts = (np.array([0,1,2], dtype=np.int64), np.array([3], dtype=np.int64))
        lines = (np.array([0,1], dtype=np.int64), np.array([2], dtype=np.int64))
        polys = (np.array([0,1,2], dtype=np.int64), np.array([3], dtype=np.int64))
        strips = None
        point_data = {"V": np.arange(3, dtype=np.float32)}
        cell_data = {"C": np.arange(1, dtype=np.float32)}
        field_data = {"F": np.arange(1, dtype=np.float32)}
        filename = tmp_path / "poly"
        writer = VTKHDFPolyDataWriter(
            filename=str(filename),
            points=points,
            verts=verts,
            lines=lines,
            polys=polys,
            strips=strips,
            point_data=point_data,
            cell_data=cell_data,
            field_data=field_data
        )
        writer.write_vtkhdf_file()
        with h5py.File(str(filename) + ".vtkhdf", "r") as f:
            root = f["VTKHDF"]
            np.testing.assert_array_equal(root["Points"][:], points)
            np.testing.assert_array_equal(root["Vertices/Connectivity"][:], verts[0])
            np.testing.assert_array_equal(root["Vertices/Offsets"][:], np.array([0,3]))
            np.testing.assert_array_equal(root["Lines/Connectivity"][:], lines[0])
            np.testing.assert_array_equal(root["Lines/Offsets"][:], np.array([0,2]))
            np.testing.assert_array_equal(root["Polygons/Connectivity"][:], polys[0])
            np.testing.assert_array_equal(root["Polygons/Offsets"][:], np.array([0,3]))
            np.testing.assert_array_equal(root["PointData/V"][:], point_data["V"])
            np.testing.assert_array_equal(root["CellData/C"][:], cell_data["C"])
            np.testing.assert_array_equal(root["FieldData/F"][:], field_data["F"])

    def test_multiblock(tmp_path):
        # Block 1: UnstructuredGrid
        nodes = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], dtype=np.float32)
        cell_types = np.array([10], dtype=np.uint8)
        connectivity = np.array([0,1,2,3], dtype=np.int64)
        offsets = np.array([4], dtype=np.int64)
        writer1 = VTKHDFUnstructuredGridWriter(
            filename="dummy",
            nodes=nodes,
            cell_types=cell_types,
            connectivity=connectivity,
            offsets=offsets
        )
        # Block 2: ImageData
        whole_extent = np.array([0, 1, 0, 1, 0, 1])
        origin = np.array([0.0, 0.0, 0.0])
        spacing = np.array([1.0, 1.0, 1.0])
        writer2 = VTKHDFImageDataWriter(
            filename="dummy",
            whole_extent=whole_extent,
            origin=origin,
            spacing=spacing
        )
        # Block 3: PolyData
        points = np.array([[0,0,0],[1,0,0],[0,1,0]], dtype=np.float32)
        verts = (np.array([0,1,2], dtype=np.int64), np.array([3], dtype=np.int64))
        writer3 = VTKHDFPolyDataWriter(
            filename="dummy",
            points=points,
            verts=verts
        )
        blocks = {"Block0": writer1, "Block1": writer2, "Block2": writer3}
        filename = tmp_path / "multiblock"
        writer = VTKHDFMultiBlockWriter(
            filename=str(filename),
            blocks=blocks
        )
        writer.write_vtkhdf_file()
        with h5py.File(str(filename) + ".vtkhdf", "r") as f:
            root = f["VTKHDF"]
            assert "Block0" in root
            assert "Block1" in root
            assert "Block2" in root
            assert "Assembly" in root
            assert "Block0" in root["Assembly"]
            assert "Block1" in root["Assembly"]
            assert "Block2" in root["Assembly"]

    def test_unstructured_grid_missing_data(tmp_path):
        nodes = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], dtype=np.float32)
        cell_types = np.array([10], dtype=np.uint8)
        connectivity = np.array([0,1,2,3], dtype=np.int64)
        offsets = np.array([4], dtype=np.int64)
        filename = tmp_path / "unstructured_missing"
        writer = VTKHDFUnstructuredGridWriter(
            filename=str(filename),
            nodes=nodes,
            cell_types=cell_types,
            connectivity=connectivity,
            offsets=offsets
        )
        writer.write_vtkhdf_file()
        with h5py.File(str(filename) + ".vtkhdf", "r") as f:
            root = f["VTKHDF"]
            np.testing.assert_array_equal(root["Points"][:], nodes)
            np.testing.assert_array_equal(root["Connectivity"][:], connectivity)
            np.testing.assert_array_equal(root["Offsets"][:], np.array([0,4]))
            np.testing.assert_array_equal(root["Types"][:], cell_types)

    def test_image_data_no_data(tmp_path):
        whole_extent = np.array([0, 1, 0, 1, 0, 1])
        origin = np.array([0.0, 0.0, 0.0])
        spacing = np.array([1.0, 1.0, 1.0])
        filename = tmp_path / "image_no_data"
        writer = VTKHDFImageDataWriter(
            filename=str(filename),
            whole_extent=whole_extent,
            origin=origin,
            spacing=spacing
        )
        writer.write_vtkhdf_file()
        with h5py.File(str(filename) + ".vtkhdf", "r") as f:
            root = f["VTKHDF"]
            np.testing.assert_array_equal(root.attrs["WholeExtent"], whole_extent)
            np.testing.assert_array_equal(root.attrs["Origin"], origin)
            np.testing.assert_array_equal(root.attrs["Spacing"], spacing)

    def test_polydata_only_points(tmp_path):
        points = np.array([[0,0,0],[1,0,0],[0,1,0]], dtype=np.float32)
        filename = tmp_path / "poly_only_points"
        writer = VTKHDFPolyDataWriter(
            filename=str(filename),
            points=points
        )
        writer.write_vtkhdf_file()
        with h5py.File(str(filename) + ".vtkhdf", "r") as f:
            root = f["VTKHDF"]
            np.testing.assert_array_equal(root["Points"][:], points)

    def test_multiblock_empty(tmp_path):
        filename = tmp_path / "empty_multiblock"
        writer = VTKHDFMultiBlockWriter(
            filename=str(filename),
            blocks={}
        )
        writer.write_vtkhdf_file()
        with h5py.File(str(filename) + ".vtkhdf", "r") as f:
            root = f["VTKHDF"]
            assert "Assembly" in root
            assert len(root["Assembly"].keys()) == 0

    def test_unstructured_grid_invalid_args(tmp_path):
        nodes = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], dtype=np.float32)
        cell_types = np.array([10], dtype=np.uint8)
        connectivity = np.array([0,1,2,3], dtype=np.int64)
        # offsets wrong shape
        offsets = np.array([4, 5], dtype=np.int64)
        filename = tmp_path / "unstructured_invalid"
        with pytest.raises(Exception):
            VTKHDFUnstructuredGridWriter(
                filename=str(filename),
                nodes=nodes,
                cell_types=cell_types,
                connectivity=connectivity,
                offsets=offsets
            ).write_vtkhdf_file()

    def test_image_data_invalid_extent(tmp_path):
        whole_extent = np.array([0, 1, 0, 1, 0], dtype=np.int32)  # Wrong shape
        origin = np.array([0.0, 0.0, 0.0])
        spacing = np.array([1.0, 1.0, 1.0])
        filename = tmp_path / "image_invalid"
        with pytest.raises(Exception):
            VTKHDFImageDataWriter(
                filename=str(filename),
                whole_extent=whole_extent,
                origin=origin,
                spacing=spacing
            ).write_vtkhdf_file()

    def test_polydata_invalid_points(tmp_path):
        points = np.array([[0,0],[1,0],[0,1]], dtype=np.float32)  # Should be (N,3)
        filename = tmp_path / "poly_invalid_points"
        with pytest.raises(Exception):
            VTKHDFPolyDataWriter(
                filename=str(filename),
                points=points
            ).write_vtkhdf_file()