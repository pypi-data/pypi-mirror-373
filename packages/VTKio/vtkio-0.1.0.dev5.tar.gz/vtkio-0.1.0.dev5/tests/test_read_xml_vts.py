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
from vtkio.vtk_structures import StructuredData

# Set test data directory
TEST_DATA_PATH = Path(__file__).parent.parent / "TestData" / "vts"

# Test file configurations
DISTORTED_CUBE_FILES = [
    "distorted_cube.vts",                 # ASCII
    "distorted_cube_binary.vts",          # Binary
    "distorted_cube_appended_encoded.vts", # Appended encoded
    "distorted_cube_appended_raw.vts"     # Appended raw
]

STRUCTURED_SECTION_FILES = [
    "structured_section.vts",                 # ASCII
    "structured_section_binary.vts",          # Binary
    "structured_section_appended_encoded.vts", # Appended encoded
    "structured_section_appended_raw.vts"     # Appended raw
]

def validate_distorted_cube_data(vtk_data):
    """Validate distorted cube data structure and values."""
    # Assert result type
    assert isinstance(vtk_data, StructuredData)
    
    # Assert data types
    assert vtk_data.field_data is None
    assert isinstance(vtk_data.cell_data, dict)
    assert len(vtk_data.cell_data) == 1
    assert isinstance(vtk_data.point_data, dict)
    assert len(vtk_data.point_data) == 1
    
    # Assert data keys
    expected_cell_data = ['pressure']
    expected_point_data = ['temp']
    assert list(vtk_data.cell_data.keys()) == expected_cell_data
    assert list(vtk_data.point_data.keys()) == expected_point_data
    
    # Assert extents
    assert vtk_data.whole_extents.size == 6
    
    # Assert results to expect
    assert vtk_data.num_cells == 72
    assert vtk_data.num_points == 147
    assert vtk_data.points.shape[1] == 3
    
    # Assert cell data values
    assert vtk_data.cell_data['pressure'].size == 72
    assert vtk_data.cell_data['pressure'][1] == 12
    assert vtk_data.cell_data['pressure'][47] == 63
    
    # Assert point data values
    assert vtk_data.point_data['temp'].size == 147
    assert np.allclose(vtk_data.point_data['temp'][1], 0.79128334993)
    assert np.allclose(vtk_data.point_data['temp'][144], 0.72054898907)

def validate_structured_section_data(vtk_data):
    """Validate structured section data structure and values."""
    # Assert result type
    assert isinstance(vtk_data, StructuredData)
    
    # Assert data types
    assert vtk_data.field_data is None
    assert vtk_data.cell_data is None
    assert isinstance(vtk_data.point_data, dict)
    assert len(vtk_data.point_data) == 3
    
    # Assert data keys
    expected_point_data = ['Density', 'Momentum', 'StagnationEnergy']
    assert list(vtk_data.point_data.keys()) == expected_point_data
    
    # Assert extents
    assert vtk_data.whole_extents.size == 6
    
    # Assert results to expect
    assert vtk_data.num_cells == 440
    assert vtk_data.num_points == 648
    assert vtk_data.points.shape[1] == 3
    
    # Assert point data values
    assert vtk_data.point_data['Density'].size == 648
    assert np.allclose(vtk_data.point_data['Density'][1], 0.31161246)
    assert np.allclose(vtk_data.point_data['Density'][47], 0.40333515)
    
    assert vtk_data.point_data['StagnationEnergy'].size == 648
    assert np.allclose(vtk_data.point_data['StagnationEnergy'][1], 0.0)
    assert np.allclose(vtk_data.point_data['StagnationEnergy'][144], 0.0)
    
    assert vtk_data.point_data['Momentum'].shape == (648, 3)

@pytest.mark.parametrize("filename", DISTORTED_CUBE_FILES)
def test_read_distorted_cube(filename):
    """Test reading distorted cube VTS files with different encodings."""
    file_path = TEST_DATA_PATH / filename
    vtk_data = read_vtkxml_data(file_path)

    
    validate_distorted_cube_data(vtk_data)

@pytest.mark.parametrize("filename", STRUCTURED_SECTION_FILES)
def test_read_structured_section(filename):
    """Test reading structured section VTS files with different encodings."""
    file_path = TEST_DATA_PATH / filename
    vtk_data = read_vtkxml_data(file_path)

    
    validate_structured_section_data(vtk_data)

