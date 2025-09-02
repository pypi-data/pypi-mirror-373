#!/usr/bin/env python
"""
Test module for VTK PolyData (.vtp) file writing functionality.

This module contains comprehensive tests for the write_vtp function, covering
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
from vtkio.vtk_structures import PolyData, PolyDataTopology
from vtkio.writer.writers import write_vtp

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
    test_data_path = Path(__file__).parent.parent / "TestData" / "vtp"
    
    # Check if the test data directory exists
    if not test_data_path.exists():
        pytest.skip(f"Test data directory not found: {test_data_path}. "
                    f"To run this test, create the directory and add required test files.")
    
    return test_data_path


def test_write_vtp_minimal(test_dir):
    """
    Test that write_vtp correctly writes a minimal VTP file with no data.
    
    Tests basic file generation for empty PolyData.
    """
    test_path = test_dir / "test_minimal"
    test_file = str(test_path)

    # Write a minimal VTP file with no data
    write_vtp(test_file, points=None, verts=None, lines=None, polys=None, strips=None,
              point_data=None, cell_data=None, field_data=None, encoding='ascii')

    # Assert file exists with .vtp extension
    output_file = test_path.with_suffix('.vtp')
    assert output_file.exists(), "Minimal output file was not created"

    # Read the file back to verify it is a valid VTP file
    reader = Reader(str(output_file))
    data = reader.parse()
    
    # Verify it is an empty PolyData object
    assert isinstance(data, PolyData), "Output is not a PolyData object"
    assert data.points is None, "Points array should be empty"


def test_write_vtp_points_only(test_dir):
    """
    Test that write_vtp correctly writes a VTP file with only points.
    
    Tests basic file generation with point data but no topology.
    """
    test_path = test_dir / "test_points_only"
    test_file = str(test_path)

    # Create some points
    num_points = 10
    points = np.random.random((num_points, 3))
    
    # Create some point data
    point_data = {
        'temperature': np.random.random(num_points),
        'velocity': np.random.random((num_points, 3))
    }

    # Write test file
    write_vtp(test_file, points=points, verts=None, lines=None, polys=None, strips=None,
              point_data=point_data, cell_data=None, field_data=None, encoding='ascii')

    # Assert file exists with .vtp extension
    output_file = test_path.with_suffix('.vtp')
    assert output_file.exists(), "Points-only output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify points
    assert len(data.points) == num_points, "Number of points doesn't match"
    assert np.allclose(data.points, points), "Points don't match"

    # Verify point data
    assert 'temperature' in data.point_data, "Point data 'temperature' missing"
    assert 'velocity' in data.point_data, "Point data 'velocity' missing"
    assert np.allclose(data.point_data['temperature'], point_data['temperature']), "Temperature values don't match"
    assert np.allclose(data.point_data['velocity'], point_data['velocity']), "Velocity values don't match"


def test_write_vtp_with_vertices(test_dir):
    """
    Test that write_vtp correctly writes a VTP file with vertices.
    
    Tests file generation with point data and vertex topology.
    """
    test_path = test_dir / "test_with_vertices"
    test_file = str(test_path)

    # Create some points
    num_points = 10
    points = np.random.random((num_points, 3))
    
    # Create vertices (each point is a vertex)
    connectivity = np.arange(num_points, dtype=np.int32)
    offsets = np.arange(1, num_points + 1, dtype=np.int32)
    
    # Create some point and cell data
    point_data = {
        'temperature': np.random.random(num_points),
    }
    
    cell_data = {
        'visibility': np.ones(num_points, dtype=np.int32)
    }

    # Write test file
    write_vtp(test_file, points=points, verts=(connectivity, offsets), lines=None, polys=None, strips=None,
              point_data=point_data, cell_data=cell_data, field_data=None, encoding='ascii')

    # Assert file exists with .vtp extension
    output_file = test_path.with_suffix('.vtp')
    assert output_file.exists(), "Vertices output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify points
    assert len(data.points) == num_points, "Number of points doesn't match"
    assert np.allclose(data.points, points), "Points don't match"

    # Verify vertices
    assert hasattr(data, 'verts'), "Vertices data missing"
    assert np.array_equal(data.verts.connectivity, connectivity), "Vertices connectivity doesn't match"
    assert np.array_equal(data.verts.offsets, offsets), "Vertices offsets don't match"

    # Verify point and cell data
    assert 'temperature' in data.point_data, "Point data missing"
    assert 'visibility' in data.cell_data, "Cell data missing"
    assert np.allclose(data.point_data['temperature'], point_data['temperature']), "Point data values don't match"
    assert np.array_equal(data.cell_data['visibility'], cell_data['visibility']), "Cell data values don't match"


def test_write_vtp_with_lines(test_dir):
    """
    Test that write_vtp correctly writes a VTP file with lines.
    
    Tests file generation with point data and line topology.
    """
    test_path = test_dir / "test_with_lines"
    test_file = str(test_path)

    # Create points for lines
    points = np.array([
        [0, 0, 0], [1, 0, 0],  # Line 1
        [0, 1, 0], [1, 1, 0],  # Line 2
        [0, 0, 1], [1, 0, 1],  # Line 3
        [0, 0, 0], [0, 1, 0], [0, 0, 1]  # Line 4 (polyline with 3 points)
    ])
    
    # Line connectivity (indices into points array)
    connectivity = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8])
    
    # Line offsets (end index of each line in connectivity)
    offsets = np.array([2, 4, 6, 9])
    
    # Point data
    point_data = {
        'temperature': np.linspace(0, 100, len(points))
    }
    
    # Cell data (one value per line)
    cell_data = {
        'line_id': np.arange(1, 5),
        'line_type': np.array([1, 1, 1, 2])  # 1 for regular line, 2 for polyline
    }

    # Field data
    field_data = {
        'time_value': np.array([0.5]),
        'model_name': np.array([ord(c) for c in "LineTest"])
    }

    # Write test file
    write_vtp(test_file, points=points, verts=None, lines=(connectivity, offsets), polys=None, strips=None,
              point_data=point_data, cell_data=cell_data, field_data=field_data, encoding='ascii')

    # Assert file exists with .vtp extension
    output_file = test_path.with_suffix('.vtp')
    assert output_file.exists(), "Lines output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify points
    assert len(data.points) == len(points), "Number of points doesn't match"
    assert np.allclose(data.points, points), "Points don't match"

    # Verify lines
    assert hasattr(data, 'lines'), "Lines data missing"
    assert np.array_equal(data.lines.connectivity, connectivity), "Lines connectivity doesn't match"
    assert np.array_equal(data.lines.offsets, offsets), "Lines offsets don't match"

    # Verify point data
    assert 'temperature' in data.point_data, "Point data missing"
    assert np.allclose(data.point_data['temperature'], point_data['temperature']), "Point data values don't match"

    # Verify cell data
    assert 'line_id' in data.cell_data, "Cell data 'line_id' missing"
    assert 'line_type' in data.cell_data, "Cell data 'line_type' missing"
    assert np.array_equal(data.cell_data['line_id'], cell_data['line_id']),\
        "Cell data 'line_id' values don't match"
    assert np.array_equal(data.cell_data['line_type'], cell_data['line_type']),\
        "Cell data 'line_type' values don't match"

    # Verify field data
    assert 'time_value' in data.field_data, "Field data 'time_value' missing"
    assert np.isclose(data.field_data['time_value'][0], field_data['time_value'][0]),\
        "Field data 'time_value' doesn't match"


def test_write_vtp_with_polygons(test_dir):
    """
    Test that write_vtp correctly writes a VTP file with polygons.
    
    Tests file generation with point data and polygon topology.
    """
    test_path = test_dir / "test_with_polygons"
    test_file = str(test_path)

    # Create points for polygons
    points = np.array([
        # Square (4 vertices)
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        # Triangle (3 vertices)
        [2, 0, 0], [3, 0, 0], [2.5, 1, 0],
        # Pentagon (5 vertices)
        [0, 2, 0], [1, 2, 0], [1.5, 2.5, 0], [0.8, 3, 0], [0, 2.8, 0]
    ])
    
    # Polygon connectivity
    connectivity = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    
    # Polygon offsets
    offsets = np.array([4, 7, 12])
    
    # Point data
    point_data = {
        'temperature': np.linspace(0, 100, len(points)),
        'position': points  # Use points as vector field
    }
    
    # Cell data (one value per polygon)
    cell_data = {
        'polygon_id': np.arange(1, 4),
        'polygon_type': np.array([4, 3, 5])  # Number of sides
    }

    # Write test file
    write_vtp(test_file, points=points, verts=None, lines=None, polys=(connectivity, offsets), strips=None,
              point_data=point_data, cell_data=cell_data, field_data=None, encoding='ascii')

    # Assert file exists with .vtp extension
    output_file = test_path.with_suffix('.vtp')
    assert output_file.exists(), "Polygons output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify points
    assert len(data.points) == len(points), "Number of points doesn't match"
    assert np.allclose(data.points, points), "Points don't match"

    # Verify polygons
    assert hasattr(data, 'polys'), "Polygons data missing"
    assert np.array_equal(data.polys.connectivity, connectivity), "Polygon connectivity doesn't match"
    assert np.array_equal(data.polys.offsets, offsets), "Polygon offsets don't match"

    # Verify point data
    assert 'temperature' in data.point_data, "Point data 'temperature' missing"
    assert 'position' in data.point_data, "Point data 'position' missing"
    assert np.allclose(data.point_data['temperature'], point_data['temperature']),\
        "Point data 'temperature' doesn't match"
    assert np.allclose(data.point_data['position'], point_data['position']),\
        "Point data 'position' doesn't match"

    # Verify cell data
    assert 'polygon_id' in data.cell_data, "Cell data 'polygon_id' missing"
    assert 'polygon_type' in data.cell_data, "Cell data 'polygon_type' missing"
    assert np.array_equal(data.cell_data['polygon_id'], cell_data['polygon_id']),\
        "Cell data 'polygon_id' doesn't match"
    assert np.array_equal(data.cell_data['polygon_type'], cell_data['polygon_type']),\
        "Cell data 'polygon_type' doesn't match"


def test_write_vtp_triangle_strips(test_dir):
    """
    Test that write_vtp correctly writes a VTP file with triangle strips.
    
    Tests file generation with point data and triangle strip topology.
    """
    test_path = test_dir / "test_with_strips"
    test_file = str(test_path)

    # Create points for a triangle strip
    # A strip with 6 points forms 4 triangles
    points = np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0],  # First triangle 
        [1, 1, 0],  # Second triangle with previous 2 points
        [0, 2, 0],  # Third triangle with previous 2 points
        [1, 2, 0],  # Fourth triangle with previous 2 points
    ])
    
    # Strip connectivity - one strip with all 6 points
    connectivity = np.array([0, 1, 2, 3, 4, 5])
    
    # Strip offsets - end index of each strip in connectivity
    offsets = np.array([6])
    
    # Point data
    point_data = {
        'temperature': np.linspace(20, 80, len(points))
    }
    
    # Cell data (one value per strip - in this case just one strip)
    cell_data = {
        'strip_id': np.array([1])
    }

    # Write test file
    write_vtp(test_file, points=points, verts=None, lines=None, polys=None, strips=(connectivity, offsets),
              point_data=point_data, cell_data=cell_data, field_data=None, encoding='ascii')

    # Assert file exists with .vtp extension
    output_file = test_path.with_suffix('.vtp')
    assert output_file.exists(), "Triangle strips output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify points
    assert len(data.points) == len(points), "Number of points doesn't match"
    assert np.allclose(data.points, points), "Points don't match"

    # Verify strips
    assert hasattr(data, 'strips'), "Strips data missing"
    assert np.array_equal(data.strips.connectivity, connectivity), "Strips connectivity doesn't match"
    assert np.array_equal(data.strips.offsets, offsets), "Strips offsets don't match"

    # Verify point data
    assert 'temperature' in data.point_data, "Point data missing"
    assert np.allclose(data.point_data['temperature'], point_data['temperature']), "Point data values don't match"

    # Verify cell data
    assert 'strip_id' in data.cell_data, "Cell data missing"
    assert np.array_equal(data.cell_data['strip_id'], cell_data['strip_id']), "Cell data values don't match"


def test_write_vtp_mixed_topology(test_dir):
    """
    Test that write_vtp correctly writes a VTP file with mixed topology.
    
    Tests file generation with points, vertices, lines, and polygons.
    """
    test_path = test_dir / "test_mixed_topology"
    test_file = str(test_path)

    # Create points
    points = np.array([
        # Points for vertices (0-2)
        [0, 0, 0], [0, 0, 1], [0, 0, 2],
        # Points for line (3-6)
        [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0],
        # Points for polygon (7-10)
        [0, 1, 0], [1, 1, 0], [1, 2, 0], [0, 2, 0]
    ])
    
    # Vertex topology
    vert_connectivity = np.array([0, 1, 2])
    vert_offsets = np.array([1, 2, 3])
    
    # Line topology (one polyline with 4 points)
    line_connectivity = np.array([3, 4, 5, 6])
    line_offsets = np.array([4])
    
    # Polygon topology (one quad)
    poly_connectivity = np.array([7, 8, 9, 10])
    poly_offsets = np.array([4])
    
    # Point data
    point_data = {
        'temperature': np.linspace(0, 100, len(points))
    }
    
    # Cell data - one entry for each cell (3 vertices + 1 line + 1 polygon = 5 cells)
    cell_data = {
        'cell_id': np.array([1, 2, 3, 4, 5]),
        'cell_type': np.array([0, 0, 0, 1, 2])  # 0=vertex, 1=line, 2=polygon
    }
    
    # Field data
    field_data = {
        'time': np.array([1.25]),
        'iteration': np.array([50])
    }

    # Write test file
    write_vtp(test_file, points=points, 
              verts=(vert_connectivity, vert_offsets),
              lines=(line_connectivity, line_offsets),
              polys=(poly_connectivity, poly_offsets),
              strips=None,
              point_data=point_data, 
              cell_data=cell_data, 
              field_data=field_data,
              encoding='ascii')

    # Assert file exists with .vtp extension
    output_file = test_path.with_suffix('.vtp')
    assert output_file.exists(), "Mixed topology output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify points
    assert len(data.points) == len(points), "Number of points doesn't match"
    assert np.allclose(data.points, points), "Points don't match"

    # Verify all topologies
    assert hasattr(data, 'verts'), "Vertices data missing"
    assert hasattr(data, 'lines'), "Lines data missing"
    assert hasattr(data, 'polys'), "Polygons data missing"
    
    assert np.array_equal(data.verts.connectivity, vert_connectivity), "Vertices connectivity doesn't match"
    assert np.array_equal(data.verts.offsets, vert_offsets), "Vertices offsets don't match"
    
    assert np.array_equal(data.lines.connectivity, line_connectivity), "Lines connectivity doesn't match"
    assert np.array_equal(data.lines.offsets, line_offsets), "Lines offsets don't match"
    
    assert np.array_equal(data.polys.connectivity, poly_connectivity), "Polygons connectivity doesn't match"
    assert np.array_equal(data.polys.offsets, poly_offsets), "Polygons offsets don't match"

    # Verify point data
    assert 'temperature' in data.point_data, "Point data missing"
    assert np.allclose(data.point_data['temperature'], point_data['temperature']), "Point data values don't match"

    # Verify cell data
    assert 'cell_id' in data.cell_data, "Cell data missing"
    assert np.array_equal(data.cell_data['cell_id'], cell_data['cell_id']), "Cell data values don't match"

    # Verify field data
    assert 'time' in data.field_data, "Field data missing"
    assert np.isclose(data.field_data['time'][0], field_data['time'][0]), "Field data values don't match"
    assert data.field_data['iteration'][0] == field_data['iteration'][0], "Field data values don't match"


def test_write_vtp_different_encodings(test_dir):
    """
    Test that write_vtp correctly handles different encodings.
    
    Tests ascii, binary, and appended encoding formats to ensure data integrity
    is maintained regardless of the encoding used.
    """
    # Create a simple triangle
    points = np.array([
        [0, 0, 0], [1, 0, 0], [0.5, 1, 0]
    ])
    
    # Triangle polygon
    poly_connectivity = np.array([0, 1, 2])
    poly_offsets = np.array([3])
    
    # Point data
    point_data = {
        'temperature': np.array([20.0, 30.0, 40.0]),
        'velocity': np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    }
    
    # Cell data
    cell_data = {
        'pressure': np.array([101.3])
    }
    
    # Field data
    field_data = {
        'time': np.array([0.5]),
        'simulation_name': np.array([ord(c) for c in "test_simulation"])
    }

    encodings = ['ascii', 'binary', 'appended']

    for encoding in encodings:
        test_file_name = f"test_encoding_{encoding}"
        test_path = test_dir / test_file_name
        test_file = str(test_path)

        # Write test file with current encoding
        write_vtp(test_file, points=points, 
                  verts=None,
                  lines=None,
                  polys=(poly_connectivity, poly_offsets),
                  strips=None,
                  point_data=point_data, 
                  cell_data=cell_data, 
                  field_data=field_data,
                  encoding=encoding)

        # Assert file exists with .vtp extension
        output_file = test_path.with_suffix('.vtp')
        assert output_file.exists(), f"Output file with {encoding} encoding was not created"

        # Read the file back and verify the content
        reader = Reader(str(output_file))
        data = reader.parse()

        # Verify data values for each encoding
        assert np.allclose(data.point_data['temperature'], 
                          point_data['temperature']), f"{encoding} encoding: Temperature values mismatch"
        assert np.allclose(data.point_data['velocity'], 
                          point_data['velocity']), f"{encoding} encoding: Velocity values mismatch"
        assert np.allclose(data.cell_data['pressure'], 
                          cell_data['pressure']), f"{encoding} encoding: Pressure values mismatch"
        assert np.isclose(data.field_data['time'][0], 
                         field_data['time'][0]), f"{encoding} encoding: Time value mismatch"


def test_write_vtp_roundtrip_comparison(test_dir):
    """
    Test that data written to a VTP file can be read back identically.
    
    Creates a complex PolyData object, writes it to a file, then reads it back
    to ensure all data is preserved correctly during the write-read cycle.
    """
    test_path = test_dir / "test_roundtrip"
    test_file = str(test_path)

    # Create a more complex dataset with multiple topology elements
    # Create points
    points = np.array([
        # Isolated vertices (0-2)
        [0, 0, 0], [0.5, 0, 0], [1, 0, 0],
        # Line points (3-6)
        [0, 1, 0], [1, 1, 0], [2, 1, 0], [3, 1, 0],
        # Triangle points (7-9)
        [0, 2, 0], [1, 2, 0], [0.5, 3, 0],
        # Quad points (10-13)
        [2, 2, 0], [3, 2, 0], [3, 3, 0], [2, 3, 0]
    ])
    
    # Vertex topology
    vert_connectivity = np.array([0, 1, 2])
    vert_offsets = np.array([1, 2, 3])
    
    # Line topology (polyline)
    line_connectivity = np.array([3, 4, 5, 6])
    line_offsets = np.array([4])
    
    # Polygon topology (triangle + quad)
    poly_connectivity = np.array([7, 8, 9, 10, 11, 12, 13])
    poly_offsets = np.array([3, 7])  # First 3 points for triangle, next 4 for quad
    
    # Point data
    point_data = {
        'scalar': np.linspace(0, 100, len(points)),
        'vector': np.random.random((len(points), 3)),
        'tensor': np.random.random((len(points), 9))
    }
    
    # Cell data (3 vertices + 1 line + 2 polygons = 6 cells)
    cell_data = {
        'id': np.arange(6),
        'type': np.array([0, 0, 0, 1, 2, 2]),  # 0=vertex, 1=line, 2=polygon
        'material': np.array([1, 1, 1, 2, 3, 3])
    }
    
    # Field data
    field_data = {
        'time': np.array([10.5]),
        'iteration': np.array([42]),
        'description': np.array([ord(c) for c in "A complex polydata example"])
    }
    
    # Create original PolyData object
    original_data = PolyData(
        points=points,
        verts=PolyDataTopology(vert_connectivity, vert_offsets),
        lines=PolyDataTopology(line_connectivity, line_offsets),
        polys=PolyDataTopology(poly_connectivity, poly_offsets),
        strips=None,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data
    )
    
    # Write the data to a VTP file
    original_data.write(test_file, xml_encoding='ascii')
    
    # Assert file exists with .vtp extension
    output_file = test_path.with_suffix('.vtp')
    assert output_file.exists(), "Roundtrip output file was not created"
    
    # Read the file back
    reader = Reader(str(output_file))
    read_data = reader.parse()
    
    # Compare points
    assert len(read_data.points) == len(original_data.points), "Number of points doesn't match"
    assert np.allclose(read_data.points, original_data.points), "Points don't match"
    
    # Compare topologies
    # Vertices
    assert hasattr(read_data, 'verts'), "Vertices missing in read data"
    assert np.array_equal(read_data.verts.connectivity, original_data.verts.connectivity),\
        "Vertices connectivity doesn't match"
    assert np.array_equal(read_data.verts.offsets, original_data.verts.offsets), "Vertices offsets don't match"
    
    # Lines
    assert hasattr(read_data, 'lines'), "Lines missing in read data"
    assert np.array_equal(read_data.lines.connectivity, original_data.lines.connectivity),\
        "Lines connectivity doesn't match"
    assert np.array_equal(read_data.lines.offsets, original_data.lines.offsets), "Lines offsets don't match"
    
    # Polygons
    assert hasattr(read_data, 'polys'), "Polygons missing in read data"
    assert np.array_equal(read_data.polys.connectivity, original_data.polys.connectivity),\
        "Polygons connectivity doesn't match"
    assert np.array_equal(read_data.polys.offsets, original_data.polys.offsets),\
        "Polygons offsets don't match"
    
    # Compare point data
    for key in original_data.point_data:
        assert key in read_data.point_data, f"Point data '{key}' missing in read data"
        assert np.allclose(read_data.point_data[key], original_data.point_data[key]),\
            f"Point data '{key}' doesn't match"
    
    # Compare cell data
    for key in original_data.cell_data:
        assert key in read_data.cell_data, f"Cell data '{key}' missing in read data"
        assert np.array_equal(read_data.cell_data[key], original_data.cell_data[key]),\
            f"Cell data '{key}' doesn't match"
    
    # Compare field data
    for key in original_data.field_data:
        assert key in read_data.field_data, f"Field data '{key}' missing in read data"
        # For numeric data
        if key in ['time', 'iteration']:
            assert np.allclose(read_data.field_data[key], original_data.field_data[key]),\
                f"Field data '{key}' doesn't match"
        # For string data (stored as arrays of ASCII values)
        else:
            assert np.array_equal(read_data.field_data[key], original_data.field_data[key]),\
                f"Field data '{key}' doesn't match"