#!/usr/bin/env python
"""VTKHDF Reader Module."""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'


# Standard Library


# Imports
import h5py

# Local Sources
from ..vtk_structures import (
    Cell,
    Grid,
    GridCoordinates,
    ImageData,
    PolyData,
    PolyDataTopology,
    RectilinearData,
    StructuredData,
    UnstructuredGrid,
)

__all__ = ['read_vtkhdf_data']


def read_data_arrays_from_group(vtk_group):
    """
    Reads data arrays from a vtkGroup object and processes them into a dictionary.

    This function iterates through the items of a given vtkGroup, processes each data
    array based on its number of components, and stores the result in a dictionary.
    If the number of components is less than or equal to 1, the function reshapes and
    flattens the array. If more components are present, the function reshapes the
    array without flattening. The returned dictionary contains the processed data
    arrays with the original keys from the vtkGroup. If no data is extracted, the
    function returns None.

    Parameters
    ----------
    vtk_group : HDF5 File Group
        A dictionary-like object representing a vtkGroup where keys are the names
        of data arrays, and values are multidimensional NumPy arrays.

    Returns
    -------
    dict or None
        A dictionary containing the processed data arrays, where keys are the
        same as in the input vtkGroup, or None if no data arrays are available.

    """
    data = {}
    for dname, darray in vtk_group.items():
        num_comp = darray.shape[-1]

        if num_comp <= 1:
            data[dname] = darray[:].reshape(-1, num_comp).flatten()
        else:
            data[dname] = darray[:].reshape(-1, num_comp)

    if data:
        return data
    else:
        return None


def read_unstructured_grid(vtkhdf):
    """
    Reads an unstructured grid from a provided VTK HDF5 file structure. This function extracts
    data arrays for points, point data, cell data, and field data, as well as topology information
    including connectivity, offsets, and cell types. It creates an UnstructuredGrid object
    using the extracted information.

    Parameters
    ----------
    vtkhdf : h5py.File or h5py.Group
        A VTK HDF5 group or file object containing the unstructured grid information.

    Returns
    -------
    UnstructuredGrid
        An object representing the unstructured grid with its point coordinates, cell topology,
        and associated data arrays for points, cells, and fields.
    """
    # get point coordinates
    points = vtkhdf['Points'][:]

    # Get Data Arrays
    # point data
    point_data = read_data_arrays_from_group(vtkhdf['PointData'])

    # cell data
    cell_data = read_data_arrays_from_group(vtkhdf['CellData'])

    # field data
    field_data = read_data_arrays_from_group(vtkhdf['FieldData'])

    # get cell data
    connectivity = vtkhdf['Connectivity'][:]
    offsets = vtkhdf['Offsets'][1::]
    types = vtkhdf['Types'][:]

    topology = Cell(connectivity=connectivity, offsets=offsets, types=types)

    num_points = vtkhdf['NumberOfPoints'][:][0]
    num_cells = vtkhdf['NumberOfCells'][:][0]
    num_connectivity = vtkhdf['NumberOfConnectivityIds'][:][0]

    # check
    # data_check = num_points == len(points)

    return UnstructuredGrid(points=points, cells=topology,
                            point_data=point_data, cell_data=cell_data, field_data=field_data)


