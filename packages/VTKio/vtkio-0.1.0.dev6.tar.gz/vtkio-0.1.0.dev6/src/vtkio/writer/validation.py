#!/usr/bin/env python
"""
Shared validation utilities for VTK writers.

Contains common validation functions used across XML and VTKHDF writers.
"""

import numpy as np
from pathlib import Path
from ..utilities import flatten


class DataValidator:
    """Shared validation methods for VTK data structures."""

    @staticmethod
    def validate_extent(extent, name="extent"):
        """
        Validate extent parameters for structured grids.

        Parameters
        ----------
        extent : array-like
            Six values defining [xmin, xmax, ymin, ymax, zmin, zmax]
        name : str
            Name for error messages

        Returns
        -------
        np.ndarray
            Validated extent as integer array
        """
        try:
            extent = np.asarray(extent, dtype=int)
        except (ValueError, TypeError) as e:
            raise TypeError(f"{name} must be convertible to integer array: {e}")

        if extent.shape != (6,):
            raise ValueError(
                f"{name} must have exactly 6 elements [xmin, xmax, ymin, ymax, zmin, zmax], "
                f"got shape {extent.shape}"
            )

        # Check that min <= max for each dimension
        if extent[0] > extent[1]:
            raise ValueError(f"{name}: xmin ({extent[0]}) > xmax ({extent[1]})")
        if extent[2] > extent[3]:
            raise ValueError(f"{name}: ymin ({extent[2]}) > ymax ({extent[3]})")
        if extent[4] > extent[5]:
            raise ValueError(f"{name}: zmin ({extent[4]}) > zmax ({extent[5]})")

        return extent

    @staticmethod
    def validate_coordinates(coords, name):
        """
        Validate coordinate arrays for rectilinear grids.

        Parameters
        ----------
        coords : array-like
            Coordinate values along one axis
        name : str
            Coordinate name ('x', 'y', or 'z') for error messages

        Returns
        -------
        np.ndarray
            Validated coordinates as numeric array
        """
        if not isinstance(coords, (np.ndarray, list, tuple)):
            raise TypeError(f"{name} coordinates must be array-like (list, tuple, or numpy array)")

        try:
            coords = np.asarray(coords)
        except (ValueError, TypeError) as e:
            raise TypeError(f"Could not convert {name} coordinates to numpy array: {e}")

        if not np.issubdtype(coords.dtype, np.number):
            raise TypeError(f"{name} coordinates must contain numeric data, got dtype {coords.dtype}")

        if coords.ndim != 1:
            raise ValueError(f"{name} coordinates must be 1-dimensional, got shape {coords.shape}")

        if coords.size == 0:
            raise ValueError(f"{name} coordinates cannot be empty")

        # Check for NaN or infinite values
        if not np.all(np.isfinite(coords)):
            raise ValueError(f"{name} coordinates contain NaN or infinite values")

        return coords

    @staticmethod
    def validate_points_array(points, name="points"):
        """Validate points array for structured/unstructured grids."""
        if not isinstance(points, (np.ndarray, list)):
            raise TypeError(f"{name} must be a numpy array or list")

        points = np.asarray(points)

        if not np.issubdtype(points.dtype, np.number):
            raise TypeError(f"{name} must contain numeric data")

        if points.ndim != 2:
            raise ValueError(f"{name} must be 2D array with shape (n_points, 3), got shape {points.shape}")

        if points.shape[1] != 3:
            raise ValueError(f"{name} must have 3 columns (x, y, z), got {points.shape[1]} columns")

        if not np.all(np.isfinite(points)):
            raise ValueError(f"{name} contain NaN or infinite values")

        return points

    @staticmethod
    def validate_spacing(spacing):
        """Validate grid spacing parameters."""
        spacing = np.asarray(spacing, dtype=float)
        if spacing.shape != (3,):
            raise ValueError(f"spacing must have 3 elements [dx, dy, dz], got shape {spacing.shape}")
        if np.any(spacing <= 0):
            raise ValueError("All spacing values must be positive")
        return spacing

    @staticmethod
    def validate_origin(origin):
        """Validate origin parameters."""
        origin = np.asarray(origin, dtype=float)
        if origin.shape != (3,):
            raise ValueError(f"origin must have 3 elements [x0, y0, z0], got shape {origin.shape}")
        return origin

    @staticmethod
    def validate_direction(direction):
        """Validate direction matrix."""
        direction = np.asarray(direction, dtype=float)
        if direction.shape != (9,):
            raise ValueError(f"direction must have 9 elements (3x3 matrix flattened), got shape {direction.shape}")
        return direction

    @staticmethod
    def check_array_sizes(array_data):
        """
        Check the size of all data arrays to be written to ensure they are all the same length.

        Parameters
        ----------
        array_data : dict
            Dictionary of data arrays to be written.

        Returns
        -------
        int
            Array size if all arrays have the same size

        Raises
        ------
        ValueError
            If arrays have different sizes or contain None values
        """
        if not array_data:
            return 0

        # Flatten dictionary to check sizes more easily
        flattened_arrays = flatten(array_data, parent_key='', separator='_')

        size_info = {}
        for key, val in flattened_arrays.items():
            if val is None:
                raise ValueError(f"Array '{key}' is None - all arrays must contain data")

            if isinstance(val, np.ndarray):
                size = val.shape[0] if val.ndim > 0 else 0
            else:
                size = len(val)

            size_info[key] = size

        # Check if all sizes are equal
        sizes = list(size_info.values())
        if not sizes:
            return 0

        first_size = sizes[0]
        mismatched = [(k, v) for k, v in size_info.items() if v != first_size]

        if mismatched:
            error_msg = f"Array size mismatch. Expected size: {first_size}\n"
            for key, size in mismatched:
                error_msg += f"  - '{key}': {size}\n"
            raise ValueError(error_msg)

        return first_size

    @staticmethod
    def correct_offsets(offsets, reference_length):
        """
        Correct offsets array to ensure proper format.

        Parameters
        ----------
        offsets : array-like
            The offsets array to correct
        reference_length : int
            Expected length for validation (e.g., number of cells)

        Returns
        -------
        np.ndarray
            Corrected offsets array
        """
        offsets = np.asarray(offsets)

        if len(offsets) == reference_length:
            offsets = np.hstack([0, offsets])
        elif len(offsets) != reference_length + 1:
            raise ValueError(
                f"Offsets must be length {reference_length}+1 or {reference_length} (will prepend 0 if needed).")

        if offsets[0] != 0:
            offsets = offsets - offsets[0]

        return offsets


class DataSizeChecker:
    """Helper class for checking data array sizes against expected counts."""

    def __init__(self, npoints=0, ncells=0, point_data=None, cell_data=None):
        self.npoints = npoints
        self.ncells = ncells
        self.point_data = point_data
        self.cell_data = cell_data

    def check_point_data_sizes(self):
        """Compare size of point data with the number of points."""
        if self.point_data is not None:
            point_data_size = DataValidator.check_array_sizes(self.point_data)
            if point_data_size != self.npoints:
                raise ValueError(f'Points ({self.npoints}) and point data ({self.point_data}) sizes do not match')

    def check_cell_data_sizes(self):
        """Compare size of cell data with the number of cells."""
        if self.cell_data is not None:
            cell_data_size = DataValidator.check_array_sizes(self.cell_data)
            if cell_data_size != self.ncells:
                raise ValueError(f'Cells ({self.ncells}) and cell data ({self.cell_data_size}) sizes do not match')