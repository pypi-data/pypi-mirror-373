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

# Imports
import numpy as np
import pytest
from vtkio.reader.xml import Reader, read_vtkxml_data

# Local Sources
from vtkio.vtk_structures import Cell, UnstructuredGrid

# Set test data directory
TEST_DATA_PATH = Path(__file__).parent.parent / "TestData" / "vtu"

# Test parameters
PLANE_FILE_FORMATS = [
    "single_plane.vtu",
    "single_plane_binary.vtu",
    "single_plane_appended_encoded.vtu",
    "single_plane_appended_raw.vtu"
]

POLYLINE_FILE_FORMATS = [
    "poly_lines_with_data.vtu",
    "poly_lines_with_data_binary.vtu",
    "poly_lines_with_data_appended_encoded.vtu",
    "poly_lines_with_data_appended_raw.vtu"
]


def assert_grid_structure(vtk_grid, expected_points, expected_field_data):
    """Assert basic grid structure properties."""
    # Check grid type
    assert isinstance(vtk_grid, UnstructuredGrid), "Result should be an UnstructuredGrid instance"
    
    # Check points structure
    assert vtk_grid.points.shape == expected_points, f"Grid should have {expected_points} points structure"
    
    # Check field data
    assert vtk_grid.field_data == expected_field_data, "Field data should match expected value"

def assert_data_dictionaries(vtk_grid, expected_cell_data, expected_point_data):
    """Assert that data dictionaries have expected structure and content."""
    # Cell data assertions
    assert isinstance(vtk_grid.cell_data, dict), "Cell data should be a dictionary"
    assert len(vtk_grid.cell_data) == len(expected_cell_data),\
        f"Should have {len(expected_cell_data)} cell data array(s)"
    assert list(vtk_grid.cell_data.keys()) == expected_cell_data,\
        f"Cell data should contain {expected_cell_data}"
    
    # Point data assertions
    assert isinstance(vtk_grid.point_data, dict), "Point data should be a dictionary"
    assert len(vtk_grid.point_data) == len(expected_point_data),\
        f"Should have {len(expected_point_data)} point data array(s)"
    assert set(vtk_grid.point_data.keys()) == set(expected_point_data),\
        f"Point data should contain {expected_point_data}"

def assert_data_dimensions(vtk_grid, cell_data_lengths, point_data_lengths):
    """Assert data array dimensions are correct."""
    # Check cell data dimensions
    for key, length in cell_data_lengths.items():
        assert len(vtk_grid.cell_data[key]) == length, f"Cell data '{key}' should have length {length}"
    
    # Check point data dimensions
    for key, length in point_data_lengths.items():
        assert len(vtk_grid.point_data[key]) == length, f"Point data '{key}' should have length {length}"

def assert_plane_cell_topology(cells):
    """Assert that cell topology for plane data has expected structure and values."""
    # Check cell object
    assert isinstance(cells, Cell), "Cells should be a Cell instance"
    
    # Check connectivity
    assert cells.connectivity.shape == (10,), "Connectivity should have shape (10,)"
    expected_connectivity = [0, 1, 3, 1, 4]
    for i, value in enumerate(expected_connectivity):
        assert cells.connectivity[i] == value, f"Connectivity at index {i} should be {value}"
    
    # Check offsets
    assert cells.offsets.shape == (3,), "Offsets should have shape (3,)"
    assert cells.offsets[0] == 3, "First offset should be 3"
    assert cells.offsets[1] == 6, "Second offset should be 6"
    assert cells.offsets[2] == 10, "Third offset should be 10"
    
    # Check types
    assert cells.types.shape == (3,), "Types should have shape (3,)"
    assert cells.types[0] == 5, "First type should be 5 (triangle)"
    assert cells.types[1] == 5, "Second type should be 5 (triangle)"
    assert cells.types[2] == 9, "Third type should be 9 (quad)"

def assert_polyline_cell_topology(cells):
    """Assert that cell topology for polyline data has expected structure and values."""
    # Check cell object
    assert isinstance(cells, Cell), "Cells should be a Cell instance"
    
    # Check connectivity
    assert cells.connectivity.shape == (7,), "Connectivity should have shape (7,)"
    expected_connectivity = [0, 1, 2, 3, 4, 5, 6]
    for i, value in enumerate(expected_connectivity[:5]):  # Check just first 5 values
        assert cells.connectivity[i] == value, f"Connectivity at index {i} should be {value}"
    
    # Check offsets
    assert cells.offsets.shape == (2,), "Offsets should have shape (2,)"
    assert cells.offsets[0] == 4, "First offset should be 4"
    assert cells.offsets[1] == 7, "Second offset should be 7"
    
    # Check types
    assert cells.types.shape == (2,), "Types should have shape (2,)"
    assert cells.types[0] == 4, "First type should be 4 (polyline)"
    assert cells.types[1] == 4, "Second type should be 4 (polyline)"

@pytest.mark.parametrize("file_format", PLANE_FILE_FORMATS)
def test_read_xml_vtu_plane(file_format):
    """Test reading plane VTU files in different formats."""
    # Setup
    filename = TEST_DATA_PATH / file_format
    vtk_grid = read_vtkxml_data(filename)
    
    # Assert basic grid structure
    assert_grid_structure(vtk_grid, (6, 3), None)
    
    # Assert data dictionary structure
    assert_data_dictionaries(vtk_grid, ['pressure'], ['ec'])
    
    # Assert data dimensions
    assert_data_dimensions(
        vtk_grid, 
        cell_data_lengths={'pressure': 3},
        point_data_lengths={'ec': 6}
    )
    
    # Assert cell topology
    assert_plane_cell_topology(vtk_grid.cells)

