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
from contextlib import contextmanager
from xml.etree.ElementTree import indent

import numpy as np
import pybase64

## Local Imports
from ..helpers import _parse_bytecount_type
from ..utilities import first_key
from ..vtk_cell_types import *

from .validation import DataValidator, DataSizeChecker
from .base_writer import (VTKWriterBase, StructuredGridMixin, ImageDataMixin,
                          RectilinearGridMixin, UnstructuredGridMixin, PolyDataMixin)


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


class XMLWriterBase(VTKWriterBase):
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
        # Integer types
        "int8": "Int8",
        "uint8": "UInt8",
        "int16": "Int16",
        "uint16": "UInt16",
        "int32": "Int32",
        "uint32": "UInt32",
        "int64": "Int64",
        "uint64": "UInt64",

        # Platform-dependent integers
        "int": "Int64" if np.dtype(int).itemsize == 8 else "Int32",
        "int_": "Int64" if np.dtype(int).itemsize == 8 else "Int32",

        # Floating point
        "float16": "Float32",  # VTK doesn't support float16, promote
        "float32": "Float32",
        "float64": "Float64",
        "float": "Float64",
        "float_": "Float64",

        # String types - all variations map to String
        "str_": "String",
        "unicode_": "String",
        "bytes_": "String",
        "object_": "String",
        "StringDType()": "String",
        "<U": "String",  # Handle numpy unicode string dtypes like '<U10'
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

    def __init__(self, filepath, filetype, encoding='ascii', ascii_precision=15, ascii_ncolumns=6, declaration=True,
                 appended_encoding='base64', version='1.0', compression=None, **kwargs):

        # Set file path with correct extension
        self.path = Path(filepath).with_suffix(self._filetypes[filetype])
        super().__init__(filepath=self.path, **kwargs)

        # check if extension provided and strip - correct extension is added next
        self.filetype = filetype

        # Validate and normalize encoding (base64 -> binary)
        self.encoding = self._validate_encoding(encoding)

        self.ascii_precision = ascii_precision
        self.ascii_ncolumns = ascii_ncolumns
        self._add_declaration = declaration

        # Set header type based on version
        self.vtk_version = version
        if self.vtk_version == '1.0':
            self.header_type = 'UInt64'
        elif self.vtk_version == '0.1':
            self.header_type = 'UInt32'
        else:
            raise ValueError('Invalid VTK version specified.')

        self._byteorder = 'LittleEndian' if sys.byteorder == "little" else 'BigEndian'
        self._byteorder_char = '<' if sys.byteorder == "little" else '>'

        # set attributes for vtk files that are not multiblock files
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

            # Validate byte order compatibility
            self._validate_byte_order()

    def _validate_encoding(self, encoding):
        """Validate encoding parameter."""
        valid_encodings = ['ascii', 'binary', 'base64', 'appended']
        if encoding not in valid_encodings:
            raise ValueError(f'Encoding must be one of {valid_encodings}.')

        # Normalize base64 to binary for internal consistency
        if encoding == 'base64':
            encoding = 'binary'

        return encoding

    def _validate_appended_encoding(self, appended_encoding):
        """Validate appended encoding parameter."""
        if appended_encoding not in ['base64', 'raw']:
            raise ValueError('Appended encoding must be base64 or raw.')
        return appended_encoding

    def _validate_compression(self, compression):
        """Validate compression parameter."""
        if compression is None or compression is False or compression == 0:
            return 0
        elif compression is True or compression in list(range(-1, 10)):
            raise NotImplementedError("Compression to be implemented at a later date")
        else:
            raise ValueError(f'compression level {compression} is not recognized by zlib')

    def _setup_byte_order(self):
        """Setup byte order attributes."""
        self._byteorder = 'LittleEndian' if sys.byteorder == "little" else 'BigEndian'
        self._byteorder_char = '<' if sys.byteorder == "little" else '>'
        self._validate_byte_order()

    def _validate_byte_order(self):
        """Validate that byte order is properly handled."""
        system_endian = sys.byteorder
        vtk_endian = 'little' if self._byteorder == 'LittleEndian' else 'big'
        if system_endian != vtk_endian:
            import warnings
            warnings.warn(
                f"System byte order ({system_endian}) differs from VTK byte order ({vtk_endian}). "
                f"Binary data may need byte swapping for proper reading.", UserWarning
            )

    def write_file(self):
        """Main entry point for writing XML files."""
        self.write_xml_file()

    @contextmanager
    def file_writer(self):
        """Context manager for safe file operations."""
        try:
            self.file = open(self.path, "wb")
            if (self._add_declaration and
                    (self.encoding == 'binary' or
                     (hasattr(self, '_appended_encoding') and self._appended_encoding == 'base64'))):
                self.add_declaration()
            yield self.file
        except IOError as e:
            raise IOError(f'Failed to open file {self.path}: {e}')
        finally:
            if hasattr(self, 'file') and self.file and not self.file.closed:
                self.file.close()

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

        # Add file type specific attributes
        self._add_filetype_attributes()

    def _add_filetype_attributes(self):
        """Add file type specific attributes - to be overridden by subclasses."""
        attrs = []

        if hasattr(self, 'whole_extent'):
            fmt = ' '.join(['%.16g'] * 6)
            attrs.append(f'WholeExtent="{fmt % tuple(self.whole_extent)}"')

        if self.filetype == 'ImageData' and hasattr(self, 'origin'):
            fmt2 = ' '.join(['%.16g'] * 3)
            fmt3 = ' '.join(['%.16g'] * 9)
            attrs.append(f'Origin="{fmt2 % tuple(self.origin)}"')
            attrs.append(f'Spacing="{fmt2 % tuple(self.grid_spacing)}"')
            attrs.append(f'Direction="{fmt3 % tuple(self.direction)}"')

        # Write file type node and attributes
        file_type_str = f"  <{self.filetype}" + " ".join(attrs) + ">\n"
        self.file.write(file_type_str.encode(self._text_encoding))

    def close_filetype(self):
        """Add closing file tag."""
        self.file.write(f'  </{self.filetype}>\n'.encode(self._text_encoding))

    def get_vtk_type(self, numpy_dtype):
        """Get VTK type string from numpy dtype - uses shared logic."""
        dtype_str = str(numpy_dtype)

        # Handle string dtypes
        if any(s in dtype_str.lower() for s in ['str', 'unicode', 'string']):
            return "String"

        if dtype_str.startswith('<U') or dtype_str.startswith('U'):
            return "String"

        # Try direct mapping first
        vtk_type = self._np_to_vtk.get(dtype_str)
        if vtk_type:
            return vtk_type

        # Use numpy dtype introspection for unmapped types
        if numpy_dtype.kind == 'i':  # signed integer
            size_map = {1: "Int8", 2: "Int16", 4: "Int32", 8: "Int64"}
            return size_map.get(numpy_dtype.itemsize, "Int32")
        elif numpy_dtype.kind == 'u':  # unsigned integer
            size_map = {1: "UInt8", 2: "UInt16", 4: "UInt32", 8: "UInt64"}
            return size_map.get(numpy_dtype.itemsize, "UInt32")
        elif numpy_dtype.kind == 'f':  # floating point
            return "Float32" if numpy_dtype.itemsize <= 4 else "Float64"

        raise ValueError(
            f"Unsupported numpy dtype: {numpy_dtype} (kind='{numpy_dtype.kind}', "
            f"itemsize={numpy_dtype.itemsize}). Supported types are numeric types and strings."
        )

    def open_element(self, element="Points", Scalars=None, Vectors=None,
                     Tensors=None, TCoords=None, Normals=None, indent_lvl=2):
        """Open XML element with optional VTK data attributes."""
        attrs = []
        if Scalars is not None:
            fkey = first_key(Scalars)
            if fkey is not None:
                attrs.append(f'Scalars="{fkey}"')
        if Vectors is not None:
            fkey = first_key(Vectors)
            if fkey is not None:
                attrs.append(f'Vectors="{fkey}"')
        if Tensors is not None:
            fkey = first_key(Tensors)
            if fkey is not None:
                attrs.append(f'Tensors="{fkey}"')
        if TCoords is not None:
            fkey = first_key(TCoords)
            if fkey is not None:
                attrs.append(f'TCoords="{fkey}"')
        if Normals is not None:
            fkey = first_key(Normals)
            if fkey is not None:
                attrs.append(f'Normals="{fkey}"')

        self.open_element_base(element, attrs, indent_lvl=indent_lvl)

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

    def add_cell_point_data(self, data, data_type="PointData"):
        """Add data arrays to specified vtk data type."""
        if data is not None:
            # Check if nested dictionary structure
            is_nested = any(isinstance(i, dict) for i in data.values())

            if is_nested:
                # Handle nested structure with scalars, vectors, etc.
                scalars = data.get('scalars')
                vectors = data.get('vectors')
                tensors = data.get('tensors')
                normals = data.get('normals')
                texture_coords = data.get('texture_coords')

                self.open_element(data_type, Scalars=scalars, Vectors=vectors,
                                  Tensors=tensors, Normals=normals, TCoords=texture_coords, indent_lvl=3)

                for data_category in [scalars, vectors, tensors, normals, texture_coords]:
                    if data_category is not None:
                        self.add_data_from_dict(data_type, data_category)
            else:
                # Simple flat dictionary
                self.open_element(data_type)
                self.add_data_from_dict(data_type, data)

            self.close_element(data_type, 3)

    def add_data_from_dict(self, data_type, data_dict):
        """Add data to object using dictionary of data and specified data type."""
        for prop_name, prop_data in data_dict.items():
            self._add_dataarray(prop_data, prop_name, data_type=data_type)

    def _generate_dataarray_attributes(self, data, name, data_type, vtk_type, data_min, data_max):
        """Generate XML attributes for a data array."""
        attrs = []

        if vtk_type is None:
            vtk_type = self.get_vtk_type(data.dtype)
            if vtk_type is None:
                raise ValueError(f"Unsupported data type: {data.dtype}")

        num_components = data.shape[1] if len(data.shape) > 1 else 1

        if data_type == 'field_data':
            attrs.append(f'NumberOfTuples="{num_components}"')
        elif name not in ['connectivity', 'offsets', 'types'] and vtk_type != "String":
            attrs.append(f'NumberOfComponents="{num_components}"')

        # Report the correct format in the XML
        format_name = 'binary' if self.encoding == 'binary' else self.encoding
        attrs.append(f'type="{vtk_type}" format="{format_name}"')

        if vtk_type != "String" and data_min is not None:
            attrs.append(f'RangeMin="{data_min}" RangeMax="{data_max}"')

        return attrs

    @staticmethod
    def _convert_to_array(list_1d):
        if (list_1d is not None) and (type(list_1d).__name__ != "ndarray"):
            assert isinstance(list_1d, (list, tuple))
            return np.array(list_1d)
        return None

    def _add_dataarray(self, data, name, data_type='CellData', vtk_type=None):
        """Add data array with proper encoding."""

        # Process and validate data using shared logic
        if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
            data_min, data_max = np.min(data), np.max(data)
        elif hasattr(data, '__iter__') and len(data) > 0 and isinstance(data[0], str):
            vtk_type = "String"
            processor = DataArrayProcessor(self)

            data = processor.process_string_data(data)
            data_min = data_max = None
        else:
            data = np.asarray(data)
            if data.size == 0:
                raise ValueError(f"Empty data array for {name}")
            data_min, data_max = np.min(data), np.max(data)

        # Generate attributes and write
        attrs = self._generate_dataarray_attributes(data, name, data_type, vtk_type, data_min, data_max)
        self._write_dataarray_to_file(data, name, attrs)

    def _write_dataarray_to_file(self, data, name, attrs, indent_lvl=4):
        """Write data array to file with specified encoding."""
        # For appended data, we need to add offset information to attributes
        if self.encoding == 'appended':
            attrs.append(f'offset="{self._offset}"')

        # Open DataArray element
        element_str = '  ' * indent_lvl + f'<DataArray Name="{name}" ' + " ".join(attrs)

        if self.encoding == 'appended':
            # For appended data, self-close the element (no inline data)
            element_str += '/>\n'
            self.file.write(element_str.encode(self._text_encoding))
            # Update appended data and offset
            self.appended_encoder(data)
        else:
            # For inline data (ascii or binary), open element normally
            element_str += '>\n'
            self.file.write(element_str.encode(self._text_encoding))

            # Write data based on encoding
            if self.encoding == 'ascii':
                self.ascii_encoder(data, indent_level=indent_lvl + 1)
            elif self.encoding == 'binary':  # This is the inline base64 case
                self.Base64Encoder(data)

            # Close DataArray element
            closing_tag = '  ' * indent_lvl + f'</DataArray>\n'
            self.file.write(closing_tag.encode(self._text_encoding))

    # Encoding methods (keep existing implementation)
    def ascii_encoder(self, array, indent_level=5):
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
        max_cpl = 140
        # Keep existing implementation but use shared validation
        array = array.flatten(order='C')

        if np.issubdtype(array.dtype, np.integer):
            precision = 0
            max_val = np.max(np.abs(array)) if array.size > 0 else 0
            int_str_length = len(str(max_val)) + (1 if np.any(array < 0) else 0)
            num_cols = max(1, max_cpl // (int_str_length + 3))
        else:
            precision = self.ascii_precision
            user_spec_line_width = self.ascii_ncolumns * precision + self.ascii_ncolumns - 1
            # Estimate number of columns based on precision and a max line width of 140 characters
            num_cols = max(1, min(max_cpl, user_spec_line_width) // precision )

        line_start = '  ' * indent_level

        # fmt_single = '{:d}' if precision == 0 else f'{{:.{precision}f}}'
        # data_str = [line_start]
        # for i in range(0, array.size, num_cols):
        #     chunk = array[i:i + num_cols]
        #     line = ' '.join(fmt_single.format(val) for val in chunk) + '\n'
        #     data_str.append(line)
        #     if i + num_cols < array.size:
        #         data_str.append(line_start)

        # calculate number of full rows
        fmt = ' '.join([f'%.{precision}f'] * num_cols) + '\n'
        nrows = 1 if array.size <= num_cols else int(array.size / num_cols)

        # write full rows
        data_str = [line_start]
        if array.size > num_cols:
            for row in range(nrows):
                shift = row * num_cols
                data_str.append(fmt % tuple(array[shift:num_cols + shift]))
                if row < nrows-1:
                    data_str.append(line_start)

            # write any remaining data in last non-full row
            if array.size % num_cols != 0:
                data_str.append(line_start)
                rem = array[num_cols + shift::]
                fmt = ' '.join([f'%.{precision}f'] * len(rem)) + '\n'
                data_str.append(fmt % tuple(rem))
        else:
            rem = array
            fmt = ' '.join([f'%.{precision}f'] * len(rem)) + '\n'
            data_str.append(fmt % tuple(rem))

        result = ''.join(data_str)
        self.file.write(result.encode(self._text_encoding))

        return result

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
        indent_level = 3
        opening_tag = '  ' * indent_level + '<FieldData>\n'
        closing_tag = '  ' * indent_level + '</FieldData>\n'

        if field_data is not None:
            self.file.write(opening_tag.encode(self._text_encoding))

            for key, value in field_data.items():
                self._add_dataarray(value, name=key, data_type='field_data')

            self.file.write(closing_tag.encode(self._text_encoding))

    def open_piece(self):
        """
        Open `Piece` element of XML file.

        Each piece file contains the attribute tags for the number of points,
        cells, vertices, lines, strips and polydata items.

        """
        indent_level = 2
        opening_tag = '  ' * indent_level + '<Piece '
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

        piece_str = opening_tag + " ".join(attrs) + ">\n"

        self.file.write(piece_str.encode(self._text_encoding))

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
        if not isinstance(data_array, np.ndarray):
            raise TypeError(f'Expected NumPy array, got {type(data_array)}')

        if data_array.size == 0:
            raise ValueError('Cannot calculate block size for empty array')

        try:
            fmt_block = _parse_bytecount_type(self.header_type, self._byteorder)[0]
            block_size_bytes = struct.pack(fmt_block, data_array.nbytes)
            return block_size_bytes
        except struct.error as e:
            raise ValueError(f'Failed to pack block size: {e}')

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
        if not isinstance(data_array, np.ndarray):
            raise TypeError('Expected NumPy Array.')

        # Handle string data (uint8 arrays) specially
        if data_array.dtype == np.uint8:
            return data_array.tobytes()

        # For all other data types, ensure C-contiguous layout
        # VTK expects data in C order (row-major)
        if not data_array.flags["C_CONTIGUOUS"]:
            data_array = np.ascontiguousarray(data_array)

        return data_array.tobytes()

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
        self.file.write(b'\n')

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
            # Raw binary data with block size header
            block_size = self.calculate_blocksize(data_array)
            block_data = self.convert_blockdata(data_array)
            self._appended_data += block_size + block_data
            self._offset += len(block_size) + len(block_data)
        elif self._appended_encoding == 'base64':
            # Base64 encoded data (no block size header needed for base64)
            encoded = self.b64_encode_array(data_array)
            self._appended_data += encoded
            self._offset += len(encoded)

    def is_inline_encoding(self):
        """Check if encoding writes data inline in DataArray elements."""
        return self.encoding in ['ascii', 'binary']

    def is_appended_encoding(self):
        """Check if encoding writes data in AppendedData section."""
        return self.encoding == 'appended'

    # Common XML Operations

    def add_appended_data(self):
        """
        Write appended data in a specific format to a file.

        The method generates an XML-like structure with encoding and appended data included.
        The data is written directly to a file-like object provided during the initialization of the calling instance.

        """
        self.file.write((f'  <AppendedData encoding="{self._appended_encoding}">\n').encode(self._text_encoding))
        self.file.write(b'    _')  # Underscore marks start of binary data
        self.file.write(self._appended_data)
        self.file.write(b'\n  </AppendedData>\n')


class DataArrayProcessor:
    """Helper class to handle data array processing."""

    def __init__(self, writer):
        self.writer = writer

    def process_string_data(self, data):
        """Process string data for different encodings."""
        if self.writer.encoding == 'ascii':
            return self._strings_to_ascii(data)
        else:
            return self._strings_to_binary(data)

    def _strings_to_ascii(self, data):
        """Convert strings to ASCII format (character codes)."""
        char_arrays = []
        for element in data:
            char_codes = [ord(c) for c in str(element)] + [0]  # null terminator
            char_arrays.extend(char_codes)
        return np.array(char_arrays, dtype=np.int32)

    def _strings_to_binary(self, data):
        """Convert strings to binary format (UTF-8 bytes)."""
        byte_data = bytearray()
        for element in data:
            string_bytes = str(element).encode('utf-8') + b'\0'
            byte_data.extend(string_bytes)
        return np.frombuffer(byte_data, dtype=np.uint8)


class XMLImageDataWriter(ImageDataMixin, XMLWriterBase):
    """VTI XML Writer Class using mixin pattern."""

    def __init__(self, filepath, whole_extent, spacing=(1, 1, 1), origin=(0, 0, 0),
                 direction=(1, 0, 0, 0, 1, 0, 0, 0, 1), piece_extent=None, **kwargs):
        super().__init__(
            filepath=filepath,
            filetype='ImageData',
            whole_extent=whole_extent,
            spacing=spacing,
            origin=origin,
            direction=direction,
            piece_extent=piece_extent,
            **kwargs
        )
        self.check_data_consistency()

    def write_xml_file(self):
        """Write VTI file in XML format."""
        with self.file_writer():
            self.add_filetype()
            self.open_piece()
            self.add_fielddata(self.field_data)
            self.add_cell_point_data(self.point_data, data_type="PointData")
            self.add_cell_point_data(self.cell_data, data_type="CellData")
            self.close_element('Piece', 2)
            self.close_filetype()
            if self.encoding == 'appended':
                self.add_appended_data()


class XMLRectilinearGridWriter(RectilinearGridMixin, XMLWriterBase):
    """VTR XML Writer Class using mixin pattern."""

    def __init__(self, filepath, x, y, z, whole_extent=None, piece_extent=None, **kwargs):
        super().__init__(
            filepath=filepath,
            filetype='RectilinearGrid',
            x=x,
            y=y,
            z=z,
            whole_extent=whole_extent,
            piece_extent=piece_extent,
            **kwargs
        )
        self.check_data_consistency()

    def write_xml_file(self):
        """Write VTR file in XML format."""
        # open xml file
        with self.file_writer():
            self.add_filetype()

            # open piece and add counts
            self.open_piece()

            # add FieldData
            self.add_fielddata(self.field_data)

            # add variables at points (PointData)
            self.add_cell_point_data(self.point_data, data_type="PointData")

            # add variables at cells (CellData)
            self.add_cell_point_data(self.cell_data, data_type="CellData")

            # add coordinates
            self.add_coordinates()

            # file.close_piece()
            self.close_element('Piece', 2)
            self.close_filetype()

            # add any appended data
            if self.encoding == 'appended':
                self.add_appended_data()

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


class XMLStructuredGridWriter(StructuredGridMixin, XMLWriterBase):
    """VTS XML Writer Class."""

    def __init__(self, filepath, points, whole_extent, piece_extent=None, **kwargs):
        super().__init__(
            filepath=filepath,
            filetype='StructuredGrid',
            whole_extent=whole_extent,
            piece_extent=piece_extent,
            **kwargs
        )

        # Validate and set points
        self.points = self.validator.validate_points_array(points)
        self.npoints = len(self.points)

        # Check consistency between points and extent
        expected_npoints = np.prod(self.num_cells + 1)
        if self.points.shape[0] != expected_npoints:
            raise ValueError(
                f"Number of points ({self.points.shape[0]}) doesn't match extent. "
                f"Expected {expected_npoints} points for extent {self.piece_extent}"
            )

        self.check_data_consistency()

    def add_points(self, points):
        """Add points to the StructuredGrid."""
        self.open_element("Points", indent_lvl=3)
        self._add_dataarray(points, "Points", data_type='points')
        self.close_element('Points', 3)

    def write_xml_file(self):
        """Write VTS file in XML format."""
        # open xml file
        with self.file_writer():
            self.add_filetype()

            # open piece and add counts
            self.open_piece()

            # add FieldData
            self.add_fielddata(self.field_data)

            # add variables at points (PointData)
            self.add_cell_point_data(self.point_data, data_type="PointData")

            # add variables at cells (CellData)
            self.add_cell_point_data(self.cell_data, data_type="CellData")

            # add coordinates
            self.add_points(self.points)

            # file.close_piece()
            self.close_element('Piece', 2)
            self.close_filetype()

            # add any appended data
            if self.encoding == 'appended':
                self.add_appended_data()


class XMLUnstructuredGridWriter(UnstructuredGridMixin, XMLWriterBase):
    """VTU XML Writer Class using mixin pattern."""

    def __init__(self, filepath, points, cell_types=None, connectivity=None,
                 offsets=None, **kwargs):
        super().__init__(
            filepath=filepath,
            filetype='UnstructuredGrid',
            points=points,
            cell_types=cell_types,
            connectivity=connectivity,
            offsets=offsets,
            **kwargs
        )
        self.check_data_consistency()

    def write_xml_file(self):
        """Write VTU file in XML format."""
        with self.file_writer():
            self.add_filetype()

            self.open_piece()
            self.add_fielddata(self.field_data)
            self.add_cell_point_data(self.point_data, data_type="PointData")
            self.add_cell_point_data(self.cell_data, data_type="CellData")
            self.add_points()
            self.add_unstruct_cells()
            self.close_element('Piece', 2)
            self.close_filetype()

            if self.encoding == 'appended':
                self.add_appended_data()

    def add_points(self):
        """Add points to the VTU structure."""
        self.open_element("Points", indent_lvl=3)
        if self.points is not None:
            self._add_dataarray(self.points, "Points", data_type='Points')
        self.close_element('Points', 3)

    def add_unstruct_cells(self):
        """Add unstructured cell data."""
        self.open_element("Cells", indent_lvl=3)
        if self.connectivity is not None:
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


class XMLPolyDataWriter(PolyDataMixin, XMLWriterBase):
    """VTP XML Writer Class using mixin pattern."""

    def __init__(self, filepath, points=None, verts=None, lines=None,
                 strips=None, polys=None, **kwargs):
        super().__init__(
            filepath=filepath,
            filetype='PolyData',
            points=points,
            verts=verts,
            lines=lines,
            strips=strips,
            polys=polys,
            **kwargs
        )
        self.check_data_consistency()

    def write_xml_file(self):
        """Write a VTP file in XMK format."""
        # open xml file
        with self.file_writer():
            self.add_filetype()

            # open piece and add counts
            self.open_piece()

            # add FieldData
            self.add_fielddata(self.field_data)

            # add variables at points (PointData)
            self.add_cell_point_data(self.point_data, data_type="PointData")

            # add variables at cells (CellData)
            self.add_cell_point_data(self.cell_data, data_type="CellData")

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

    """

    def __init__(self, filepath, filetype='vtkMultiBlockDataSet', encoding='ascii', declaration=True):
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
                piece_name = (block_data[block]['names'][piece_indx] if 'names' in block_data[block]
                              else f'block_{indx}_{piece_indx}')

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
        if self._add_declaration:
            self.add_declaration()


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
