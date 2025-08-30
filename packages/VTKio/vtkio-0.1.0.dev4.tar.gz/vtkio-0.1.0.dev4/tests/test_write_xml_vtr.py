#!/usr/bin/env python
"""
Test module for VTK RectilinearGrid (.vtr) file writing functionality.

This module contains comprehensive tests for the write_vtr function, covering
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
from vtkio.vtk_structures import GridCoordinates, RectilinearData
from vtkio.writer.writers import write_vtr

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
    test_data_path = Path(__file__).parent.parent / "TestData" / "vtr"
    
    # Check if the test data directory exists
    if not test_data_path.exists():
        pytest.skip(f"Test data directory not found: {test_data_path}. "
                    f"To run this test, create the directory and add required test files.")
    
    return test_data_path


def test_write_vtr_basic(test_dir):
    """
    Test that write_vtr correctly writes a basic VTR file with minimal data.
    
    Tests basic file generation, metadata correctness, and data integrity.
    """
    test_path = test_dir / "test_output"
    test_file = str(test_path)

    # Create simple test data - coordinates along each axis
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([0.0, 0.5, 1.0, 1.5])
    z = np.array([0.0, 1.0])
    
    # Compute expected dimensions
    nx, ny, nz = len(x), len(y), len(z)
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    expected_point_count = nx * ny * nz  # 24 points total
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 6 cells total

    # Simple point data (temperature)
    point_data = {
        'temperature': np.linspace(20.0, 80.0, expected_point_count)
    }
    
    # Simple cell data (pressure)
    cell_data = {
        'pressure': np.linspace(100.0, 150.0, expected_cell_count)
    }

    # Write test file
    write_vtr(test_file, x, y, z, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, cell_data=cell_data, encoding='ascii')

    # Assert file exists with .vtr extension
    output_file = test_path.with_suffix('.vtr')
    assert output_file.exists(), "Output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify coordinates
    assert np.array_equal(data.coordinates.x, x), "X coordinates mismatch"
    assert np.array_equal(data.coordinates.y, y), "Y coordinates mismatch"
    assert np.array_equal(data.coordinates.z, z), "Z coordinates mismatch"
    
    # Verify extents
    assert np.array_equal(data.coordinates.whole_extents, whole_extent), "Whole extent mismatch"

    # Verify data
    assert 'temperature' in data.point_data, "Point data missing"
    assert 'pressure' in data.cell_data, "Cell data missing"

    # Verify array values
    assert np.allclose(data.point_data['temperature'], point_data['temperature']), "Point data values mismatch"
    assert np.allclose(data.cell_data['pressure'], cell_data['pressure']), "Cell data values mismatch"


def test_write_vtr_different_encodings(test_dir):
    """
    Test that write_vtr correctly handles different encodings.
    
    Tests ascii, binary, and appended encoding formats to ensure data integrity
    is maintained regardless of the encoding used.
    """
    # Create test data - coordinates along each axis
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    y = np.array([0.0, 1.0, 2.0, 3.0])
    z = np.array([0.0, 1.0, 2.0])
    
    # Calculate dimensions
    nx, ny, nz = len(x), len(y), len(z)
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    expected_point_count = nx * ny * nz  # 60 points total
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 32 cells total

    # Create random point data
    point_data = {
        'temperature': np.random.random(expected_point_count).astype(np.float32),
        'velocity': np.random.random((expected_point_count, 3)).astype(np.float32)
    }

    # Create random cell data
    cell_data = {
        'pressure': np.random.random(expected_cell_count).astype(np.float32),
        'stress': np.random.random((expected_cell_count, 6)).astype(np.float32)
    }

    encodings = ['ascii', 'binary', 'appended']

    for encoding in encodings:
        test_file_name = f"test_output_{encoding}"
        test_path = test_dir / test_file_name
        test_file = str(test_path)

        # Write test file with current encoding
        write_vtr(test_file, x, y, z, whole_extent=whole_extent, piece_extent=whole_extent,
                  point_data=point_data, cell_data=cell_data, encoding=encoding)

        # Assert file exists with .vtr extension
        output_file = test_path.with_suffix('.vtr')
        assert output_file.exists(), f"Output file with {encoding} encoding was not created"

        # Read the file back and verify the content
        reader = Reader(str(output_file))
        data = reader.parse()

        # Verify coordinates
        assert np.array_equal(data.coordinates.x, x), f"{encoding} encoding: X coordinates mismatch"
        assert np.array_equal(data.coordinates.y, y), f"{encoding} encoding: Y coordinates mismatch"
        assert np.array_equal(data.coordinates.z, z), f"{encoding} encoding: Z coordinates mismatch"

        # Verify data values
        assert np.allclose(data.point_data['temperature'], 
                          point_data['temperature']), f"{encoding} encoding: Point data (temperature) values mismatch"
        assert np.allclose(data.point_data['velocity'], 
                          point_data['velocity']), f"{encoding} encoding: Point data (velocity) values mismatch"
        assert np.allclose(data.cell_data['pressure'], 
                          cell_data['pressure']), f"{encoding} encoding: Cell data (pressure) values mismatch"
        assert np.allclose(data.cell_data['stress'], 
                          cell_data['stress']), f"{encoding} encoding: Cell data (stress) values mismatch"


def test_write_vtr_field_data(test_dir):
    """
    Test that write_vtr correctly handles field data.
    
    Tests the inclusion of various field data types including scalar, vector, 
    and string data.
    """
    test_path = test_dir / "test_with_field_data"
    test_file = str(test_path)

    # Create simple test data
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([0.0, 1.0, 2.0])
    z = np.array([0.0, 1.0, 2.0])
    
    # Compute dimensions
    nx, ny, nz = len(x), len(y), len(z)
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
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
    write_vtr(test_file, x, y, z, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, cell_data=cell_data, field_data=field_data, encoding='ascii')

    # Assert file exists with .vtr extension
    output_file = test_path.with_suffix('.vtr')
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


def test_write_vtr_nonuniform_grid(test_dir):
    """
    Test that write_vtr correctly handles non-uniform grid spacing.
    
    Tests a rectilinear grid with non-uniform spacing in each dimension.
    """
    test_path = test_dir / "test_nonuniform_grid"
    test_file = str(test_path)

    # Create non-uniform coordinates
    x = np.array([0.0, 0.1, 0.3, 0.7, 1.5])  # Non-uniform in x
    y = np.array([0.0, 0.5, 1.5, 3.0])       # Non-uniform in y
    z = np.array([0.0, 0.2, 0.5, 1.0, 2.0])  # Non-uniform in z
    
    # Compute dimensions
    nx, ny, nz = len(x), len(y), len(z)
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    expected_point_count = nx * ny * nz  # 80 points total
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 48 cells total

    # Point data
    point_data = {
        'scalar': np.random.random(expected_point_count)
    }
    
    # Cell data
    cell_data = {
        'vector': np.random.random((expected_cell_count, 3))
    }

    # Write test file
    write_vtr(test_file, x, y, z, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, cell_data=cell_data, encoding='ascii')

    # Assert file exists with .vtr extension
    output_file = test_path.with_suffix('.vtr')
    assert output_file.exists(), "Output file was not created"

    # Read the file back and verify content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify coordinates and non-uniform spacing
    assert np.array_equal(data.coordinates.x, x), "X coordinates mismatch"
    assert np.array_equal(data.coordinates.y, y), "Y coordinates mismatch"
    assert np.array_equal(data.coordinates.z, z), "Z coordinates mismatch"
    
    # Verify non-uniform spacing by checking differences between adjacent coordinates
    x_diffs = np.diff(x)
    y_diffs = np.diff(y)
    z_diffs = np.diff(z)
    
    assert not np.allclose(x_diffs, x_diffs[0]), "X spacing should be non-uniform"
    assert not np.allclose(y_diffs, y_diffs[0]), "Y spacing should be non-uniform"
    assert not np.allclose(z_diffs, z_diffs[0]), "Z spacing should be non-uniform"

    # Verify data
    assert 'scalar' in data.point_data, "Point data missing"
    assert 'vector' in data.cell_data, "Cell data missing"
    assert np.allclose(data.point_data['scalar'], point_data['scalar']), "Point data mismatch"
    assert np.allclose(data.cell_data['vector'], cell_data['vector']), "Cell data mismatch"


def test_write_vtr_roundtrip_comparison(test_dir):
    """
    Test that data written to a VTR file can be read back identically.
    
    Creates complex RectilinearData object, writes it to a file, then reads it back
    to ensure all data is preserved correctly during the write-read cycle.
    """
    test_path = test_dir / "test_roundtrip"
    test_file = str(test_path)

    # Create coordinates
    x = np.array([0.0, 1.0, 2.0, 3.0])
    y = np.array([0.0, 1.0, 2.0])
    z = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    
    # Calculate dimensions
    nx, ny, nz = len(x), len(y), len(z)
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    expected_point_count = nx * ny * nz  # 60 points total
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 24 cells total

    # Create coordinates object
    coordinates = GridCoordinates(
        x=x,
        y=y,
        z=z,
        whole_extents=np.array(whole_extent)
    )

    # Create point data
    point_data = {
        'scalar': np.linspace(0, 100, expected_point_count),
        'vector': np.random.random((expected_point_count, 3)),
        'tensor': np.random.random((expected_point_count, 9))
    }
    
    # Create cell data
    cell_data = {
        'pressure': np.random.random(expected_cell_count),
        'stress': np.random.random((expected_cell_count, 6))
    }
    
    # Create field data
    field_data = {
        'time': np.array([10.5]),
        'iteration': np.array([42]),
        'description': np.array([ord(c) for c in "Rectilinear test"])
    }
    
    # Create original data object
    original_data = RectilinearData(
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data,
        coordinates=coordinates
    )
    
    # Write data using RectilinearData write method (which calls write_vtr)
    original_data.write(test_file, xml_encoding='ascii')
    
    # Assert file exists with .vtr extension
    output_file = test_path.with_suffix('.vtr')
    assert output_file.exists(), "Output file was not created"
    
    # Read the data back
    reader = Reader(str(output_file))
    read_data = reader.parse()
    
    # Compare coordinates
    assert np.array_equal(read_data.coordinates.x, original_data.coordinates.x), "X coordinates don't match"
    assert np.array_equal(read_data.coordinates.y, original_data.coordinates.y), "Y coordinates don't match"
    assert np.array_equal(read_data.coordinates.z, original_data.coordinates.z), "Z coordinates don't match"
    assert np.array_equal(read_data.coordinates.whole_extents, original_data.coordinates.whole_extents),\
        "Extents don't match"
    
    # Compare point data
    for key in original_data.point_data:
        assert key in read_data.point_data, f"Point data '{key}' missing in read data"
        assert np.allclose(read_data.point_data[key], original_data.point_data[key]),\
            f"Point data '{key}' values don't match"
    
    # Compare cell data
    for key in original_data.cell_data:
        assert key in read_data.cell_data, f"Cell data '{key}' missing in read data"
        assert np.allclose(read_data.cell_data[key], original_data.cell_data[key]),\
            f"Cell data '{key}' values don't match"
    
    # Compare field data
    for key in original_data.field_data:
        assert key in read_data.field_data, f"Field data '{key}' missing in read data"
        assert np.array_equal(read_data.field_data[key], original_data.field_data[key]),\
            f"Field data '{key}' values don't match"


def test_write_vtr_against_reference_file(test_dir, test_data_directory):
    """
    Test write_vtr by comparing output with a reference file.
    
    Uses a reference file from the test data directory to validate that
    write_vtr produces identical output when given the same input data.
    
    Parameters
    ----------
    test_dir : Path
        Temporary directory for test output
    test_data_directory : Path
        Directory containing reference test data files
    """
    # Try to find a reference file
    reference_file = test_data_directory / 'rect_example_points_cells.vtr'
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
    write_vtr(
        test_file,
        reference_data.coordinates.x,
        reference_data.coordinates.y,
        reference_data.coordinates.z,
        whole_extent=reference_data.coordinates.whole_extents.tolist(),
        piece_extent=reference_data.coordinates.whole_extents.tolist(),
        point_data=reference_data.point_data,
        cell_data=reference_data.cell_data,
        field_data=reference_data.field_data,
        encoding='ascii'
    )

    # Assert file exists with .vtr extension
    output_file = test_path.with_suffix('.vtr')
    assert output_file.exists(), "Output file was not created"

    # Read the generated file
    reader = Reader(str(output_file))
    test_data = reader.parse()

    # Compare the data structures
    assert np.allclose(test_data.coordinates.x, reference_data.coordinates.x), "X coordinates don't match"
    assert np.allclose(test_data.coordinates.y, reference_data.coordinates.y), "Y coordinates don't match"
    assert np.allclose(test_data.coordinates.z, reference_data.coordinates.z), "Z coordinates don't match"

    # Compare point data
    for key in reference_data.point_data:
        assert key in test_data.point_data, f"Point data '{key}' missing in test data"
        assert np.allclose(test_data.point_data[key], reference_data.point_data[key]),\
            f"Point data '{key}' values don't match"

    # Compare cell data
    for key in reference_data.cell_data:
        assert key in test_data.cell_data, f"Cell data '{key}' missing in test data"
        assert np.allclose(test_data.cell_data[key], reference_data.cell_data[key]),\
            f"Cell data '{key}' values don't match"


def test_write_vtr_parameter_validation(test_dir):
    """
    Test validation of required parameters for write_vtr.
    
    Tests that appropriate exceptions are raised when required parameters
    are missing or invalid.
    """
    test_path = test_dir / "test_output"
    test_file = str(test_path)
    
    # Test with missing x coordinates (required parameter)
    with pytest.raises(TypeError):
        write_vtr(test_file)
    
    # Test with missing y coordinates (required parameter)
    with pytest.raises(TypeError):
        write_vtr(test_file, x=np.array([0, 1]))
    
    # Test with missing z coordinates (required parameter)
    with pytest.raises(TypeError):
        write_vtr(test_file, x=np.array([0, 1]), y=np.array([0, 1]))
    
    # Create valid coordinates
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([0.0, 1.0, 2.0])
    z = np.array([0.0, 1.0, 2.0])
    
    # Test with invalid coordinates format
    with pytest.raises((ValueError, TypeError)):
        write_vtr(test_file, x="invalid", y=y, z=z)
    
    with pytest.raises((ValueError, TypeError)):
        write_vtr(test_file, x=x, y=y, z=["invalid", "type"])


def test_write_vtr_with_invalid_data(test_dir):
    """
    Test that write_vtr correctly handles invalid data.
    
    Tests error handling for invalid file format and encoding specifications.
    """
    test_path = test_dir / "test_invalid_data"
    test_file = str(test_path)
    
    # Create valid coordinates
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([0.0, 1.0, 2.0])
    z = np.array([0.0, 1.0])
    
    # Compute dimensions
    nx, ny, nz = len(x), len(y), len(z)
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    # expected_point_count = nx * ny * nz  # 12 points total
    # expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 2 cells total
    
    # Test with incorrect file format
    with pytest.raises(ValueError) as excinfo:
        write_vtr(test_file, x, y, z, whole_extent=whole_extent, piece_extent=whole_extent,
                  point_data=None, cell_data=None, field_data=None,
                  file_format='invalid_format')
    assert "Unsupported file format" in str(excinfo.value)
    
    # Test with invalid encoding
    with pytest.raises((ValueError, NotImplementedError)):
        write_vtr(test_file, x, y, z, whole_extent=whole_extent, piece_extent=whole_extent,
                  point_data=None, cell_data=None, field_data=None,
                  encoding='invalid_encoding')
    
    # Test for consistency in array sizes - point data too small
    with pytest.raises((ValueError, AssertionError)):
        write_vtr(
            test_file, 
            x, y, z,
            whole_extent=whole_extent, 
            piece_extent=whole_extent,
            point_data={"temperature": np.array([1.0, 2.0])},  # Only 2 points, should be 12
            cell_data=None
        )
    
    # Test for consistency in array sizes - cell data too small
    with pytest.raises((ValueError, AssertionError)):
        write_vtr(
            test_file, 
            x, y, z,
            whole_extent=whole_extent, 
            piece_extent=whole_extent,
            point_data=None,
            cell_data={"pressure": np.array([1.0])}  # Only 1 cell, should be 2
        )


def test_write_vtr_large_dataset_performance(test_dir):
    """
    Test write_vtr performance with a larger dataset.
    
    This test creates and writes a larger dataset to ensure the write_vtr
    function can handle larger data volumes efficiently.
    """
    test_path = test_dir / "test_large_output"
    test_file = str(test_path)
    
    # Create a larger dataset (50x40x30 grid)
    nx, ny, nz = 50, 40, 30
    x = np.linspace(0, 10, nx)
    y = np.linspace(0, 8, ny)
    z = np.linspace(0, 6, nz)
    
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    expected_point_count = nx * ny * nz  # 60,000 points
    # expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 57,038 cells
    
    # Create large point data array (just one to keep memory usage reasonable)
    scalar_data = np.random.random(expected_point_count).astype(np.float32)
    point_data = {'scalar_field': scalar_data}
    
    # No cell data for simplicity
    cell_data = None
    
    # Write the file with binary encoding (faster for large datasets)
    write_vtr(test_file, x, y, z, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, cell_data=cell_data, encoding='binary')
    
    # Verify the file was created
    output_file = test_path.with_suffix('.vtr')
    assert output_file.exists(), "Large output file was not created"
    
    # Check file size is reasonable
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"Large file size: {file_size_mb:.2f} MB")
    assert file_size_mb > 0.1, "File is unexpectedly small"


def test_write_vtr_piece_extent(test_dir):
    """
    Test that write_vtr correctly handles piece extents different from whole extents.
    
    Tests writing a subset of a larger domain.
    """
    test_path = test_dir / "test_piece_extent"
    test_file = str(test_path)

    # Create coordinates for the piece
    x = np.array([1.0, 2.0, 3.0])  # Piece is from indices 1-3 in x
    y = np.array([0.0, 1.0])       # Piece is from indices 0-1 in y
    z = np.array([2.0, 3.0, 4.0])  # Piece is from indices 2-4 in z
    
    # Define whole and piece extents
    whole_extent = [0, 4, 0, 2, 0, 5]     # Full domain: 5x3x6
    piece_extent = [1, 3, 0, 1, 2, 4]     # Piece: 3x2x3 (matches coordinates)
    
    # Calculate point count in the piece
    nx_piece, ny_piece, nz_piece = len(x), len(y), len(z)
    expected_point_count = nx_piece * ny_piece * nz_piece  # 18 points
    expected_cell_count = (nx_piece-1) * (ny_piece-1) * (nz_piece-1)  # 4 cells
    
    # Create data for the piece
    point_data = {
        'temperature': np.random.random(expected_point_count)
    }
    
    cell_data = {
        'pressure': np.random.random(expected_cell_count)
    }
    
    # Write test file
    write_vtr(test_file, x, y, z, whole_extent=whole_extent, piece_extent=piece_extent,
              point_data=point_data, cell_data=cell_data, encoding='ascii')
    
    # Assert file exists with .vtr extension
    output_file = test_path.with_suffix('.vtr')
    assert output_file.exists(), "Output file was not created"
    
    # Read the file back
    reader = Reader(str(output_file))
    data = reader.parse()
    
    # Verify the coordinates match
    assert np.array_equal(data.coordinates.x, x), "X coordinates don't match"
    assert np.array_equal(data.coordinates.y, y), "Y coordinates don't match"
    assert np.array_equal(data.coordinates.z, z), "Z coordinates don't match"
    
    # Verify the extents are stored correctly
    assert np.array_equal(data.coordinates.whole_extents, whole_extent), "Whole extents don't match"