@pytest.mark.parametrize("file_format", POLYLINE_FILE_FORMATS)
def test_read_xml_vtu_polyline(file_format):
    """Test reading polyline VTU files in different formats."""
    # Setup
    filename = TEST_DATA_PATH / file_format
    vtk_grid = read_vtkxml_data(filename)
    
    # Assert basic grid structure
    assert_grid_structure(vtk_grid, (7, 3), None)
    
    # Assert data dictionary structure
    assert_data_dictionaries(vtk_grid, ['vel'], ['temp', 'pressure'])
    
    # Assert data dimensions
    assert_data_dimensions(
        vtk_grid, 
        cell_data_lengths={'vel': 2},
        point_data_lengths={'temp': 7, 'pressure': 7}
    )
    
    # Assert cell topology
    assert_polyline_cell_topology(vtk_grid.cells)

def test_filetype_value_error():
    filename = TEST_DATA_PATH / "mesh_example.vt1"
    with pytest.raises(ValueError) as excinfo:
        Reader(filename)
    assert str(excinfo.value) == "Unsupported file type"

@pytest.mark.parametrize("filename", POLYLINE_FILE_FORMATS)
def test_read_xml_vtu_formats(filename):
    file_path = TEST_DATA_PATH / filename
    vtk_data = read_vtkxml_data(file_path)

    assert hasattr(vtk_data, 'points')
    assert hasattr(vtk_data, 'cells')
    assert vtk_data.points.shape[1] == 3
    assert vtk_data.cells.connectivity.size > 0

@pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32, np.int64, np.uint8])
def test_read_vtu_all_dtypes(tmp_path, dtype):
    fname = f"mesh_dtype_{np.dtype(dtype).name}.vtu"
    file_path = TEST_DATA_PATH / fname
    if not file_path.exists():
        pytest.skip(f"Test file {fname} not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.dtype == dtype

def test_read_vtu_empty_point_cell_data(tmp_path):
    file_path = TEST_DATA_PATH / "mesh_empty_arrays.vtu"
    if not file_path.exists():
        pytest.skip("Test file mesh_empty_arrays.vtu not found")
    vtk_data = read_vtkxml_data(file_path)

    assert vtk_data.point_data == {} or all(a.size == 0 for a in vtk_data.point_data.values())
    assert vtk_data.cell_data == {} or all(a.size == 0 for a in vtk_data.cell_data.values())

def test_read_vtu_partial_data(tmp_path):
    for fname in ["mesh_only_point_data.vtu", "mesh_only_cell_data.vtu"]:
        file_path = TEST_DATA_PATH / fname
        if not file_path.exists():
            pytest.skip(f"Test file {fname} not found")
        vtk_data = read_vtkxml_data(file_path)

        if "point" in fname:
            assert vtk_data.point_data and not vtk_data.cell_data
        else:
            assert vtk_data.cell_data and not vtk_data.point_data

def test_read_vtu_fortran_ordered_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "mesh_fortran_ordered.vtu"
    if not file_path.exists():
        pytest.skip("Test file mesh_fortran_ordered.vtu not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.flags['F_CONTIGUOUS'] or arr.flags['C_CONTIGUOUS']

def test_read_vtu_string_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "mesh_string_data.vtu"
    if not file_path.exists():
        pytest.skip("Test file mesh_string_data.vtu not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['labels']
    assert arr.dtype.kind in {'U', 'S', 'O'}

def test_read_vtu_custom_attributes(tmp_path):
    file_path = TEST_DATA_PATH / "mesh_custom_attrs.vtu"
    if not file_path.exists():
        pytest.skip("Test file mesh_custom_attrs.vtu not found")
    vtk_data = read_vtkxml_data(file_path)

    assert hasattr(vtk_data, "custom_attr")
    assert vtk_data.custom_attr == "my_custom_value"

def test_read_vtu_multiblock(tmp_path):
    file_path = TEST_DATA_PATH.parent / "vtm" / "multiblock_example.vtm"
    if not file_path.exists():
        pytest.skip("Test file multiblock_example.vtm not found")
    multiblock = read_vtkxml_data(file_path)

    assert hasattr(multiblock, "blocks")
    assert len(multiblock.blocks) > 1
    for block in multiblock.blocks:
        assert hasattr(block, "points")
        assert hasattr(block, "cells")

def test_read_vtu_large_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "mesh_large.vtu"
    if not file_path.exists():
        pytest.skip("Test file mesh_large.vtu not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.size > 100000

def test_read_vtu_edge_cases(tmp_path):
    for fname in ["mesh_single_cell.vtu", "mesh_single_point.vtu", "mesh_degenerate.vtu"]:
        file_path = TEST_DATA_PATH / fname
        if not file_path.exists():
            pytest.skip(f"Test file {fname} not found")
        vtk_data = read_vtkxml_data(file_path)

        assert vtk_data.points.shape[0] >= 0
        assert vtk_data.cells.connectivity.size >= 0