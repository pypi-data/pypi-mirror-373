#!/usr/bin/env python
"""
Module for writing data files in VTK's XML and VTKHDF based formats.

Supports ASCII, Base64 and Appended Raw encoding of data.

This module contains the following functions:

Functions
---------
vtk_writer()
    Generic XML writer class for VTK files.
write_vti()
    Function for writing VTK `ImageData` datasets to VTK files.
write_vtr()
    Function for writing VTK `RectilinearData` datasets to VTK files.
write_vts()
    Function for writing VTK `StructuredData` datasets to VTK files.
write_vtp()
    Function for writing VTK `PolyData` datasets to VTK files.
write_vtu()
    Function for writing VTK `UnstructuredData` datasets to VTK files.
vtk_multiblock_writer()
    Function for writing VTK multi-block files.

"""


__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'


# Standard Library


# Imports
import numpy as np

# Local Sources
from .vtkhdf import VTKHDFImageDataWriter, VTKHDFStructuredGridWriter, VTKHDFRectilinearGridWriter, \
    VTKHDFUnstructuredGridWriter, VTKHDFPolyDataWriter, VTKHDFMultiBlockWriter
from .xml import XMLImageDataWriter, XMLPolyDataWriter, XMLRectilinearGridWriter, XMLStructuredGridWriter, \
    XMLUnstructuredGridWriter, xml_multiblock_writer, XML_MultiBlockWriter

__all__ = ['write_vti', 'write_vtr', 'write_vts', 'write_vtu', 'write_vtp', 'vtk_multiblock_writer']


def write_vti(filepath, whole_extent: object, piece_extent: object=None, spacing: object=(1, 1, 1), origin: object=(0, 0, 0),
              direction: object = (1, 0, 0, 0, 1, 0, 0, 0, 1), point_data: object = None, cell_data: object = None,
              field_data: object = None, additional_metadata=None, encoding='ascii', ascii_precision=16,
              ascii_ncolumns=6, add_declaration=True, appended_encoding='base64', version='1.0', file_format='xml'):
    """
    Write data to a .vti (VTK Image Data - uniformly spaced 3D grid) file.

    This function supports customization of dataset attributes such as origin, spacing,
    and direction, as well as the inclusion of point, cell, and field data.
    It handles various encodings and enables fine control over ASCII format precision and structure.

    Parameters
    ----------
    filepath : str
        Path of the .vti file where the data will be written.
    whole_extent : object
        The full extent of the dataset described in terms of its bounds.
    piece_extent : object
        The extent of the individual piece of the dataset being written.
    spacing : object, optional
        Spacing between points in the dataset. Default is (1, 1, 1).
    origin : object, optional
        Coordinates of the origin of the dataset. Default is (0, 0, 0).
    direction : object, optional
        Direction cosine matrix specifying the orientation of the dataset.
        Default is (1, 0, 0, 0, 1, 0, 0, 0, 1).
    point_data : object, optional
        Data assigned to the points of the dataset.
        Default is None.
    cell_data : object, optional
        Data assigned to the cells of the dataset.
        Default is None.
    field_data : object, optional
        General field data that is not associated with points or cells.
        Default is None.
    encoding : str, optional
        File encoding type. Options include 'ascii', 'binary', and 'appended'.
        Default is 'ascii'.
    ascii_precision : int, optional
        Precision for floating-point numbers in ASCII format. Default is 16.
    ascii_ncolumns : int, optional
        Number of columns for writing in ASCII format. Default is 6.
    add_declaration : bool, optional
        Whether to add an XML declaration in the .vti file. Default is True.
    appended_encoding : str, optional
        Encoding type for appended data in the file. Default is 'base64'.
    version : str, optional
        Version of the VTK XML format to use. Default is '1.0'.

    """
    if file_format.lower() == 'xml':

        file = XMLImageDataWriter(filepath, encoding=encoding, origin=origin, spacing=spacing, whole_extent=whole_extent,
                                  piece_extent=piece_extent, direction=direction, cell_data=cell_data, field_data=field_data,
                                  point_data=point_data, appended_encoding=appended_encoding, ascii_precision=ascii_precision,
                                  ascii_ncolumns=ascii_ncolumns, declaration=add_declaration, version=version)

        file.write_xml_file()

    elif file_format.lower() in ['vtkhdf', 'hdf5', 'hdf', 'vtk hdf']:
        file = VTKHDFImageDataWriter(filepath, whole_extent, origin, spacing, direction=direction, cell_data=cell_data,
                                     point_data=point_data, field_data=field_data,
                                     additional_metadata=additional_metadata)
        file.write_vtkhdf_file()

    else:
        raise ValueError(f"Unsupported file format: {file_format}. Supported formats are 'xml' and 'vtkhdf'.")


