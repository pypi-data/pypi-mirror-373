#!/usr/bin/env python
"""
Module documentation goes here.

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
from vtkio.reader import read_vtkxml_data
from vtkio.writer.writers import write_vtp

write_vtp('test_blank_vtp', points=None, lines=None, verts=None, point_data=None,
         cell_data=None, field_data=None, encoding='ascii')

#%% Set some constants
# --8<-- [start:create_points_data]

# set numpy seed value so that all arrays contain repeatable numbers
np.random.seed(77)

# Points dataset Topology
npoints = 20
points = np.random.random((npoints, 3))

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

pressure = np.arange(npoints)
cell_data = {"scalars": {"pressure": pressure}
             }

fielddata = {'TimeValue': 0.122654987}
# --8<-- [end:create_points_data]

# %% Poly data for points

from vtkio.vtk_cell_types import VTK_Vertex
print(VTK_Vertex)

# --8<-- [start:create_topology_arrays]

# create cell topology by creating the cell types, connectivity and offsets arrays
cell_types = np.empty(npoints, dtype="uint8")
cell_types[:] = VTK_Vertex.type_id

# for points, this is simply a list of the points ids and offset by 1
connectivity = np.arange(npoints, dtype="int32")  # each point is only connected to itself
offsets = np.arange(start=1, stop=npoints + 1, dtype="int32")  # index of last node in each cell

# --8<-- [end:create_topology_arrays]


#%% write with xml base writer
# --8<-- [start:write_points_data_ascii]
from vtkio.writer.xml import XMLPolyDataWriter

# Write the file using the xml writer class
file = XMLPolyDataWriter('test_points_polydata.vtp',
                         points=points,
                         verts=(connectivity, offsets),
                         point_data=point_data,
                         cell_data=cell_data,
                         field_data=fielddata,
                         encoding='ascii')

file.write_xml_file()
# --8<-- [end:write_points_data_ascii]

# --8<-- [start:write_points_data_binary]
# Write the file using the xml writer class
file = XMLPolyDataWriter('test_points_polydata_binary.vtp',
                         points=points,
                         verts=(connectivity, offsets),
                         point_data=point_data,
                         cell_data=cell_data,
                         field_data=fielddata,
                         encoding='binary')

file.write_xml_file()
# --8<-- [end:write_points_data_binary]

# --8<-- [start:write_points_data_appended_encoded]
# Write the file using the xml writer class
file = XMLPolyDataWriter('test_points_polydata_appended_encoded.vtp',
                         points=points,
                         verts=(connectivity, offsets),
                         point_data=point_data,
                         cell_data=cell_data,
                         field_data=fielddata,
                         encoding='appended')

file.write_xml_file()
# --8<-- [end:write_points_data_appended_encoded]

# --8<-- [start:write_points_data_appended_raw]
# Write the file using the xml writer class
file = XMLPolyDataWriter('test_points_polydata_appended_raw.vtp',
                         points=points,
                         verts=(connectivity, offsets),
                         point_data=point_data,
                         cell_data=cell_data,
                         field_data=fielddata,
                         encoding='appended',
                         appended_encoding='raw')

file.write_xml_file()
# --8<-- [end:write_points_data_appended_raw]

#%% write point dataset to vtkhdf
# --8<-- [start:write_points_vtkhdf]
from vtkio.writer.vtkhdf import VTKHDFPolyDataWriter

points_test = VTKHDFPolyDataWriter('test_points_polydata_vtkhdf', points,
                                   verts=(connectivity, offsets),
                                   point_data=point_data,
                                   cell_data=cell_data,
                                   field_data=fielddata)

points_test.write_vtkhdf_file()

# --8<-- [end:write_points_vtkhdf]


#%% write with helper function

# --8<-- [start:write_points_writer_api_xml]
from vtkio.writer import write_vtp

write_vtp('test_points_polydata_ascii',
          points=points, verts=(connectivity, offsets),
          point_data=point_data,
          cell_data=None, field_data=None,
          encoding='ascii')

write_vtp('test_points_polydata_binary', points=points,
          verts=(connectivity, offsets),
          point_data=point_data, cell_data=None, field_data=None,
          encoding='binary')

write_vtp('test_points_polydata_appended_encoded',
          points=points, verts=(connectivity, offsets),
          point_data=point_data, cell_data=None, field_data=None,
          encoding='appended')

write_vtp('test_points_polydata_appended_raw',
          points=points, verts=(connectivity, offsets),
          point_data=point_data, cell_data=None, field_data=None,
          encoding='appended', appended_encoding='raw')

# --8<-- [end:write_points_writer_api_xml]


# --8<-- [start:write_points_writer_api_vtkhdf]

write_vtp('polytest', points=points,
          verts=(connectivity, offsets),
          point_data=point_data, cell_data=None, field_data=None,
          file_format='vtkhdf')

# --8<-- [end:write_points_writer_api_vtkhdf]

#%% With High level wrapper
# --8<-- [start:write_points_helper]
from vtkio.simplified import points_to_poly

points_to_poly('polytest', points, data=point_data,
               fieldData=None, encoding='ascii')

points_to_poly('polytest_binary', points, data=point_data,
                 fieldData=None, encoding='binary')

points_to_poly('polytest_base64', points, data=point_data,
                 fieldData=None, encoding='appended')

# --8<-- [end:write_points_helper]

#%% test hdf5 polydata
plate_data = read_vtkxml_data('../TestData/vtp/plate_vectors.vtp')
map_data = read_vtkxml_data('../TestData/vtp/map.vtp')
poly_verts_data = read_vtkxml_data('../TestData/vtp/polytest.vtp')
lines_data = read_vtkxml_data('../TestData/vtp/ibm_with_data.vtp')
cow_data = read_vtkxml_data('../TestData/vtp/cow.vtp')

map_data_base_64 = read_vtkxml_data('map_base64_ref.vtp')

write_vtp('plate_vectors', points=plate_data.points,
          polys=(plate_data.polys.connectivity, plate_data.polys.offsets),
          point_data={"vectors": plate_data.point_data}, field_data=fielddata)

write_vtp('cow2', points=cow_data.points,
          polys=(cow_data.polys.connectivity, cow_data.polys.offsets),
          point_data=None)

write_vtp('map', points=map_data.points,
          lines=(map_data.lines.connectivity, map_data.lines.offsets),
          cell_data={"vectors": map_data.cell_data},
          field_data=fielddata, encoding='ascii')

write_vtp('map_base64', points=map_data.points,
          lines=(map_data.lines.connectivity, map_data.lines.offsets),
          cell_data={"vectors": map_data.cell_data},
          field_data=fielddata, encoding='binary')

write_vtp('map_appended', points=map_data.points,
          lines=(map_data.lines.connectivity, map_data.lines.offsets),
          cell_data={"vectors": map_data.cell_data},
          field_data=fielddata, encoding='appended')

write_vtp('polytest', points=poly_verts_data.points,
          verts=(poly_verts_data.verts.connectivity, poly_verts_data.verts.offsets),
          point_data={"vectors": poly_verts_data.point_data},
          field_data=fielddata)

write_vtp('ibm_with_data', points=lines_data.points,
          lines=(lines_data.lines.connectivity, lines_data.lines.offsets),
          point_data={"vectors": lines_data.point_data},
          field_data=fielddata)

write_vtp('map', points=map_data.points,
          lines=(map_data.lines.connectivity, map_data.lines.offsets),
          cell_data={"vectors": map_data.cell_data},
          field_data=fielddata, file_format='vtkhdf')

#%% test vtkhdf writer class


plate_test = VTKHDFPolyDataWriter('plate_vectors_hdf_new', plate_data.points,
                                  polys=(plate_data.polys.connectivity, plate_data.polys.offsets),
                                  point_data={"vectors": plate_data.point_data}, field_data=fielddata)

plate_test.write_vtkhdf_file()

#%% Create lines

# --8<-- [start:create_lines_dataset]

# Positions of points that define lines
npoints = 10
points = np.zeros((npoints, 3))
# points = np.random.random((npoints, 3))

# First line segments
points[0, :] = 0.0, 0.0, 0.0
points[1, :] = 1.0, 1.0, 0.0
points[2, :] = 1.0, 1.0, 0.0
points[3, :] = 2.0, 0.0, 0.0
points[4, :] = 2.0, 0.0, 0.0
points[5, :] = 3.0, 1.5, 0.0

# Second line segments
points[6, :] = 0.0, 0.0, 3.0
points[7, :] = 1.0, 1.0, 3.0
points[8, :] = 1.0, 1.0, 3.0
points[9, :] = 2.0, 0.0, 3.0

# Some point variables
pressure = np.random.rand(npoints)
temp = np.random.rand(npoints)
scales = np.random.rand(5)
point_scales = np.array([scales,scales]).T.flatten()

# some line variables (cell data)
vel = np.arange(5) + 1

point_data = {"temp": temp, "pressure": pressure, "point_scales": point_scales}
cell_data = {"velocity": vel, "cell_scales": scales}

# --8<-- [end:create_lines_dataset]


# --8<-- [start:write_lines_dataset]

# create connectivity and offsets for lines data
# each point is only connected to itself
connectivity = np.arange(npoints, dtype="int32")
num_lines = connectivity.size // 2
offsets = (np.arange(num_lines) + 1) * 2

# write data
write_vtp('test_lines_polydata_appended_encoded',
          points=points, lines=(connectivity, offsets),
          point_data=point_data,
          cell_data=cell_data,
          field_data=None,
          encoding='appended')

# --8<-- [end:write_lines_dataset]


# --8<-- [start:write_lines_dataset_hl]
from vtkio.simplified import lines_to_poly

lines_to_poly('line_test', points,
              point_data=point_data,
              cell_data=cell_data,
              fieldData=None, encoding='ascii')

lines_to_poly('line_test_binary', points, point_data=point_data,
                cell_data=cell_data, fieldData=None, encoding='binary')

lines_to_poly('line_test_base64', points, point_data=point_data,
                cell_data=cell_data, fieldData=None, encoding='appended')

# --8<-- [end:write_lines_dataset_hl]

#%% create lines More efficient method passing connected nodes list

# Positions of points that define lines
npoints = 7
points = np.zeros((npoints, 3))

# 6 line segments  each sharing the previous node
points[0, :] = 0.0, 0.0, 0.0
points[1, :] = 1.0, 1.0, 0.0
points[2, :] = 2.0, 0.0, 0.0
points[3, :] = 3.0, 1.5, 0.0
points[4, :] = 0.0, 0.0, 3.0
points[5, :] = 1.0, 1.0, 3.0
points[6, :] = 2.0, 0.0, 3.0

# define connectivity of the 6 lines
connectivity = np.array([[0, 1], [1, 2], [2, 3], [4, 5], [5, 6]])

# Some point variables
pressure = np.random.rand(npoints)
temp = np.random.rand(npoints)

# some line variables (cell data)
# 5 separate lines each with a different velocity
vel = np.arange(5) +1

pointData = {"temp": temp, "pressure": pressure},

lines_to_poly('line_dedup_test', points, connectivity=connectivity,
                point_data={"1_temp": temp, "2_pressure": pressure},
                cell_data={'velocity': vel}, fieldData=None, encoding='ascii')

lines_to_poly('line_dedup_test_binary', points, connectivity=connectivity,
                point_data={"1_temp": temp, "2_pressure": pressure},
                cell_data={'velocity': vel}, fieldData=None, encoding='binary')

lines_to_poly('line_dedup_test_base64', points, connectivity=connectivity,
                point_data={"1_temp": temp, "2_pressure": pressure},
                cell_data={'velocity': vel}, fieldData=None, encoding='appended')

#%% Create poly_lines

# --8<-- [start:write_polylines_dataset_hl]
from vtkio.simplified import polylines_to_poly

# Connectivity of the two polylines
pointsPerLine = np.zeros(2)
pointsPerLine[0] = 4
pointsPerLine[1] = 3

# some new polyline variables (cell data)
# there are now only two cells
vel = np.zeros(2)
vel[0] = 1.086
vel[1] = 5.0

polylines_to_poly('polyline_test', points, pointsPerLine,
                  point_data={"1_temp": temp, "2_pressure": pressure},
                  cell_data={'velocity': vel}, fieldData=None,
                  encoding='ascii')

polylines_to_poly('polyline_test_binary', points, pointsPerLine,
                  point_data={"1_temp": temp, "2_pressure": pressure},
                  cell_data={'velocity': vel}, fieldData=None,
                  encoding='binary')

polylines_to_poly('polyline_test_base64', points, pointsPerLine,
                  point_data={"1_temp": temp, "2_pressure": pressure},
                  cell_data={'velocity': vel}, fieldData=None,
                  encoding='appended')

# --8<-- [end:write_polylines_dataset_hl]

#%% test writing multiblock files

# --8<-- [start:write_poly_multiblock_xml]
from vtkio.writer.xml import xml_multiblock_writer

xml_multiblock_writer('new_vtk_multiblock_file', {
    'Base': {'files': ['edem_cube_base_t_0.vtp']},
    'Sides': {'files':['edem_cube_back_wall_t_0.vtp', 'edem_cube_left_wall_t_0.vtp',
              'edem_cube_front_wall_t_0.vtp', 'edem_cube_right_wall_t_0.vtp'],
              'names':['back', 'left', 'front', 'right']},
    'Loading': {'files':['edem_cube_loading_platen_t_0.vtp']}
    })

# --8<-- [end:write_poly_multiblock_xml]


# --8<-- [start:write_poly_multiblock_vtkhdf]
from vtkio.writer.vtkhdf import VTKHDFMultiBlockWriter

blocks = {'block1': plate_data, 'block2': map_data, 'block3': cow_data, 'block4': lines_data}
writer = VTKHDFMultiBlockWriter('hdf_multiblock_test', blocks)
writer.write_vtkhdf_file()

# --8<-- [end:write_poly_multiblock_vtkhdf]
