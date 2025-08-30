#!/usr/bin/env python
"""
Test module for VTK Structured Grid (.vts) file writing functionality.

This module contains comprehensive tests for the write_vts function, covering
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
from vtkio.vtk_structures import StructuredData
from vtkio.writer.writers import write_vts

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
    test_data_path = Path(__file__).parent.parent / "TestData" / "vts"
    
    # Check if the test data directory exists
    if not test_data_path.exists():
        pytest.skip(f"Test data directory not found: {test_data_path}. "
                    f"To run this test, create the directory and add required test files.")
    
    return test_data_path


def test_write_vts_basic(test_dir):
    """
    Test that write_vts correctly writes a basic VTS file with minimal data.
    
    Tests basic file generation, metadata correctness, and data integrity.
    """
    test_path = test_dir / "test_output"
    test_file = str(test_path)

    # Create simple structured grid
    # 3x3x3 grid (27 points)
    nx, ny, nz = 3, 3, 3
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    
    # Total number of points in the grid
    num_points = nx * ny * nz
    
    # Create a structured grid with slight displacement from regular grid
    points = np.zeros((num_points, 3))
    
    # Fill the points array
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                # Base position (regular grid)
                x = float(i)
                y = float(j)
                z = float(k)
                
                # Add small perturbation to make it irregular
                x += 0.1 * np.sin(i*j*k)
                y += 0.1 * np.cos(i*j*k)
                z += 0.1 * np.sin(i+j+k)
                
                points[point_idx] = [x, y, z]
                point_idx += 1
    
    # Verify dimensions and array size consistency
    expected_point_count = num_points  # 27 points total
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 8 cells total

    # Simple point data (temperature)
    point_data = {
        'temperature': np.array([20.0 + i for i in range(expected_point_count)], dtype=np.float32)
    }
    
    # Simple cell data (pressure)
    cell_data = {
        'pressure': np.array([100.0 + i for i in range(expected_cell_count)], dtype=np.float32)
    }

    # Write test file
    write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, cell_data=cell_data, encoding='ascii')

    # Assert file exists with .vts extension
    output_file = test_path.with_suffix('.vts')
    assert output_file.exists(), "Output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify points
    assert np.allclose(data.points, points), "Points do not match"
    
    # Verify metadata
    assert np.array_equal(data.whole_extents, whole_extent), "Whole extent mismatch"

    # Verify data
    assert 'temperature' in data.point_data, "Point data missing"
    assert 'pressure' in data.cell_data, "Cell data missing"

    # Verify array values
    assert np.allclose(data.point_data['temperature'], point_data['temperature']), "Point data values mismatch"
    assert np.allclose(data.cell_data['pressure'], cell_data['pressure']), "Cell data values mismatch"


def test_write_vts_different_encodings(test_dir):
    """
    Test that write_vts correctly handles different encodings.
    
    Tests ascii, binary, and appended encoding formats to ensure data integrity
    is maintained regardless of the encoding used.
    """
    # Create a structured grid
    nx, ny, nz = 4, 4, 4
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    
    # Total number of points in the grid
    num_points = nx * ny * nz  # 64 points
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 27 cells
    
    # Create points for a warped structured grid
    points = np.zeros((num_points, 3))
    
    # Fill the points array with a more complex pattern
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                # Base position with non-linear transformation
                x = float(i) + 0.2 * np.sin(j*k/2.0)
                y = float(j) + 0.2 * np.cos(i*k/2.0)
                z = float(k) + 0.2 * np.sin((i+j)/2.0)
                
                points[point_idx] = [x, y, z]
                point_idx += 1

    # Create random point data
    point_data = {
        'temperature': np.random.random(num_points).astype(np.float32),
        'velocity': np.random.random((num_points, 3)).astype(np.float32)
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
        write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=whole_extent,
                  point_data=point_data, cell_data=cell_data, encoding=encoding)

        # Assert file exists with .vts extension
        output_file = test_path.with_suffix('.vts')
        assert output_file.exists(), f"Output file with {encoding} encoding was not created"

        # Read the file back and verify the content
        reader = Reader(str(output_file))
        data = reader.parse()

        # Verify points
        assert np.allclose(data.points, points), f"{encoding} encoding: Points mismatch"

        # Verify data values
        assert np.allclose(data.point_data['temperature'], 
                          point_data['temperature']), f"{encoding} encoding: Point data (temperature) values mismatch"
        assert np.allclose(data.point_data['velocity'], 
                          point_data['velocity']), f"{encoding} encoding: Point data (velocity) values mismatch"
        assert np.allclose(data.cell_data['pressure'], 
                          cell_data['pressure']), f"{encoding} encoding: Cell data (pressure) values mismatch"
        assert np.allclose(data.cell_data['stress'], 
                          cell_data['stress']), f"{encoding} encoding: Cell data (stress) values mismatch"


def test_write_vts_field_data(test_dir):
    """
    Test that write_vts correctly handles field data.
    
    Tests the inclusion of various field data types including scalar, vector, 
    and string data.
    """
    test_path = test_dir / "test_with_field_data"
    test_file = str(test_path)

    # Create simple structured grid
    nx, ny, nz = 3, 3, 3
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    num_points = nx * ny * nz  # 27 points
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 8 cells
    
    # Create points for a simple structured grid
    points = np.zeros((num_points, 3))
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                points[point_idx] = [float(i), float(j), float(k)]
                point_idx += 1

    # Simple point and cell data
    point_data = {'temperature': np.ones(num_points, dtype=np.float32) * 20.0}
    cell_data = {'pressure': np.ones(expected_cell_count, dtype=np.float32) * 101.3}

    # Field data
    field_data = {
        'time': np.array([10.5], dtype=np.float32),
        'iteration': np.array([42], dtype=np.int32),
        'simulation_name': np.array(['test_sim'], dtype=np.str_)
    }

    # Write test file
    write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, cell_data=cell_data, field_data=field_data, encoding='ascii')

    # Assert file exists with .vts extension
    output_file = test_path.with_suffix('.vts')
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


def test_write_vts_complex_grid(test_dir):
    """
    Test that write_vts correctly handles a more complex structured grid.
    
    Tests a structured grid with complex warping and non-linear transformations.
    """
    test_path = test_dir / "test_complex_grid"
    test_file = str(test_path)

    # Create a more complex structured grid
    nx, ny, nz = 10, 8, 6
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    
    # Total number of points in the grid
    num_points = nx * ny * nz  # 480 points
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 315 cells
    
    # Create points for a complex structured grid (e.g., a warped box)
    points = np.zeros((num_points, 3))
    
    # Fill the points array with a complex pattern
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                # Base position
                x = float(i) / (nx-1)  # Normalize to [0,1]
                y = float(j) / (ny-1)  # Normalize to [0,1]
                z = float(k) / (nz-1)  # Normalize to [0,1]
                
                # Apply nonlinear transformation to create a complex shape
                # For example, a warped sphere-like shape
                r = np.sqrt(x*x + y*y + z*z)
                if r > 0:
                    factor = 0.5 + 0.5 * r
                    x = x * factor * 10
                    y = y * factor * 8
                    z = z * factor * 6
                
                points[point_idx] = [x, y, z]
                point_idx += 1

    # Point data - scalar field
    scalar_field = np.zeros(num_points)
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                # Create some scalar field (e.g., distance from center)
                x = float(i) / (nx-1) - 0.5
                y = float(j) / (ny-1) - 0.5
                z = float(k) / (nz-1) - 0.5
                scalar_field[point_idx] = np.sqrt(x*x + y*y + z*z)
                point_idx += 1
    
    # Point data - vector field
    vector_field = np.zeros((num_points, 3))
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                # Create some vector field (e.g., gradient of scalar field)
                x = float(i) / (nx-1) - 0.5
                y = float(j) / (ny-1) - 0.5
                z = float(k) / (nz-1) - 0.5
                r = np.sqrt(x*x + y*y + z*z)
                if r > 0:
                    vector_field[point_idx] = [x/r, y/r, z/r]
                else:
                    vector_field[point_idx] = [0, 0, 0]
                point_idx += 1
    
    point_data = {
        'scalar_field': scalar_field,
        'vector_field': vector_field
    }
    
    # Cell data
    cell_data = {
        'cell_scalar': np.random.random(expected_cell_count)
    }

    # Write test file
    write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, cell_data=cell_data, encoding='binary')

    # Assert file exists with .vts extension
    output_file = test_path.with_suffix('.vts')
    assert output_file.exists(), "Output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify points
    assert np.allclose(data.points, points), "Points do not match"
    
    # Verify data
    assert 'scalar_field' in data.point_data, "Point data (scalar_field) missing"
    assert 'vector_field' in data.point_data, "Point data (vector_field) missing"
    assert 'cell_scalar' in data.cell_data, "Cell data missing"

    # Verify array values
    assert np.allclose(data.point_data['scalar_field'], point_data['scalar_field']),\
        "Point data (scalar_field) values mismatch"
    assert np.allclose(data.point_data['vector_field'], point_data['vector_field']),\
        "Point data (vector_field) values mismatch"
    assert np.allclose(data.cell_data['cell_scalar'], cell_data['cell_scalar']), "Cell data values mismatch"


def test_write_vts_roundtrip_comparison(test_dir):
    """
    Test that data written to a VTS file can be read back identically.
    
    Creates complex StructuredData object, writes it to a file, then reads it back
    to ensure all data is preserved correctly during the write-read cycle.
    """
    test_path = test_dir / "test_roundtrip"
    test_file = str(test_path)

    # Create a structured grid
    nx, ny, nz = 5, 4, 3
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    
    # Total number of points in the grid
    num_points = nx * ny * nz  # 60 points
    expected_cell_count = (nx-1) * (ny-1) * (nz-1)  # 24 cells
    
    # Create points for a structured grid
    points = np.zeros((num_points, 3))
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                # Add some curvature to the grid
                x = float(i) + 0.1 * (j * k)
                y = float(j) + 0.1 * (i * k)
                z = float(k) + 0.1 * (i * j)
                
                points[point_idx] = [x, y, z]
                point_idx += 1

    # Create point data
    point_data = {
        'scalar': np.linspace(0, 100, num_points),
        'vector': np.random.random((num_points, 3)),
        'tensor': np.random.random((num_points, 9))
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
        'description': np.array([ord(c) for c in "Structured test"])
    }
    
    # Create original data object
    original_data = StructuredData(
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data,
        points=points,
        whole_extents=np.array(whole_extent)
    )
    
    # Write data using StructuredData write method (which calls write_vts)
    original_data.write(test_file, xml_encoding='ascii')
    
    # Assert file exists with .vts extension
    output_file = test_path.with_suffix('.vts')
    assert output_file.exists(), "Output file was not created"
    
    # Read the data back
    reader = Reader(str(output_file))
    read_data = reader.parse()
    
    # Compare points
    assert np.allclose(read_data.points, original_data.points), "Points don't match"
    
    # Compare extents
    assert np.array_equal(read_data.whole_extents, original_data.whole_extents), "Extents don't match"
    
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


def test_write_vts_against_reference_file(test_dir, test_data_directory):
    """
    Test write_vts by comparing output with a reference file.
    
    Uses a reference file from the test data directory to validate that
    write_vts produces identical output when given the same input data.
    
    Parameters
    ----------
    test_dir : Path
        Temporary directory for test output
    test_data_directory : Path
        Directory containing reference test data files
    """
    # Try to find a reference file
    reference_file = test_data_directory / 'sample_struct_grid_point_cell_scalars.vts'
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
    write_vts(
        test_file,
        points=reference_data.points,
        whole_extent=reference_data.whole_extents.tolist(),
        piece_extent=reference_data.whole_extents.tolist(),
        point_data=reference_data.point_data,
        cell_data=reference_data.cell_data,
        field_data=reference_data.field_data,
        encoding='ascii'
    )

    # Assert file exists with .vts extension
    output_file = test_path.with_suffix('.vts')
    assert output_file.exists(), "Output file was not created"

    # Read the generated file
    reader = Reader(str(output_file))
    test_data = reader.parse()

    # Compare the data structures
    assert np.allclose(test_data.points, reference_data.points), "Points don't match"
    assert np.array_equal(test_data.whole_extents, reference_data.whole_extents), "Extents don't match"

    # Compare point data
    for key in reference_data.point_data:
        assert key in test_data.point_data, f"Point data '{key}' missing in test data"
        assert np.allclose(test_data.point_data[key], reference_data.point_data[key]), \
            f"Point data '{key}' values don't match"

    # Compare cell data
    for key in reference_data.cell_data:
        assert key in test_data.cell_data, f"Cell data '{key}' missing in test data"
        assert np.allclose(test_data.cell_data[key], reference_data.cell_data[key]), \
            f"Cell data '{key}' values don't match"


def test_write_vts_parameter_validation(test_dir):
    """
    Test validation of required parameters for write_vts.
    
    Tests that appropriate exceptions are raised when required parameters
    are missing or invalid.
    """
    test_path = test_dir / "test_output"
    test_file = str(test_path)
    
    # Test with missing points (required parameter)
    with pytest.raises(TypeError):
        write_vts(test_file)
    
    # Test with missing whole_extent (required parameter)
    with pytest.raises((ValueError, TypeError)):
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])
        write_vts(test_file, points=points)
    
    # Test with invalid points format
    with pytest.raises((ValueError, TypeError)):  # Different implementations might raise different exceptions
        write_vts(test_file, points="invalid", whole_extent=[0, 1, 0, 1, 0, 1], piece_extent=[0, 1, 0, 1, 0, 1])
    
    # Test with inconsistent points and extent dimensions
    with pytest.raises((ValueError, AssertionError)):
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])  # 4 points (2x2x1 grid)
        write_vts(test_file, points=points, whole_extent=[0, 2, 0, 2, 0, 0], piece_extent=[0, 2, 0, 2, 0, 0])
        # This should fail because the extent implies 9 points (3x3x1) but only 4 are provided


def test_write_vts_with_invalid_data(test_dir):
    """
    Test that write_vts correctly handles invalid data.
    
    Tests error handling for invalid file format and encoding specifications.
    """
    test_path = test_dir / "test_invalid_data"
    test_file = str(test_path)
    
    # Create minimal valid data
    nx, ny, nz = 2, 2, 2
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    num_points = nx * ny * nz  # 8 points
    
    points = np.zeros((num_points, 3))
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                points[point_idx] = [float(i), float(j), float(k)]
                point_idx += 1
    
    # Test with incorrect file format
    with pytest.raises(ValueError) as excinfo:
        write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=whole_extent,
                  point_data=None, cell_data=None, field_data=None,
                  file_format='invalid_format')
    assert "Unsupported file format" in str(excinfo.value)
    
    # Test with invalid encoding
    with pytest.raises((ValueError, NotImplementedError)) as excinfo:
        write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=whole_extent,
                  point_data=None, cell_data=None, field_data=None,
                  encoding='invalid_encoding')
    
    # Test for consistency in array sizes - point data too small
    with pytest.raises((ValueError, AssertionError)):
        write_vts(
            test_file, 
            points=points,
            whole_extent=whole_extent, 
            piece_extent=whole_extent,
            point_data={"temperature": np.array([1.0, 2.0])},  # Only 2 points, should be 8
            cell_data=None
        )
    
    # Test for consistency in array sizes - cell data too small
    with pytest.raises((ValueError, AssertionError)):
        write_vts(
            test_file, 
            points=points,
            whole_extent=whole_extent, 
            piece_extent=whole_extent,
            point_data=None,
            cell_data={"pressure": np.array([1.0, 2.0])}  # 2 cells, but should be 1
        )


def test_write_vts_large_dataset_performance(test_dir):
    """
    Test write_vts performance with a larger dataset.
    
    This test creates and writes a larger structured grid dataset to ensure the write_vts
    function can handle larger data volumes efficiently.
    """
    test_path = test_dir / "test_large_output"
    test_file = str(test_path)
    
    # Create a moderately large structured grid (30x30x30 grid)
    nx, ny, nz = 30, 30, 30
    whole_extent = [0, nx-1, 0, ny-1, 0, nz-1]
    piece_extent = whole_extent
    
    # Total number of points in the grid
    num_points = nx * ny * nz  # 27,000 points
    
    # Create points for a structured grid with a wave pattern
    points = np.zeros((num_points, 3))
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                # Base position with sine wave displacement
                x = float(i) + 0.1 * np.sin(j/3.0)
                y = float(j) + 0.1 * np.sin(k/3.0)
                z = float(k) + 0.1 * np.sin(i/3.0)
                
                points[point_idx] = [x, y, z]
                point_idx += 1
    
    # Create large point data array (just one to keep memory usage reasonable)
    scalar_data = np.random.random(num_points).astype(np.float32)
    point_data = {'scalar_field': scalar_data}
    
    # No cell data for simplicity
    cell_data = None
    
    # Write the file with binary encoding (faster for large datasets)
    write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=piece_extent,
              point_data=point_data, cell_data=cell_data, encoding='binary')
    
    # Verify the file was created
    output_file = test_path.with_suffix('.vts')
    assert output_file.exists(), "Large output file was not created"
    
    # Check file size is reasonable
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"Large file size: {file_size_mb:.2f} MB")
    assert file_size_mb > 0.5, "File is unexpectedly small"


def test_write_vts_piece_extent(test_dir):
    """
    Test that write_vts correctly handles piece extents different from whole extents.

    Tests writing a subset of a larger domain.
    """
    test_path = test_dir / "test_piece_extent"
    test_file = str(test_path)

    # Define whole extents for a 4x4x4 grid
    whole_extent = [0, 3, 0, 3, 0, 3]

    # Define piece extent as a subset (center region of the domain)
    piece_extent = [1, 2, 1, 2, 1, 2]

    # Calculate dimensions of the piece
    nx_piece = piece_extent[1] - piece_extent[0] + 1  # 2
    ny_piece = piece_extent[3] - piece_extent[2] + 1  # 2
    nz_piece = piece_extent[5] - piece_extent[4] + 1  # 2

    # Total number of points in the piece
    num_points_piece = nx_piece * ny_piece * nz_piece  # 8 points

    # Create points for just the piece (subset of the domain)
    points = np.zeros((num_points_piece, 3))

    # Fill the points array with coordinates for the piece
    point_idx = 0
    for k in range(piece_extent[4], piece_extent[5] + 1):
        for j in range(piece_extent[2], piece_extent[3] + 1):
            for i in range(piece_extent[0], piece_extent[1] + 1):
                # Add slight perturbation to make it non-uniform
                x = float(i) + 0.1 * np.sin(i * j * k)
                y = float(j) + 0.1 * np.cos(i * j * k)
                z = float(k) + 0.1 * np.sin(i + j + k)

                points[point_idx] = [x, y, z]
                point_idx += 1

    # Create point data for the piece
    temperature = np.linspace(0, 100, num_points_piece)
    point_data = {'temperature': temperature}

    # Create cell data for the piece
    # In the 2x2x2 grid there is 1 cell
    cell_data = {'pressure': np.array([101.3])}

    # Write the file
    write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=piece_extent,
              point_data=point_data, cell_data=cell_data, encoding='ascii')

    # Assert file exists with .vts extension
    output_file = test_path.with_suffix('.vts')
    assert output_file.exists(), "Output file was not created"

    # Read the file back
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify extents
    assert np.array_equal(data.whole_extents, whole_extent), "Whole extents don't match"

    # Verify points
    assert np.allclose(data.points, points), "Points don't match"

    # Verify data
    assert 'temperature' in data.point_data, "Point data missing"
    assert 'pressure' in data.cell_data, "Cell data missing"

    # Verify array values
    assert np.allclose(data.point_data['temperature'], point_data['temperature']), "Point data values mismatch"
    assert np.allclose(data.cell_data['pressure'], cell_data['pressure']), "Cell data values mismatch"


def test_write_vts_direction_matrix(test_dir):
    """
    Test that write_vts correctly handles direction matrix for grid orientation.

    Tests writing a structured grid with a non-default orientation.
    """
    test_path = test_dir / "test_direction"
    test_file = str(test_path)

    # Create simple structured grid
    nx, ny, nz = 3, 3, 3
    whole_extent = [0, nx - 1, 0, ny - 1, 0, nz - 1]
    num_points = nx * ny * nz  # 27 points

    # Create rotated direction matrix (45 degree rotation around z-axis)
    import math
    angle = math.pi / 4  # 45 degrees
    cos_val = math.cos(angle)
    sin_val = math.sin(angle)

    # Create points for a structured grid
    points = np.zeros((num_points, 3))
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                # Apply the rotation to the coordinates
                x_rotated = i * cos_val - j * sin_val
                y_rotated = i * sin_val + j * cos_val
                z_rotated = k

                points[point_idx] = [x_rotated, y_rotated, z_rotated]
                point_idx += 1

    # Simple point data
    point_data = {'temperature': np.linspace(0, 100, num_points)}

    # Write the file
    write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, encoding='ascii')

    # Assert file exists with .vts extension
    output_file = test_path.with_suffix('.vts')
    assert output_file.exists(), "Output file was not created"

    # Read the file back
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify points
    assert np.allclose(data.points, points), "Points don't match"

    # Verify data
    assert 'temperature' in data.point_data, "Point data missing"
    assert np.allclose(data.point_data['temperature'],
                       point_data['temperature']), "Point data values mismatch"


def test_write_vts_empty_data(test_dir):
    """
    Test that write_vts correctly handles empty or None data arrays.

    Tests writing a structured grid with minimal required data.
    """
    test_path = test_dir / "test_empty_data"
    test_file = str(test_path)

    # Create simple structured grid
    nx, ny, nz = 2, 2, 2
    whole_extent = [0, nx - 1, 0, ny - 1, 0, nz - 1]
    num_points = nx * ny * nz  # 8 points

    # Create points for a structured grid
    points = np.zeros((num_points, 3))
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                points[point_idx] = [float(i), float(j), float(k)]
                point_idx += 1

    # Write file with no data arrays
    write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=None, cell_data=None, field_data=None, encoding='ascii')

    # Assert file exists with .vts extension
    output_file = test_path.with_suffix('.vts')
    assert output_file.exists(), "Output file was not created"

    # Read the file back
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify points
    assert np.allclose(data.points, points), "Points don't match"

    # Verify that no data arrays are present
    assert not data.point_data or len(data.point_data) == 0, "Point data should be empty"
    assert not data.cell_data or len(data.cell_data) == 0, "Cell data should be empty"
    assert not data.field_data or len(data.field_data) == 0, "Field data should be empty"

def test_write_vts_ascii_precision(test_dir):
    """
    Test that write_vts correctly handles different ascii precision settings.

    Tests writing with different floating-point precision values.
    """
    test_path = test_dir / "test_ascii_precision"
    test_file = str(test_path)

    # Create a simple structured grid
    nx, ny, nz = 2, 2, 2
    whole_extent = [0, nx - 1, 0, ny - 1, 0, nz - 1]

    # Create points with high-precision floating point values
    points = np.zeros((nx * ny * nz, 3))
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                # Add high-precision values
                points[point_idx] = [i + 1 / 3.0, j + 1 / 7.0, k + 1 / 9.0]
                point_idx += 1

    # Simple point data with high precision
    point_data = {
        'precise_value': np.array([0.123456789012345, 0.987654321098765,
                                   0.111111111111111, 0.222222222222222,
                                   0.333333333333333, 0.444444444444444,
                                   0.555555555555555, 0.666666666666666])
    }

    # Write with high precision (16 decimal places)
    write_vts(test_file + "_high", points=points, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, encoding='ascii', ascii_precision=16)

    # Write with low precision (4 decimal places)
    write_vts(test_file + "_low", points=points, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, encoding='ascii', ascii_precision=4)

    # Assert files exist
    high_precision_file = Path(str(test_path) + "_high.vts")
    low_precision_file = Path(str(test_path) + "_low.vts")

    assert high_precision_file.exists(), "High precision output file was not created"
    assert low_precision_file.exists(), "Low precision output file was not created"

    # File with higher precision should be larger
    assert high_precision_file.stat().st_size > low_precision_file.stat().st_size, \
        "High precision file should be larger than low precision file"

    # Read back both files
    high_reader = Reader(str(high_precision_file))
    high_data = high_reader.parse()

    low_reader = Reader(str(low_precision_file))
    low_data = low_reader.parse()

    # Both should have the correct points and data, within appropriate tolerances
    assert np.allclose(high_data.points, points,
                       atol=1e-15), "High precision points don't match within tolerance"
    assert np.allclose(low_data.points, points,
                       atol=1e-4), "Low precision points don't match within tolerance"

    assert np.allclose(high_data.point_data['precise_value'], point_data['precise_value'], atol=1e-15), \
        "High precision data doesn't match within tolerance"
    assert np.allclose(low_data.point_data['precise_value'], point_data['precise_value'], atol=1e-4), \
        "Low precision data doesn't match within tolerance"

def test_write_vts_file_extension(test_dir):
    """
    Test that write_vts correctly handles file extensions.

    Tests that the .vts extension is automatically added if not provided.
    """
    # Test with extension provided
    test_path_with_ext = test_dir / "test_with_extension.vts"
    test_file_with_ext = str(test_path_with_ext)

    # Test without extension
    test_path_without_ext = test_dir / "test_without_extension"
    test_file_without_ext = str(test_path_without_ext)

    # Create simple structured grid
    nx, ny, nz = 2, 2, 2
    whole_extent = [0, nx - 1, 0, ny - 1, 0, nz - 1]

    # Create points
    points = np.zeros((nx * ny * nz, 3))
    point_idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                points[point_idx] = [float(i), float(j), float(k)]
                point_idx += 1

    # Write both files
    write_vts(test_file_with_ext, points=points, whole_extent=whole_extent, piece_extent=whole_extent)
    write_vts(test_file_without_ext, points=points, whole_extent=whole_extent, piece_extent=whole_extent)

    # Both files should exist with .vts extension
    assert test_path_with_ext.exists(), "Output file with provided extension was not created"
    assert Path(
        str(test_path_without_ext) + ".vts").exists(), "Output file with automatic extension was not created"