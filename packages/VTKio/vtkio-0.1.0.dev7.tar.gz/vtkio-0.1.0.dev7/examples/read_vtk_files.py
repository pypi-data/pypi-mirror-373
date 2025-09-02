#!/usr/bin/env python
"""
Module documentation goes here.

Created at 12:46, 08 Jul, 2024
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'


# Standard Library


# Imports


# Local Sources
from vtkio.reader.hdf5 import read_vtkhdf_data
from vtkio.reader.xml import Reader

# Read different ascii files
data1 = Reader('revolution_triangular_mesh_test.vtu').parse()

data2 = Reader('test.vtu').parse()
data2a = Reader('test_binary.vtu').parse()
data2b = Reader('test_appended.vtu').parse()

data3 = Reader('test_uniform_image_data.vti').parse()
data3a = Reader('test_uniform_image_data_binary.vti').parse()
data3b = Reader('test_uniform_image_data_appended.vti').parse()
data3c = Reader('test_uniform_image_data_2.vti').parse()

data4 = Reader('rect_example_2.vtr').parse()
data4a = Reader('rect_example_2_base64.vtr').parse()
data4b = Reader('rect_example_2_appended.vtr').parse()

data5 = Reader('distorted_grid.vts').parse()
data5a = Reader('distorted_grid_binary.vts').parse()
data5b = Reader('distorted_grid_appended.vts').parse()

data6 = Reader('polytest.vtp').parse()
data6a = Reader('polytest_binary.vtp').parse()
data6b = Reader('polytest_base64.vtp').parse()

data7 = Reader('line_test.vtp').parse()
data7a = Reader('line_test_binary.vtp').parse()
data7b = Reader('line_test_base64.vtp').parse()

# Read VTKHDF files
data8 = read_vtkhdf_data('test_uniform_image_data_2.vtkhdf')
print(f'{data3c == data8}')

data9 = read_vtkhdf_data('revolution_triangular_mesh_test.vtkhdf')
print(f'{data9 == data1}')

data10 = read_vtkhdf_data('cow.vtkhdf')
data11 = Reader('../TestData/vtp/cow.vtp').parse()
print(f'{data10 == data11}')

data12 = read_vtkhdf_data('rect_example_2.vtkhdf')

data13 = Reader('cylinder_segment.vts').parse()
data14 = read_vtkhdf_data('cylinder_segment.vtkhdf')
print(f'{data13 == data14}')

data1.write('data1_test_out', file_format='xml', xml_encoding='ascii')
data1.write('data1_test_out', file_format='vtkhdf')

data3.write('data3_test_out', file_format='xml', xml_encoding='ascii')
data3.write('data3_test_out', file_format='vtkhdf')

data4.write('data4_test_out', file_format='xml', xml_encoding='ascii')
data4.write('data4_test_out', file_format='vtkhdf')

data5.write('data5_test_out', file_format='xml', xml_encoding='ascii')
data5.write('data5_test_out', file_format='vtkhdf')

data10.write('data10_test_out', file_format='xml', xml_encoding='ascii')
data10.write('data10_test_out', file_format='vtkhdf')