def write_vtr(filepath, x, y, z, whole_extent=None, piece_extent=None, point_data=None, cell_data=None, field_data=None,
              additional_metadata=None, encoding='ascii', ascii_precision=16,
              ascii_ncolumns=6, add_declaration=True, appended_encoding='base64', version='1.0',file_format='xml'):
    """
    Write a .vtr file (VTK RectilinearGrid format).

    The function manages the entire file writing process and it handles various encodings and enables fine control
    over ASCII format precision and structure.


    Parameters
    ----------
    filepath : str
        The file path where the .vtr file will be saved.
    x : array_like
        A 1D array representing the x-coordinates of the rectilinear grid.
    y : array_like
        A 1D array representing the y-coordinates of the rectilinear grid.
    z : array_like
        A 1D array representing the z-coordinates of the rectilinear grid.
    whole_extent : tuple of int, optional
        A tuple that specifies the whole extent of the grid as (x_min, x_max, y_min, y_max, z_min, z_max).
    piece_extent : tuple of int, optional
        A tuple that specifies the extent of this piece of the grid as (x_min, x_max, y_min, y_max, z_min, z_max).
    point_data : dict, optional
        A dictionary containing point data arrays to be written as part of the PointData section.
    cell_data : dict, optional
        A dictionary containing cell data arrays to be written as part of the CellData section.
    field_data : dict, optional
        A dictionary containing field data arrays to be added to the FieldData section.
    encoding : {'ascii', 'binary', 'appended'}, optional
        Specifies how data is encoded in the file. Default is 'ascii'.
    ascii_precision : int, optional
        The precision for floating point numbers when using 'ascii' encoding. Default is 16.
    ascii_ncolumns : int, optional
        The number of columns per row for data arrays in 'ascii' encoding. Default is 6.
    add_declaration : bool, optional
        If True, writes an XML declaration header at the beginning of the file. Default is True.
    appended_encoding : {'base64', 'raw'}, optional
        Specifies the secondary encoding scheme for the appended data sections when using 'appended' encoding.
        Default is 'base64'.
    version : str, optional
        Version of the VTK XML format to use. Default is '1.0'.

    """
    if file_format.lower() == 'xml':

        file = XMLRectilinearGridWriter(filepath, x, y, z, cell_data=cell_data, field_data=field_data, point_data=point_data,
                                        whole_extent=whole_extent, piece_extent=piece_extent, encoding=encoding,
                                        appended_encoding=appended_encoding, version=version, ascii_precision=ascii_precision,
                                        ascii_ncolumns=ascii_ncolumns, declaration=add_declaration)

        file.write_xml_file()

    elif file_format.lower() in ['vtkhdf', 'hdf5', 'hdf', 'vtk hdf']:
       file = VTKHDFRectilinearGridWriter(filepath, x, y, z, point_data=point_data, cell_data=cell_data, field_data=field_data,
                               additional_metadata=additional_metadata)
       file.write_vtkhdf_file()

    else:
        raise ValueError(f"Unsupported file format: {file_format}. Supported formats are 'xml' and 'vtkhdf'.")


def write_vts(filepath, points, whole_extent=None, piece_extent=None, num_cells=None, point_data=None, 
              cell_data=None, field_data=None, additional_metadata=None, encoding='ascii', ascii_precision=16,
              ascii_ncolumns=6, add_declaration=True, appended_encoding='base64', version='1.0', file_format='xml'):
    """
    Write the given data to a .vts (VTK Structured Grid XML) file format.

    This function generates a VTS file given the points that define the grid, along
    with optional data arrays for points, cells, and fields.

    The whole extent defines the global extents of the entire data, while the piece extent specifies the sub-region
    of data applicable for the generated VTS file.

    Parameters
    ----------
    filepath : str
        Path to save the output VTS file.
    points : array_like
        Array of points to define the spatial grid.
    whole_extent : array_like, optional
        Defines the extent of the entire dataset. Defaults to None.
    piece_extent : array_like, optional
        Defines the piece extent corresponding to the data being saved. Defaults to None.
    num_cells : array_like, optional
        Number of cells in each dimension. If provided, it overrides `whole_extent`
        and `piece_extent`. Defaults to None.
    point_data : dict, optional
        Dictionary containing data arrays to associate with each grid point. Defaults to None.
    cell_data : dict, optional
        Dictionary containing data arrays to associate with each cell in the grid. Defaults to None.
    field_data : dict, optional
        Dataset-wide field data to include in the file. Defaults to None.
    encoding : {'ascii', 'binary', 'appended'}, optional
        Specifies the data encoding format. Defaults to 'ascii'.
    ascii_precision : int, optional
        Number of decimal places for floating-point numbers in ASCII encoding.
        Defaults to 16.
    ascii_ncolumns : int, optional
        Maximum number of columns when writing ASCII data. Defaults to 6.
    add_declaration : bool, optional
        Whether to include an XML declaration at the start of the file. Defaults to True.
    appended_encoding : {'base64', 'raw'}, optional
        Encoding type for appended data. Used only when the `encoding` parameter
        is set to 'appended'. Defaults to 'base64'.
    version : str, optional
        Version of the VTK file format. Defaults to '1.0'.

    """
    if num_cells is not None:
        num_cells = np.asarray(num_cells, dtype=np.int32)
        whole_extent = np.array([[0, 0, 0], num_cells]).T.flatten()
        piece_extent = whole_extent

    if file_format.lower() == 'xml':

        file = XMLStructuredGridWriter(filepath, points, cell_data=cell_data, field_data=field_data, point_data=point_data,
                                       whole_extent=whole_extent, piece_extent=piece_extent, encoding=encoding,
                                       appended_encoding=appended_encoding, version=version, ascii_precision=ascii_precision,
                                       ascii_ncolumns=ascii_ncolumns, declaration=add_declaration)

        file.write_xml_file()

    elif file_format.lower() in ['vtkhdf', 'hdf5', 'hdf', 'vtk hdf']:
        file = VTKHDFStructuredGridWriter(filepath, points, num_cells=num_cells, 
                              point_data=point_data, cell_data=cell_data, field_data=field_data,
                              additional_metadata=additional_metadata)
        file.write_vtkhdf_file()

    else:
        raise ValueError(f"Unsupported file format: {file_format}. Supported formats are 'xml' and 'vtkhdf'.")


