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
from vtkio.vtk_structures import GridCoordinates
from vtkio.reader.xml import Reader, read_vtkxml_data


# Local Sources


# Set test data directory
TEST_DATA_PATH = Path(__file__).parent.parent / "TestData" / "vtr"

# Expected test values as constants
EXPECTED_NUM_CELLS = 72
EXPECTED_NUM_POINTS = 147
EXPECTED_COORD_X_SIZE = 7
EXPECTED_COORD_Y_SIZE = 7
EXPECTED_COORD_Z_SIZE = 3
EXPECTED_PRESSURE_SIZE = 72
EXPECTED_PRESSURE_VALUE_1 = 12
EXPECTED_PRESSURE_VALUE_47 = 63
EXPECTED_TEMP_SIZE = 147
EXPECTED_TEMP_VALUE_1 = 0.156746658792
EXPECTED_TEMP_VALUE_144 = 0.568486859039


def assert_vtr_data(vtk_data):
    """
    Assert expected values for VTR file data.
    
    Parameters
    ----------
    vtk_data : RectilinearData
        Parsed VTK data to validate
    """
    # Assert coordinates properties
    assert vtk_data.coordinates.num_cells == EXPECTED_NUM_CELLS
    assert vtk_data.coordinates.num_points == EXPECTED_NUM_POINTS
    assert vtk_data.coordinates.x.size == EXPECTED_COORD_X_SIZE
    assert vtk_data.coordinates.y.size == EXPECTED_COORD_Y_SIZE
    assert vtk_data.coordinates.z.size == EXPECTED_COORD_Z_SIZE
    
    # Assert cell data
    assert vtk_data.cell_data['pressure'].size == EXPECTED_PRESSURE_SIZE
    assert vtk_data.cell_data['pressure'][1] == EXPECTED_PRESSURE_VALUE_1
    assert vtk_data.cell_data['pressure'][47] == EXPECTED_PRESSURE_VALUE_47
    
    # Assert point data
    assert vtk_data.point_data['temp'].size == EXPECTED_TEMP_SIZE
    assert np.allclose(vtk_data.point_data['temp'][1], EXPECTED_TEMP_VALUE_1)
    assert np.allclose(vtk_data.point_data['temp'][144], EXPECTED_TEMP_VALUE_144)


def test_filetype_value_error():
    filename = TEST_DATA_PATH / "rect_example.vt1"
    with pytest.raises(ValueError) as excinfo:
        Reader(filename)
    assert str(excinfo.value) == "Unsupported file type"


def test_read_xml_vtr_ascii():
    file_path = TEST_DATA_PATH / "rect_example_points_cells.vtr"
    vtk_data = read_vtkxml_data(file_path)

    assert_vtr_data(vtk_data)


def test_read_xml_vtr_binary():
    file_path = TEST_DATA_PATH / "rect_example_points_cells_binary.vtr"
    vtk_data = read_vtkxml_data(file_path)

    assert_vtr_data(vtk_data)


def test_read_xml_vtr_appended_encoded():
    file_path = TEST_DATA_PATH / "rect_example_points_cells_appended_encoded.vtr"
    vtk_data = read_vtkxml_data(file_path)

    assert_vtr_data(vtk_data)


def test_read_xml_vtr_appended_raw():
    file_path = TEST_DATA_PATH / "rect_example_points_cells_appended_raw.vtr"
    vtk_data = read_vtkxml_data(file_path)

    assert_vtr_data(vtk_data)


@pytest.mark.parametrize("filename", [
    "rect_example_points_cells.vtr",
    "rect_example_points_cells_binary.vtr",
    "rect_example_points_cells_appended_encoded.vtr",
    "rect_example_points_cells_appended_raw.vtr"
])
def test_read_xml_vtr_formats(filename):
    file_path = TEST_DATA_PATH / filename
    vtk_data = read_vtkxml_data(file_path)

    # vtk coordinates do not have to have a specific label, but the order of the coordinates is important
    # assigned to x y and z
    assert hasattr(vtk_data, "coordinates")
    assert isinstance(vtk_data.coordinates, GridCoordinates)
    assert hasattr(vtk_data.coordinates, "x")
    assert hasattr(vtk_data.coordinates, "y")
    assert hasattr(vtk_data.coordinates, "z")


@pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32, np.int64, np.uint8])
def test_read_vtr_all_dtypes(tmp_path, dtype):
    fname = f"rect_dtype_{np.dtype(dtype).name}.vtr"
    file_path = TEST_DATA_PATH / fname
    if not file_path.exists():
        pytest.skip(f"Test file {fname} not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.dtype == dtype


def test_read_vtr_empty_point_cell_data(tmp_path):
    file_path = TEST_DATA_PATH / "rect_empty_arrays.vtr"
    if not file_path.exists():
        pytest.skip("Test file rect_empty_arrays.vtr not found")
    vtk_data = read_vtkxml_data(file_path)

    assert vtk_data.point_data == {} or all(a.size == 0 for a in vtk_data.point_data.values())
    assert vtk_data.cell_data == {} or all(a.size == 0 for a in vtk_data.cell_data.values())


def test_read_vtr_partial_data(tmp_path):
    for fname in ["rect_only_point_data.vtr", "rect_only_cell_data.vtr"]:
        file_path = TEST_DATA_PATH / fname
        if not file_path.exists():
            pytest.skip(f"Test file {fname} not found")
        vtk_data = read_vtkxml_data(file_path)

        if "point" in fname:
            assert vtk_data.point_data and not vtk_data.cell_data
        else:
            assert vtk_data.cell_data and not vtk_data.point_data


def test_read_vtr_fortran_ordered_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "rect_fortran_ordered.vtr"
    if not file_path.exists():
        pytest.skip("Test file rect_fortran_ordered.vtr not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.flags['F_CONTIGUOUS'] or arr.flags['C_CONTIGUOUS']


def test_read_vtr_string_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "rect_string_data.vtr"
    if not file_path.exists():
        pytest.skip("Test file rect_string_data.vtr not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['labels']
    assert arr.dtype.kind in {'U', 'S', 'O'}


def test_read_vtr_custom_attributes(tmp_path):
    file_path = TEST_DATA_PATH / "rect_custom_attrs.vtr"
    if not file_path.exists():
        pytest.skip("Test file rect_custom_attrs.vtr not found")
    vtk_data = read_vtkxml_data(file_path)

    assert hasattr(vtk_data, "custom_attr")
    assert vtk_data.custom_attr == "my_custom_value"


def test_read_vtr_multiblock(tmp_path):
    file_path = TEST_DATA_PATH.parent / "vtm" / "multiblock_example.vtm"
    if not file_path.exists():
        pytest.skip("Test file multiblock_example.vtm not found")
    multiblock = read_vtkxml_data(file_path)

    assert hasattr(multiblock, "blocks")
    assert len(multiblock.blocks) > 1
    for block in multiblock.blocks:
        assert hasattr(block, "x")
        assert hasattr(block, "y")
        assert hasattr(block, "z")


def test_read_vtr_large_arrays(tmp_path):
    file_path = TEST_DATA_PATH / "rect_large.vtr"
    if not file_path.exists():
        pytest.skip("Test file rect_large.vtr not found")
    vtk_data = read_vtkxml_data(file_path)

    arr = vtk_data.point_data['A']
    assert arr.size > 100000


def test_read_vtr_edge_cases(tmp_path):
    for fname in ["rect_single_cell.vtr", "rect_single_point.vtr", "rect_degenerate.vtr"]:
        file_path = TEST_DATA_PATH / fname
        if not file_path.exists():
            pytest.skip(f"Test file {fname} not found")
        vtk_data = read_vtkxml_data(file_path)

        assert hasattr(vtk_data, "x")
        assert hasattr(vtk_data, "y")
        assert hasattr(vtk_data, "z")