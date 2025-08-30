#!/usr/bin/env python
"""
Module for reading data files in VTK's XML based format. This module contains the following classes and functions:

Classes
-------
Reader()
    Class to read VTK XML data files.

Functions
---------
convert_to_vtkhdf(x=1)
    Convert a VTK XML file to an equivalent VTKHDF file.

"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'


import struct
from pathlib import Path

import numpy as np
import pybase64
import xmltodict
from dotwiz import DotWiz

from ..helpers import BIG_ENDIAN, LITTLE_ENDIAN, _determine_points_key, _parse_bytecount_type
from ..utilities import dict_extract_generator, get_recursively

# import vtk
# from vtk.util.numpy_support import vtk_to_numpy
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

__all__ = ['convert_to_vtkhdf', 'read_vtkxml_data', 'Reader']


# read using vtk library
# def read_vtp(path):
#     reader = vtk.vtkXMLPolyDataReader()
#     reader.SetFileName(path)
#     reader.Update()
#     data = reader.GetOutput().GetPointData()
#     field_count = data.GetNumberOfArrays()
#
#     return {data.GetArrayName(i): vtk_to_numpy(data.GetArray(i)) for i in range(field_count)}


class Reader:
    """VTK XML Reader Class."""

    supported_filetypes = ['.vti', '.vtr', '.vts', '.vtu', '.vtp']

    def __init__(self, file_path, encoding='utf-8'):
        """
        Create an instance of the VTK XML reader.

        This reads the XML file and extracts the key metadata required to parse the `DataArray`s.

        Extract the data by calling the `parse()` method.

        Parameters
        ----------
        file_path: str
            Relative or absolute path of the VTK XML file.
        encoding: str
            Filetype encoding. Default is 'utf-8'.
        """
        self.file_path = Path(file_path)
        if self.file_path.suffix.lower() not in Reader.supported_filetypes:
            raise ValueError('Unsupported file type')

        # check if file exists
        if not self.file_path.exists():
            raise FileNotFoundError(f"File {self.file_path} does not exist.")

        # set placeholders
        self.encoding = encoding
        self.grid = None
        self.topology = None
        self.points = None
        self.field_data = None
        self.cell_data = None
        self.point_data = None
        self.appended_data = False
        self.appended_data_arrays = None
        self.is_valid_xml = True

        # process vtk file
        self.parse_xml_structure()



    def parse(self):
        """
        Parses the file based on its type and selects the appropriate parsing method.

        This method determines the type of grid data from the file, such as
        'UnstructuredGrid', 'StructuredGrid', 'RectilinearGrid', 'ImageData', or 'PolyData',
        and delegates the parsing task to the corresponding specialized parsing method.
        It encapsulates the logic for selecting an appropriate parser and retrieving
        the data.

        Returns
        -------
        data : Any
            Parsed data resulting from the specific parsing logic based on the grid type.
        """
        # select correct parser
        if self.file_type == 'UnstructuredGrid':
            data = self.parse_unstructured()

        elif self.file_type == 'StructuredGrid':
            data = self.parse_structured()

        elif self.file_type == 'RectilinearGrid':
            data = self.parse_rectilinear()

        elif self.file_type == 'ImageData':
            data = self.parse_imagedata()

        elif self.file_type == 'PolyData':
            data = self.parse_polydata()

        return data

    def parse_xml_structure(self):
        """
        Extract the key metadata from the XML file.

        Returns
        -------
        None

        """
        _raw_file_contents_bytes = self.file_path.read_bytes()

        try:
            # parse a valid xml file
            self._vtk_xml_file = xmltodict.parse(_raw_file_contents_bytes)['VTKFile']

            # check for appended data
            try:
                self.appended_data_bstr = self._vtk_xml_file['AppendedData']['#text'].strip('_')
                self.binary_data_encoding = self._vtk_xml_file['AppendedData']['@encoding']
                self.appended_data = True

            except:
                self.appended_data_bstr = None
                self.binary_data_encoding = None

        except:
            # invalid xml where raw binary is appended to file
            self.is_valid_xml = False
            self.appended_data = True
            self.binary_data_encoding = 'raw'

            binary_parts_a = _raw_file_contents_bytes.split(b'<AppendedData encoding="raw">\n')
            binary_parts_b = binary_parts_a[1].split(b'</AppendedData>')

            reconstituted_file = binary_parts_a[0] + b'<AppendedData encoding="raw">\n' + b'\n   </AppendedData>\n </VTKFile>\n'
            self._vtk_xml_file = xmltodict.parse(reconstituted_file)['VTKFile']

            self.appended_data_bstr = binary_parts_b[0].split(b' _', 1)[1]


        # set file descriptors
        self.file_type = self._vtk_xml_file['@type']
        self.file_version = float(self._vtk_xml_file['@version'])
        self.byte_order = self._vtk_xml_file['@byte_order'].lower()
        if self.file_version < 1:
            self.byte_count_type = 'Uint32'
        else:
            self.byte_count_type = self._vtk_xml_file['@header_type']
        self.byte_count_format = _parse_bytecount_type(self.byte_count_type, self.byte_order)
        try:
            self.data_format = next(dict_extract_generator('@format', self._vtk_xml_file[self.file_type]['Piece']))
        except StopIteration:
            self.data_format = None

        # split appended data now so only dictionary look-up required later
        if self.appended_data:
            appended_offset_keys = get_recursively(self._vtk_xml_file[self.file_type]['Piece'], '@offset')
            if self.binary_data_encoding == 'base64':
                appended_offsets = [int(x) for x in appended_offset_keys]
                data_arrays = [self.appended_data_bstr[i:j] for i, j in zip(appended_offsets, appended_offsets[1:] + [None])]

                # decode base64 data now instead of later
                decoded_data_arrays = []
                for array in data_arrays:
                    decoded_data_arrays.append(pybase64.b64decode(array))

                    data_arrays = decoded_data_arrays

                # collate arrays
                self.appended_data_arrays = dict(zip(appended_offset_keys, data_arrays))

            elif self.binary_data_encoding == 'raw':
                current_offset = 0
                data_arrays = {}
                # looping over each array with exact size ensure no rubbish data at end is included
                for offset in appended_offset_keys:
                    arr_size = struct.unpack_from(self.byte_count_format[0], self.appended_data_bstr[current_offset:])
                    data_start = current_offset
                    data_end = current_offset + self.byte_count_format[1] + arr_size[0]
                    data_arrays[offset] = self.appended_data_bstr[data_start:data_end]
                    current_offset += self.byte_count_format[1] + arr_size[0]

                # collate arrays
                self.appended_data_arrays = data_arrays

            else:
                # set empty arrays
                self.appended_data_arrays = {}

        # set data flags
        try:
            self._vtk_xml_file[self.file_type]['Piece']['PointData']
            self.point_data = True
        except:
            pass

        try:
            self._vtk_xml_file[self.file_type]['Piece']['CellData']
            self.cell_data = True
        except:
            pass

        try:
            self._vtk_xml_file[self.file_type]['Piece']['FieldData']
            self.field_data = True
        except:
            pass

    def parse_imagedata(self):
        """
        Reads and processes image data from the provided file and appended data.

        The function extracts grid topology information, including extents, origin,
        spacing, and direction, from the file's `ImageData` attribute. It then
        retrieves the data arrays (cell data, field data, and point data) by
        processing the `ImageData` attribute in conjunction with the appended data.


        Returns
        -------
        ImageData
            An instance of the `ImageData` class holding the extracted data arrays
            (cell data, field data, point data) and the grid topology information.
        """
        grid_topology = Grid(whole_extents=np.fromstring(self._vtk_xml_file[self.file_type]['@WholeExtent'], dtype=int, sep=' '),
                             origin=np.fromstring(self._vtk_xml_file[self.file_type]['@Origin'], dtype=np.float32, sep=' '),
                             spacing=np.fromstring(self._vtk_xml_file[self.file_type]['@Spacing'], dtype=np.float32, sep=' '),
                             direction=np.fromstring(self._vtk_xml_file[self.file_type]['@Direction'], dtype=np.float32, sep=' '))

        # Get Data Arrays
        field_data = self.get_data('FieldData')
        cell_data = self.get_data('CellData')
        point_data = self.get_data('PointData')


        return ImageData(point_data=point_data, cell_data=cell_data, field_data=field_data, grid=grid_topology)


    def parse_rectilinear(self):
        """
        Reads and processes rectilinear grid data from the given file and appends
        additional data if provided.

        The function extracts grid coordinates, topology, and associated data arrays
        such as cell data, field data, and point data. It consolidates these into a
        RectilinearData object for further use.

        Returns
        -------
        RectilinearData
            A consolidated object representing the rectilinear grid, including
            coordinates, topology, cell data, field data, and point data.
        """
        # read coordinates - always present
        grid_topology = self.recover_grid_coordinates()

        # Get Data Arrays
        field_data = self.get_data('FieldData')
        cell_data = self.get_data('CellData')
        point_data = self.get_data('PointData')

        return RectilinearData(point_data=point_data, cell_data=cell_data, field_data=field_data,
                               coordinates=grid_topology)


    def parse_structured(self):
        """
        Reads and processes a structured grid from a given data file and appends relevant data arrays to the result.

        The function extracts structured grid information such as grid points, whole extents, and associated
        data arrays (cell data, field data, and point data) from the provided data file .
        Returns an instance of `StructuredData` containing the processed information.


        Returns
        -------
        StructuredData
            An instance of `StructuredData` containing point data, cell data, field data, grid points,
            and grid whole extents.

        """
        # get point coordinates
        raw_points = self.get_data_arrays(self._vtk_xml_file[self.file_type]['Piece']['Points']['DataArray'])
        points = _determine_points_key(raw_points)

        # read coordinates - always present
        whole_extents = np.fromstring(self._vtk_xml_file[self.file_type]['@WholeExtent'], sep=' ')

        # Get Data Arrays
        field_data = self.get_data('FieldData')
        cell_data = self.get_data('CellData')
        point_data = self.get_data('PointData')

        return StructuredData(point_data=point_data, cell_data=cell_data, field_data=field_data, points=points,
                              whole_extents=whole_extents)


    def parse_unstructured(self):
        """
        Reads unstructured data from a provided file and returns it as an `UnstructuredGrid`.

        The function retrieves point coordinates, topology, and data arrays, including cell
        data, field data, and point data, from the unstructured grid file.

        This is useful for loading and processing unstructured grid representations in computational geometry
        or scientific computing applications.

        Returns
        -------
        UnstructuredGrid
            A data structure containing points, cells, point data, cell data,
            and field data for the unstructured grid.
        """
        piece_ = self._vtk_xml_file[self.file_type]['Piece']

        # get point coordinates
        raw_points = self.get_data_arrays(piece_['Points']['DataArray'])
        points = _determine_points_key(raw_points)

        # get cell topology
        try:
            topology = self.get_data_arrays(piece_['Cells']['DataArray'])
        except:
            topology = self.get_data_arrays(piece_['Cells']['Array'])

        cell_topology = Cell(connectivity=topology['connectivity'], offsets=topology['offsets'],
                             types=topology['types'])

        # Get Data Arrays
        _fielddata = self.get_data('FieldData')
        _celldata = self.get_data('CellData')
        _pointdata = self.get_data('PointData')

        field_data = DotWiz(_fielddata) if _fielddata else None
        cell_data = DotWiz(_celldata) if _celldata else None
        point_data = DotWiz(_pointdata) if _pointdata else None

        return UnstructuredGrid(points=points, cells=cell_topology,
                                point_data=point_data, cell_data=cell_data, field_data=field_data)


    def parse_polydata(self):
        """
        Parses `PolyData` from a provided dictionary object and additional appended binary data.

        The function retrieves point coordinates, topology, and data arrays, including cell data, field data, and point
        data from the PolyData file.

        This is useful for loading and processing unstructured grid representations in computational geometry
        or scientific computing applications.

        Returns
        -------
        PolyData
            An instance of `PolyData` containing the parsed point coordinates, topology (vertices, lines, strips,
            including cell data, field data, and point data.


        """
        # read topology - always present
        piece_ = self._vtk_xml_file[self.file_type]['Piece']

        # get poly counts
        num_points = int(piece_['@NumberOfPoints'])
        num_verts = int(piece_['@NumberOfVerts'])
        num_lines = int(piece_['@NumberOfLines'])
        num_strips = int(piece_['@NumberOfStrips'])
        num_polys = int(piece_['@NumberOfPolys'])

        # get topology
        # get point coordinates
        points = None
        if num_points > 0:
            raw_points = self.get_data_arrays(piece_['Points']['DataArray'])
            points = _determine_points_key(raw_points)

        verts = None
        lines = None
        strips = None
        polys = None

        # get vertices
        if num_verts > 0:
            vert_topology = self.get_data_arrays(piece_['Verts']['DataArray'])
            verts = PolyDataTopology(connectivity=vert_topology['connectivity'], offsets=vert_topology['offsets'])

        # get lines
        if num_lines > 0:
            line_topology = self.get_data_arrays(piece_['Lines']['DataArray'])
            lines = PolyDataTopology(connectivity=line_topology['connectivity'], offsets=line_topology['offsets'])

        # get strips
        if num_strips > 0:
            strip_topology = self.get_data_arrays(piece_['Strips']['DataArray'])
            strips = PolyDataTopology(connectivity=strip_topology['connectivity'], offsets=strip_topology['offsets'])

        # get polys
        if num_polys > 0:
            poly_topology = self.get_data_arrays(piece_['Polys']['DataArray'])
            polys = PolyDataTopology(connectivity=poly_topology['connectivity'], offsets=poly_topology['offsets'])

        # Get Data Arrays
        field_data = self.get_data('FieldData')
        cell_data = self.get_data('CellData')
        point_data = self.get_data('PointData')

        return PolyData(points=points, verts=verts, lines=lines, strips=strips, polys=polys,
                        point_data=point_data, cell_data=cell_data, field_data=field_data)


    def get_data(self, data_type):
        """
        Retrieve data arrays from a VTK XML file.

        This method extracts and recovers data arrays for a given data type in the `Piece` element of a VTK XML file.
        If no data is present in a specific section, the corresponding return value will be `None`.

        Returns
        -------
        data: The extracted data arrays from the `PointData` section or `None` if unavailable.
        """
        piece_ = self._vtk_xml_file[self.file_type]['Piece']

        if data_type in piece_:
            if piece_[data_type]:
                data_ = piece_[data_type]
                # Try to get data from DataArray, fall back to Array if needed
                try:
                    return self.get_data_arrays(data_['DataArray'])
                except KeyError:
                    return self.get_data_arrays(data_['Array'])

        else:
            return None


    def decode_byte_data(self, data, data_type):
        """Helper to decode input data based on encoding type."""
        data_size = struct.unpack_from(self.byte_count_format[0], data)[0]

        if data_type != 's':
            dtype = self.decode_np_byteorder(data_type)
            return np.frombuffer(data[self.byte_count_format[1]:self.byte_count_format[1] + data_size], dtype=dtype)
        else:
            dtype = self.decode_str_byteorder(data_type, data_size)
            data_strs = struct.unpack(dtype, data[self.byte_count_format[1]:])[0]
            return data_strs.decode('utf8').rstrip('\x00').split('\x00')

    def decode_array(self, data, data_type, offset=None):
        """
        Decode data into a NumPy array based on the given format type and parameters.

        This function decodes data from either an ASCII-encoded string, a binary Base64
        encoded string, or an appended Base64 encoded source, transforming it into a
        NumPy array with the specified data type. The decoding process varies based on
        the selected format type.

        Parameters
        ----------
        data : str
            Input data that is either ASCII-encoded or Base64-encoded.
        data_type : type
            The desired NumPy data type for the resulting array.
        offset : Optional[any], default=None
            Key used to locate the required segment in the appended_data when
            the 'appended' format type is used.

        Returns
        -------
        numpy.ndarray
            A NumPy array containing the decoded data as per the specified
            format and parameters.

        """
        if self.data_format == 'ascii':
            if data_type != 's':
                return np.fromstring(data, dtype=data_type, sep=' ')
            else:
                chars = list(map(chr, map(int, data.split())))
                return ''.join(chars).rstrip('\x00').split('\x00')

        elif self.data_format == 'binary':
            binary_data = pybase64.b64decode(data)
            return self.decode_byte_data(binary_data, data_type)

        elif self.data_format == 'appended':
            if self.appended_data_bstr is None:
                raise ValueError("Appended input data is required for 'appended' format.")
            return self.decode_byte_data(self.appended_data_arrays[offset], data_type)
        else:
            raise ValueError(f"Unknown format type: {self.data_format}")

    @staticmethod
    def reshape_array(array, components):
        """Reshape array if multiple components are present."""
        return array.reshape(-1, components) if components > 1 else array

    def extract_data_array(self, data):
        """
        Extract an array and its associated name from the provided data structure.

        This function processes a structured data input, extracting a named data array
        and decoding it using specific parameters. If multiple components are defined,
        the array will be reshaped accordingly. The `dtype` and `start_index` values
        are derived from specific fields in the input data.

        Parameters
        ----------
        data : dict
            A dictionary containing structured data with keys such as '@Name', '@type',
            '@NumberOfComponents', '@NumberOfTuples', '#text', and '@offset'.

        Returns
        -------
        tuple
            A tuple containing two elements:
            - str: The name of the data array extracted from the '@Name' key of the
              input data. If not provided, defaults to 'unknown_name'.
            - numpy.ndarray: The decoded and optionally reshaped data array.

        """
        # Extract common data fields
        data_name = data.get('@Name', 'unknown_name')
        dtype = self.parse_data_type(data.get('@type', ''))
        num_components = int(data.get('@NumberOfComponents', data.get('@NumberOfTuples', 1)))
        data_text = data.get('#text', '')

        # Decode array using helper function
        decoded_array = self.decode_array(data=data_text, data_type=dtype, offset=data.get('@offset'))

        # Reshape array based on components and add to data_arrays
        if num_components > 1:
            decoded_array = self.reshape_array(decoded_array, num_components)

        return data_name, decoded_array

    @staticmethod
    def parse_data_type(data_type):
        """Resolves the NumPy dtype and start index based on data type."""
        type_mapping = {
            'int': np.int64,
            'float': np.float32,
            'double': np.float64,
            'float16': np.float16,
            'float32': np.float32,
            'float64': np.float64,
            'int8': np.int8,
            'int16': np.int16,
            'int32': np.int32,
            'int64': np.int64,
            'uint8': np.uint8,
            'uint16': np.uint16,
            'uint32': np.uint32,
            'uint64': np.uint64,
            'string': 's'
        }
        return type_mapping.get(data_type.lower(), None)

    def decode_np_byteorder(self, dtype):
        """Helper to adjust dtype based on byte order."""
        new_byteorder = LITTLE_ENDIAN if self.byte_order in ['<', 'littleendian'] else BIG_ENDIAN
        return np.dtype(dtype).newbyteorder(new_byteorder)

    def decode_str_byteorder(self, dtype, data_size):
        """Helper to adjust dtype based on byte order."""
        new_byteorder = LITTLE_ENDIAN if self.byte_order in ['<', 'littleendian'] else BIG_ENDIAN
        return new_byteorder + str(data_size) + dtype

    def recover_grid_coordinates(self):
        """
        Recover grid coordinates from the given data.

        This function extracts grid coordinates from a nested dictionary structure
        if they are available. It checks for the existence of the 'Coordinates' key
        within the 'Piece' dictionary of the input data and retrieves the corresponding
        data using the provided `recover_data_arrays` function. If no coordinates are
        found or the 'Coordinates' key is not present, it returns `None`.

        Returns
        -------
        list or None
            The recovered grid coordinates in the form of a `GridCoordinates` instance if available,
            or `None` if the coordinates are not present in the input data.


        """
        try:
            xml_data = self._vtk_xml_file[self.file_type]['Piece']['Coordinates']['DataArray']

            data_arrays = self.get_data_arrays(xml_data)

            grid_topology = GridCoordinates(x=data_arrays[[s for s in data_arrays if 'x' in s.lower()][0]],
                                            y=data_arrays[[s for s in data_arrays if 'y' in s.lower()][0]],
                                            z=data_arrays[[s for s in data_arrays if 'z' in s.lower()][0]],
                                            whole_extents=np.fromstring(self._vtk_xml_file[self.file_type]['@WholeExtent'], sep=' '))
            return grid_topology

        except:
            return None

    def get_data_arrays(self, xml_data):
        """
        Recovers and organizes data arrays by iterating over XML data and appending it
        to an existing structure for return.

        This function processes XML-like input data in a dictionary, organizes them into a dictionary,
        and combines their contents with a provided data structure.

        Parameters
        ----------
        xml_data : dictionary
            The data to be processed. It can either be a list of XML-like items or a
            single XML-like item.

        Returns
        -------
        dict
            A dictionary containing the organized data arrays.
        """
        if type(xml_data) == list:
            data_arrays = {}
            for data in xml_data:
                name, array = self.extract_data_array(data)
                data_arrays[name] = array

        else:
            name, array = self.extract_data_array(xml_data)
            data_arrays = {name: array}

        return data_arrays


def convert_to_vtkhdf(xml_file_path):
    """
    Convert a VTK XML file to an equivalent VTKHDF file.

    Parameters
    ----------
    xml_file_path : str
        Path to XML file, including file extension. This file will be converted to a VTKHDF file of the same type.

    Warnings
    --------
    Currently RectilinearData and StructuredGrid are not supported by the VTK format as this is not yet finalised.
    The file formats used here are the proposed formats.

    """
    data = Reader(xml_file_path).parse()

    data.write_vtkhdf_file(xml_file_path.split['.'][0], file_format='vtkhdf')


# Function to read data using the Reader class
def read_vtkxml_data(filename):
    """
    Reads and parses data from the specified file.

    This function initializes a `Reader` object with the provided filename
    and invokes its `parse` method to process and return the parsed data.

    Parameters
    ----------
    filename : str
        Path to the file that needs to be read and parsed.

    Returns
    -------
    Any
        Parsed data produced by the `Reader.parse()` method.
    """
    reader = Reader(filename)
    return reader.parse()