def read_polydata(vtkhdf):
    """
    Reads and processes polydata from a VTK HDF dataset. This function extracts
    the point coordinates, data arrays (associated with points, cells, and fields), and
    geometrical topology information (vertices, lines, strips, polygons) from the provided
    VTK HDF file and returns a structured PolyData object.

    Parameters
    ----------
    vtkhdf : h5py.File
        An HDF5 group/file object representing the structure and data of a
        VTK HDF PolyData file.

    Returns
    -------
    PolyData
        A PolyData object containing the points, topology (vertices, lines, strips, polygons),
        as well as the point data, cell data, and field data arrays extracted from the
        VTK HDF dataset.

    Raises
    ------
    Exception
        This function may raise exceptions when accessing or processing data arrays or topology
        groups (e.g., if any required data is missing or malformed). Errors are caught individually
        for topology entries (Vertices, Lines, Strips, Polygons) and handled by defaulting
        corresponding elements to None in case of failures.

    """
    # get point coordinates
    num_points = vtkhdf['NumberOfPoints'][:][0]
    points = vtkhdf['Points'][:]

    # Get Data Arrays
    # point data
    point_data = read_data_arrays_from_group(vtkhdf['PointData'])

    # cell data
    cell_data = read_data_arrays_from_group(vtkhdf['CellData'])

    # field data
    field_data = read_data_arrays_from_group(vtkhdf['FieldData'])

    # get vertices
    try:
        data = read_data_arrays_from_group(vtkhdf['Vertices'])
        verts = PolyDataTopology(connectivity=data['Connectivity'][0], offsets=data['Offsets'][0][1::])
    except:
        verts = None

    # get lines
    try:
        data = read_data_arrays_from_group(vtkhdf['Lines'])
        lines = PolyDataTopology(connectivity=data['Connectivity'][0], offsets=data['Offsets'][0][1::])
    except:
        lines = None

    # get strips
    try:
        data = read_data_arrays_from_group(vtkhdf['Strips'])
        strips = PolyDataTopology(connectivity=data['Connectivity'][0], offsets=data['Offsets'][0][1::])
    except:
        strips = None

    # get polys
    try:
        data = read_data_arrays_from_group(vtkhdf['Polygons'])
        polys = PolyDataTopology(connectivity=data['Connectivity'][0], offsets=data['Offsets'][0][1::])
    except:
        polys = None


    return PolyData(points=points, verts=verts, lines=lines, strips=strips, polys=polys,
                    point_data=point_data, cell_data=cell_data, field_data=field_data)




def read_image_data(vtkhdf):
    """
    Reads image data from a VTK HDF5 file and constructs an ImageData object.

    This function reads various attributes such as Direction, Origin, Spacing,
    Version, and Whole_Extent from the VTK HDF5 file to define the grid topology.
    It then reads PointData, CellData, and FieldData from the corresponding groups
    in the HDF5 file. Finally, it creates and returns an ImageData object that
    encapsulates the read data along with the grid topology information.

    Parameters
    ----------
    vtkhdf : h5py.File
        An HDF5 file object containing VTK-related attributes and data arrays.

    Returns
    -------
    ImageData
        An object encapsulating the read point data, cell data, field data,
        and grid topology definitions.
    """
    Direction = vtkhdf.attrs['Direction']
    Origin = vtkhdf.attrs['Origin']
    Spacing = vtkhdf.attrs['Spacing']
    version = vtkhdf.attrs['Version']
    Whole_Extent = vtkhdf.attrs['WholeExtent']

    grid_topology = Grid(whole_extents=Whole_Extent, origin=Origin, spacing=Spacing, direction=Direction)

    # point data
    point_data = read_data_arrays_from_group(vtkhdf['PointData'])

    # cell data
    cell_data = read_data_arrays_from_group(vtkhdf['CellData'])

    # field data
    field_data = read_data_arrays_from_group(vtkhdf['FieldData'])

    return ImageData(point_data=point_data, cell_data=cell_data, field_data=field_data, grid=grid_topology)


def read_structured_grid(vtkhdf):
    """
    Reads and processes the structured grid data from the provided vtkhdf dataset. The function
    extracts point coordinates, extents, and associated data arrays such as point data, cell data,
    and field data. It then organizes these elements into a `StructuredData` object, which can
    be used for further analysis or visualization.

    Parameters
    ----------
    vtkhdf : h5py.File
        An HDF5 file handle that represents a VTK dataset containing structured grid data. It is
        expected to have specific datasets and attributes such as 'NumberOfPoints', 'Points',
        'WholeExtent', and data groups for 'PointData', 'CellData', and 'FieldData'.

    Returns
    -------
    StructuredData
        A structured representation of the VTK dataset, encapsulating the point data, cell data,
        field data, point coordinates, and the extents of the structured grid.
    """
    # get point coordinates
    num_points = vtkhdf['NumberOfPoints'][:][0]
    points = vtkhdf['Points'][:]
    whole_extents = vtkhdf.attrs['WholeExtent']

    # Get Data Arrays
    # point data
    point_data = read_data_arrays_from_group(vtkhdf['PointData'])

    # cell data
    cell_data = read_data_arrays_from_group(vtkhdf['CellData'])

    # field data
    field_data = read_data_arrays_from_group(vtkhdf['FieldData'])


    return StructuredData(point_data=point_data, cell_data=cell_data, field_data=field_data, points=points,
                          whole_extents=whole_extents)


