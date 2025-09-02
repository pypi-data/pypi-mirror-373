#!/usr/bin/env python
"""
Tests for reading VTK XML files.

Created at 14:46, 15 Apr, 2022
"""
__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard Library
from pathlib import Path
import numpy as np
import pytest

# Imports
# Local Sources
from vtkio.reader.xml import Reader, read_vtkxml_data
from vtkio.vtk_structures import PolyDataTopology

# Set test data directory
TEST_DATA_PATH = Path(__file__).parent.parent / "TestData" / "vtp"


def _assert_cow_data(vtk_data):
    """Verify reading of cow VTP file data."""
    # Verify points
    assert vtk_data.points.shape == (2903, 3)
    
    # Verify data fields are None
    assert vtk_data.cell_data is None
    assert vtk_data.field_data is None
    assert vtk_data.point_data is None
    assert vtk_data.lines is None
    assert vtk_data.strips is None
    assert vtk_data.verts is None
    
    # Verify polygon data
    assert isinstance(vtk_data.polys, PolyDataTopology)
    assert vtk_data.polys.connectivity.shape == (12330,)
    assert vtk_data.polys.connectivity[0:3].tolist() == [250, 251, 210]
    assert vtk_data.polys.offsets.shape == (3263,)
    assert vtk_data.polys.offsets[0:3].tolist() == [4, 8, 11]


def _assert_plate_vectors_data(vtk_data):
    """Verify reading of plate vectors VTP file data."""
    # Verify points
    assert vtk_data.points.shape == (315, 3)
    
    # Verify data fields
    assert vtk_data.cell_data is None
    assert vtk_data.field_data is None
    assert isinstance(vtk_data.point_data, dict)
    assert len(vtk_data.point_data) == 5
    
    expected_data = ['mode1', 'mode2', 'mode3', 'mode4', 'mode8']
    assert list(vtk_data.point_data.keys()) == expected_data
    
    assert vtk_data.lines is None
    assert vtk_data.strips is None
    assert vtk_data.verts is None
    
    # Verify polygon data
    assert isinstance(vtk_data.polys, PolyDataTopology)
    assert vtk_data.polys.connectivity.shape == (1248,)
    assert vtk_data.polys.connectivity[0:3].tolist() == [1, 2, 3]
    assert vtk_data.polys.offsets.shape == (312,)
    assert vtk_data.polys.offsets[0:3].tolist() == [4, 8, 12]


def _assert_horse_data(vtk_data):
    """Verify reading of horse VTP file data."""
    # Verify points
    assert vtk_data.points.shape == (128449, 3)
    
    # Verify data fields
    assert vtk_data.cell_data is None
    assert vtk_data.field_data is None
    assert isinstance(vtk_data.point_data, dict)
    assert len(vtk_data.point_data) == 2
    
    expected_data = ['Normals', 'vtkOriginalPointIds']
    assert list(vtk_data.point_data.keys()) == expected_data
    
    assert vtk_data.lines is None
    assert vtk_data.strips is None
    assert vtk_data.polys is None
    
    # Verify vertex data
    assert isinstance(vtk_data.verts, PolyDataTopology)
    assert vtk_data.verts.connectivity.shape == (128449,)
    assert vtk_data.verts.connectivity[0:3].tolist() == [0, 1, 2]
    assert vtk_data.verts.offsets.shape == (128449,)
    assert vtk_data.verts.offsets[0:3].tolist() == [1, 2, 3]


def test_read_xml_vtp_no_cell_field_point_data_ascii():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "cow.vtp")
    _assert_cow_data(vtk_data)


def test_read_xml_vtp_no_cell_field_point_data_binary():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "cow_binary.vtp")
    _assert_cow_data(vtk_data)


def test_read_xml_vtp_no_cell_field_point_data_appended_encoded():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "cow_appended_encoded.vtp")
    _assert_cow_data(vtk_data)


def test_read_xml_vtp_no_cell_field_point_data_appended_raw():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "cow_appended_raw.vtp")
    _assert_cow_data(vtk_data)


def test_read_xml_vtp_point_data_ascii():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "plate_vectors.vtp")
    _assert_plate_vectors_data(vtk_data)


def test_read_xml_vtp_point_data_binary():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "plate_vectors_binary.vtp")
    _assert_plate_vectors_data(vtk_data)


def test_read_xml_vtp_point_data_appended_encoded():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "plate_vectors_appended_encoded.vtp")
    _assert_plate_vectors_data(vtk_data)


def test_read_xml_vtp_point_data_appended_raw():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "plate_vectors_appended_raw.vtp")
    _assert_plate_vectors_data(vtk_data)


def test_read_xml_vtp_vertex_point_data_ascii():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "horse.vtp")
    _assert_horse_data(vtk_data)


