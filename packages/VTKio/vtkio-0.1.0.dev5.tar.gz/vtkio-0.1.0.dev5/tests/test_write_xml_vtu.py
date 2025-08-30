#!/usr/bin/env python
"""
Test module for VTK Unstructured Grid (.vtu) file writing functionality.

This module contains comprehensive tests for the write_vtu function, covering
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
from vtkio.vtk_cell_types import (
    VTK_Hexahedron,
    VTK_Line,
    VTK_Pyramid,
    VTK_Quad,
    VTK_Tetra,
    VTK_Triangle,
    VTK_Vertex,
    VTK_Wedge,
)
from vtkio.vtk_structures import Cell, UnstructuredGrid
from vtkio.writer.writers import write_vtu

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
    test_data_path = Path(__file__).parent.parent / "TestData" / "vtu"
    
    # Check if the test data directory exists
    if not test_data_path.exists():
        pytest.skip(f"Test data directory not found: {test_data_path}. "
                    f"To run this test, create the directory and add required test files.")
    
    return test_data_path


def test_write_vtu_basic(test_dir):
    """
    Test that write_vtu correctly writes a basic VTU file with minimal data.
    
    Tests basic file generation, metadata correctness, and data integrity.
    """
    test_path = test_dir / "test_basic_output"
    test_file = str(test_path)

    # Create simple test data - a single hexahedron (cube)
    nodes = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # Bottom face
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # Top face
    ])
    
    # Single cell of type hexahedron
    cell_type = np.array([VTK_Hexahedron.type_id])
    
    # Connectivity list for the hexahedron (8 vertices)
    connectivity = np.array([0, 1, 2, 3, 4, 5, 6, 7])
    
    # Offset for single cell
    offsets = np.array([8])
    
    # Simple point data (temperature)
    point_data = {
        'temperature': np.array([0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0], dtype=np.float32)
    }
    
    # Simple cell data (pressure)
    cell_data = {
        'pressure': np.array([101.3], dtype=np.float32)
    }

    # Write test file
    write_vtu(test_file, nodes=nodes, cell_type=cell_type, connectivity=connectivity, offsets=offsets,
              point_data=point_data, cell_data=cell_data, encoding='ascii')

    # Assert file exists with .vtu extension
    output_file = test_path.with_suffix('.vtu')
    assert output_file.exists(), "Output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify node count and positions
    assert len(data.points) == len(nodes), "Number of nodes doesn't match"
    assert np.allclose(data.points, nodes), "Node positions don't match"
    
    # Verify cell count and type
    assert len(data.cells.types) == len(cell_type), "Number of cells doesn't match"
    assert data.cells.types[0] == cell_type[0], "Cell type doesn't match"
    
    # Verify connectivity and offsets
    assert np.array_equal(data.cells.connectivity, connectivity), "Connectivity doesn't match"
    assert np.array_equal(data.cells.offsets, offsets), "Offsets don't match"

    # Verify data
    assert 'temperature' in data.point_data, "Point data missing"
    assert 'pressure' in data.cell_data, "Cell data missing"

    # Verify array values
    assert np.allclose(data.point_data['temperature'], point_data['temperature']), "Point data values mismatch"
    assert np.allclose(data.cell_data['pressure'], cell_data['pressure']), "Cell data values mismatch"


def test_write_vtu_different_encodings(test_dir):
    """
    Test that write_vtu correctly handles different encodings.
    
    Tests ascii, binary, and appended encoding formats to ensure data integrity
    is maintained regardless of the encoding used.
    """
    # Create a tetrahedron
    nodes = np.array([
        [0, 0, 0],  # Vertex 0
        [1, 0, 0],  # Vertex 1
        [0, 1, 0],  # Vertex 2
        [0, 0, 1]   # Vertex 3
    ])
    
    # Single cell of type tetrahedron
    cell_type = np.array([VTK_Tetra.type_id])
    
    # Connectivity list for the tetrahedron (4 vertices)
    connectivity = np.array([0, 1, 2, 3])
    
    # Offset for single cell
    offsets = np.array([4])
    
    # Create random point data
    point_data = {
        'temperature': np.random.random(4).astype(np.float32),
        'velocity': np.random.random((4, 3)).astype(np.float32)
    }

    # Create random cell data
    cell_data = {
        'pressure': np.random.random(1).astype(np.float32),
        'stress_tensor': np.random.random((1, 6)).astype(np.float32)  # Symmetric 3x3 tensor stored as 6 components
    }
    
    # Create field data
    field_data = {
        'time_value': np.array([0.5]),
        'iteration': np.array([100])
    }

    encodings = ['ascii', 'binary', 'appended']

    for encoding in encodings:
        test_file_name = f"test_encoding_{encoding}"
        test_path = test_dir / test_file_name
        test_file = str(test_path)

        # Write test file with current encoding
        write_vtu(test_file, nodes=nodes, cell_type=cell_type, connectivity=connectivity, offsets=offsets,
                 point_data=point_data, cell_data=cell_data, field_data=field_data, encoding=encoding)

        # Assert file exists with .vtu extension
        output_file = test_path.with_suffix('.vtu')
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
        assert np.allclose(data.cell_data['stress_tensor'],
                          cell_data['stress_tensor']), f"{encoding} encoding: Cell data (stress_tensor) values mismatch"
        
        # Verify field data
        assert np.isclose(data.field_data['time_value'][0], field_data['time_value'][0]), \
            f"{encoding} encoding: Field data (time_value) mismatch"
        assert data.field_data['iteration'][0] == field_data['iteration'][0], \
            f"{encoding} encoding: Field data (iteration) mismatch"


def test_write_vtu_multiple_cell_types(test_dir):
    """
    Test that write_vtu correctly handles multiple cell types in a single file.
    
    Creates a dataset with different cell types (hexahedron, tetrahedron, pyramid,
    wedge, quad, triangle, line, vertex) to ensure the writer handles mixed meshes.
    """
    test_path = test_dir / "test_multiple_cell_types"
    test_file = str(test_path)

    # Define nodes for various cell types
    nodes = np.array([
        # Nodes 0-7: Hexahedron
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
        
        # Nodes 8-11: Tetrahedron
        [2, 0, 0], [3, 0, 0], [2.5, 1, 0], [2.5, 0.5, 1],
        
        # Nodes 12-16: Pyramid
        [0, 2, 0], [1, 2, 0], [1, 3, 0], [0, 3, 0], [0.5, 2.5, 1],
        
        # Nodes 17-22: Wedge
        [2, 2, 0], [3, 2, 0], [2.5, 3, 0],
        [2, 2, 1], [3, 2, 1], [2.5, 3, 1],
        
        # Nodes 23-26: Quad
        [4, 0, 0], [5, 0, 0], [5, 1, 0], [4, 1, 0],
        
        # Nodes 27-29: Triangle
        [4, 2, 0], [5, 2, 0], [4.5, 3, 0],
        
        # Nodes 30-31: Line
        [0, 4, 0], [1, 4, 0],
        
        # Node 32: Vertex
        [2, 4, 0]
    ])
    
    # Cell types in order
    cell_type = np.array([
        VTK_Hexahedron.type_id,  # 0: Hexahedron (8 nodes)
        VTK_Tetra.type_id,       # 1: Tetrahedron (4 nodes)
        VTK_Pyramid.type_id,     # 2: Pyramid (5 nodes)
        VTK_Wedge.type_id,       # 3: Wedge (6 nodes)
        VTK_Quad.type_id,        # 4: Quad (4 nodes)
        VTK_Triangle.type_id,    # 5: Triangle (3 nodes)
        VTK_Line.type_id,        # 6: Line (2 nodes)
        VTK_Vertex.type_id       # 7: Vertex (1 node)
    ])
    
    # Connectivity list for all cells
    connectivity = np.array([
        # Hexahedron connectivity (8 points)
        0, 1, 2, 3, 4, 5, 6, 7,
        
        # Tetrahedron connectivity (4 points)
        8, 9, 10, 11,
        
        # Pyramid connectivity (5 points)
        12, 13, 14, 15, 16,
        
        # Wedge connectivity (6 points)
        17, 18, 19, 20, 21, 22,
        
        # Quad connectivity (4 points)
        23, 24, 25, 26,
        
        # Triangle connectivity (3 points)
        27, 28, 29,
        
        # Line connectivity (2 points)
        30, 31,
        
        # Vertex connectivity (1 point)
        32
    ])
    
    # Offsets for each cell (cumulative count of points)
    offsets = np.array([8, 12, 17, 23, 27, 30, 32, 33])
    
    # Cell data - one value per cell
    cell_data = {
        'cell_id': np.arange(8, dtype=np.int32),
        'material': np.array([1, 2, 1, 3, 2, 1, 4, 5], dtype=np.int32)
    }
    
    # Point data - one value per node
    point_data = {
        'temperature': np.linspace(0, 100, 33, dtype=np.float32),
        'displacement': np.random.random((33, 3)).astype(np.float32)
    }

    # Write test file
    write_vtu(test_file, nodes=nodes, cell_type=cell_type, connectivity=connectivity, offsets=offsets,
             point_data=point_data, cell_data=cell_data, encoding='ascii')

    # Assert file exists with .vtu extension
    output_file = test_path.with_suffix('.vtu')
    assert output_file.exists(), "Output file was not created"

    # Read the file back and verify the content
    reader = Reader(str(output_file))
    data = reader.parse()

    # Verify cell count and types
    assert len(data.cells.types) == len(cell_type), "Number of cells doesn't match"
    assert np.array_equal(data.cells.types, cell_type), "Cell types don't match"
    
    # Verify connectivity and offsets
    assert np.array_equal(data.cells.connectivity, connectivity), "Connectivity doesn't match"
    assert np.array_equal(data.cells.offsets, offsets), "Offsets don't match"

    # Verify data
    for key in point_data:
        assert key in data.point_data, f"Point data '{key}' missing"
        assert np.allclose(data.point_data[key], point_data[key]), f"Point data '{key}' values mismatch"
        
    for key in cell_data:
        assert key in data.cell_data, f"Cell data '{key}' missing"
        assert np.array_equal(data.cell_data[key], cell_data[key]), f"Cell data '{key}' values mismatch"


def test_write_vtu_large_mesh(test_dir):
    """
    Test that write_vtu correctly handles a larger mesh.
    
    Creates a structured grid of hexahedra to test performance and correctness
    with larger datasets.
    """
    test_path = test_dir / "test_large_mesh"
    test_file = str(test_path)
    
    # Create a structured grid of hexahedra
    nx, ny, nz = 10, 10, 10  # 10x10x10 = 1000 hexahedra
    
    # Create points for structured grid
    x = np.linspace(0, 1, nx+1)
    y = np.linspace(0, 1, ny+1)
    z = np.linspace(0, 1, nz+1)
    
    # Create mesh grid
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    # Reshape to get node coordinates
    nodes = np.vstack([X.ravel(), Y.ravel(), Z.ravel()]).T
    
    # Calculate total number of cells and points
    num_cells = nx * ny * nz
    num_points = (nx+1) * (ny+1) * (nz+1)
    
    # All cells are hexahedra
    cell_type = np.tile(VTK_Hexahedron.type_id, num_cells)
    
    # Create connectivity list
    connectivity = []
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                # Get local indices for the 8 vertices of current hexahedron
                idx = i + j*(nx+1) + k*(nx+1)*(ny+1)
                connectivity.extend([
                    idx, idx+1, idx+(nx+1)+1, idx+(nx+1),
                    idx+(nx+1)*(ny+1), idx+1+(nx+1)*(ny+1),
                    idx+(nx+1)+1+(nx+1)*(ny+1), idx+(nx+1)+(nx+1)*(ny+1)
                ])
    
    connectivity = np.array(connectivity, dtype=np.int32)
    
    # Create offsets (increments of 8 for hexahedra)
    offsets = np.arange(8, 8*num_cells+1, 8, dtype=np.int32)
    
    # Create point data
    point_data = {
        'temperature': np.sin(np.pi * nodes[:, 0]) * np.cos(np.pi * nodes[:, 1]) * np.exp(-nodes[:, 2]),
        'pressure': np.random.random(num_points)
    }
    
    # Create cell data
    cell_data = {
        'cell_id': np.arange(num_cells, dtype=np.int32),
        'material': np.random.randint(1, 5, num_cells, dtype=np.int32)
    }
    
    # Create field data
    field_data = {
        'time_step': np.array([1.0]),
        'iteration': np.array([42])
    }
    
    # Write test file with binary encoding (more efficient for large files)
    write_vtu(test_file, nodes=nodes, cell_type=cell_type, connectivity=connectivity, offsets=offsets,
             point_data=point_data, cell_data=cell_data, field_data=field_data, encoding='binary')

    # Assert file exists with .vtu extension
    output_file = test_path.with_suffix('.vtu')
    assert output_file.exists(), "Output file was not created"
    
    # Check file size is reasonable
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    assert file_size_mb > 0.1, "File is unexpectedly small"
    
    # Read the file back and verify basic information
    reader = Reader(str(output_file))
    data = reader.parse()
    
    # Verify point and cell counts
    assert len(data.points) == num_points, "Number of points doesn't match"
    assert len(data.cells.offsets) == num_cells, "Number of cells doesn't match"
    
    # Verify cell types are all hexahedra
    assert np.all(data.cells.types == VTK_Hexahedron.type_id), "Not all cells are hexahedra"
    
    # Verify field data
    assert 'time_step' in data.field_data, "Field data missing"
    assert np.isclose(data.field_data['time_step'][0], field_data['time_step'][0]), "Field data value mismatch"


def test_write_vtu_field_data(test_dir):
    """
    Test that write_vtu correctly handles field data of various types.
    
    Creates a simple mesh with comprehensive field data including scalars,
    vectors, arrays, and string data.
    """
    test_path = test_dir / "test_field_data"
    test_file = str(test_path)

    # Create a simple tetrahedron
    nodes = np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]
    ])
    
    cell_type = np.array([VTK_Tetra.type_id])
    connectivity = np.array([0, 1, 2, 3])
    offsets = np.array([4])
    
    # Create comprehensive field data of various types
    field_data = {
        # Scalar values
        'time': np.array([10.5]),
        'iteration': np.array([42]),
        'active': np.array([1]),
        
        # Vector/array values
        'domain_bounds': np.array([-1, -1, -1, 1, 1, 1]),
        'color': np.array([255, 0, 0]),
        
        # 2D array
        'transformation': np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ]),
        
        # String data (stored as array of ASCII codes)
        'simulation_name': np.array([ord(c) for c in "TestSimulation"]),
        
        # Integer array
        'timesteps': np.array([0, 10, 20, 30, 40, 50]),
        
        # Mixed data type in tuple
        'mixed_data': np.array([42, 3.14, 2.718])
    }
    
    # Write test file
    write_vtu(test_file, nodes=nodes, cell_type=cell_type, connectivity=connectivity, offsets=offsets,
             field_data=field_data, encoding='ascii')

    # Read the file back
    reader = Reader(str(test_path.with_suffix('.vtu')))
    data = reader.parse()
    
    # Verify field data presence
    for key in field_data:
        assert key in data.field_data, f"Field data '{key}' missing"
    
    # Verify scalar values
    assert np.isclose(data.field_data['time'][0], field_data['time'][0]), "Field data (time) value mismatch"
    assert data.field_data['iteration'][0] == field_data['iteration'][0], "Field data (iteration) value mismatch"
    
    # Verify array values
    assert np.array_equal(data.field_data['domain_bounds'], field_data['domain_bounds']), \
        "Field data (domain_bounds) value mismatch"
    assert np.array_equal(data.field_data['color'], field_data['color']), \
        "Field data (color) value mismatch"
    
    # Verify 2D array
    assert np.array_equal(data.field_data['transformation'], field_data['transformation']), \
        "Field data (transformation) value mismatch"
    
    # Verify integer array
    assert np.array_equal(data.field_data['timesteps'], field_data['timesteps']), \
        "Field data (timesteps) value mismatch"


def test_write_vtu_roundtrip_comparison(test_dir):
    """
    Test that data written to a VTU file can be read back identically.
    
    Creates an UnstructuredGrid object, writes it to a file, then reads it back
    to ensure all data is preserved correctly during the write-read cycle.
    """
    test_path = test_dir / "test_roundtrip"
    test_file = str(test_path)

    # Create a mesh with multiple cell types
    nodes = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
        [2, 0, 0], [2, 1, 0], [2, 0, 1]
    ])
    
    # One hexahedron and one tetrahedron
    cell_type = np.array([VTK_Hexahedron.type_id, VTK_Tetra.type_id])
    
    # Connectivity for both cells
    connectivity = np.array([0, 1, 2, 3, 4, 5, 6, 7, 1, 8, 9, 10])
    
    # Offsets for each cell
    offsets = np.array([8, 12])
    
    # Point data with various data types
    point_data = {
        'temperature': np.linspace(0, 100, 11),
        'velocity': np.random.random((11, 3)),
        'flags': np.random.randint(0, 2, 11, dtype=np.int32)
    }
    
    # Cell data
    cell_data = {
        'cell_id': np.array([1, 2]),
        'pressure': np.array([101.3, 203.5]),
        'material': np.array([1, 3], dtype=np.int32)
    }
    
    # Field data
    field_data = {
        'time': np.array([0.5]),
        'iteration': np.array([100])
    }
    
    # Create UnstructuredGrid object
    original_grid = UnstructuredGrid(
        points=nodes,
        cells=Cell(connectivity, offsets, cell_type),
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data
    )
    
    # Write the UnstructuredGrid to a VTU file
    original_grid.write(test_file, xml_encoding='ascii')
    
    # Read the file back
    reader = Reader(str(test_path.with_suffix('.vtu')))
    read_grid = reader.parse()
    
    # Compare points
    assert np.allclose(read_grid.points, original_grid.points), "Points don't match"
    
    # Compare cell types, connectivity, and offsets
    assert np.array_equal(read_grid.cells.types, original_grid.cells.types), "Cell types don't match"
    assert np.array_equal(read_grid.cells.connectivity, original_grid.cells.connectivity), "Connectivity doesn't match"
    assert np.array_equal(read_grid.cells.offsets, original_grid.cells.offsets), "Offsets don't match"
    
    # Compare point data
    for key in original_grid.point_data:
        assert key in read_grid.point_data, f"Point data '{key}' missing in read data"
        assert np.allclose(read_grid.point_data[key], original_grid.point_data[key]), \
            f"Point data '{key}' values don't match"
    
    # Compare cell data
    for key in original_grid.cell_data:
        assert key in read_grid.cell_data, f"Cell data '{key}' missing in read data"
        assert np.allclose(read_grid.cell_data[key], original_grid.cell_data[key]), \
            f"Cell data '{key}' values don't match"
    
    # Compare field data
    for key in original_grid.field_data:
        assert key in read_grid.field_data, f"Field data '{key}' missing in read data"
        assert np.allclose(read_grid.field_data[key], original_grid.field_data[key]), \
            f"Field data '{key}' values don't match"


def test_write_vtu_parameter_validation(test_dir):
    """
    Test validation of required parameters for write_vtu.
    
    Tests that appropriate exceptions are raised when required parameters
    are missing or invalid.
    """
    test_path = test_dir / "test_validation"
    test_file = str(test_path)
    
    # Test missing nodes (required parameter)
    with pytest.raises(TypeError):
        write_vtu(test_file)
    
    # Test with invalid cell_type format
    with pytest.raises((ValueError, TypeError)):
        write_vtu(test_file, nodes=np.array([[0, 0, 0]]), cell_type="invalid",
                 connectivity=np.array([0]), offsets=np.array([1]))
    
    # Test with mismatched cell_type and offsets lengths
    with pytest.raises(ValueError):
        write_vtu(test_file, nodes=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]),
                 cell_type=np.array([VTK_Triangle.type_id, VTK_Triangle.type_id]),
                 connectivity=np.array([0, 1, 2]),
                 offsets=np.array([3]))  # Should be [3, 6] for two triangles
    
    # Test with invalid point_data format
    with pytest.raises((ValueError, TypeError)):
        write_vtu(test_file, nodes=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]),
                 cell_type=np.array([VTK_Triangle.type_id]),
                 connectivity=np.array([0, 1, 2]), offsets=np.array([3]),
                 point_data="invalid")


def test_write_vtu_with_invalid_data(test_dir):
    """
    Test that write_vtu correctly handles invalid data.
    
    Tests error handling for invalid file format and encoding specifications.
    """
    test_path = test_dir / "test_invalid_data"
    test_file = str(test_path)
    
    # Create minimal valid data
    nodes = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    cell_type = np.array([VTK_Triangle.type_id])
    connectivity = np.array([0, 1, 2])
    offsets = np.array([3])
    
    # Test with incorrect file format
    with pytest.raises(ValueError) as excinfo:
        write_vtu(test_file, nodes=nodes, cell_type=cell_type, connectivity=connectivity, offsets=offsets,
                 file_format='invalid_format')
    assert "Unsupported file format" in str(excinfo.value)
    
    # Test with invalid encoding
    with pytest.raises((ValueError, NotImplementedError)) as excinfo:
        write_vtu(test_file, nodes=nodes, cell_type=cell_type, connectivity=connectivity, offsets=offsets,
                 encoding='invalid_encoding')
    
    # Test for consistency in array sizes - point data size mismatch
    with pytest.raises((ValueError, AssertionError)):
        write_vtu(test_file,
                  nodes=nodes,
                  cell_type=cell_type,
                  connectivity=connectivity,
                  offsets=offsets,
                  encoding='ascii',
                  point_data={"temperature": np.array([1.02])},  # Only 1 points, should be 3
                  cell_data=None
        )

    # Test for consistency in array sizes - cell data size mismatch
    with pytest.raises((ValueError, AssertionError)):
        write_vtu(test_file,
                  nodes=nodes,
                  cell_type=cell_type,
                  connectivity=connectivity,
                  offsets=offsets,
                  encoding='ascii',
                  point_data=None,
                  cell_data={"pressure": np.array([1.0, 2.0])}  # Only 2 cells, should be 1
        )