def test_filetype_value_error():
    filename = TEST_DATA_PATH / "struct_example.vt1"
    with pytest.raises(ValueError) as excinfo:
        Reader(filename)
    assert str(excinfo.value) == "Unsupported file type"

@pytest.mark.parametrize("filename", [
    "sample_struct_grid_point_cell_scalars.vts",
    "sample_struct_grid_point_cell_scalars_binary.vts",
    "sample_struct_grid_point_cell_scalars_appended_encoded.vts",
    "sample_struct_grid_point_cell_scalars_appended_raw.vts"
])
def test_read_xml_vts_formats(filename):
    file_path = TEST_DATA_PATH / filename
    vtk_data = read_vtkxml_data(file_path)

    assert hasattr(vtk_data, "points")
    assert hasattr(vtk_data, "cell_data")
    assert hasattr(vtk_data, "field_data")
    assert hasattr(vtk_data, "point_data")
    assert hasattr(vtk_data, "whole_extents")

@pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32, np.int64, np.uint8])
def test_read_vts_all_dtypes(tmp_path, dtype):
    fname = f"struct_dtype_{np.dtype(dtype).name}.vts"
    file_path = TEST_DATA_PATH / fname
    if not file_path.exists():
        pytest.skip(f"Test file {fname} not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.dtype == dtype

def test_read_vts_empty_point_cell_data(tmp_path):
    file_path = TEST_DATA_PATH / "struct_empty_arrays.vts"
    if not file_path.exists():
        pytest.skip("Test file struct_empty_arrays.vts not found")
    vtk_data = read_vtkxml_data(file_path)

    assert vtk_data.point_data == {} or all(a.size == 0 for a in vtk_data.point_data.values())
    assert vtk_data.cell_data == {} or all(a.size == 0 for a in vtk_data.cell_data.values())

def test_read_vts_partial_data(tmp_path):
    for fname in ["struct_only_point_data.vts", "struct_only_cell_data.vts"]:
        file_path = TEST_DATA_PATH / fname
        if not file_path.exists():
            pytest.skip(f"Test file {fname} not found")
        vtk_data = read_vtkxml_data(file_path)

        if "point" in fname:
            assert vtk_data.point_data and not vtk_data.cell_data
        else:
            assert vtk_data.cell_data and not vtk_data.point_data

def test_read_vts_fortran_ordered_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "struct_fortran_ordered.vts"
    if not file_path.exists():
        pytest.skip("Test file struct_fortran_ordered.vts not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.flags['F_CONTIGUOUS'] or arr.flags['C_CONTIGUOUS']

def test_read_vts_string_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "struct_string_data.vts"
    if not file_path.exists():
        pytest.skip("Test file struct_string_data.vts not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['labels']
    assert arr.dtype.kind in {'U', 'S', 'O'}

def test_read_vts_custom_attributes(tmp_path):
    file_path = TEST_DATA_PATH / "struct_custom_attrs.vts"
    if not file_path.exists():
        pytest.skip("Test file struct_custom_attrs.vts not found")
    vtk_data = read_vtkxml_data(file_path)

    assert hasattr(vtk_data, "custom_attr")
    assert vtk_data.custom_attr == "my_custom_value"

def test_read_vts_multiblock(tmp_path):
    file_path = TEST_DATA_PATH.parent / "vtm" / "multiblock_example.vtm"
    if not file_path.exists():
        pytest.skip("Test file multiblock_example.vtm not found")
    multiblock = read_vtkxml_data(file_path)

    assert hasattr(multiblock, "blocks")
    assert len(multiblock.blocks) > 1
    for block in multiblock.blocks:
        assert hasattr(block, "points")
        assert hasattr(block, "cells")

def test_read_vts_large_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "struct_large.vts"
    if not file_path.exists():
        pytest.skip("Test file struct_large.vts not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.size > 100000

def test_read_vts_edge_cases(tmp_path):
    for fname in ["struct_single_cell.vts", "struct_single_point.vts", "struct_degenerate.vts"]:
        file_path = TEST_DATA_PATH / fname
        if not file_path.exists():
            pytest.skip(f"Test file {fname} not found")
        vtk_data = read_vtkxml_data(file_path)

        assert hasattr(vtk_data, "points")
        assert hasattr(vtk_data, "cells")