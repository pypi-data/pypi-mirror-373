#!/usr/bin/env python
"""
VTKWriter Class for creating VTK's XML based format.

Supports ASCII, Base64 and Appended Raw encoding of data.

Classes
_______
XML_MultiBlockWriter()
    Multiblock writing class for XML files


Created at 13:01, 24 Feb, 2022
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard Library
from dataclasses import dataclass
import struct
import sys
from pathlib import Path

import numpy as np
import pybase64

## Local Imports
from ..helpers import _parse_bytecount_type
from ..utilities import first_key, flatten
from ..vtk_cell_types import *


@dataclass
class VTK_xml_filetype:
    name: str
    extension: str


VTKImageData = VTK_xml_filetype('ImageData', '.vti')
VTKPolyData = VTK_xml_filetype('PolyData', '.vtp')
VTKRectilinearGrid = VTK_xml_filetype('RectilinearGrid', '.vtr')
VTKStructuredGrid = VTK_xml_filetype('StructuredGrid', '.vts')
VTKUnstructuredGrid = VTK_xml_filetype('UnstructuredGrid', '.vtu')

__all__ = ['xml_multiblock_writer']

class XMLWriterBase:
    """Base class for XML VTK file writers."""

    _text_encoding = 'utf-8'
    _filetypes = {
        "ImageData": ".vti",
        "PolyData": ".vtp",
        "RectilinearGrid": ".vtr",
        "StructuredGrid": ".vts",
        "UnstructuredGrid": ".vtu",
        "vtkMultiBlockDataSet": ".vtm"
    }

    _np_to_struct = {'int8': 'b',
                     'uint8': 'B',
                     'int16': 'h',
                     'uint16': 'H',
                     'int32': 'i',
                     'uint32': 'I',
                     'int64': 'q',
                     'uint64': 'Q',
                     'float32': 'f',
                     'float64': 'd'
                     }

    # Map numpy to VTK data types
    _np_to_vtk = {
        "int8": "Int8",
        "uint8": "UInt8",
        "int16": "Int16",
        "uint16": "UInt16",
        "int": "Int32",
        "int32": "Int32",
        "uint32": "UInt32",
        "int64": "Int64",
        "uint64": "UInt64",
        "float": "Float32",
        "float32": "Float32",
        "float64": "Float64",
        "StringDType()": "String",
    }

    # Map VTK data types to numpy
    _vtk_to_np = {v: k for k, v in _np_to_vtk.items()}

    #    CELL TYPES
    _cellType = {
        "Vertex": VTK_Vertex,
        "PolyVertex": VTK_PolyVertex,
        "Line": VTK_Line,
        "PolyLine": VTK_PolyLine,
        "Triangle": VTK_Triangle,
        "TriangleStrip": VTK_TriangleStrip,
        "Polygon": VTK_Polygon,
        "Pixel": VTK_Pixel,
        "Quad": VTK_Quad,
        "Tetra": VTK_Tetra,
        "Voxel": VTK_Voxel,
        "Hexahedron": VTK_Hexahedron,
        "Wedge": VTK_Wedge,
        "Pyramid": VTK_Pyramid,
        "Pentagonal_Prism": VTK_Pentagonal_Prism,
        "Hexagonal_Prism": VTK_Hexagonal_Prism,
        "Quadratic_Edge": VTK_Quadratic_Edge,
        "Quadratic_Triangle": VTK_Quadratic_Triangle,
        "Quadratic_Quad": VTK_Quadratic_Quad,
        "Quadratic_Tetra": VTK_Quadratic_Tetra,
        "Quadratic_Hexahedron": VTK_Quadratic_Hexahedron,
        "Quadratic_Wedge": VTK_Quadratic_Wedge,
        "Quadratic_Pyramid": VTK_Quadratic_Pyramid,
        "BiQuadratic_Quad": VTK_BiQuadratic_Quad,
        "TriQuadratic_Hexahedron": VTK_TriQuadratic_Hexahedron,
        "Quadratic_Linear_Quad": VTK_Quadratic_Linear_Quad,
        "Quadratic_Linear_Wedge": VTK_Quadratic_Linear_Wedge,
        "BiQuadratic_Quadratic_Wedge": VTK_BiQuadratic_Quadratic_Wedge,
        "BiQuadratic_Quadratic_Hexahedron": VTK_BiQuadratic_Quadratic_Hexahedron,
        "BiQuadratic_Triangle": VTK_BiQuadratic_Triangle,
    }

    # VTK data types
    _DataType = {"Int8": 1,
                 "UInt8": 1,
                 "Int16": 2,
                 "UInt16": 2,
                 "Int32": 4,
                 "UInt32": 4,
                 "Int64": 8,
                 "UInt64": 8,
                 "Float32": 4,
                 "Float64": 8,
                 }

    def __init__(self, filepath, filetype, encoding='ascii', ascii_precision=16, ascii_ncolumns=6, declaration=True,
                 appended_encoding='base64', version='1.0', compression=None):
        # check if extension provided and strip - correct extension is added next
        self.path = Path(filepath).with_suffix(self._filetypes[filetype])
        self.filetype = filetype
        if encoding not in ['ascii', 'binary', 'base64', 'appended']:
            raise ValueError('Encoding must be ascii, binary, base64 or appended.')
        self.encoding = encoding
        self.ascii_precision = ascii_precision
        self.ascii_ncolumns = ascii_ncolumns
        self._add_declaration = declaration
        self.vtk_version = version
        if self.vtk_version == '1.0':
            self.header_type = 'UInt64'
        elif self.vtk_version == '0.1':
            self.header_type = 'UInt32'
        else:
            raise ValueError('Invalid VTK version specified.')

        self._byteorder = 'LittleEndian' if sys.byteorder == "little" else 'BigEndian'
        self._byteorder_char = '<' if sys.byteorder == "little" else '>'

        # set attributes for vtk files that ar enot multiblock files
        if self.filetype != 'VTKMultiBlockDataSet':
            self._appended_data = b''
            if appended_encoding not in ['base64', 'raw']:
                raise ValueError('Appended encoding must be base64 or raw.')
            self._appended_encoding = appended_encoding
            self._offset = 0


            if compression is None or compression is False or compression == 0:
                self.compression = 0
            elif compression is True:
                self.compression = -1
                raise NotImplementedError("To be implemented at a later date")
            elif compression in list(range(-1, 10)):
                self.compression = compression
                raise NotImplementedError("To be implemented at a later date")
            else:
                raise ValueError(f'compression level {compression} is not recognized by zlib')

            # set data attributes
            # num points and cells can be calculated from the extents for ImageData, StructuredGrid and RectilinearGrid
            self.npoints = 0
            self.ncells = 0

            # needs to be calculated from the data first and passed at instantiation
            self.nverts = 0
            self.nlines = 0
            self.nstrips = 0
            self.npolys = 0

    def open_file(self):
        """
        Open a file for writing and optionally add a declaration for encoding.

        This method handles opening a file in write-binary mode based on the provided
        file path. If specified by internal flags, it appends an encoding declaration
        to the file, particularly for base64 encoding. The operation may modify the
        internal representation of the file stream.

        Attributes
        ----------
        file : file object
            The open file stream associated with the provided path.

        Parameters
        ----------
        self : object
            Refers to the class instance.

        Notes
        -----
        Ensure that the `__path` attribute has been set before calling this method,
        as it specifies the file location to be opened. The `_add_declaration` and
        `_appended_encoding` attributes must also be correctly configured to apply
        the encoding declaration if needed.
        """
        self.file = open(self.path, "wb")
        if self._add_declaration and self._appended_encoding == 'base64':
            self.add_declaration()

    # Move common methods here:
    def add_declaration(self):
        """
        Add an XML declaration to the start of the file.

        This can be included in all files.
        However, it should be noted that XML files with an encoding of `appended` may be considered invalid XML.

        """
        self.file.write(b'<?xml version="1.0"?>\n')

    def add_filetype(self):
        """
        Add XML root node and file type node.

        """
        # add vtk root node
        if self.vtk_version == '1.0':
            vtk_filestr = (f'<VTKFile type="{self.filetype}" version="1.0" '
                           f'byte_order="{self._byteorder}" header_type="{self.header_type}">')
        elif self.vtk_version == '0.1':
            vtk_filestr = f'<VTKFile type="{self.filetype}" version="0.1" byte_order="{self._byteorder}">'

        self.file.write((vtk_filestr + "\n").encode(self._text_encoding))

        # gather appropriate file type attributes
        attrs = []
        if self.filetype == 'ImageData' or self.filetype == 'RectilinearGrid' or self.filetype == 'StructuredGrid':
            fmt = ' '.join(['%.16g'] * 6)
            attrs.append(f'WholeExtent="{fmt % tuple(self.whole_extent)}"')

            if self.filetype == 'ImageData':
                fmt2 = ' '.join(['%.16g'] * 3)
                fmt3 = ' '.join(['%.16g'] * 9)
                attrs.append(f'Origin="{fmt2 % tuple(self.origin)}"')
                attrs.append(f'Spacing="{fmt2 % tuple(self.grid_spacing)}"')
                attrs.append(f'Direction="{fmt3 % tuple(self.direction)}"')

            # write file type node and attributes
            file_type_str = f"  <{self.filetype} " + " ".join(attrs) + ">\n"

        else:
            # write file type node
            file_type_str = f"  <{self.filetype}" + ">\n"

        self.file.write(file_type_str.encode(self._text_encoding))

    def close_filetype(self):
        """Add closing file tag."""
        self.file.write(f'  </{self.filetype}>\n'.encode(self._text_encoding))

    def close_file(self, verbose=False):
        """
        Close file after writing data to it.

        Returns
        -------
        None

        """
        self.file.write("</VTKFile>".encode(self._text_encoding))
        self.file.close()

        if verbose:
            print('  File successfully written.')

    def add_fielddata(self, field_data):
        """
        Add field data to the file in a specific format if the provided field_data is not None.

        Writes the opening and closing FieldData tags and processes each entry within the field_data dictionary.

        Parameters
        ----------
        field_data : dict or None
            A dictionary containing the field data to be added, where each key is the
            name of the field and the corresponding value represents the associated
            data. If None, no field data is written.

        """
        if field_data is not None:
            self.file.write(b'    <FieldData>\n')

            for key, value in field_data.items():
                self._add_dataarray(value, name=key, data_type='field_data')

            self.file.write(b'    </FieldData>\n')

    def open_piece(self):
        """
        Open `Piece` element of XML file.

        Each piece file contains the attribute tags for the number of points,
        cells, vertices, lines, strips and polydata items.

        """
        attrs = []

        if self.filetype == 'ImageData' or self.filetype == 'RectilinearGrid' or self.filetype == 'StructuredGrid':
            fmt = ' '.join(['%.16g'] * 6)
            attrs.append(f'Extent="{fmt % tuple(self.piece_extent)}"')

        if self.filetype == 'UnstructuredGrid':
            attrs.append(f'NumberOfPoints="{self.npoints}"')
            attrs.append(f'NumberOfCells="{self.ncells}"')

        if self.filetype == 'PolyData':
            attrs.append(f'NumberOfPoints="{self.npoints}"')
            attrs.append(f'NumberOfVerts="{self.nverts}"')
            attrs.append(f'NumberOfLines="{self.nlines}"')
            attrs.append(f'NumberOfStrips="{self.nstrips}"')
            attrs.append(f'NumberOfPolys="{self.npolys}"')

        piece_str = "    <Piece " + " ".join(attrs) + ">\n"

        self.file.write(piece_str.encode(self._text_encoding))

    def open_element_base(self, element, attrs=None, indent_lvl=2, self_closing=False):
        """Open a generic XML element with common functionality."""
        if attrs is None:
            attrs = []

        line_end = "/>\n" if self_closing else ">\n"

        element_str = '  ' * indent_lvl + f'<{element}'

        if attrs:
            element_str += " " + " ".join(attrs)

        element_str += line_end

        self.file.write(element_str.encode(self._text_encoding))

    def close_element(self, tag_name, indent_lvl=0):
        """
        Add element closing tag to file.

        Returns
        -------
        None

        """
        closing_tag = '  ' * indent_lvl + f'</{tag_name}>\n'
        self.file.write(closing_tag.encode(self._text_encoding))

    def calculate_blocksize(self, data_array):
        """
        Calculate and return the block size of a given NumPy array in bytes.

        The result is packed as a 64-bit unsigned integer in accordance with the machine's byte order.
        This function determines the byte order from the instance's attribute `_byteorder_char`
        and uses it to format the packed result.

        Parameters
        ----------
        data_array : numpy.ndarray
            The NumPy array for which the block size is to be calculated.

        Returns
        -------
        bytes
            The size of the data array in bytes, packed as a 64-bit unsigned
            integer.

        Raises
        ------
        TypeError
            If `data_array` is not a NumPy array.

        """
        if isinstance(data_array, np.ndarray):
            # Write size as unsigned long long == 64 bits unsigned integer
            fmt_block = _parse_bytecount_type(self.header_type, self._byteorder)[0]
            block_size_bytes = struct.pack(fmt_block, data_array.nbytes)

            return block_size_bytes
        else:
            print('Expected NumPy Array.')

    def convert_blockdata(self, data_array):
        """
        Convert a NumPy array into a binary data block for VTK, ensuring compatibility with specific memory layouts.

        Multidimensional arrays are processed to produce a contiguous binary representation, depending on their
        memory order (Fortran or C layout). This function requires the input data to be of type `numpy.ndarray`.

        Parameters
        ----------
        data_array : numpy.ndarray
            The input array to be converted into a binary data block. The function expects
            either Fortran-contiguous or C-contiguous memory layout for proper handling.

        Returns
        -------
        bytes
            The binary representation of the input data, formatted in C-contiguous layout.

        Raises
        ------
        TypeError
            If the input is not an instance of `numpy.ndarray`.
        """
        if isinstance(data_array, np.ndarray):
            # NOTE: VTK expects binary data in FORTRAN order
            if data_array.flags["F_CONTIGUOUS"]:
                # This is only needed when a multidimensional array has F-layout
                data_block = np.ravel(data_array, order='C').tobytes()
            else:
                # This is needed when a multidimensional array has C-layout
                data_block = np.ravel(data_array, order='C').tobytes()

            return data_block
        else:
            raise TypeError('Expected NumPy Array.')

    def ascii_encoder(self, array):
        """
        Encode a given NumPy array into an ASCII-formatted string and write it to a file.

        This function converts the flattened input array into rows of ASCII text, where each
        row contains a fixed or remaining number of elements formatted to a specified decimal
        precision. The ASCII representation is written to a pre-defined file using a specific
        text encoding. It supports arrays that may not divide evenly by the defined number
        of columns, ensuring the final row contains the residual elements if present.

        Parameters
        ----------
        array : numpy.ndarray
            The array containing the numerical data to be formatted as ASCII text.

        Returns
        -------
        str
            A string containing the ASCII-formatted representation of the array.

        """
        # set precision for formatting
        if np.issubdtype(array.dtype, np.integer):
            precision = 0
            try:
                int_str_length = len(str(array.max()))
            except:
                int_str_length = 255
            num_cols = min(120 // (int_str_length + 3), 40)
        else:
            precision = self.ascii_precision
            num_cols = 132 // (precision + 6)

        fmt = ' '.join([f'%.{precision}f'] * num_cols) + '\n'
        data_str = [' ' * 10]

        # calculate number of full rows
        nrows = 1 if array.size <= num_cols else int(array.size / num_cols)

        array = array.flatten(order='C')

        # write full rows
        if array.size > num_cols:
            for row in range(nrows):
                shift = row * num_cols
                data_str.append(fmt % tuple(array[shift:num_cols + shift]))
                data_str.append(' ' * 10)

            # write any remaining data in last non-full row
            if array.size % num_cols != 0:
                rem = array[num_cols + shift::]
                fmt = ' '.join([f'%.{precision}f'] * len(rem)) + '\n'
                data_str.append(fmt % tuple(rem))

        else:
            rem = array
            fmt = ' '.join([f'%.{precision}f'] * len(rem)) + '\n'
            data_str.append(fmt % tuple(rem))

        data_str = ''.join(data_str)
        self.file.write(data_str.encode(self._text_encoding))

        return data_str

    def Base64Encoder(self, data_array):
        """
        Encode the given data array using Base64 encoding and write the encoded result to a file.

        This method takes an input array, encodes it into Base64 format, and appends
        the encoded content to a file. Initial padding may also be written to the file
        depending on implementation.

        Parameters
        ----------
        data_array :
            The data array to be encoded into Base64 format.
        """
        self.file.write(b'          ')
        encoded = self.b64_encode_array(data_array)
        self.file.write(encoded)

    def b64_encode_array(self, data_array):
        """
        Encode a given data array into a Base64 encoded byte string.

        This method takes a data array, calculates a block size for encoding,
        converts the data into block data format suitable for Base64 encoding,
        and returns the Base64 encoded result.

        Parameters
        ----------
        data_array : Any
            The input data array to be encoded. The exact type of this array
            will depend on the use case and internal implementation of your
            data handling.

        Returns
        -------
        bytes
            The Base64 encoded representation of the input data array as a
            byte string.
        """
        block_size = self.calculate_blocksize(data_array)
        block_data = self.convert_blockdata(data_array)
        encoded = pybase64.b64encode(block_size + block_data)

        return encoded

    def appended_encoder(self, data_array):
        """
        Encode and append the provided data according to the specified encoding scheme.

        Parameters
        ----------
        data_array : numpy.ndarray
            The input data array that needs to be encoded and appended. The type and
            structure of the array are determined by its usage in the encoding
            process.

        Notes
        -----
        The behavior of the encoding depends on the value of the `_appended_encoding`
        attribute of the class. The supported encoding schemes are:
        - 'raw': Data is appended in raw format along with a calculated blocksize.
        - 'base64' or 'binary': Data is encoded using the base64 encoding and appended.

        The method ensures the internal `_offset` and `_appended_data` attributes are
        updated to reflect the appended data and current position.

        This method relies on helper methods like `calculate_blocksize` and
        `convert_blockdata` for 'raw' encoding, and `b64_encode_array` for 'base64' or
        'binary' encoding. These helper methods are assumed to be present within
        the same class and are utilized to transform the `data_array` accordingly.
        """
        # write appended data in raw format
        if self._appended_encoding == 'raw':
            self._offset += data_array.nbytes + 8
            self._appended_data += self.calculate_blocksize(data_array)
            self._appended_data += self.convert_blockdata(data_array)

        # write appended data in base64 binary
        if self._appended_encoding == 'base64' or self._appended_encoding == 'binary':
            encoded = self.b64_encode_array(data_array)
            self._offset += len(encoded)
            self._appended_data += self.b64_encode_array(data_array)

    # Common XML Operations

    def add_appended_data(self):
        """
        Write appended data in a specific format to a file.

        The method generates an XML-like structure with encoding and appended data included.
        The data is written directly to a file-like object provided during the initialization of the calling instance.

        Attributes
        ----------
        _appended_encoding : str
            Encoding type for the `AppendedData` XML tag.
        _text_encoding : str
            Encoding used for converting strings into bytes before writing to the file.
        _appended_data : bytes
            The actual binary data to be inserted between `<AppendedData>` tags.
        """
        self.file.write((f'  <AppendedData encoding="{self._appended_encoding}">\n').encode(self._text_encoding))
        self.file.write(b'    _')
        self.file.write(self._appended_data)
        self.file.write(('\n  </AppendedData>\n').encode(self._text_encoding))

    def _add_dataarray(self, data, name, data_type='CellData', vtk_type=None):
        """
        Add a data array to the VTK file with specified attributes and encoding.

        The method processes the provided data, determines its properties such as
        minimum, maximum, and number of components, and generates attributes required
        for the VTK output. It also encodes the data into the specified VTK format
        (e.g., ASCII, binary, or appended) and writes it to the file. If `vtk_type`
        is not provided, the method determines the appropriate VTK type from the
        data's NumPy dtype.

        Parameters
        ----------
        data : numpy.ndarray
            Numerical data to be added to the VTK file. Should be convertible to
            a NumPy ndarray.
        name : str
            Name of the data array in the VTK file (e.g., 'Varaible1', 'Temp').
        data_type : str, default 'CellData'
            Specifies the type of data to be added. Expected types are 'CellData',
            'PointData', or 'field_data'.
        vtk_type : str, optional
            Specific VTK data type for this array. If not provided, it will be
            inferred based on the NumPy dtype of the input array.

        Raises
        ------
        TypeError
            If the input data cannot be converted to a NumPy ndarray.
        ValueError
            If the data has unsupported dimensions or invalid input values.

        """
        # convert data to np ndarray for ease of use
        data = np.asarray(data)
        if np.issubdtype(data.dtype, np.number):
            try:
                # numpy (>1.26) seems to be quicker than bottleneck for arrays where there will definitely be no nans
                data_min = np.min(data)
                data_max = np.max(data)
            except:
                data_min = 1e+299
                data_max = -1e+299
        else:
            # data = np.array(data, dtype=StringDType())
            # vtk_type = self._np_to_vtk[str(data.dtype)]
            vtk_type = "String"

            # Calculate string lengths
            # string_lengths = np.array([len(s) for s in data], dtype=np.int32)

            if self.encoding == 'ascii':
                char_array = []
                # chars = data.view('int32')
                # convert to ascii characters
                for element in data:
                    char_array.append(np.array(list(element)).view('int32'))
                    char_array.append(0)

                data = np.hstack(char_array)

        # set attributes
        attrs = []

        # check data type
        if vtk_type is None:
            vtk_type = self._np_to_vtk[str(data.dtype)]

        # count num components
        num_components = data.shape[1] if len(data.shape) > 1 else 1
        if data_type == 'field_data':
            attrs.append(f'NumberOfTuples="{num_components}"')
        else:
            if name not in ['connectivity', 'offsets', 'types']:
                if vtk_type != "String":
                    attrs.append(f'NumberOfComponents="{num_components}"')

        # add remaining attributes to list for writing to file
        attrs.append(f'type="{vtk_type}" format="{self.encoding}"')
        if vtk_type != "String":
            attrs.append(f'RangeMin="{data_min}" RangeMax="{data_max}"')

        # encode array
        if self.encoding == 'ascii' or self.encoding == 'binary':
            data_opentag = f'        <DataArray Name="{name}" ' + " ".join(attrs) + ">\n"
            data_closetag = '        </DataArray>\n'

            # add opening tag to file
            self.file.write(data_opentag.encode(self._text_encoding))

            # add data to file if not appended data
            if self.encoding == 'ascii':
                self.ascii_encoder(data)

            if self.encoding == 'binary':
                self.Base64Encoder(data)
                data_closetag = '\n' + data_closetag

            # add closing tag to file
            self.file.write(data_closetag.encode(self._text_encoding))

        elif self.encoding == 'appended':
            # combined opening and closing tag for appended data
            data_tag = f'        <DataArray Name="{name}" ' + " ".join(attrs) + f' offset="{self._offset}"/>\n'

            self.file.write(data_tag.encode(self._text_encoding))
            self.appended_encoder(data)
        else:
            raise ValueError("Invalid encoding type. Expected 'ascii', 'binary', or 'appended'.")

    @staticmethod
    def _check_array_sizes(array_data):
        """
        Check the size of all data arrays to be written to ensure they are all the same length.

        Parameters
        ----------
        array_data : dictionary of data arrays to be written.

        Returns
        -------
        Array Size : Int

        """
        # flatten dictionary to check sizes more easily
        flattened_arrays = flatten(array_data, parent_key='', separator='_')

        sizes = []
        for _key, val in flattened_arrays.items():
            if val is not None:
                if isinstance(val, np.ndarray):
                    if val.ndim == 1:
                        sizes.append(val.size)
                    else:
                        sizes.append(val.shape[0])
                else:
                    sizes.append(len(val))
            else:
                raise ValueError("Warning: `None` is not a valid data array.")

        all_equal = all(sizes)

        if all_equal:
            return sizes[0]
        else:
            raise ValueError("Warning: Arrays provided are not all the same length. Data not written to file.")

    @staticmethod
    def _convert_to_array(list_1d):
        if (list_1d is not None) and (type(list_1d).__name__ != "ndarray"):
            assert isinstance(list_1d, (list, tuple))
            return np.array(list_1d)
        return None


class XMLwriter(XMLWriterBase):
    """Regular XML VTK file writer."""

    def __init__(self, filepath, filetype, point_data=None, cell_data=None, field_data=None, encoding='ascii',
                 ascii_precision=16, ascii_ncolumns=6, declaration=True, appended_encoding='base64', version='1.0'):

        super().__init__(filepath, filetype, encoding, ascii_precision, ascii_ncolumns, declaration, appended_encoding,
                         version)

        # set data attributes
        if isinstance(point_data, str):
            raise TypeError("Expected a dictionary of data arrays to be written to the VTK file for point_data.")
        if isinstance(cell_data, str):
            raise TypeError("Expected a dictionary of data arrays to be written to the VTK file for cell_data.")
        if isinstance(field_data, str):
            raise TypeError("Expected a dictionary of data arrays to be written to the VTK file for field_data.")

        # assign data after checking type
        self.point_data = point_data
        self.cell_data = cell_data
        self.field_data = field_data

    # Keep specialized methods for regular XML writing:
    def check_array_sizes_for_cell_data(self, cell_data):
        """Compare size of cell data with the number of cells in the file."""
        if cell_data is not None:
            cell_data_size = self._check_array_sizes(cell_data)
            if cell_data_size != self.ncells:
                raise ValueError('Cells and cell data sizes do not match')

    def check_array_sizes_for_point_data(self, point_data):
        """Compare size of point data with the number of points in the file."""
        if point_data is not None:
            point_data_size = self._check_array_sizes(point_data)
            if point_data_size != self.npoints:
                raise ValueError('Points and point data sizes do not match')

    # Data Structure Methods
    def add_points(self, points):
        """
        Add a collection of points to the data structure.

        This method processes and adds a structured set of points to
        the internal data storage. It uses auxiliary methods to
        handle specifics of the data array creation, data structure
        settings, and integration of the points.

        Parameters
        ----------
        points : Any
            The collection of points to be added. The parameter
            should conform to the data type `points` as expected
            by the `_add_dataarray` method.

        Notes
        -----
        Points are only required for `UnstructuredGrid` and `PolyData`.

        """
        self.open_element("Points")
        self._add_dataarray(points, "Points", data_type='points')
        self.close_element('Points', 3)

    def add_data_from_dict(self, data_type, data_dict):
        """
        Add data to the object using a dictionary of data and a specified data type.

        This method iterates through a dictionary of data and adds each individual
        data array to the object. The name of each property in the dictionary is
        used as the identifier for the corresponding data array.

        Parameters
        ----------
        data_type : str
            A string indicating the type of data being added. This value is passed
            to the `_add_dataarray` method to categorize the data.
        data_dict : dict
            A dictionary where keys represent property names, and values represent
            the corresponding data to be added. Each key-value pair is processed
            separately to add the data to the object.
        """
        for prop_name, prop_data in data_dict.items():
            self._add_dataarray(prop_data, prop_name, data_type=data_type)

    def add_data_array(self, data, data_type="PointData"):
        """
        Add data arrays to a specified vtk data type.

        This inclides processing nested dictionary structures
        and managing data elements such as scalars, vectors, tensors, normals, and texture
        coordinates. The function categorizes and processes the data based on its structure
        and type while ensuring proper opening and closing of the relevant elements.

        Parameters
        ----------
        data : dict
            The data to be added. It can be provided either as a flat dictionary or a nested
            dictionary with keys such as 'scalars', 'vectors', 'tensors', 'normals', and
            'texture_coords'.

        data_type : str, optional
            Specifies the vtk data type to which the data should be added. Defaults to
            "PointData".
        """
        # Process Data items
        if data is not None:
            # check if sorted by variable
            is_nested = any(isinstance(i, dict) for i in data.values())

            if is_nested:
                # split data into types if provided as nested dict
                scalars = data.get('scalars')
                vectors = data.get('vectors')
                tensors = data.get('tensors')
                normals = data.get('normals')
                texture_coords = data.get('texture_coords')

                # open element
                self.open_element(data_type, Scalars=scalars, Vectors=vectors, Tensors=tensors, Normals=normals,
                                  TCoords=texture_coords)

                if scalars is not None:
                    self.add_data_from_dict(data_type, scalars)

                if vectors is not None:
                    self.add_data_from_dict(data_type, vectors)

                if tensors is not None:
                    self.add_data_from_dict(data_type, tensors)

                if normals is not None:
                    self.add_data_from_dict(data_type, normals)

                if texture_coords is not None:
                    self.add_data_from_dict(data_type, texture_coords)

            else:
                # open element without setting any active data types
                self.open_element(data_type)

                # add data arrays to file
                self.add_data_from_dict(data_type, data)

            # close data array element
            self.close_element(data_type, 3)

    # Element Methods (Standard Version)
    def open_element(self, element="Points", Scalars=None, Vectors=None,
                     Tensors=None, TCoords=None, Normals=None, indent_lvl=2):
        """Specialized for VTK data types."""
        attrs = []
        if Scalars is not None:
            fkey = first_key(Scalars)
            if fkey is not None:
                attrs.append(f'Vectors="{fkey}"')
        if Vectors is not None:
            fkey = first_key(Vectors)
            if fkey is not None:
                attrs.append(f'Vectors="{fkey}"')
        if Tensors is not None:
            fkey = first_key(Tensors)
            if fkey is not None:
                attrs.append(f'Vectors="{fkey}"')

        if TCoords is not None:
            fkey = first_key(TCoords)
            if fkey is not None:
                attrs.append(f'Vectors="{fkey}"')

        if Normals is not None:
            fkey = first_key(Normals)
            if fkey is not None:
                attrs.append(f'Vectors="{fkey}"')

        self.open_element_base(element, attrs, indent_lvl=indent_lvl)


class XMLImageDataWriter(XMLwriter):
    """VTI XML Writer Class."""

    def __init__(self, filepath, whole_extent: object, piece_extent: object = None, spacing: object = (1, 1, 1),
                 origin: object = (0, 0, 0), direction: object = (1, 0, 0, 0, 1, 0, 0, 0, 1), point_data: object = None,
                 cell_data: object = None, field_data: object = None, encoding='ascii', ascii_precision=16,
                 ascii_ncolumns=6, declaration=True, appended_encoding='base64', version='1.0'):

        super().__init__(filepath, 'ImageData', point_data, cell_data, field_data, encoding,
                         ascii_precision, ascii_ncolumns, declaration, appended_encoding, version)

        self.whole_extent = np.asarray(whole_extent).astype(int)
        if len(self.whole_extent) != 6:
            raise ValueError("whole_extent must be a list or array of length 6.")

        # check if piece_extent is provided, otherwise use whole_extent
        if piece_extent is None:
            self.piece_extent = np.asarray(whole_extent).astype(int)
        else:
            self.piece_extent = np.asarray(piece_extent).astype(int)

        self.grid_spacing = np.asarray(spacing)
        self.origin = np.asarray(origin)
        self.direction = np.asarray(direction)

        # check input data
        self.num_cells = self.piece_extent[1::2] - self.piece_extent[0::2]
        self.ncells = np.prod(self.num_cells)
        self.npoints = np.prod(self.num_cells + 1)

        self.check_array_sizes_for_point_data(point_data)
        self.check_array_sizes_for_cell_data(cell_data)

    def write_xml_file(self):
        """Write VTI file in XML format."""
        # open xml file
        self.open_file()
        self.add_filetype()

        # open piece and add counts
        self.open_piece()

        # add FieldData
        self.add_fielddata(self.field_data)

        # add variables at points (PointData)
        self.add_data_array(self.point_data, data_type="PointData")

        # add variables at cells (CellData)
        self.add_data_array(self.cell_data, data_type="CellData")

        # file.close_piece()
        self.close_element('Piece', 2)
        self.close_filetype()

        # add any appended data
        if self.encoding == 'appended':
            self.add_appended_data()

        # close file
        self.close_file()

class XMLRectilinearGridWriter(XMLwriter):
    """VTR XML Writer Class."""

    def __init__(self, filepath, x, y, z, whole_extent=None, piece_extent=None, point_data: object = None,
                 cell_data: object = None, field_data: object = None, encoding='ascii', ascii_precision=16,
                 ascii_ncolumns=6, declaration=True, appended_encoding='base64', version='1.0'):

        # simple check on coordinates - must first be a list or array
        if not (isinstance(x, (np.ndarray, list, tuple))):
            raise TypeError("x must be a numpy array, tuple or list")
        if not (isinstance(y, (np.ndarray, list, tuple))):
            raise TypeError("y must be a numpy array, tuple or list")
        if not (isinstance(z, (np.ndarray, list, tuple))):
            raise TypeError("z must be a numpy array, tuple or list")

        # check if list or array is numeric
        x = np.asarray(x)
        y = np.asarray(y)
        z = np.asarray(z)
        if not (np.issubdtype(x.dtype, np.number)):
            raise TypeError("x must be a numeric numpy array or list")
        if not (np.issubdtype(y.dtype, np.number)):
            raise TypeError("y must be a numeric numpy array or list")
        if not (np.issubdtype(z.dtype, np.number)):
            raise TypeError("z must be a numeric numpy array or list")


        super().__init__(filepath, 'RectilinearGrid', point_data, cell_data, field_data, encoding,
                         ascii_precision, ascii_ncolumns, declaration, appended_encoding, version)

        self.x = x
        self.y = y
        self.z = z
        if whole_extent is None:
            self.whole_extent = np.array([0, len(x) - 1, 0, len(y) - 1, 0, len(z) - 1])
        else:
            self.whole_extent = np.asarray(whole_extent)

        if piece_extent is None:
            self.piece_extent = np.array([0, len(x) - 1, 0, len(y) - 1, 0, len(z) - 1])
        else:
            self.piece_extent = np.asarray(piece_extent)

        # check input data
        self.num_cells = self.piece_extent[1::2] - self.piece_extent[0::2]
        self.ncells = np.prod(self.num_cells)
        self.npoints = np.prod(self.num_cells + 1)

        self.check_array_sizes_for_point_data(point_data)
        self.check_array_sizes_for_cell_data(cell_data)


    def write_xml_file(self):
        """Write VTR file in XML format."""
        # open xml file
        self.open_file()
        self.add_filetype()

        # open piece and add counts
        self.open_piece()

        # add FieldData
        self.add_fielddata(self.field_data)

        # add variables at points (PointData)
        self.add_data_array(self.point_data, data_type="PointData")

        # add variables at cells (CellData)
        self.add_data_array(self.cell_data, data_type="CellData")

        # add coordinates
        self.add_coordinates()

        # file.close_piece()
        self.close_element('Piece', 2)
        self.close_filetype()

        # add any appended data
        if self.encoding == 'appended':
            self.add_appended_data()

        # close file
        self.close_file()

    def add_coordinates(self):
        """
        Add 3D coordinate arrays to the corresponding elements in a structured data format.

        The method adds arrays representing X, Y, and Z coordinates to a data element
        while creating a hierarchical organisation. These arrays are tagged as
        'coordinates' to denote their type of data. The method ensures each coordinate
        array is associated with its respective spatial dimension.

        """
        self.open_element("Coordinates")
        self._add_dataarray(self.x, "XCoordinates", data_type='coordinates')
        self._add_dataarray(self.y, "YCoordinates", data_type='coordinates')
        self._add_dataarray(self.z, "ZCoordinates", data_type='coordinates')
        self.close_element('Coordinates', 3)


class XMLStructuredGridWriter(XMLwriter):
    """VTS XML Writer Class."""

    def __init__(self, filepath, points, whole_extent, piece_extent=None,
                 point_data: object = None, cell_data: object = None, field_data: object = None, encoding='ascii',
                 ascii_precision=16, ascii_ncolumns=6, declaration=True, appended_encoding='base64', version='1.0'):

        if not (isinstance(points, (np.ndarray, list))):
            raise TypeError("points must be a numpy array")

        # convert to numpy array and do final checks
        points = np.asarray(points)
        if not (np.issubdtype(points.dtype, np.number)):
            raise TypeError("points must be a numeric numpy array")
        if points.ndim != 2:
            raise TypeError("points must be a 2D numpy array")


        super().__init__(filepath, 'StructuredGrid', point_data, cell_data, field_data, encoding,
                         ascii_precision, ascii_ncolumns, declaration, appended_encoding, version)

        if whole_extent is None:
            raise ValueError('Warning: The whole extent or num_cells must be provided for the VTS data type.')
        else:
            self.whole_extent = np.asarray(whole_extent).astype(int)

        if piece_extent is None:
            self.piece_extent = np.asarray(whole_extent).astype(int)
        else:
            self.piece_extent = np.asarray(piece_extent).astype(int)

        self.points = points

        # check input data
        self.num_cells = self.piece_extent[1::2] - self.piece_extent[0::2]
        self.ncells = np.prod(self.num_cells)
        self.npoints = np.prod(self.num_cells + 1)

        if self.points.shape[0] != self.npoints:
            raise ValueError('Warning: The number of points does not match the number of points in the whole extent.')

        self.check_array_sizes_for_point_data(point_data)
        self.check_array_sizes_for_cell_data(cell_data)

    def write_xml_file(self):
        """Write VTS file in XML format."""
        # open xml file
        self.open_file()
        self.add_filetype()

        # open piece and add counts
        self.open_piece()

        # add FieldData
        self.add_fielddata(self.field_data)

        # add variables at points (PointData)
        self.add_data_array(self.point_data, data_type="PointData")

        # add variables at cells (CellData)
        self.add_data_array(self.cell_data, data_type="CellData")

        # add coordinates
        self.add_points(self.points)

        # file.close_piece()
        self.close_element('Piece', 2)
        self.close_filetype()

        # add any appended data
        if self.encoding == 'appended':
            self.add_appended_data()

        # close file
        self.close_file()


class XMLUnstructuredGridWriter(XMLwriter):
    """VTU XML Writer Class."""

    def __init__(self, filepath, nodes, cell_type: object = None, connectivity: object = None, offsets: object = None,
                 point_data: object = None,
                 cell_data: object = None, field_data: object = None, encoding='ascii', ascii_precision=16,
                 ascii_ncolumns=6,
                 declaration=True, appended_encoding='base64', version='1.0'):

        super().__init__(filepath, 'UnstructuredGrid', point_data, cell_data, field_data, encoding,
                         ascii_precision, ascii_ncolumns, declaration, appended_encoding, version)

        # check input and allow for blank file
        if cell_type is not None:
            self.cell_types = np.asarray(cell_type)
        else:
            self.cell_types = None

        if connectivity is not None:
            self.connectivity = np.asarray(connectivity)
        else:
            self.connectivity = None

        if offsets is not None:
            self.offsets = np.asarray(offsets)
        else:
            self.offsets = None

        if nodes is not None:
            self.nodes = np.asarray(nodes)
        else:
            self.nodes = None


        if point_data is not None:
            self.npoints = len(nodes)

        if cell_data is not None:
            self.ncells = len(cell_type)

        # check topology
        # In xml file this should be an array of the same length as number of cells
        # if not bail out now before writing and raise error
        if self.cell_types is not None and len(self.cell_types) != len(self.offsets):
            raise ValueError("Offsets array must the same length as the cell types array.")

        # check input data
        self.check_array_sizes_for_point_data(point_data)
        self.check_array_sizes_for_cell_data(cell_data)

    def write_xml_file(self):
        """Write VTU file in XML format."""
        # open xml file
        self.open_file()
        self.add_filetype()

        # open piece and add counts
        self.open_piece()

        # add FieldData
        self.add_fielddata(self.field_data)

        # add variables at points (PointData)
        self.add_data_array(self.point_data, data_type="PointData")

        # add variables at cells (CellData)
        self.add_data_array(self.cell_data, data_type="CellData")

        # add points and cells
        self.add_points()
        self.add_unstruct_cells()

        # file.close_piece()
        self.close_element('Piece', 2)
        self.close_filetype()

        # add any appended data
        if self.encoding == 'appended':
            self.add_appended_data()

        # close file
        self.close_file()

    # Unstructured Grid Methods
    def add_points(self):
        """
        Add a set of points to the PolyData structure.

        This method is used to add a collection of points to a PolyData element. The
        points are passed as input and are processed, encapsulated in a data array,
        and added to the PolyData structure. The method ensures proper encapsulation
        and manages the hierarchy of elements by opening and closing the relevant
        tag for the points.


        """
        self.open_element("Points")
        if self.nodes is not None:
            # Add data for points
            self._add_dataarray(self.nodes, "Points", data_type='Points')
        self.close_element('Points', 3)

    def add_unstruct_cells(self):
        """
        Add unstructured cell data to an XML VTK file.

        The method manages the addition of connectivity, offsets, and types arrays
        required to define cells in the VTK format. If `unstruct_cells` contains None values,
        empty arrays are created for the missing data.

        """
        # add data for cells
        self.open_element("Cells")
        if self.connectivity is not None:
            # by default, paraview only supports 32bit ints unless it is specifically compiled with 64 bit option in
            # cmake, therefore, 32 bit will be the default value used here.
            # Note that the numpy array of ints being received is more than likely 64 bit but since this is about
            # conenctivty and offset we can usually safely just declare as 32 bit
            self._add_dataarray(self.connectivity.astype(np.int32, copy=False),
                                "connectivity", data_type='cells', vtk_type="UInt32")
            self._add_dataarray(self.offsets.astype(np.int32, copy=False),
                                "offsets", data_type='cells', vtk_type="UInt32")
            self._add_dataarray(self.cell_types.astype(np.int8, copy=False),
                                "types", data_type='cells', vtk_type="UInt8")
        else:
            self._add_dataarray(np.empty(0, dtype=np.int32), "connectivity", data_type='cells')
            self._add_dataarray(np.empty(0, dtype=np.int32), "offsets", data_type='cells')
            self._add_dataarray(np.empty(0, dtype=np.uint8), "types", data_type='cells')

        self.close_element('Cells', 3)


class XMLPolyDataWriter(XMLwriter):
    """VTP XML Writer Class."""

    def __init__(self, filepath, points=None, verts=None, lines=None, strips=None, polys=None,
                 point_data: object = None, cell_data: object = None, field_data: object = None,
                 encoding='ascii', ascii_precision=16, ascii_ncolumns=6, declaration=True, appended_encoding='base64',
                 version='1.0'):

        super().__init__(filepath, 'PolyData', point_data, cell_data, field_data, encoding,
                         ascii_precision, ascii_ncolumns, declaration, appended_encoding, version)

        self.points = points
        self.verts = verts
        self.lines = lines
        self.strips = strips
        self.polys = polys

        # set topology attributes
        if self.points is not None:
            self.npoints = len(points)
        if self.verts is not None:
            self.nverts = len(verts[1])
        if self.lines is not None:
            self.nlines = len(lines[1])
        if self.strips is not None:
            self.nstrips = len(strips[1])
        if self.polys is not None:
            self.npolys = len(polys[1])

        if self.cell_data:
            self.ncells = self.nverts + self.nlines + self.nstrips + self.npolys

        # data size checks
        self.check_array_sizes_for_point_data(point_data)
        self.check_array_sizes_for_cell_data(cell_data)


    def write_xml_file(self):
        """Write a VTP file in XMK format."""
        # open xml file
        self.open_file()
        self.add_filetype()

        # open piece and add counts
        self.open_piece()

        # add FieldData
        self.add_fielddata(self.field_data)

        # add variables at points (PointData)
        self.add_data_array(self.point_data, data_type="PointData")

        # add variables at cells (CellData)
        self.add_data_array(self.cell_data, data_type="CellData")

        # add polydata topology
        self.add_points()
        self.add_verts()
        self.add_lines()
        self.add_strips()
        self.add_polys()

        # file.close_piece()
        self.close_element('Piece', 2)
        self.close_filetype()

        # add any appended data
        if self.encoding == 'appended':
            self.add_appended_data()

        # close file
        self.close_file()

    # PolyData Methods
    def add_points(self):
        """
        Add a set of points to the PolyData structure.

        This method is used to add a collection of points to a PolyData element. The
        points are passed as input and are processed, encapsulated in a data array,
        and added to the PolyData structure. The method ensures proper encapsulation
        and manages the hierarchy of elements by opening and closing the relevant
        tag for the points.

        """
        self.open_element("Points", indent_lvl=3)
        if self.points is not None:
            # Add data for points
            self._add_dataarray(self.points, "Points", data_type='polydata')
        self.close_element('Points', 3)

    def add_lines(self):
        """
        Add polydata lines to the current XML structure.

        The polydata lines include
        both connectivity and offsets data, specified in the input parameter. The
        method adds these details into the current element context.


        """
        self.open_element("Lines", indent_lvl=3)
        if self.lines is not None:
            # add data for Lines
            self._add_dataarray(self.lines[0], "connectivity", data_type='polydata')
            self._add_dataarray(self.lines[1], "offsets", data_type='polydata')
        self.close_element('Lines', 3)

    def add_verts(self):
        """
        Add vertex data for a polydata element in a VTK file structure.

        The method
        opens a `Verts` element, incorporates the provided vertex connectivity
        and offsets data, and subsequently closes the element after processing.

        """
        self.open_element("Verts", indent_lvl=3)
        if self.verts is not None:
            # add data for Verts
            self._add_dataarray(self.verts[0], "connectivity", data_type='polydata')
            self._add_dataarray(self.verts[1], "offsets", data_type='polydata')
        self.close_element('Verts', 3)

    def add_strips(self):
        """
        Add polygonal data in the form of strips.

        This method allows adding connectivity and offsets data for polygonal strips
        to the current instance. The input strips must contain two arrays: one for
        connectivity and another for offsets. These arrays are handled and added
        to the instance in a structured manner with specific data types.

        """
        self.open_element("Strips", indent_lvl=3)
        if self.strips is not None:
            # add data for Strips
            self._add_dataarray(self.strips[0], "connectivity", data_type='polydata')
            self._add_dataarray(self.strips[1], "offsets", data_type='polydata')
        self.close_element('Strips', 3)

    def add_polys(self):
        """
        Add polygonal data to the output.

        This method is responsible for adding polygonal element data, such as
        connectivity and offsets, to the data structure. The "Polys" element
        is opened, and relevant data arrays are added if provided. The element
        is closed after processing.

        """
        self.open_element("Polys", indent_lvl=3)
        if self.polys is not None:
            # add data for Polys
            self._add_dataarray(self.polys[0], "connectivity", data_type='polydata')
            self._add_dataarray(self.polys[1], "offsets", data_type='polydata')
        self.close_element('Polys', 3)


class XML_MultiBlockWriter(XMLWriterBase):
    """
    Represents an XML MultiBlock Writer for VTK (Visualization Toolkit) files.

    This class facilitates writing structured grid-like hierarchical datasets in XML
    format using Visual Toolkit-compliant structures.
    This class is built on top of the `XMLWriterBase` and provides additional functionalities
    specific to multi-block structures.

    It is designed to work with multiple file types such as ImageData, PolyData,
    RectilinearGrid, among others. This class is useful for generating complex
    visualisation data files programmatically.

    Attributes
    ----------
    filetype : str
        Type of the file being written (e.g., 'ImageData', 'RectilinearGrid', 'StructuredGrid').
    encoding : str
        Character set used to encode the XML file.
    declaration : bool
        Indicates if an XML declaration is included at the beginning of the file.
    whole_extents : tuple of float
        Coordinates defining the global extents of the dataset in space.
    origin : tuple of float
        Origin of the structured grid or image data defined within the file.
    grid_spacing : tuple of float
        Spacing between grid points for structured data.
    direction : tuple of float
        Direction cosine matrix to describe the orientation of the grid in space.
    _text_encoding : str
        Encoding format used for writing text elements to the file.
    _byteorder : str
        Byte ordering format of the data, either 'LittleEndian' or 'BigEndian'.
    file : object
        File handle to which the XML content is being written.
    """

    def __init__(self, filepath, filetype, encoding='ascii', declaration=True):
        super().__init__(filepath, filetype, encoding, declaration)

        # open file and set header
        self.open_file()
        self.add_filetype()

    def open_element(self, element="Block", index=0, name=None, file=None, indent_lvl=2, self_closing=False):
        """Specialized for multi-block structure."""
        attrs = []
        attrs.append(f'index="{index}"')
        if name is not None:
            attrs.append(f'name="{name}"')
        if file is not None:
            attrs.append(f'file="{file}"')

        self.open_element_base(element, attrs, indent_lvl, self_closing)

    def close_element(self, tag_name, indent_lvl=0):
        """
        Add element closing tag to file.

        Returns
        -------
        None

        """
        closing_tag = '  ' * indent_lvl + f'</{tag_name}>\n'
        self.file.write(closing_tag.encode(self._text_encoding))

    def add_filetype(self):
        """
        Add XML root node and file type node.

        """
        # add vtk root node
        vtk_filestr = (f'<VTKFile type="{self.filetype}" version="1.0" '
        f'byte_order="{self._byteorder}" header_type="{self.header_type}">')
        self.file.write((vtk_filestr + "\n").encode(self._text_encoding))

        # write file type node
        file_type_str = f"  <{self.filetype}" + ">\n"

        self.file.write(file_type_str.encode(self._text_encoding))

    def write_blocks(self, block_data):
        """
        Write VTK MultiBlockData blocks to the file.

        A multi-block dataset allows several datasets to be combined as a single dataset.
        Each dataset will have an independent xml file and this creates a `.vtm` file
        that is a catalogue of the respective xml files.

        Parameters
        ----------
        block_data : dict
            A dictionary containing the block name as key and block info as value.
            Expected structure:
            {
                'block_name': {
                    'files': [list of file paths],
                    'names': [optional list of piece names]
                }
            }
        """
        # add blocks
        for indx, block in enumerate(block_data):
            self.open_element(index=indx, name=block)

            # add piece
            for piece_indx, piece_file in enumerate(block_data[block]['files']):

                if 'names' in block_data[block]:
                    piece_name = block_data[block]['names'][piece_indx]
                else:
                    piece_name = f'block_{indx}_{piece_indx}'

                self.open_element(element="Piece", index=piece_indx, name=piece_name, indent_lvl=3)
                # add Dataset
                dataset_indx = 0
                self.open_element(element="DataSet", index=dataset_indx, name=None, file=piece_file, indent_lvl=4,
                                self_closing=True)

                self.close_element("Piece", indent_lvl=3)

            # close block
            self.close_element("Block", indent_lvl=2)

        # close Multiblock filetype
        self.close_filetype()

        # close file
        self.close_file()

    @classmethod
    def write_multiblock(cls, filepath, block_data, add_declaration=True):
        """
        Convenience class method to write VTK MultiBlockData to VTK files.

        A multi-block dataset allows several datasets to be combined as a single dataset.
        In VTK XML format this means each dataset will have an independent xml file and
        a `.vtm` file that is a catalogue of the respective xml files.

        Parameters
        ----------
        filepath : str
            The filepath of the VTK vtm file. This can be a local file name or a complete filename and file path.
        block_data : dict
            A dictionary containing the block name to be used as a key and the block info as value.
        add_declaration : bool, default True
            Add declaration to file for valid XML file.

        Examples
        --------
        >>> block_data = {
        ...     'Geometries': {
        ...         'files': ['geom1.vtp', 'geom2.vtp'],
        ...         'names': ['geometry1', 'geometry2']
        ...     }
        ... }
        >>> XML_MultiBlockWriter.write_multiblock('output.vtm', block_data)
        """
        writer = cls(filepath, 'vtkMultiBlockDataSet', declaration=add_declaration)
        writer.write_blocks(block_data)


# Keep the standalone function for backward compatibility
def xml_multiblock_writer(filepath, block_data, add_declaration=True):
    """
    Write VTK `MultiBlockData` to VTK files.

    A multi-block dataset allows several datasets to be combined as a single dataset. In VTK XML format this means
    each dataset will have an independent xml file and a `.vtm` files that is a catalogue of the respective xml files.

    Parameters
    ----------
    filepath : str
        The filepath of the VTK vtm file. This can be a local file name or a complete filename and file path.
    block_data: dictionary
        A `dictionary` containing the block name to be used as a key and the
    add_declaration: bool, default True
        Add declaration to file for valid XML file.

    """
    XML_MultiBlockWriter.write_multiblock(filepath, block_data, add_declaration)