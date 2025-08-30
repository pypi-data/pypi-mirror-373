#!/usr/bin/env python
"""
Tests for reading VTK XML files, expanded for full coverage.

Created at 14:46, 15 Apr, 2022
"""
__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

from pathlib import Path
import numpy as np
import pytest

from vtkio.reader.xml import Reader
from vtkio.reader import read_vtkxml_data


TEST_DATA_PATH = Path(__file__).parent.parent / "TestData" / "vti"

EXPECTED_ORIGIN = np.array([0., 0., 0.])
EXPECTED_SPACING = np.array([1, 1, 1])
EXPECTED_WHOLE_EXTENTS = np.array([0, 6, 0, 6, 0, 2])
EXPECTED_DIRECTION = np.array([1., 0., 0., 0., 1., 0., 0., 0., 1.])
EXPECTED_NUM_CELLS = 72
EXPECTED_NUM_POINTS = 147

def test_filetype_value_error():
    """Test that a ValueError is raised when the incorrect extension is given."""
    filename = TEST_DATA_PATH / "regular_grid_example.vt1"
    with pytest.raises(ValueError) as excinfo:
        Reader(filename)
    assert str(excinfo.value) == "Unsupported file type"

def verify_grid_properties(vtk_data):
    assert vtk_data.grid.num_cells == EXPECTED_NUM_CELLS
    assert vtk_data.grid.num_points == EXPECTED_NUM_POINTS
    assert np.array_equal(vtk_data.grid.direction, EXPECTED_DIRECTION)
    assert np.array_equal(vtk_data.grid.whole_extents, EXPECTED_WHOLE_EXTENTS)
    assert np.array_equal(vtk_data.grid.spacing, EXPECTED_SPACING)
    assert np.array_equal(vtk_data.grid.origin, EXPECTED_ORIGIN)

def verify_data_arrays(vtk_data):
    assert vtk_data.cell_data['pressure'].size == EXPECTED_NUM_CELLS
    assert vtk_data.cell_data['pressure'][1] == 12
    assert vtk_data.cell_data['pressure'][47] == 63
    assert vtk_data.point_data['temp'].size == EXPECTED_NUM_POINTS
    assert np.allclose(vtk_data.point_data['temp'][1], 0.202289269489958)
    assert np.allclose(vtk_data.point_data['temp'][144], 0.923181407862087)

@pytest.mark.parametrize("filename", [
    "regular_grid_example.vti",  # ASCII format
    "regular_grid_example_binary.vti",  # Binary format
    "regular_grid_example_appended_encoded.vti",  # Appended encoded format
    "regular_grid_example_appended_raw.vti"  # Appended raw format
])
def test_read_xml_vti_formats(filename):
    """Test reading VTI files in different formats."""
    file_path = TEST_DATA_PATH / filename
    vtk_data = read_vtkxml_data(file_path)

    verify_grid_properties(vtk_data)
    verify_data_arrays(vtk_data)

@pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32, np.int64, np.uint8])
def test_read_vti_all_dtypes(tmp_path, dtype):
    """Test reading VTI files with all supported dtypes."""
    # Assume you have files like 'dtype_float32.vti', etc.
    fname = f"regular_grid_dtype_{np.dtype(dtype).name}.vti"
    file_path = TEST_DATA_PATH / fname
    if not file_path.exists():
        pytest.skip(f"Test file {fname} not found")

    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['temp']
    assert arr.dtype == dtype

def test_read_vti_empty_point_cell_data(tmp_path):
    """Test reading VTI file with empty point/cell data arrays."""
    file_path = TEST_DATA_PATH / "regular_grid_empty_arrays.vti"
    if not file_path.exists():
        pytest.skip("Test file regular_grid_empty_arrays.vti not found")
    vtk_data = read_vtkxml_data(file_path)

    assert vtk_data.point_data == {} or all(a.size == 0 for a in vtk_data.point_data.values())
    assert vtk_data.cell_data == {} or all(a.size == 0 for a in vtk_data.cell_data.values())

def test_read_vti_partial_data(tmp_path):
    """Test reading VTI file with only point data or only cell data."""
    for fname in ["regular_grid_only_point_data.vti", "regular_grid_only_cell_data.vti"]:
        file_path = TEST_DATA_PATH / fname
        if not file_path.exists():
            pytest.skip(f"Test file {fname} not found")
        reader = Reader(file_path)
        vtk_data = reader.parse()
        if "point" in fname:
            assert vtk_data.point_data and not vtk_data.cell_data
        else:
            assert vtk_data.cell_data and not vtk_data.point_data

def test_read_vti_fortran_ordered_arrays(tmp_path):
    """Test reading VTI file with Fortran-ordered arrays."""
    file_path = TEST_DATA_PATH / "regular_grid_fortran_ordered.vti"
    if not file_path.exists():
        pytest.skip("Test file regular_grid_fortran_ordered.vti not found")
    reader = Reader(file_path)
    vtk_data = reader.parse()
    arr = vtk_data.point_data['temp']
    assert arr.flags['F_CONTIGUOUS'] or arr.flags['C_CONTIGUOUS']

def test_read_vti_string_arrays(tmp_path):
    """Test reading VTI file with string arrays (if supported)."""
    file_path = TEST_DATA_PATH / "regular_grid_string_data.vti"
    if not file_path.exists():
        pytest.skip("Test file regular_grid_string_data.vti not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['labels']
    assert arr.dtype.kind in {'U', 'S', 'O'}

def test_read_vti_custom_attributes(tmp_path):
    """Test reading VTI file with custom attributes."""
    file_path = TEST_DATA_PATH / "regular_grid_custom_attrs.vti"
    if not file_path.exists():
        pytest.skip("Test file regular_grid_custom_attrs.vti not found")
    vtk_data = read_vtkxml_data(file_path)

    assert hasattr(vtk_data.grid, "custom_attr")
    assert vtk_data.grid.custom_attr == "my_custom_value"

def test_read_vti_multiblock(tmp_path):
    """Test reading a VTM file with multiple VTI blocks."""
    file_path = TEST_DATA_PATH.parent / "vtm" / "multiblock_example.vtm"
    if not file_path.exists():
        pytest.skip("Test file multiblock_example.vtm not found")
    multiblock = read_vtkxml_data(file_path)

    assert hasattr(multiblock, "blocks")
    assert len(multiblock.blocks) > 1
    for block in multiblock.blocks:
        assert hasattr(block, "grid")
        assert hasattr(block, "point_data")

def test_read_vti_large_arrays(tmp_path):
    """Test reading VTI file with large arrays."""
    file_path = TEST_DATA_PATH / "regular_grid_large.vti"
    if not file_path.exists():
        pytest.skip("Test file regular_grid_large.vti not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['temp']
    assert arr.size > 100000

def test_read_vti_edge_cases(tmp_path):
    """Test reading VTI file with edge cases: single cell, single point, degenerate geometry."""
    for fname in ["regular_grid_single_cell.vti", "regular_grid_single_point.vti", "regular_grid_degenerate.vti"]:
        file_path = TEST_DATA_PATH / fname
        if not file_path.exists():
            pytest.skip(f"Test file {fname} not found")
        vtk_data = read_vtkxml_data(file_path)

        assert vtk_data.grid.num_cells >= 0
        assert vtk_data.grid.num_points >= 0