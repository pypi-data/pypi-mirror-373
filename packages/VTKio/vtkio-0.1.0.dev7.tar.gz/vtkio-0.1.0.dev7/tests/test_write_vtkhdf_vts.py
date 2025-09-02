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


def test_write_vts_additional_metadata(test_dir):
    """
    Test that write_vts correctly handles additional metadata.

    Tests writing a structured grid with custom metadata fields.
    """
    test_path = test_dir / "test_metadata"
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

    # Simple point data
    point_data = {'temperature': np.linspace(0, 100, num_points)}

    # Additional metadata
    additional_metadata = {
        'Author': 'Test User',
        'CreationDate': '2025-04-22',
        'Description': 'Test structured grid file with metadata',
        'Version': '1.0.0'
    }

    # Write the file with additional metadata (only meaningful for HDF5 format)
    write_vts(test_file, points=points, whole_extent=whole_extent, piece_extent=whole_extent,
              point_data=point_data, additional_metadata=additional_metadata,
              file_format='vtkhdf')

    # Assert file exists with .vtkhdf extension
    output_file = Path(str(test_path) + '.vtkhdf')
    assert output_file.exists(), "Output file was not created"

    # Note: Reading back and testing the additional metadata would require HDF5-specific code
    # This is more of a functionality test to ensure the API accepts the metadata parameter
