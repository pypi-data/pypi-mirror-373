#!/usr/bin/env python
"""
Module documentation goes here.

Created at 16:44, 18 May, 2025
"""


__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2025, {project_name}'
__credits__ = ['{credit_list}']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'j.morrissey@ed.ac.uk'
__status__ = '{dev_status}'



# Standard Library


# Imports


# Local Sources



LITTLE_ENDIAN = '<'  # Constant for little-endian byte order
BIG_ENDIAN = '>'  # Constant for big-endian byte order

def _parse_dtype_size(data_type):
    """Resolves the NumPy dtype and start index based on data type."""
    type_size_mapping = {
        'float16': 2,
        'float32': 4,
        'float64': 8,
        'int8': 1,
        'int16': 2,
        'int32': 4,
        'int64': 8,
        'uint8': 1,
        'uint16': 2,
        'uint32': 4,
        'uint64': 8,
    }
    return type_size_mapping.get(data_type.lower(), (None, None))


def _parse_bytecount_type(data_type, byteorder):
    """Resolves the NumPy dtype and start index based on data type."""
    fmt_byteorder = LITTLE_ENDIAN if byteorder.lower() in ['<', 'littleendian'] else BIG_ENDIAN

    type_size_mapping = {
        'int8': ('b', 1),
        'short': ('h', 2),
        'int16': ('h', 2),
        'int': ('i', 4),
        'int32': ('i', 4),
        'int64': ('q', 8),
        'longlong': ('q', 8),
        'uint8': ('B', 1),
        'ushort': ('H', 2),
        'uint16': ('H', 2),
        'uint': ('I', 4),
        'uint32': ('I', 4),
        'uint64': ('Q', 8),
        'ulonglong': ('Q', 8),

    }
    mapped = type_size_mapping.get(data_type.lower(), (None, None))

    return fmt_byteorder + mapped[0], mapped[1]


def _get_numpy_struct_mapping(data_type):

    # Mapping of numpy dtype to struct format
    np_to_struct_mapping = {
        "int8": "b",
        "uint8": "B",
        "int16": "h",
        "uint16": "H",
        "int32": "i",
        "uint32": "I",
        "int64": "q",
        "uint64": "Q",
        "float32": "f",
        "float64": "d",
        'short': 'h',
        'int': 'i',
        'uint': 'I',
        'ushort': 'H',
        'longlong': 'q',
        'ulonglong': 'Q',
    }

    return np_to_struct_mapping.get(data_type.lower(), "d")


def _determine_points_key(points_data):
    """Determine the correct key for points in the recovered data."""
    try:
        return points_data['Points']
    except KeyError:
        try:
            return points_data['points']
        except KeyError:
            return points_data[next(iter(points_data))]
