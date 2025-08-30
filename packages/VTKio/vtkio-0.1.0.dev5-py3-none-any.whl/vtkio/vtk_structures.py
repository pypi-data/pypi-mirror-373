#!/usr/bin/env python
"""
Module documentation goes here.

Created at 17:27, 22 Jul, 2024
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard Library
from dataclasses import astuple, dataclass

# Imports
import numpy as np

# Local Sources
from .writer.writers import write_vti, write_vtp, write_vtr, write_vts, write_vtu


def compare_exact(first, second):
    """Return whether two dicts of arrays are exactly equal."""
    if first.keys() != second.keys():
        return False
    return all(np.array_equal(first[key], second[key]) for key in first)


def compare_approximate(first, second):
    """
    Return whether two dicts of arrays are roughly equal.

    This is used otherwise comparing floats would return `False`.
    """
    if first.keys() != second.keys():
        return False
    return all(np.allclose(first[key], second[key]) for key in first)


def array_safe_eq(a, b) -> bool:
    """Check if a and b are equal, even if they are numpy arrays."""
    if a is b:
        return True

    if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
        # return np.array_equal(a, b)
        return np.allclose(a, b)

    if isinstance(a, dict) and isinstance(b, dict):
        return compare_approximate(a, b)

    if isinstance(a, list) and isinstance(b, list):
        pass

    if isinstance(a, tuple) and isinstance(b, tuple):
        return all((a == b).all() for a, b in zip(a, b))

    try:
        return a == b
    except TypeError:
        return NotImplemented


def dataclass_equality_check(dc1, dc2) -> bool:
    """Checks if two dataclasses which hold numpy arrays are equal."""
    if dc1 is dc2:
        return True

    if dc1.__class__ is not dc2.__class__:
        return NotImplemented  # better than False

    t1 = astuple(dc1)
    t2 = astuple(dc2)

    if len(t1) != len(t2):
        return False
    else:
        return all(array_safe_eq(a1, a2) for a1, a2 in zip(t1, t2))


@dataclass
class VTKData:
    point_data: dict
    cell_data: dict
    field_data: dict


@dataclass
class Cell:
    connectivity: np.ndarray
    offsets: np.ndarray
    types: np.ndarray


@dataclass
class PolyDataTopology:
    connectivity: np.ndarray
    offsets: np.ndarray


@dataclass
class VTKDataArray:
    Scalars: dict
    Vectors: dict
    Tensors: dict
    Normals: dict
    TCoords: dict


@dataclass
class Grid:
    whole_extents: np.ndarray
    origin: np.ndarray
    spacing: np.ndarray
    direction: np.ndarray

    def __post_init__(self):
        _cells = np.array([self.whole_extents[1] - self.whole_extents[0],
                                  self.whole_extents[3] - self.whole_extents[2],
                                  self.whole_extents[5] - self.whole_extents[4]])
        self.num_cells = np.prod(_cells)
        self.num_points = np.prod(_cells + 1)


@dataclass
class GridCoordinates:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    whole_extents: np.ndarray

    def __post_init__(self):
        self.num_points = np.prod([self.x.size, self.y.size, self.z.size])
        self.num_cells = np.prod([self.x.size - 1, self.y.size - 1, self.z.size - 1])


@dataclass
class ImageData(VTKData):
    grid: Grid

    def __eq__(self, other):
        return dataclass_equality_check(self, other)

    def write(self, filepath, file_format='xml', xml_encoding='appended'):
        """

        Parameters
        ----------
        filepath : str
        file_format : {'xml', 'vtkhdf'}, default 'xml'
        xml_encoding : {'ascii', 'binary', 'appended'}, default='appended'
            Encoding of XML files can be ascii, binary or appended. The default formatting is 'appended'.

        """
        if file_format in ['xml','vtkhdf', 'hdf', 'hdf5', 'vtk hdf']:
            write_vti(filepath, whole_extent=self.grid.whole_extents, piece_extent=self.grid.whole_extents,
                     spacing=self.grid.spacing, origin=self.grid.origin, direction=self.grid.direction,
                     point_data=self.point_data, cell_data=self.cell_data, field_data=self.field_data,
                     encoding=xml_encoding, file_format=file_format)

        else:
            raise NotImplementedError("This is not a supported file type")


@dataclass
class RectilinearData(VTKData):
    coordinates: GridCoordinates

    def __eq__(self, other):
        return dataclass_equality_check(self, other)

    def write(self, filepath, file_format='xml', xml_encoding='appended'):
        """

        Parameters
        ----------
        filepath : str
        file_format : {'xml', 'vtkhdf'}, default 'xml'
        xml_encoding : {'ascii', 'binary', 'appended'}, default='appended'
            Encoding of XML files can be ascii, binary or appended. The default formatting is 'appended'.

        """
        if file_format in ['xml','vtkhdf', 'hdf', 'hdf5', 'vtk hdf']:
            write_vtr(filepath, self.coordinates.x, self.coordinates.y, self.coordinates.z,
                     whole_extent=self.coordinates.whole_extents, piece_extent=self.coordinates.whole_extents,
                     point_data=self.point_data, cell_data=self.cell_data, field_data=self.field_data,
                     encoding=xml_encoding, file_format=file_format)

        else:
            raise NotImplementedError("This is not a supported file type")


@dataclass
class StructuredData(VTKData):
    points: np.ndarray
    whole_extents: np.ndarray

    def __post_init__(self):
        self.num_points = self.points.shape[0]
        self.num_cells = np.prod([self.whole_extents[1] - self.whole_extents[0],
                                  self.whole_extents[3] - self.whole_extents[2],
                                  self.whole_extents[5] - self.whole_extents[4]])

    def __eq__(self, other):
        return dataclass_equality_check(self, other)

    def write(self, filepath, file_format='xml', xml_encoding='appended'):
        """
        Write the data to a file.

        This function writes the data to a file in either XML or HDF5 format.
        The file format is determined by the `file_format` parameter.

        
        Parameters
        ----------
        filepath : str
        file_format : {'xml', 'vtkhdf'}, default 'xml'
        xml_encoding : {'ascii', 'binary', 'appended'}, default='appended'
            Encoding of XML files can be ascii, binary or appended. The default formatting is 'appended'.

        """
        if file_format in ['xml','vtkhdf', 'hdf', 'hdf5', 'vtk hdf']:
            write_vts(filepath, self.points, whole_extent=self.whole_extents, piece_extent=self.whole_extents,
                     point_data=self.point_data, cell_data=self.cell_data, field_data=self.field_data,
                     encoding=xml_encoding, file_format=file_format)

        else:
            raise NotImplementedError("This is not a supported file type")


@dataclass
class UnstructuredGrid(VTKData):
    points: np.ndarray
    cells: Cell

    def __eq__(self, other):
        return dataclass_equality_check(self, other)

    def write(self, filepath, file_format='xml', xml_encoding='appended'):
        """

        Parameters
        ----------
        filepath : str
        file_format : {'xml', 'vtkhdf'}, default 'xml'
        xml_encoding : {'ascii', 'binary', 'appended'}, default='appended'
            Encoding of XML files can be ascii, binary or appended. The default formatting is 'appended'.

        """
        if file_format in ['xml','vtkhdf', 'hdf', 'hdf5', 'vtk hdf']:
            write_vtu(filepath, nodes=self.points, cell_type=self.cells.types, connectivity=self.cells.connectivity,
                     offsets=self.cells.offsets, point_data=self.point_data, cell_data=self.cell_data,
                     field_data=self.field_data, encoding=xml_encoding, file_format=file_format)

        else:
            raise NotImplementedError("This is not a supported file type")


@dataclass
class PolyData(VTKData):
    points: np.ndarray
    verts: PolyDataTopology
    lines: PolyDataTopology
    strips: PolyDataTopology
    polys: PolyDataTopology

    def __eq__(self, other):
        return dataclass_equality_check(self, other)

    def write(self, filepath, file_format='xml', xml_encoding='appended'):
        """

        Parameters
        ----------
        filepath : str
        file_format : {'xml', 'vtkhdf'}, default 'xml'
        xml_encoding : {'ascii', 'binary', 'appended'}, default='appended'
            Encoding of XML files can be ascii, binary or appended. The default formatting is 'appended'.

        """
        lines = None
        verts = None
        strips = None
        polys = None

        # check for none
        if self.lines:
            lines = astuple(self.lines)
        if self.strips:
            strips = astuple(self.strips)
        if self.polys:
            polys = astuple(self.polys)
        if self.verts:
            verts = astuple(self.verts)

        if file_format in ['xml','vtkhdf', 'hdf', 'hdf5', 'vtk hdf']:

            write_vtp(filepath, points=self.points, verts=verts, lines=lines, strips=strips, polys=polys,
                     point_data=self.point_data, cell_data=self.cell_data, field_data=self.field_data,
                     encoding=xml_encoding, file_format=file_format,)

        else:
            raise NotImplementedError("This is not a supported file type")