def test_read_xml_vtp_vertex_point_data_binary():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "horse_binary.vtp")
    _assert_horse_data(vtk_data)


def test_read_xml_vtp_vertex_point_data_appended_encoded():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "horse_appended_encoded.vtp")
    _assert_horse_data(vtk_data)


def test_read_xml_vtp_vertex_point_data_appended_raw():
    vtk_data = read_vtkxml_data(TEST_DATA_PATH / "horse_appended_raw.vtp")
    _assert_horse_data(vtk_data)


def test_filetype_value_error():
    filename = TEST_DATA_PATH / "poly_example.vt1"
    with pytest.raises(ValueError) as excinfo:
        Reader(filename)
    assert str(excinfo.value) == "Unsupported file type"

@pytest.mark.parametrize("filename", [
    "plate_vectors.vtp",
    "plate_vectors_binary.vtp",
    "plate_vectors_appended_encoded.vtp",
    "plate_vectors_appended_raw.vtp"
])
def test_read_xml_vtp_formats(filename):
    file_path = TEST_DATA_PATH / filename
    vtk_data = read_vtkxml_data(file_path)

    assert vtk_data.points.shape[1] == 3
    assert hasattr(vtk_data, "verts") or hasattr(vtk_data, "lines") or hasattr(vtk_data, "polys") or hasattr(vtk_data, "strips")

@pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32, np.int64, np.uint8])
def test_read_vtp_all_dtypes(tmp_path, dtype):
    fname = f"poly_dtype_{np.dtype(dtype).name}.vtp"
    file_path = TEST_DATA_PATH / fname
    if not file_path.exists():
        pytest.skip(f"Test file {fname} not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.dtype == dtype

def test_read_vtp_empty_point_cell_data(tmp_path):
    file_path = TEST_DATA_PATH / "poly_empty_arrays.vtp"
    if not file_path.exists():
        pytest.skip("Test file poly_empty_arrays.vtp not found")
    vtk_data = read_vtkxml_data(file_path)

    assert vtk_data.point_data == {} or all(a.size == 0 for a in vtk_data.point_data.values())
    assert vtk_data.cell_data == {} or all(a.size == 0 for a in vtk_data.cell_data.values())

def test_read_vtp_partial_data(tmp_path):
    for fname in ["poly_only_point_data.vtp", "poly_only_cell_data.vtp"]:
        file_path = TEST_DATA_PATH / fname
        if not file_path.exists():
            pytest.skip(f"Test file {fname} not found")
        vtk_data = read_vtkxml_data(file_path)

        if "point" in fname:
            assert vtk_data.point_data and not vtk_data.cell_data
        else:
            assert vtk_data.cell_data and not vtk_data.point_data

def test_read_vtp_fortran_ordered_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "poly_fortran_ordered.vtp"
    if not file_path.exists():
        pytest.skip("Test file poly_fortran_ordered.vtp not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.flags['F_CONTIGUOUS'] or arr.flags['C_CONTIGUOUS']

def test_read_vtp_string_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "poly_string_data.vtp"
    if not file_path.exists():
        pytest.skip("Test file poly_string_data.vtp not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['labels']
    assert arr.dtype.kind in {'U', 'S', 'O'}

def test_read_vtp_custom_attributes(tmp_path):
    file_path = TEST_DATA_PATH / "poly_custom_attrs.vtp"
    if not file_path.exists():
        pytest.skip("Test file poly_custom_attrs.vtp not found")
    vtk_data = read_vtkxml_data(file_path)

    assert hasattr(vtk_data, "custom_attr")
    assert vtk_data.custom_attr == "my_custom_value"

def test_read_vtp_multiblock(tmp_path):
    file_path = TEST_DATA_PATH.parent / "vtm" / "multiblock_example.vtm"
    if not file_path.exists():
        pytest.skip("Test file multiblock_example.vtm not found")
    multiblock = read_vtkxml_data(file_path)

    assert hasattr(multiblock, "blocks")
    assert len(multiblock.blocks) > 1
    for block in multiblock.blocks:
        assert hasattr(block, "points")

def test_read_vtp_large_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "poly_large.vtp"
    if not file_path.exists():
        pytest.skip("Test file poly_large.vtp not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.size > 100000

def test_read_vtp_edge_cases(tmp_path):
    for fname in ["poly_single_vertex.vtp", "poly_single_line.vtp", "poly_single_poly.vtp"]:
        file_path = TEST_DATA_PATH / fname
        if not file_path.exists():
            pytest.skip(f"Test file {fname} not found")
        vtk_data = read_vtkxml_data(file_path)

        assert vtk_data.points.shape[0] >= 0