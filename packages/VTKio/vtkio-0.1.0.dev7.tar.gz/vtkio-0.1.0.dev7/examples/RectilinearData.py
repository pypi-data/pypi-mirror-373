#!/usr/bin/env python
"""
VTK RectilinearData examples.

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
from vtkio.writer import write_vtr


# %% Rectilinear Grid Example
print("Running rectilinear...")

# write blank template file
write_vtr("rectilinear_grid_file_test", (0, 1), (0, 1), (0, 1),
         whole_extent=[0, 1, 0, 1, 0, 1], piece_extent=[0, 1, 0, 1, 0, 1], encoding='ascii')

# --8<-- [start:create_grid_data]

# set numpy seed value so that all arrays contain repeatable numbers
np.random.seed(77)


# Dimensions
num_cells = np.array([3, 3, 2])
ncells = np.prod(num_cells)
npoints = np.prod(num_cells + 1)

# Grid Dimensions / Topology
origin = np.array([0, 0, 0])
max_extent = np.array([3, 3, 2])
whole_extent = np.array([0, 3, 0, 3, 0, 2])

# Grid Coordinates
x, x_step = np.linspace(origin[0], max_extent[0], num_cells[0] + 1,
                        retstep=True, dtype='float64')
y, y_step = np.linspace(origin[1], max_extent[1], num_cells[1] + 1,
                        retstep=True, dtype='float64')
z, z_step = np.linspace(origin[2], max_extent[2], num_cells[2] + 1,
                        retstep=True, dtype='float64')

# Variables
random_sample = np.random.random(npoints)
temp = random_sample
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
point_data = {"scalars": {"temp": temp, "2-components": multi_component2, "3-components": multi_component3,
                          "4-components": multi_component4},
              "vectors": {"force": force},
              "tensors": {"stress": stress},
              "normals": {"normals": norms},
              }

pressure = np.arange(ncells)
cell_data = {"scalars": {"pressure": pressure}}

field_data = {'TimeValue': 0.122654987}

# --8<-- [end:create_grid_data]


# --8<-- [start:write_rectilineargriddata_writer_ascii]
from vtkio.writer.xml import XMLRectilinearGridWriter


file = XMLRectilinearGridWriter('test_rectilinear_grid_data.vtr',
                                x, y, z,
                                cell_data={"scalars": {"pressure": pressure}},
                                field_data=field_data,
                                point_data=point_data)

file.write_xml_file()

# --8<-- [end:write_rectilineargriddata_writer_ascii]


# --8<-- [start:write_rectilineargriddata_writer_binary]
file = XMLRectilinearGridWriter('test_rectilinear_grid_data.vtr',
                                x, y, z,
                                cell_data={"scalars": {"pressure": pressure}},
                                field_data=field_data,
                                point_data=point_data,
                                encoding='binary')

file.write_xml_file()

# --8<-- [end:write_rectilineargriddata_writer_binary]


# --8<-- [start:write_rectilineargriddata_writer_appended_encoded]
file = XMLRectilinearGridWriter('test_rectilinear_grid_data.vtr',
                                x, y, z,
                                cell_data={"scalars": {"pressure": pressure}},
                                field_data=field_data,
                                point_data=point_data,
                                encoding='appended')

file.write_xml_file()

# --8<-- [end:write_rectilineargriddata_writer_appended_encoded]


# --8<-- [start:write_rectilineargriddata_writer_appended_raw]
file = XMLRectilinearGridWriter('test_rectilinear_grid_data.vtr',
                                x, y, z,
                                cell_data={"scalars": {"pressure": pressure}},
                                field_data=field_data,
                                point_data=point_data,
                                encoding='appended',
                                appended_encoding='raw')

file.write_xml_file()

# --8<-- [end:write_rectilineargriddata_writer_appended_raw]

#%% Writer API
# --8<-- [start:write_rectilineargrid_data_writer_api]
from vtkio.writer import write_vtr

write_vtr('test_rectilineardata_grid',
          x, y, z,
          whole_extent=whole_extent,
          point_data=point_data,
          cell_data={"scalars": {"pressure": pressure}},
          field_data=None,
          encoding='ascii')

write_vtr('test_rectilineardata_grid_binary',
          x, y, z,
          whole_extent=whole_extent,
          point_data=point_data,
          cell_data={"scalars": {"pressure": pressure}},
          field_data=None,
          encoding='binary')

write_vtr('test_rectilineardata_grid_appended',
          x, y, z,
          whole_extent=whole_extent,
          point_data=point_data,
          cell_data={"scalars": {"pressure": pressure}},
          field_data=None,
          encoding='appended',
          appended_encoding='raw')

write_vtr('test_rectilineardata_grid_raw_appended',
          x, y, z,
          whole_extent=whole_extent,
          point_data=point_data,
          cell_data={"scalars": {"pressure": pressure}},
          field_data=None,
          encoding='appended',
          appended_encoding='raw')

# --8<-- [end:write_rectilineargrid_data_writer_api]


# --8<-- [start:write_rectilineargrid_data_writer_api_vtkhdf]
write_vtr('test_rectilineardata_grid_vtkhdf',
          x, y, z,
          whole_extent=whole_extent,
          point_data=point_data,
          cell_data={"scalars": {"pressure": pressure}},
          field_data=None,
          file_format='vtkhdf')

# --8<-- [end:write_rectilineargrid_data_writer_api_vtkhdf]





#%% Simplified API
#TODO: this should just be imagedata?

# --8<-- [start:write_grid_from_extents_hl]
from vtkio.simplified import regular_grid_from_extents

# Grid Dimensions / Topology
origin = np.array([0, 0, 0])
max_extent = np.array([3, 3, 2])

nx, ny, nz = num_cells
spacing = (max_extent - origin) / num_cells

# write data
regular_grid_from_extents('rect_example_2',
                          origin, max_extent, num_cells,
                          cell_data=cell_data,
                          point_data=point_data,
                          field_data=field_data)

regular_grid_from_extents('rect_example_2_base64',
                          origin, max_extent, num_cells,
                          cell_data=cell_data,
                          point_data=point_data,
                          field_data=None,
                          encoding='binary')

regular_grid_from_extents('rect_example_2_appended',
                          origin, max_extent, num_cells,
                          cell_data=cell_data,
                          point_data=point_data,
                          encoding='appended')

# --8<-- [end:write_grid_from_extents_hl]

# --8<-- [start:write_grid_from_coordinates_hl]

# point values based on points list
from vtkio.simplified import regular_grid_from_coordinates

# Grid Coordinates
x, x_step = np.linspace(origin[0], max_extent[0], num_cells[0] + 1,
                        retstep=True, dtype='float64')
y, y_step = np.linspace(origin[1], max_extent[1], num_cells[1] + 1,
                        retstep=True, dtype='float64')
z, z_step = np.linspace(origin[2], max_extent[2], num_cells[2] + 1,
                        retstep=True, dtype='float64')

xx, yy, zz = np.array(np.meshgrid(x, y, z))
coordinates = np.vstack((xx.ravel(), yy.ravel(), zz.ravel())).T
node_spacing = np.array((x_step, y_step, z_step))

# Add some data
temp = random_sample
pressure = np.arange(ncells)

# write to file
regular_grid_from_coordinates('rect_example_3',
                              coordinates,
                              cell_data=cell_data,
                              point_data=point_data)

# --8<-- [end:write_grid_from_coordinates_hl]

#%% test proposed rectilinear grid structure

# --8<-- [start:write_rectilineargriddata_vtkhdf_writer]
from vtkio.writer.vtkhdf import VTKHDFRectilinearGridWriter

file = VTKHDFRectilinearGridWriter('rect_example_2', x, y, z, cell_data={"scalars": {"pressure": pressure}},
                       point_data=point_data, field_data=field_data)

file.write_vtkhdf_file()

# --8<-- [start:write_rectilineargriddata_vtkhdf_writer]