def read_rectilinear_grid(vtkhdf):
    """
    Reads a rectilinear grid from the provided HDF5 file formatted in the VTK convention.

    This function parses the given VTK-compliant HDF5 file to extract rectilinear grid
    data. It reads the grid topology, including its coordinates and extents, as well
    as associated data arrays for points, cells, and fields. The extracted information
    is then packed into a `RectilinearData` object, which serves as a structured
    representation of the grid.

    Parameters
    ----------
    vtkhdf : h5py.Group
        A group object from an HDF5 file structured in compliance with the VTK format.
        This object is expected to have the following datasets and attributes:
        - Datasets: `XCoordinates`, `YCoordinates`, `ZCoordinates`.
        - Attributes: `WholeExtent`.
        - Groups: `PointData`, `CellData`, `FieldData`.

    Returns
    -------
    RectilinearData
        An object containing the extracted rectilinear grid data, including the grid
        topology (coordinates and extents), point data, cell data, and field data.

    Notes
    -----
    This function assumes a specific structure for the input HDF5 group, which is
    dictated by the VTK convention for rectilinear grids. Ensure that the input
    conforms to this structure before invoking the function.
    """
    # read coordinates - always present
    grid_topology = GridCoordinates(x=vtkhdf['XCoordinates'][:],
                                    y=vtkhdf['YCoordinates'][:],
                                    z=vtkhdf['ZCoordinates'][:],
                                    whole_extents=vtkhdf.attrs['WholeExtent'])

    # Get Data Arrays
    # point data
    point_data = read_data_arrays_from_group(vtkhdf['PointData'])

    # cell data
    cell_data = read_data_arrays_from_group(vtkhdf['CellData'])

    # field data
    field_data = read_data_arrays_from_group(vtkhdf['FieldData'])

    return RectilinearData(point_data=point_data, cell_data=cell_data, field_data=field_data, coordinates=grid_topology)




def read_vtkhdf_data(filepath):
    """
    Reads VTKHDF data from an HDF5 file and returns a corresponding data structure
    based on the type of VTKHDF dataset.

    The function identifies the dataset type using the `Type` attribute within the
    VTKHDF group of the HDF5 file. It then calls the appropriate function to parse
    the dataset. Supported dataset types include ImageData, PolyData, UnstructuredGrid,
    StructuredGrid, and RectilinearGrid.

    Parameters
    ----------
    filepath : str
        Path to the HDF5 file containing the VTKHDF data.

    Returns
    -------
    object
        A data structure corresponding to the VTKHDF dataset type, parsed from the
        specified HDF5 file.

    Raises
    ------
    TypeError
        If the file does not contain a VTKHDF group or has an unsupported type.
    """
    with (h5py.File(filepath, 'r') as f):

        try:
            vtkhdf = f['VTKHDF']
            Type = vtkhdf.attrs['Type'].decode('UTF-8')

            if Type == 'ImageData':
                return read_image_data(vtkhdf)
            elif Type == 'PolyData':
                return read_polydata(vtkhdf)
            elif Type == 'UnstructuredGrid':
                return read_unstructured_grid(vtkhdf)
            elif Type == 'StructuredGrid':
                return read_structured_grid(vtkhdf)
            elif Type == 'RectilinearGrid':
                return read_rectilinear_grid(vtkhdf)
            else:
                raise TypeError(f'Unexpected type {Type}')

        except:
            raise TypeError("The specified file is not a VTKHDF file.")