def write_vtu(filepath, nodes, cell_type=None, connectivity=None, offsets=None, point_data=None, cell_data=None, 
              field_data=None, additional_metadata=None, encoding='ascii', ascii_precision=16, ascii_ncolumns=6, 
              add_declaration=True, appended_encoding='base64', version='1.0', file_format='xml'):
    """
    Write VTK Unstructured Grid (VTU) files containing required and optional data attributes.

    Supports multiple encoding formats including ASCII, binary and appended data modes for efficient storage and
    transfer. Advanced data organization methods and field data are also supported for flexibility and proper
    representation of dataset metadata.

    Parameters
    ----------
    filepath : str
        Path to the generated VTU file.
    nodes : numpy.ndarray
        Array of node coordinates, typically shape (N, 3) for 3D points.
    cell_type : numpy.ndarray, optional
        Array specifying VTK cell types for each cell.
    connectivity : numpy.ndarray, optional
        Array defining node connectivity for each cell.
    offsets : numpy.ndarray, optional
        Array indicating start indices of each cell in connectivity array.
    point_data : dict, optional
        Dictionary of arrays containing data associated with points.
    cell_data : dict, optional
        Dictionary of arrays containing data associated with cells.
    field_data : dict, optional
        Dictionary of arrays containing data associated with the entire dataset.
    encoding : {'ascii', 'binary', 'appended'}, optional
        Output encoding format. Defaults to 'ascii'.
    ascii_precision : int, optional
        Decimal precision for ASCII output. Defaults to 16.
    ascii_ncolumns : int, optional
        Number of columns for ASCII output. Defaults to 6.
    add_declaration : bool, optional
        Include XML declaration if True. Defaults to True.
    appended_encoding : {'base64', 'raw'}, optional
        Encoding for appended data mode. Defaults to 'base64'.
    version : str, optional
        VTK XML format version. Defaults to '1.0'.

    Returns
    -------
    None
        Writes VTU file to specified filepath.
    """
    if file_format.lower() == 'xml':

        file = XMLUnstructuredGridWriter(filepath, nodes, cell_type=cell_type, connectivity=connectivity, offsets=offsets,
                                         cell_data=cell_data, field_data=field_data, point_data=point_data, encoding=encoding,
                                         appended_encoding=appended_encoding, version=version, ascii_precision=ascii_precision,
                                         ascii_ncolumns=ascii_ncolumns, declaration=add_declaration)

        file.write_xml_file()

    elif file_format.lower() in ['vtkhdf', 'hdf5', 'hdf', 'vtk hdf']:
        file = VTKHDFUnstructuredGridWriter(filepath, nodes=nodes, cell_types=cell_type, connectivity=connectivity, offsets=offsets,
                                point_data=point_data, cell_data=cell_data, field_data=field_data,
                                additional_metadata=additional_metadata,)
        file.write_vtkhdf_file()

    else:
        raise ValueError(f"Unsupported file format: {file_format}. Supported formats are 'xml' and 'vtkhdf'.")


