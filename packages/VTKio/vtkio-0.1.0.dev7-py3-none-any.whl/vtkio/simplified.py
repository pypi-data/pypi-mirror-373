#!/usr/bin/env python
"""
VTK XML Writer Class for creating VTK's XML based format.

Supports ASCII, Base64 and Appended Raw encoding of data.

Created at 13:01, 24 Feb, 2022
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

__all__ = ['uniform_grid', 'rectilinear_grid', 'regular_grid_from_extents', 'regular_grid_from_extents',
            'regular_grid_from_coordinates', 'structured_grid', 'unstructured_points', 'unstructured_point_cells',
           'unstructured_grid_to_vtk', 'lines_to_poly', 'points_to_poly', 'polylines_to_poly']

# Standard Library
import numpy as np

# Local imports
from .vtk_cell_types import VTK_Line, VTK_PolyLine, VTK_Vertex
from .writer.writers import write_vti, write_vtp, write_vtr, write_vts, write_vtu


def uniform_grid(filepath, num_cells, origin=(0, 0, 0), spacing=(1, 1, 1), cell_data=None, point_data=None,
                 field_data=None, encoding='ascii'):
    """
    Create a uniform grid from a fixed number of cells and spacing.

    Results are written in to a VTK file in an `xml` format.

    Parameters
    ----------
    filepath : str
        Full path (or path relative to working directory) of the file to be written. Do not include the file extension.
    num_cells : array-like
        List, Tuple or Numpy array of the number of cells (nx, ny, nz) in each of the three grid directions.
    origin : array-like  (default = (0,0,0))
        List, Tuple or Numpy array of the origin of the grid.
    spacing : array-like (default = (1,1,1))
        List, Tuple or Numpy array of the spacing (cell dimension) of the grid in each of the three grid directions.
    cell_data : dictionary
        Cell data to be written to VTK file. The dictionary should have the following key-value pairs: variable name: data.
        Data arrays should all be the same length and should have the same number of values as the number of cells in the grid.
        Data can contain `Scalars`, `Vectors`, `Tensors`, `Normals` and `Texture Coordinates` as defined in the VTK specification.
        The number of points in the grid is the product of (nx, ny, nz).
    point_data : dictionary
        Point data to be written to VTK file. The dictionary should have the following key-value pairs: variable name: data.
        Data arrays should all be the same length and should have the same number of values as points in the grid.
        Data can contain `Scalars`, `Vectors`, `Tensors`, `Normals` and `Texture Coordinates` as defined in the VTK specification.
        The number of points in the grid is the product of (nx+1, ny+1, nz+1).
    field_data : dictionary

    encoding : str (default = 'ascii')
        Encoding methods supported by the VTK XML writer. This can be any of 'ascii', 'binary' or 'appended'.
        In order to adhere to the xml specification both the binary and appended data is written as base64 encoded.

    Returns
    -------
    None

    """
    num_cells = np.asarray(num_cells).astype(int)
    num_points = np.asarray(num_cells) + 1
    max_extent = np.asarray(num_cells)
    whole_extents = np.array([[0, 0, 0], max_extent]).T.flatten()

    # assumes single piece, so piece extents is equal to whole extents
    write_vti(filepath, whole_extents, whole_extents, spacing=spacing, origin=origin, point_data=point_data,
              cell_data=cell_data, field_data=field_data, encoding=encoding)


def unstructured_points(filepath, positions, pointData=None, fieldData=None, encoding='ascii'):
    """
    Writes unstructured points data to a VTU file. This function facilitates saving points with
    metadata in the Visualization Toolkit unstructured grid file format.

    Parameters
    ----------
    filepath : str
        The output file path where the VTU file will be written.
    positions : numpy.ndarray
        Array of shape (n, 3) representing the 3D coordinates of the points.
    pointData : dict, optional
        Dictionary of point-wise data attributes, where each key represents a data attribute
        name and the value is an array containing its values. Default is None.
    fieldData : dict, optional
        Dictionary of field data attributes, where each key represents global metadata and the
        value is its corresponding value. Default is None.
    encoding : {'ascii', 'binary'}, optional
        Format in which the VTU file is written. 'ascii' for human-readable, 'binary' for
        compact data. Default is 'ascii'.
    """
    num_points = positions.shape[0]

    write_vtu(filepath, nodes=positions, cell_type=None, connectivity=None, offsets=None,
              point_data=pointData, cell_data=None, field_data=fieldData, encoding=encoding)

def unstructured_point_cells(filepath, positions, pointData=None, fieldData=None, encoding='ascii'):
    """
    Creates and writes unstructured point cell data to a .vtu file.

    This function generates unstructured point cells for given point positions and writes
    them to a .vtu file. In this process, each point is treated as an individual cell
    connected only to itself, creating a simple topology for unstructured grid data. The
    data is then saved in the specified file employing the appropriate encoding scheme.

    Parameters
    ----------
    filepath : str
        Path to the output .vtu file where the unstructured grid data should be written.
    positions : numpy.ndarray
        Array of shape (n, 3) representing the positions of the points in 3D space.
    pointData : dict of str, numpy.ndarray, optional
        Dictionary where keys are the names of point data arrays, and values
        are numpy arrays containing the corresponding data. Defaults to None.
    fieldData : dict of str, numpy.ndarray, optional
        Dictionary where keys are the names of field data arrays, and values
        are numpy arrays containing the corresponding data. Field data associates
        metadata or attributes with the entire dataset. Defaults to None.
    encoding : str, optional
        Encoding format for the .vtu file. Common options are 'ascii' and 'binary'.
        Defaults to 'ascii'.
    """
    num_points = positions.shape[0]

    # create some arrays to set grid topology for unstructured point data
    # each point is only connected to itself (starts at zero)
    connectivity = np.arange(num_points, dtype="int32")
    # index of last node in each cell
    offsets = np.arange(start=1, stop=num_points + 1, dtype="int32")

    cell_types = np.empty(num_points, dtype="uint8")
    cell_types[:] = VTK_Vertex

    write_vtu(filepath, nodes=positions, cell_type=cell_types, connectivity=connectivity, offsets=offsets,
              point_data=pointData, cell_data=None, field_data=fieldData, encoding=encoding)


def rectilinear_grid(filepath, x, y, z, cell_data=None, point_data=None, whole_extents=None, piece_extents=None,
                     field_data=None, encoding='appended'):
    """
    A rectilinear grid consisting of cells of the same type.

    This helper functions allows the creation of a rectilinear grid from the definition of the minimum and maximum
    coordinates in each of the three principle directions combined with the number of cells in each direction.

    Parameters
    ----------
    filepath : str
        Full path (or path relative to working directory) of the file to be written. Do not include the file extension.
    x : array-like
        List, Tuple or Numpy array of the grid coordinates along the x-axis. This should be a set increasing values that
        can be unequally spaced.
    y : array-like
        List, Tuple or Numpy array of the grid coordinates along the y-axis. This should be a set increasing values that
        can be unequally spaced.
    z : array-like
        List, Tuple or Numpy array of the grid coordinates along the z-axis. This should be a set increasing values that
        can be unequally spaced.
    cell_data : dictionary
        Cell data to be written to VTK file. The dictionary should have the following key-value pairs: variable name: data.
        Data arrays should all be the same length and should have the same number of values as the number of cells in the grid.
        Data can contain `Scalars`, `Vectors`, `Tensors`, `Normals` and `Texture Coordinates` as defined in the VTK specification.
        The number of points in the grid is the product of (nx, ny, nz).
    point_data : dictionary
        Point data to be written to VTK file. The dictionary should have the following key-value pairs: variable name: data.
        Data arrays should all be the same length and should have the same number of values as points in the grid.
        Data can contain `Scalars`, `Vectors`, `Tensors`, `Normals` and `Texture Coordinates` as defined in the VTK specification.
        The number of points in the grid is the product of (nx+1, ny+1, nz+1).
    field_data : dictionary
        Additional data to be written to the VTK files.
    encoding : str (default = 'ascii')
        Encoding methods supported by the VTK XML writer. This can be any of 'ascii', 'binary' or 'appended'.
        In order to adhere to the xml specification both the binary and appended data is written as base64 encoded.

    Returns
    -------
    None

    """
    if whole_extents is None:
        whole_extents = np.array([np.zeros(3),
                                  np.array([len(x), len(y), len(z)])-1
                                  ]).T.flatten()

    if piece_extents is None:
        piece_extents = whole_extents

    write_vtr(filepath, x, y, z, whole_extent=whole_extents, piece_extent=piece_extents,
              point_data=point_data, cell_data=cell_data, field_data=field_data, encoding=encoding)


def regular_grid_from_extents(filepath, min_extents, max_extents, num_cells, cell_data=None, point_data=None,
                              piece_extents=None, field_data=None, encoding='appended'):
    """
    A uniform rectilinear grid consisting of cells of the same type.

    This helper functions allows the creation of a regular grid from the definition of the minimum and maximum
    coordinates in each of the three principle directions combined with the number of cells in each direction.

    Parameters
    ----------
    filepath : str
        Full path (or path relative to working directory) of the file to be written. Do not include the file extension.
    num_cells : array-like
        List, Tuple or Numpy array of the number of cells (nx, ny, nz) in each of the three grid directions.
    min_extents : array-like  (default = (0,0,0))
        List, Tuple or Numpy array of the origin of the grid.
    max_extents : array-like (default = (1,1,1))
        List, Tuple or Numpy array of maximum extents of the grid in each of the three grid directions.
    cell_data : dictionary
        Cell data to be written to VTK file. The dictionary should have the following key-value pairs: variable name: data.
        Data arrays should all be the same length and should have the same number of values as the number of cells in the grid.
        Data can contain `Scalars`, `Vectors`, `Tensors`, `Normals` and `Texture Coordinates` as defined in the VTK specification.
        The number of points in the grid is the product of (nx, ny, nz).
    point_data : dictionary
        Point data to be written to VTK file. The dictionary should have the following key-value pairs: variable name: data.
        Data arrays should all be the same length and should have the same number of values as points in the grid.
        Data can contain `Scalars`, `Vectors`, `Tensors`, `Normals` and `Texture Coordinates` as defined in the VTK specification.
        The number of points in the grid is the product of (nx+1, ny+1, nz+1).
    field_data : dictionary
        Additional data to be written to the VTK files.
    encoding : str (default = 'ascii')
        Encoding methods supported by the VTK XML writer. This can be any of 'ascii', 'binary' or 'appended'.
        In order to adhere to the xml specification both the binary and appended data is written as base64 encoded.

    Returns
    -------
    None

    """
    num_cells = np.asarray(num_cells).astype(int)

    whole_extents = np.array([min_extents, max_extents]).T.flatten()

    if piece_extents is None:
        piece_extents = whole_extents

    # Dimensions
    ncells = np.prod(num_cells)
    npoints = np.prod(num_cells + 1)

    # do some error checking on array data being written - does it match the number of cells and points and are they
    # all equal in length

    # Coordinates
    x = np.linspace(min_extents[0], max_extents[0], num_cells[0] + 1, dtype='float64')
    y = np.linspace(min_extents[1], max_extents[1], num_cells[1] + 1, dtype='float64')
    z = np.linspace(min_extents[2], max_extents[2], num_cells[2] + 1, dtype='float64')

    write_vtr(filepath, x, y, z, whole_extent=whole_extents, piece_extent=piece_extents,
              point_data=point_data, cell_data=cell_data, field_data=field_data, encoding=encoding)


def regular_grid_from_coordinates(filepath, coordinates, cell_data=None, point_data=None,
                                  piece_extents=None, field_data=None, encoding='appended'):
    """
    Generate a regular grid from given coordinates and write it to a VTR (VTK Rectilinear grid) file.

    This function creates a rectilinear grid from a set of 3D coordinates and writes the resulting
    grid along with associated data (if provided) to a VTR file. The function ensures the coordinates
    are properly sorted to maintain grid consistency, and it organizes the dataset according to the
    desired extents and encoding format.

    Parameters
    ----------
    filepath : str
        Path to the output VTR file.
    coordinates : numpy.ndarray
        A 2D array of shape (npoints, 3), where `npoints` is the number of points. Each row represents
        the (x, y, z) coordinate of a point.
    cell_data : dict, optional
        A dictionary containing the data associated with cells. Keys are data categories, and values
        are dictionaries where the keys are names of cell data fields and values are NumPy arrays of
        cell-related data.
    point_data : dict, optional
        A dictionary containing the data associated with points. Keys are data categories, and values
        are dictionaries where the keys are names of point data fields and values are NumPy arrays of
        point-related data. Each array within a category must have the same length as `coordinates`.
    piece_extents : numpy.ndarray, optional
        An array defining the extents of the grid piece to be written. It should be in the order
        [xmin, xmax, ymin, ymax, zmin, zmax]. If not provided, it defaults to the extents of the
        entire dataset.
    field_data : dict, optional
        A dictionary containing global field data for the VTR file. Keys are names of fields, and values
        are NumPy arrays representing the values of these fields.
    encoding : str, optional
        A string specifying the type of encoding for the VTR file. Supported values are 'ascii',
        'binary', or 'appended'. It defaults to 'appended'.

    Raises
    ------
    ValueError
        If any point data arrays have a size that is inconsistent with the number of points.

    Notes
    -----
    The function uses `np.unique` and `np.lexsort` to process and organize coordinate data before
    generating the regular grid. All associated data (point data) is also reorganized to match the
    sorted order of the coordinates. The `writeVTR` function is responsible for writing the processed
    grid and associated data to the specified VTR file.

    """
    npoints = len(coordinates)

    x = np.unique(coordinates[:, 0])
    y = np.unique(coordinates[:, 1])
    z = np.unique(coordinates[:, 2])

    nx = len(x)
    ny = len(y)
    nz = len(z)

    sort_index = np.lexsort((coordinates[:, 0], coordinates[:, 1], coordinates[:, 2]))
    sort_index_F = np.lexsort((coordinates[:, 2], coordinates[:, 1], coordinates[:, 0]))
    sorted_coords = coordinates[sort_index]
    sorted_coords_2 = coordinates[sort_index_F]

    # need to sort any point data in the same order
    if point_data:
        for key, arrays in point_data.items():
            for name, data in arrays.items():
                if data.shape[0] != npoints:
                    raise ValueError('PointData is expected to have the same size as number of points.')
                else:
                    data = data[sort_index]

    whole_extents = np.array([np.min(coordinates, axis=0), np.max(coordinates, axis=0)]).T.flatten()

    if piece_extents is None:
        piece_extents = whole_extents

    # Dimensions
    ncells = np.prod([nx - 1, ny - 1, nz - 1])

    write_vtr(filepath, x, y, z, whole_extent=whole_extents, piece_extent=piece_extents,
              point_data=point_data, cell_data=cell_data, field_data=field_data, encoding=encoding)


def vtk_structured_grid_flat_index(i, j, k, nx, ny):
    """
    VTK structured grid flat index calculator.

    Parameters
    ----------
    i : int
        Grid x-coordinate
    j : int
        Grid y-coordinate
    k : int
        Grid z-coordinate
    nx : int
        Number of point in the x-direction of the grid.
    ny : int
        Number of point in the y-direction of the grid.

    Returns
    -------
    index : int
        VTK flattened index

    """
    return (k * (nx * ny)) + (j * nx) + i


def structured_grid(filepath, points, cell_data=None, point_data=None,
                    num_cells=None, field_data=None, encoding='appended'):
    """
    A uniform rectilinear grid consisting of cells of the same type.

    This helper functions allows the creation of a regular grid from the definition of the minimum and maximum
    coordinates in each of the three principle directions combined with the number of cells in each direction.

    Parameters
    ----------
    filepath : str
        Full path (or path relative to working directory) of the file to be written. Do not include the file extension.
    num_cells : array-like
        List, Tuple or Numpy array of the number of cells (nx, ny, nz) in each of the three grid directions.
    cell_data : dictionary
        Cell data to be written to VTK file. The dictionary should have the following key-value pairs: variable name: data.
        Data arrays should all be the same length and should have the same number of values as the number of cells in the grid.
        Data can contain `Scalars`, `Vectors`, `Tensors`, `Normals` and `Texture Coordinates` as defined in the VTK specification.
        The number of points in the grid is the product of (nx, ny, nz).
    point_data : dictionary
        Point data to be written to VTK file. The dictionary should have the following key-value pairs: variable name: data.
        Data arrays should all be the same length and should have the same number of values as points in the grid.
        Data can contain `Scalars`, `Vectors`, `Tensors`, `Normals` and `Texture Coordinates` as defined in the VTK specification.
        The number of points in the grid is the product of (nx+1, ny+1, nz+1).
    field_data : dictionary
        Additional data to be written to the VTK files.
    encoding : str (default = 'ascii')
        Encoding methods supported by the VTK XML writer. This can be any of 'ascii', 'binary' or 'appended'.
        In order to adhere to the xml specification both the binary and appended data is written as base64 encoded.

    Returns
    -------
    None

    """
    num_cells = num_cells.astype(int)

    whole_extents = np.array([[0, 0, 0], num_cells]).T.flatten()
    piece_extents = whole_extents

    # Dimensions
    ncells = np.prod(num_cells)
    npoints = len(points)

    # do some error checking on array data being written - does it match the number of cells and points and are they
    # all equal in length

    write_vts(filepath, points=points, whole_extent=whole_extents, piece_extent=piece_extents,
              point_data=point_data, cell_data=cell_data, field_data=field_data, encoding=encoding)


def unstructured_grid_to_vtk(filepath, positions, connectivity, offsets, cell_types, cellData=None, pointData=None,
                             fieldData=None, encoding='appended'):
    """
    Converts data describing an unstructured grid into a VTK file format.

    The method enables exporting geometric and attribute data for unstructured grids to VTK
    files, which can then be visualized with software supporting the VTK format.
    This function supports cell, point, and field data, with flexibility in encoding
    type for exported files.

    Parameters
    ----------
    filepath : str
        The path where the resulting VTK file will be saved.
    positions : numpy.ndarray
        An array of shape (n, 3) containing the coordinates of the points in
        3D space.
    connectivity : numpy.ndarray
        A 1D array describing the connectivity of the points to form cells
        for the unstructured grid.
    offsets : numpy.ndarray
        A 1D array specifying the starting position of each cell in the
        connectivity array.
    cell_types : numpy.ndarray
        A 1D array containing the integer identifiers defining the type of
        each cell (e.g., VTK tetrahedron, VTK hexahedron, etc.).
    cellData : dict, optional
        Dictionary containing cell-specific attribute data. Keys represent
        attribute names, and values are numpy arrays for the corresponding
        attribute data.
    pointData : dict, optional
        Dictionary containing point-specific attribute data. Keys represent
        attribute names, and values are numpy arrays for the corresponding
        attribute data.
    fieldData : dict, optional
        Dictionary containing global field data. Keys represent field names,
        and values are numpy arrays for the corresponding data.
    encoding : str, optional
        Specifies the encoding type for the file. Options include 'appended',
        'ascii', or 'binary'. Default is 'appended'.
    """
    num_points = positions.shape[0]
    num_cells = cell_types.size
    assert offsets.size == num_cells

    write_vtu(filepath, nodes=None, cell_type=None, connectivity=None, offsets=None, pointData=pointData,
              cellData=cellData, fieldData=fieldData, encoding=encoding)


def lines_to_poly(filepath, positions, connectivity=None, point_data=None, cell_data=None, fieldData=None,
                  encoding='appended', comments=None):
    """
    Converts a series of line segments or points into a VTK PolyData file format and writes it to disk.

    This function takes in point coordinates, connectivity information, and optional data arrays associated with the
    points and cells to generate a VTK PolyData file. It supports a variety of input formats and encodings for
    flexibility and compatibility with visualization tools. The generated file can be used to represent both
    line-based topology and other data fields.

    Parameters
    ----------
    filepath : str
        Path to the output .vtp file.
    positions : numpy.ndarray
        Array of point coordinates with shape (n, 3), where n is the number of points.
    connectivity : numpy.ndarray or None, optional
        Array of connectivity representing line segments. If None, each point will be treated as disconnected.
    point_data : dict or None, optional
        Dictionary containing data arrays associated with points. Keys represent names of the arrays, and values
        are numpy arrays of the same length as the number of points.
    cell_data : dict or None, optional
        Dictionary containing data arrays associated with cells. Keys represent names of the arrays, and values
        are numpy arrays of the same length as the number of cells.
    fieldData : dict or None, optional
        Dictionary containing general dataset attributes. Keys represent names of attributes, and values
        are numpy arrays or other relevant data types.
    encoding : str, optional
        Type of encoding to be used for the .vtp file. Supported values are 'ascii', 'binary', and 'appended'.
        Defaults to 'appended'.
    comments : str or None, optional
        Optional comments to include in the .vtp file.

    Notes
    -----
    The function determines the number of lines and segments from the input `connectivity` array. If no
    connectivity is provided, each point is treated as an isolated entity. Different cell types
    (e.g., `VTK_PolyLine`, `VTK_Line`) are used for the topological representation of lines.

    This function uses an external helper `writeVTP` to perform the actual writing of the .vtp file.

    """
    num_points = positions.shape[0]

    # create some temporary arrays to write grid topology
    if connectivity is None:
        connectivity = np.arange(num_points, dtype="int32")  # each point is only connected to itself

    if connectivity.ndim == 2:
        connectivity = connectivity.flatten()

    num_lines = connectivity.size // 2
    offsets = (np.arange(num_lines) + 1) * 2

    cell_types = np.empty(num_points, dtype="uint8")
    cell_types[:] = VTK_PolyLine.type_id
    cell_types[:] = VTK_Line.type_id

    write_vtp(filepath, points=positions, lines=(connectivity, offsets),
              point_data=point_data, cell_data=cell_data, field_data=fieldData, encoding=encoding)


def polylines_to_poly(filepath, positions, points_per_line, point_data=None, cell_data=None, fieldData=None,
                      encoding='appended', comments=None):
    """
    Convert polylines to a VTK PolyData file and write it to the specified path.

    This function generates VTK PolyData from given input positions and generates line connectivity information based
    on the provided `points_per_line`. It then writes the resulting PolyData to the specified file.

    Parameters
    ----------
    filepath : str
        Path to the output file where the resulting VTK PolyData will be written.

    positions : numpy.ndarray
        Array of shape (n, 3) containing the coordinates of the points.

    points_per_line : numpy.ndarray
        Array specifying the number of points per line in the PolyData.

    point_data : dict, optional
        Dictionary mapping keys to arrays with per-point data (default is None).

    cell_data : dict, optional
        Dictionary mapping keys to arrays with per-line data (default is None).

    fieldData : dict, optional
        Dictionary containing field data (data not associated with points or
        lines, default is None).

    encoding : str, optional
        Encoding to use for writing the file. Possible values are 'ascii',
        'binary', or 'appended'. Defaults to 'appended'.

    comments : str, optional
        Any comments to include in the header of the VTK file (default is None).
    """
    num_points = positions.shape[0]

    # create some temporary arrays to write grid topology
    # for points, this is simply a list of the points ids and offset by 1
    # this is passed as vertices info

    connectivity = np.arange(num_points, dtype="int32")  # each point is only connected to itself
    # offsets = np.arange(start=1, stop=num_points + 1, dtype="int32")  # index of last node in each cell

    cell_types = np.empty(num_points, dtype="uint8")
    cell_types[:] = VTK_PolyLine.type_id
    cell_types[:] = VTK_Line.type_id

    write_vtp(filepath, points=positions, lines=(connectivity, np.cumsum(points_per_line)),
              point_data=point_data, cell_data=cell_data, field_data=fieldData, encoding=encoding)


def points_to_poly(filepath, positions, data=None, fieldData=None, encoding='appended'):
    """
    Generates a VTP file representing a polydata structure where each input point is treated as a vertex cell.

    This function primarily converts the input data into the required VTK file
    structure for points represented as individual vertices in the dataset.

    Parameters
    ----------
    filepath : str
        The path to save the generated VTP file.
    positions : np.ndarray
        An array of shape (N, 3) where N is the number of points, and each point is represented
        by its x, y, and z coordinates in 3D space.
    data : dict, optional
        Dictionary containing point-associated data. Keys represent the data names, and values
        are arrays of data corresponding to each point. This is used for storing per-point custom
        attributes or properties.
    fieldData : dict, optional
        Dictionary containing metadata or additional information that is not directly associated
        with the points or cells. Keys represent the names, and values are arrays of the data.
    encoding : str, optional
        Specifies how the output file should be encoded. Defaults to 'appended'.
    """
    num_points = positions.shape[0]

    cell_types = np.empty(num_points, dtype="uint8")
    cell_types[:] = VTK_Vertex.type_id

    # create some temporary arrays to write grid topology
    # for points, this is simply a list of the points ids and offset by 1
    # this is passed as vertices info
    connectivity = np.arange(num_points, dtype="int32")  # each point is only connected to itself
    offsets = np.arange(start=1, stop=num_points + 1, dtype="int32")  # index of last node in each cell

    write_vtp(filepath, points=positions, verts=(connectivity, offsets),
              point_data=data, cell_data=None, field_data=fieldData, encoding=encoding)
