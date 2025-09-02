#!/usr/bin/env python
"""
Base classes for VTK writers.

Contains common functionality shared between XML and VTKHDF writers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import numpy as np
from .validation import DataValidator, DataSizeChecker


class VTKWriterBase(ABC):
    """
    Abstract base class for all VTK writers.

    Provides common functionality for data validation, type checking,
    and basic file operations shared between XML and VTKHDF formats.
    """

    def __init__(self, filepath, point_data=None, cell_data=None, field_data=None):
        """
        Initialize the base VTK writer.

        Parameters
        ----------
        filepath : str or Path
            Path to the output file
        point_data : dict, optional
            Point data arrays
        cell_data : dict, optional
            Cell data arrays
        field_data : dict, optional
            Field data arrays
        """
        self.path = Path(filepath)
        self.point_data = self._validate_data_dict(point_data, 'point_data')
        self.cell_data = self._validate_data_dict(cell_data, 'cell_data')
        self.field_data = self._validate_data_dict(field_data, 'field_data')

        # Initialize counters
        self.npoints = 0
        self.ncells = 0
        self.nverts = 0
        self.nlines = 0
        self.nstrips = 0
        self.npolys = 0

        # Initialize validator
        self.validator = DataValidator()

    def _validate_data_dict(self, data, name):
        """Validate that data is a dictionary or None."""
        if data is None:
            return None
        if isinstance(data, str):
            raise TypeError(f"Expected a dictionary of data arrays for {name}, got string.")
        if not isinstance(data, dict):
            raise TypeError(f"Expected a dictionary of data arrays for {name}.")
        return data

    def create_size_checker(self):
        """Create a DataSizeChecker with current point/cell counts."""
        return DataSizeChecker(self.npoints, self.ncells, self.point_data, self.cell_data)

    def check_data_consistency(self):
        """Check that data arrays match expected sizes."""
        checker = self.create_size_checker()
        checker.check_point_data_sizes()
        checker.check_cell_data_sizes()

    @abstractmethod
    def write_file(self):
        """Write the VTK file. Must be implemented by subclasses."""
        pass


class StructuredGridMixin:
    """Mixin for structured grid functionality."""

    def __init__(self, whole_extent, piece_extent=None, **kwargs):
        """Initialize structured grid parameters."""
        super().__init__(**kwargs)
        self.whole_extent = self.validator.validate_extent(whole_extent, "whole_extent")

        if piece_extent is None:
            self.piece_extent = self.whole_extent.copy()
        else:
            self.piece_extent = self.validator.validate_extent(piece_extent, "piece_extent")

        # Calculate counts
        self.num_cells = self.piece_extent[1::2] - self.piece_extent[0::2]
        self.ncells = np.prod(self.num_cells)
        self.npoints = np.prod(self.num_cells + 1)


    @property
    def num_points(self):
        """Number of points in each dimension."""
        return self.num_cells + 1

    def validate_and_set_counts(self):
        """Validate and set point/cell counts."""
        # Implementation depends on mixin type
        pass

class ImageDataMixin(StructuredGridMixin):
    """Mixin for ImageData functionality."""

    def __init__(self, spacing=(1, 1, 1), origin=(0, 0, 0),
                 direction=(1, 0, 0, 0, 1, 0, 0, 0, 1), **kwargs):
        """Initialize ImageData parameters."""
        super().__init__(**kwargs)
        self.grid_spacing = self.validator.validate_spacing(spacing)
        self.origin = self.validator.validate_origin(origin)
        self.direction = self.validator.validate_direction(direction)


    def validate_and_set_counts(self):
        """Validate and set point/cell counts."""
        # Implementation depends on mixin type
        pass


class RectilinearGridMixin(StructuredGridMixin):
    """Mixin for RectilinearGrid functionality."""

    def __init__(self, x, y, z, **kwargs):
        """Initialize RectilinearGrid coordinates."""
        self.x = self.validator.validate_coordinates(x, 'x')
        self.y = self.validator.validate_coordinates(y, 'y')
        self.z = self.validator.validate_coordinates(z, 'z')

        # Auto-generate extent if not provided
        if 'whole_extent' not in kwargs:
            kwargs['whole_extent'] = np.array([
                0, len(self.x) - 1,
                0, len(self.y) - 1,
                0, len(self.z) - 1
            ])

        super().__init__(**kwargs)
        self._validate_extent_coordinate_consistency()

    def _validate_extent_coordinate_consistency(self):
        """Ensure extent matches coordinate array sizes."""
        x_size = self.whole_extent[1] - self.whole_extent[0] + 1
        y_size = self.whole_extent[3] - self.whole_extent[2] + 1
        z_size = self.whole_extent[5] - self.whole_extent[4] + 1

        if len(self.x) != x_size:
            raise ValueError(f"X coordinate array size ({len(self.x)}) doesn't match extent ({x_size})")
        if len(self.y) != y_size:
            raise ValueError(f"Y coordinate array size ({len(self.y)}) doesn't match extent ({y_size})")
        if len(self.z) != z_size:
            raise ValueError(f"Z coordinate array size ({len(self.z)}) doesn't match extent ({z_size})")

    def validate_and_set_counts(self):
        """Validate and set point/cell counts."""
        # Implementation depends on mixin type
        pass


class UnstructuredGridMixin:
    """Mixin for UnstructuredGrid functionality."""

    def __init__(self, points, cell_types=None, connectivity=None, offsets=None, **kwargs):
        """Initialize UnstructuredGrid topology."""
        super().__init__(**kwargs)

        if points is not None:
            self.points = self.validator.validate_points_array(points)
            self.npoints = len(self.points)
        else:
            self.points = None

        if cell_types is not None:
            self.cell_types = np.asarray(cell_types)
            self.ncells = len(self.cell_types)
        else:
            self.cell_types = None

        if connectivity is not None:
            self.connectivity = np.asarray(connectivity)
        else:
            self.connectivity = None

        if offsets is not None:
            self.offsets = self.validator.correct_offsets(offsets, len(cell_types) if cell_types is not None else 0)
        else:
            self.offsets = None

        # Validation
        if self.cell_types is not None and self.offsets is not None:
            if len(self.cell_types) != len(self.offsets) - 1:
                raise ValueError("Offsets array must be one element longer than cell types array.")

    def validate_and_set_counts(self):
        """Validate and set point/cell counts."""
        # Implementation depends on mixin type
        pass


class PolyDataMixin:
    """Mixin for PolyData functionality."""

    def __init__(self, points=None, verts=None, lines=None, strips=None, polys=None, **kwargs):
        """Initialize PolyData topology."""
        super().__init__(**kwargs)

        if points is not None:
            self.points = self.validator.validate_points_array(points)
            self.npoints = len(self.points)
        else:
            self.points = None

        self.verts = verts
        self.lines = lines
        self.strips = strips
        self.polys = polys

        # Set topology counts
        self.nverts = self._get_topology_count(verts)
        self.nlines = self._get_topology_count(lines)
        self.nstrips = self._get_topology_count(strips)
        self.npolys = self._get_topology_count(polys)

        if self.cell_data:
            self.ncells = self.nverts + self.nlines + self.nstrips + self.npolys

    def _get_topology_count(self, topology):
        """Get count from topology tuple or object."""
        if topology is None:
            return 0
        if hasattr(topology, 'offsets'):  # PolyDataTopology object
            return len(topology.offsets)
        elif isinstance(topology, (tuple, list)) and len(topology) >= 2:
            return len(topology[1])  # (connectivity, offsets)
        return 0

    def validate_and_set_counts(self):
        """Validate and set point/cell counts."""
        # Implementation depends on mixin type
        pass
