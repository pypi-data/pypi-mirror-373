#!/usr/bin/env python
"""
Test module for VTK Image Data (.vti) file writing functionality.

This module contains comprehensive tests for the write_vti function, covering
various encoding types, data structures, and validation scenarios.

Created at 16:22, 22 Apr, 2025
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2025, J.P.Morrissey'
__credits__ = ['J.P. Morrissey']
__license__ = '{license}'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard Library
import shutil
import tempfile
from pathlib import Path

# Imports
import numpy as np
import pytest

# Local Sources
from vtkio.reader import Reader
from vtkio.vtk_structures import Grid, ImageData
from vtkio.writer.writers import write_vti

# Set random seed for reproducibility
np.random.seed(42)


class InvalidEncodingError(Exception):
    """Custom exception for invalid encoding errors."""

    pass


@pytest.fixture
def test_dir():
    """Fixture to create and clean up a temporary test directory."""
    # Create temporary directory for test files
    temp_dir = tempfile.mkdtemp(prefix="vtkio_test_")
    yield Path(temp_dir)
    # Clean up after tests, even if they fail
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_data_directory():
    """Fixture to get and verify the test data directory."""
    test_data_path = Path(__file__).parent.parent / "TestData" / "vti"
    
    # Check if the test data directory exists
    if not test_data_path.exists():
        pytest.skip(f"Test data directory not found: {test_data_path}. "
                    f"To run this test, create the directory and add required test files.")
    
    return test_data_path


def test_write_vti_basic(test_dir):
    """
    Test that write_vti correctly writes a basic VTI file with minimal data.
    
    Tests basic file generation, metadata correctness, and data integrity.
    """
    test_path = test_dir / "test_output"
    test_file = str(test_path)

    # Create simple test data
    whole_extent = [0, 2, 0, 2, 0, 2]
    piece_extent = [0, 2, 0, 2, 0, 2]
    spacing = [1.0, 1.0, 1.0]
    origin = [0.0, 0.0, 0.0]
    
    # Verify dimensions and array size consistency
    nx, ny, nz = 3, 3, 3  # Size from extent is end+1 - start for each dimension
    expected_point_count = nx * ny * nz  # 27 points total
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 8 cells total

    # Simple point data (temperature)
    point_data = {
        'temperature': np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0,
                                 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0,
                                 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0,
                                 22.0, 23.0, 24.0, 25.0, 26.0], dtype=np.float32)
    }
    
    # Check that input array size matches expected point count
    assert len(point_data['temperature']) == expected_point_count, \
        f"Input point data size {len(point_data['temperature'])} doesn't match expected size {expected_point_count}"

    # Simple cell data (pressure)
    cell_data = {
        'pressure': np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0], dtype=np.float32)
    }
    
    # Check that input array size matches expected cell count
    assert len(cell_data['pressure']) == expected_cell_count, \
        f"Input cell data size {len(cell_data['pressure'])} doesn't match expected size {expected_cell_count}"

    # Write test file
    write_vti(test_file, whole_extent=whole_extent, piece_extent=piece_extent,
              origin=origin, spacing=spacing, point_data=point_data,
              cell_data=cell_data, encoding='ascii')

    # Assert file exists with .vti extension
    output_file = test_path.with_suffix('.vti')
    assert output_file.exists(), "Output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify metadata
    assert data.grid.whole_extents.tolist() == whole_extent, "Whole extent mismatch"
    assert np.array_equal(data.grid.origin, origin), "Origin mismatch"
    assert np.array_equal(data.grid.spacing, spacing), "Spacing mismatch"

    # Verify data
    assert 'temperature' in data.point_data, "Point data missing"
    assert 'pressure' in data.cell_data, "Cell data missing"

    # Verify array values
    assert np.allclose(data.point_data['temperature'], point_data['temperature']), "Point data values mismatch"
    assert np.allclose(data.cell_data['pressure'], cell_data['pressure']), "Cell data values mismatch"


def test_write_vti_different_encodings(test_dir):
    """
    Test that write_vti correctly handles different encodings.
    
    Tests ascii, binary, and appended encoding formats to ensure data integrity
    is maintained regardless of the encoding used.
    """
    # Create simple test data
    whole_extent = [0, 3, 0, 3, 0, 3]
    piece_extent = [0, 3, 0, 3, 0, 3]
    spacing = [0.5, 0.5, 0.5]
    origin = [1.0, 1.0, 1.0]
    
    # Verify dimensions and array size consistency
    nx, ny, nz = 4, 4, 4  # Size from extent is end+1 - start for each dimension
    expected_point_count = nx * ny * nz  # 64 points total
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 27 cells total

    # Create random point data
    point_data = {
        'temperature': np.random.random(expected_point_count).astype(np.float32),
        'velocity': np.random.random((expected_point_count, 3)).astype(np.float32)
    }

    # Create random cell data
    cell_data = {
        'pressure': np.random.random(expected_cell_count).astype(np.float32)
    }

    encodings = ['ascii', 'binary', 'appended']

    for encoding in encodings:
        test_file_name = f"test_output_{encoding}"
        test_path = test_dir / test_file_name
        test_file = str(test_path)

        # Write test file with current encoding
        write_vti(test_file, whole_extent=whole_extent, piece_extent=piece_extent,
                  origin=origin, spacing=spacing, point_data=point_data,
                  cell_data=cell_data, encoding=encoding)

        # Assert file exists with .vti extension
        output_file = test_path.with_suffix('.vti')
        assert output_file.exists(), f"Output file with {encoding} encoding was not created"

        # Read the file back and verify the content
        reader = Reader(str(output_file))
        data = reader.parse()

        # Verify data values
        assert np.allclose(data.point_data['temperature'],
                           point_data['temperature']), f"{encoding} encoding: Point data (temperature) values mismatch"
        assert np.allclose(data.point_data['velocity'],
                           point_data['velocity']), f"{encoding} encoding: Point data (velocity) values mismatch"
        assert np.allclose(data.cell_data['pressure'],
                           cell_data['pressure']), f"{encoding} encoding: Cell data values mismatch"


def test_write_vti_field_data(test_dir):
    """
    Test that write_vti correctly handles field data.
    
    Tests the inclusion of various field data types including scalar, vector, 
    and string data.
    """
    test_path = test_dir / "test_with_field_data"
    test_file = str(test_path)

    # Create simple test data
    whole_extent = [0, 2, 0, 2, 0, 2]
    piece_extent = [0, 2, 0, 2, 0, 2]
    spacing = [1.0, 1.0, 1.0]
    origin = [0.0, 0.0, 0.0]
    
    # Verify dimensions and array size consistency
    nx, ny, nz = 3, 3, 3  # Size from extent is end+1 - start for each dimension
    expected_point_count = nx * ny * nz  # 27 points total
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 8 cells total

    # Simple point and cell data
    point_data = {'temperature': np.ones(expected_point_count, dtype=np.float32) * 20.0}
    cell_data = {'pressure': np.ones(expected_cell_count, dtype=np.float32) * 101.3}

    # Field data
    field_data = {
        'time': np.array([10.5], dtype=np.float32),
        'iteration': np.array([42], dtype=np.int32),
        'simulation_name': np.array(['test_sim'], dtype=np.str_)
    }

    # Write test file
    write_vti(test_file, whole_extent=whole_extent, piece_extent=piece_extent,
              origin=origin, spacing=spacing, point_data=point_data,
              cell_data=cell_data, field_data=field_data, encoding='ascii')

    # Assert file exists with .vti extension
    output_file = test_path.with_suffix('.vti')
    assert output_file.exists(), "Output file was not created"

    # Read the file back and verify content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify field data
    assert 'time' in data.field_data, "Field data (time) missing"
    assert 'iteration' in data.field_data, "Field data (iteration) missing"
    assert 'simulation_name' in data.field_data, "Field data (simulation_name) missing"

    # Check field data values
    assert np.isclose(data.field_data['time'][0], field_data['time'][0]), "Field data (time) value mismatch"
    assert data.field_data['iteration'][0] == field_data['iteration'][0], "Field data (iteration) value mismatch"
    assert data.field_data['simulation_name'][0] == field_data['simulation_name'][0], \
        "Field data (simulation_name) value mismatch"


def test_write_vti_roundtrip_comparison(test_dir):
    """
    Test that data written to a VTI file can be read back identically.
    
    Creates complex ImageData object, writes it to a file, then reads it back
    to ensure all data is preserved correctly during the write-read cycle.
    """
    test_path = test_dir / "test_output"
    test_file = str(test_path)

    # Create a reference file using vtk_structures classes
    grid = Grid(
        whole_extents=np.array([0, 5, 0, 5, 0, 5]),
        origin=np.array([0.0, 0.0, 0.0]),
        spacing=np.array([0.2, 0.2, 0.2]),
        direction=np.array([1, 0, 0, 0, 1, 0, 0, 0, 1])
    )

    # Create vector field point data
    points_shape = tuple(grid.whole_extents[1::2] + 1)
    num_points = np.prod(points_shape)
    x = np.linspace(0, 1, num_points)
    y = np.linspace(0, 1, num_points)
    z = np.linspace(0, 1, num_points)

    vector_field = np.column_stack((x, y, z))
    scalar_field = np.sin(x * 2 * np.pi)

    original_point_data = {
        'vector_field': vector_field,
        'scalar_field': scalar_field
    }

    # Cell data
    cells_shape = tuple(grid.whole_extents[1::2])
    num_cells = np.prod(cells_shape)
    original_cell_data = {
        'cell_scalars': np.arange(num_cells, dtype=np.float32)
    }

    # Field data
    original_field_data = {
        'description': np.array(['Test VTI file'], dtype=np.str_),
        'time_step': np.array([5], dtype=np.int32)
    }

    # Create original data object
    original_data = ImageData(
        point_data=original_point_data,
        cell_data=original_cell_data,
        field_data=original_field_data,
        grid=grid
    )

    # Write data using the ImageData write method (which calls write_vti)
    original_data.write(test_file, xml_encoding='ascii')

    # Assert file exists with .vti extension
    output_file = test_path.with_suffix('.vti')
    assert output_file.exists(), "Output file was not created"

    # Now read the data back
    reader = Reader(str(output_file))
    read_data = reader.parse()

    # Compare grid properties
    assert np.allclose(read_data.grid.whole_extents, original_data.grid.whole_extents), "Whole extents don't match"
    assert np.allclose(read_data.grid.origin, original_data.grid.origin), "Origins don't match"
    assert np.allclose(read_data.grid.spacing, original_data.grid.spacing), "Spacings don't match"

    # Compare point data
    for key in original_data.point_data:
        assert key in read_data.point_data, f"Point data '{key}' missing in read data"
        assert np.allclose(read_data.point_data[key],
                           original_data.point_data[key]), f"Point data '{key}' values don't match"

    # Compare cell data
    for key in original_data.cell_data:
        assert key in read_data.cell_data, f"Cell data '{key}' missing in read data"
        assert np.allclose(read_data.cell_data[key],
                           original_data.cell_data[key]), f"Cell data '{key}' values don't match"

    # Compare field data
    for key in original_data.field_data:
        assert key in read_data.field_data, f"Field data '{key}' missing in read data"
        assert np.array_equal(read_data.field_data[key],
                              original_data.field_data[key]), f"Field data '{key}' values don't match"


def test_write_vti_against_reference_file(test_dir, test_data_directory):
    """
    Test write_vti by comparing output with a reference file.
    
    Uses a reference file from the test data directory to validate that
    write_vti produces identical output when given the same input data.
    
    Parameters
    ----------
    test_dir : Path
        Temporary directory for test output
    test_data_directory : Path
        Directory containing reference test data files
    """
    # Try to find the reference file
    reference_file = test_data_directory / 'regular_grid_example.vti'
    if not reference_file.exists():
        pytest.skip(
            f"Reference file {reference_file} not found. "
            f"To run this test, please add the reference file to the test data directory: {test_data_directory}"
        )

    test_path = test_dir / "test_output"
    test_file = str(test_path)

    # Read the reference file
    reader = Reader(str(reference_file))
    reference_data = reader.parse()

    # Write a new file with the same data
    write_vti(
        test_file,
        whole_extent=reference_data.grid.whole_extents.tolist(),
        piece_extent=reference_data.grid.whole_extents.tolist(),
        origin=reference_data.grid.origin,
        spacing=reference_data.grid.spacing,
        direction=reference_data.grid.direction,
        point_data=reference_data.point_data,
        cell_data=reference_data.cell_data,
        field_data=reference_data.field_data,
        encoding='ascii'
    )

    # Assert file exists with .vti extension
    output_file = test_path.with_suffix('.vti')
    assert output_file.exists(), "Output file was not created"

    # Read the generated file
    reader = Reader(str(output_file))
    test_data = reader.parse()

    # Compare the data structures
    assert np.array_equal(test_data.grid.whole_extents, reference_data.grid.whole_extents), "Whole extents don't match"
    assert np.array_equal(test_data.grid.origin, reference_data.grid.origin), "Origins don't match"
    assert np.array_equal(test_data.grid.spacing, reference_data.grid.spacing), "Spacings don't match"

    # Compare point data
    for key in reference_data.point_data:
        assert key in test_data.point_data, f"Point data '{key}' missing in test data"
        assert np.allclose(test_data.point_data[key],
                           reference_data.point_data[key]), f"Point data '{key}' values don't match"

    # Compare cell data
    for key in reference_data.cell_data:
        assert key in test_data.cell_data, f"Cell data '{key}' missing in test data"
        assert np.allclose(test_data.cell_data[key],
                           reference_data.cell_data[key]), f"Cell data '{key}' values don't match"


def test_write_vti_parameter_validation(test_dir):
    """
    Test validation of required parameters for write_vti.
    
    Tests that appropriate exceptions are raised when required parameters
    are missing or invalid.
    """
    test_path = test_dir / "test_output"
    test_file = str(test_path)
    
    # Test with missing whole_extent (required parameter)
    with pytest.raises(TypeError):
        write_vti(test_file)

    # Test with invalid origin format
    with pytest.raises((ValueError, TypeError)):  # Different implementations might raise different exceptions
        write_vti(test_file, whole_extent=[0, 1, 0, 1, 0, 1], piece_extent=[0, 1, 0, 1, 0, 1],
                  origin="invalid", spacing=[1, 1, 1])
    
    # Test with invalid spacing format
    with pytest.raises((ValueError, TypeError)):  # Different implementations might raise different exceptions
        write_vti(test_file, whole_extent=[0, 1, 0, 1, 0, 1], piece_extent=[0, 1, 0, 1, 0, 1],
                  origin=[0, 0, 0], spacing="invalid")


def test_write_vti_with_invalid_data(test_dir):
    """
    Test that write_vti correctly handles invalid data.
    
    Tests error handling for invalid file format and encoding specifications.
    """
    test_path = test_dir / "test_output"
    test_file = str(test_path)
    
    # Test with incorrect file format
    with pytest.raises(ValueError) as excinfo:
        write_vti(test_file, whole_extent=[0, 1, 0, 1, 0, 1], piece_extent=[0, 1, 0, 1, 0, 1],
                  spacing=[1, 1, 1], point_data=None, cell_data=None, field_data=None,
                  file_format='invalid_format')
    assert "Unsupported file format" in str(excinfo.value)
    
    # Test with invalid encoding (for XML format)
    # We should define the specific exception type expected
    with pytest.raises((ValueError, NotImplementedError)) as excinfo:
        write_vti(test_file, whole_extent=[0, 1, 0, 1, 0, 1], piece_extent=[0, 1, 0, 1, 0, 1],
                  spacing=[1, 1, 1], point_data=None, cell_data=None, field_data=None,
                  encoding='invalid_encoding')
    
    # Test for consistency in array sizes - point data too small
    with pytest.raises((ValueError, AssertionError)):
        write_vti(
            test_file, 
            whole_extent=[0, 2, 0, 2, 0, 2], 
            piece_extent=[0, 2, 0, 2, 0, 2],
            spacing=[1, 1, 1], 
            point_data={"temperature": np.array([1.0, 2.0])},  # Only 2 points, should be 27
            cell_data=None
        )
    
    # Test for consistency in array sizes - cell data too small
    with pytest.raises((ValueError, AssertionError)):
        write_vti(
            test_file, 
            whole_extent=[0, 2, 0, 2, 0, 2], 
            piece_extent=[0, 2, 0, 2, 0, 2],
            spacing=[1, 1, 1], 
            point_data=None,
            cell_data={"pressure": np.array([1.0, 2.0])}  # Only 2 cells, should be 8
        )


def test_write_vti_large_dataset_performance(test_dir):
    """
    Test write_vti performance with a larger dataset.
    
    This test creates and writes a larger dataset to ensure the write_vti
    function can handle larger data volumes efficiently.
    """
    test_path = test_dir / "test_large_output"
    test_file = str(test_path)
    
    # Create a moderately large dataset (100x100x100 grid)
    whole_extent = [0, 99, 0, 99, 0, 99]
    piece_extent = whole_extent
    spacing = [0.01, 0.01, 0.01]
    origin = [0.0, 0.0, 0.0]
    
    # Calculate points and cells
    nx, ny, nz = 100, 100, 100
    num_points = nx * ny * nz  # 1,000,000 points
    
    # Create large point data array (just one to keep memory usage reasonable)
    scalar_data = np.random.random(num_points).astype(np.float32)
    point_data = {'scalar_field': scalar_data}
    
    # No cell data for simplicity
    cell_data = None
    
    # Write the file with binary encoding (faster for large datasets)
    write_vti(test_file, whole_extent=whole_extent, piece_extent=piece_extent,
              origin=origin, spacing=spacing, point_data=point_data,
              cell_data=cell_data, encoding='binary')
    
    # Verify the file was created
    output_file = test_path.with_suffix('.vti')
    assert output_file.exists(), "Large output file was not created"
    
    # Check file size is reasonable (should be around 4-5MB for 1M float32 values plus overhead)
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"Large file size: {file_size_mb:.2f} MB")
    assert file_size_mb > 0.5, "File is unexpectedly small"