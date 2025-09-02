#!/usr/bin/env python
"""
VTK ImageDtata examples.

Created at 20:22, 26 Apr, 2022
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
from vtkio.writer import write_vti


#%% Image data example
print("Running ImageData Examples...")

# write blank skeleton file
write_vti('test_blank_vti_new', whole_extent=[0, 1, 0, 1, 0, 1], piece_extent=[0, 1, 0, 1, 0, 1],
          spacing=[1, 1, 1], point_data=None, cell_data=None, field_data=None, encoding='ascii')

# --8<-- [start:create_grid_data]

# set numpy seed value so that all arrays contain repeatable numbers
np.random.seed(77)

# Grid Dimensions / Topology
nx, ny, nz = 6, 6, 2
ncells = nx * ny * nz
npoints = (nx + 1) * (ny + 1) * (nz + 1)

origin = np.array([0, 0, 0])
num_cells = np.array([nx, ny, nz])
spacing = np.array([1, 1, 1])
max_extent = spacing * num_cells

whole_extent = np.array([origin, max_extent]).T.flatten()
piece_extent = np.array([origin, max_extent]).T.flatten()

# Variables
temp = np.random.random(npoints)
multi_component2 = np.random.random((npoints, 2))
multi_component3 = np.random.random((npoints, 3))
multi_component4 = np.random.random((npoints, 4))
force = np.random.random((npoints, 3)) * 20
stress = np.random.random([npoints, 9]) * 1000
norms = np.random.random([npoints, 3])
norms /= np.linalg.norm(norms, axis=1)[:, np.newaxis]

# data for writing for each point or cell is defined in a dict of dicts
# where the keys represent the DataArray type and the nested keys the
# DataArray name
point_data = {"scalars": {"temp": temp,
                          "2-components": multi_component2,
                          "3-components": multi_component3,
                          "4-components": multi_component4},
              "vectors": {"force": force},
              "tensors": {"stress": stress},
              "normals": {"normals": norms},
}

pressure = np.arange(ncells)

field_data = {'TimeValue': 0.122654987}

# --8<-- [end:create_grid_data]


## new version
# --8<-- [start:write_imagedata_writer_ascii]
from vtkio.writer.xml import XMLImageDataWriter


file = XMLImageDataWriter('test_uniform_image_data.vti',
                          origin=origin, spacing=spacing,
                          whole_extent=whole_extent,
                          piece_extent=piece_extent,
                          cell_data={"scalars": {"pressure": pressure}},
                          field_data=field_data,
                          point_data=point_data)

file.write_xml_file()

# --8<-- [end:write_imagedata_writer_ascii]

# --8<-- [start:write_imagedata_writer_binary]

file = XMLImageDataWriter('test_uniform_image_data.vti',
                          origin=origin, spacing=spacing,
                          whole_extent=whole_extent,
                          piece_extent=piece_extent,
                          cell_data={"scalars": {"pressure": pressure}},
                          field_data=field_data,
                          point_data=point_data,
                          encoding='binary')

file.write_xml_file()

# --8<-- [end:write_imagedata_writer_binary]

# --8<-- [start:write_imagedata_writer_appended_encoded]

file = XMLImageDataWriter('test_uniform_image_data.vti',
                          origin=origin, spacing=spacing,
                          whole_extent=whole_extent,
                          piece_extent=piece_extent,
                          cell_data={"scalars": {"pressure": pressure}},
                          field_data=field_data,
                          point_data=point_data,
                          encoding='appended')

file.write_xml_file()

# --8<-- [end:write_imagedata_writer_appended_encoded]

# --8<-- [start:write_imagedata_writer_appended_raw]

file = XMLImageDataWriter('test_uniform_image_data.vti', origin=origin, spacing=spacing,
                          whole_extent=whole_extent,
                          piece_extent=piece_extent,
                          cell_data={"scalars": {"pressure": pressure}},
                          field_data=field_data,
                          point_data=point_data,
                          encoding='appended',
                          appended_encoding='raw')

file.write_xml_file()

# --8<-- [end:write_imagedata_writer_appended_raw]

# --8<-- [start:write_grid_data_writer_api]
from vtkio.writer import write_vti

write_vti('test_image_data_grid_new',
          whole_extent=whole_extent,
          piece_extent=piece_extent,
          origin=origin, spacing=spacing,
          point_data=point_data,
          cell_data={"scalars": {"pressure": pressure}},
          field_data=None,
          encoding='ascii')

write_vti('test_image_data_grid_binary_new',
          whole_extent=whole_extent,
          piece_extent=piece_extent,
          origin=origin, spacing=spacing,
          point_data=point_data,
          cell_data={"scalars": {"pressure": pressure}},
          field_data=None,
          encoding='binary')

write_vti('test_image_data_grid_raw_appended_new',
          whole_extent=whole_extent,
          piece_extent=piece_extent,
          origin=origin, spacing=spacing,
          point_data=point_data,
          cell_data={"scalars": {"pressure": pressure}},
          field_data=None,
          encoding='appended',
          appended_encoding='raw')

write_vti('test_image_data_grid_appended_new',
          whole_extent=whole_extent,
          piece_extent=piece_extent,
          origin=origin, spacing=spacing,
          point_data=point_data,
          cell_data={"scalars": {"pressure": pressure}},
          field_data=None, encoding='appended')

# --8<-- [end:write_grid_data_writer_api]


# --8<-- [start:write_grid_data_writer_api_vtkhdf]
write_vti('test_image_data_grid_appended_new',
          whole_extent=whole_extent,
          origin=origin, spacing=spacing,
          point_data=point_data,
          cell_data={"scalars": {"pressure": pressure}},
          field_data=None, file_format='vtkhdf')

# --8<-- [end:write_grid_data_writer_api_vtkhdf]


# --8<-- [start:write_grid_data_hl]
from vtkio.simplified import uniform_grid

uniform_grid('test_uniform_image_data',
             num_cells=num_cells, spacing=spacing,
             cell_data={"scalars": {"pressure": pressure}},
             point_data=point_data)

uniform_grid('test_uniform_image_data_binary',
             num_cells=num_cells, spacing=spacing,
             cell_data={"scalars": {"pressure": pressure}},
             point_data=point_data, encoding='binary')

uniform_grid('test_uniform_image_data_appended',
             num_cells=num_cells, spacing=spacing,
             cell_data={"scalars": {"pressure": pressure}},
             point_data=point_data, encoding='appended')

uniform_grid('test_uniform_image_data_2',
             num_cells=num_cells, spacing=spacing * 0.45,
             origin=origin + 0.7312,
             cell_data={"scalars": {"pressure": pressure}},
             point_data=point_data,
             field_data=field_data)

# --8<-- [end:write_grid_data_hl]

#%% test vtkhdf writing with writer

# --8<-- [start:write_imagedata_writer_vtkhdf]
from vtkio.writer.vtkhdf import VTKHDFImageDataWriter

imagedata_test = VTKHDFImageDataWriter('test_image_data_grid_hdf5',
                                       whole_extent=whole_extent,
                                       origin=origin, spacing=spacing,
                                       field_data=field_data,
                                       point_data=point_data,
                                       cell_data={"scalars": {"pressure": pressure}})

imagedata_test.write_vtkhdf_file()
# --8<-- [end:write_imagedata_writer_vtkhdf]

#%% test vtkhdf writing with hl api

# whole_extent = [0, 3, 0, 3, 0, 3]
# origin = [0, 0, 0]
# spacing = [0.1, 0.1, 0.1]
# direction = [1, 0, 0, 0, 1, 0, 0, 0, 1]

write_vti('test_uniform_image_data_2', whole_extent, origin=origin+0.7312, spacing=spacing*0.45,
                 cell_data={"scalars": {"pressure": pressure}}, point_data=point_data, field_data=field_data)

#%% VTKHDFImageDataWriter example
imagedata_test = VTKHDFImageDataWriter('test_image_data_grid_hdf5_new', whole_extent=whole_extent, origin=origin,
                                       spacing=spacing, field_data=None, point_data=point_data,
                                       cell_data={"scalars": {"pressure": pressure}})

imagedata_test.write_vtkhdf_file()


#%% write vtkhdf file with additional metadata
from vtkio.reader import read_vtkxml_data

regular_grid_example_data = read_vtkxml_data('../TestData/vti/regular_grid_example.vti')
structured_points_data = read_vtkxml_data('../TestData/vti/structured_points.vti')
vase_data = read_vtkxml_data('../TestData/vti/vase.vti')

# --8<-- [start:write_points_writer_api_vtkhdf_additional_metadata]
from vtkio.writer.vtkhdf import VTKHDFMultiBlockWriter

blocks = {'block1': regular_grid_example_data, 'block2': structured_points_data, 'block3': vase_data,}

writer = VTKHDFMultiBlockWriter('hdf_multiblock_test_imagedata', blocks)
writer.write_vtkhdf_file()

# --8<-- [end:write_points_writer_api_vtkhdf_additional_metadata]