def write_vtp(filepath, point_data=None, cell_data=None, field_data=None, points=None, verts=None, lines=None,
              strips=None, polys=None, additional_metadata=None, encoding='ascii', ascii_precision=16,
              file_format='xml', ascii_ncolumns=6, add_declaration=True, appended_encoding='base64', version='1.0'):
    """
    Write VTK PolyData (VTP) files, in either ASCII or binary formats.

    Supports configuration of precision, encoding, and data organization in the output file and
    includes geometric data, topology, and attributes.

    Parameters
    ----------
    filepath : str
        Path to the generated VTP file.

    point_data : dict, optional
        Dictionary of data arrays associated with points. Keys represent array names, and
        values are the corresponding data.

    cell_data : dict, optional
        Dictionary of data arrays associated with cells. Keys represent array names, and
        values are the corresponding data.

    field_data : dict or None, optional
        General-purpose data arrays applicable to the entire dataset, where keys represent
        array names and values are the corresponding data.

    points : numpy.ndarray or None, optional
        Array of point coordinates, typically of shape (N, 3), representing the geometry.

    verts : numpy.ndarray or None, optional
        Vertex connectivity data, typically representing singular points.

    lines : numpy.ndarray or None, optional
        Line connectivity data, representing polyline geometry.

    strips : numpy.ndarray or None, optional
        Triangle strip connectivity data.

    polys : numpy.ndarray or None, optional
        Polygonal face connectivity data.

    encoding : {'ascii', 'binary', 'appended'}, optional
        Encoding format of the output file. Defaults to 'ascii'.

    ascii_precision : int, optional
        Number of decimal places for floating-point values in ASCII mode. Defaults to 16.

    ascii_ncolumns : int, optional
        Number of data columns for arrays written in ASCII mode. Defaults to 6.

    add_declaration : bool, optional
        Includes XML declaration at the start of the file if True. Defaults to True.

    appended_encoding : {'base64', 'raw'}, optional
        Encoding format for appended data when using appended mode. Can be either 'base64'
        or 'raw'. Defaults to 'base64'.

    version : str, optional
        Version of the VTK XML file format. Defaults to '1.0'.
    """
    if file_format.lower() == 'xml':
        file = XMLPolyDataWriter(filepath, points=points, verts=verts, lines=lines, polys=polys, strips=strips,
                                 point_data=point_data, cell_data=cell_data, field_data=field_data, encoding=encoding,
                                 appended_encoding=appended_encoding, version=version, ascii_precision=ascii_precision,
                                 ascii_ncolumns=ascii_ncolumns, declaration=add_declaration)

        file.write_xml_file()

    elif file_format.lower() in ['vtkhdf', 'hdf5', 'hdf', 'vtk hdf']:
        file = VTKHDFPolyDataWriter(filepath, points, lines=lines, strips=strips,
                        polys=polys, verts=verts, point_data=point_data,
                        cell_data=cell_data, field_data=field_data, additional_metadata=additional_metadata)
        file.write_vtkhdf_file()

    else:
        raise ValueError(f"Unsupported file format: {file_format}. Supported formats are 'xml' and 'vtkhdf'.")


def vtk_multiblock_writer(filepath, blocks, additional_metadata=None, file_format='xml', add_xml_declaration=True):
    """
    Writes a multi-block dataset to a file in either XML or HDF5 format.

    This function provides functionality to write a multi-block dataset in either XML (.vtm) or
    HDF5 (.hdmf) file format depending on the specified `file_format` parameter. Additional
    metadata can be included in the HDF5 files, while XML files can optionally include an
    XML declaration at the start of the file. The blocks to write are provided as input,
    and the specific writer is selected based on the file format.

    Arguments:
        filepath: str
            The output file path to write the dataset.
        blocks: object
            The multi-block dataset to be written in the chosen file format.
        additional_metadata: Optional[dict]
            Metadata to include in the file (applicable only for HDF5 file format).
        file_format: str
            The format of the file to write. Defaults to 'xml'. Supported values are
            'xml', 'vtkhdf', 'hdf5', 'hdf', or 'vtk hdf'.
        add_xml_declaration: bool
            Determines whether to add an XML declaration in the output file when writing
            in XML format. Defaults to True.

    Raises:
        ValueError: If the provided `file_format` is not supported.
    """


    if file_format.lower() == 'xml':
        writer = XML_MultiBlockWriter('output.vtm', 'vtkMultiBlockDataSet', declaration=add_xml_declaration)
        # ... potentially customize writer settings ...
        writer.write_blocks(blocks)


    elif file_format.lower() in ['vtkhdf', 'hdf5', 'hdf', 'h5', 'vtk hdf']:
        writer = VTKHDFMultiBlockWriter(filepath, blocks, additional_metadata=additional_metadata)
        writer.write_vtkhdf_file()

    else:
        raise ValueError(f"Unsupported file format: {file_format}. Supported formats are 'xml' and 'vtkhdf'.")