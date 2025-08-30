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
from vtkio import unstructured_points
from vtkio.vtk_cell_types import (
    VTK_Hexahedron,
    VTK_Line,
    VTK_Pixel,
    VTK_Polygon,
    VTK_PolyLine,
    VTK_Quad,
    VTK_Tetra,
    VTK_Triangle,
    VTK_TriangleStrip,
    VTK_Vertex,
    VTK_Voxel,
)
from vtkio.writer import write_vtu
from vtkio.writer.vtkhdf import VTKHDFUnstructuredGridWriter

#%% Write vtu file
write_vtu('test_blank_vtu', nodes=None, cell_type=None, connectivity=None, offsets=None,
         point_data=None, cell_data=None, field_data=None, encoding='ascii')

#%% multiple cell type example

# --8<-- [start:create_multicell_data]
# set numpy seed value so that all arrays contain repeatable numbers
np.random.seed(77)

# Create a set of points in 3D space
points = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [0, 1, 0], [1, 1, 0],
                   [2, 1, 0], [0, 0, 1], [1, 0, 1], [2, 0, 1], [0, 1, 1],
                   [1, 1, 1], [2, 1, 1], [0, 1, 2], [1, 1, 2], [2, 1, 2],
                   [0, 1, 3], [1, 1, 3], [2, 1, 3], [0, 1, 4], [1, 1, 4],
                   [2, 1, 4], [0, 1, 5], [1, 1, 5], [2, 1, 5], [0, 1, 6],
                   [1, 1, 6], [2, 1, 6],
                   ])

num_points = len(points)
num_cells = 11

# data for writing for each point or cell is defined in a dict of dicts
# where the keys represent the DataArray type and the nested keys the
# DataArray name
cell_scalars = np.arange(num_cells) + 1
point_vectors = np.random.random([num_points, 3])

point_data = {"vectors": {"velocity": point_vectors},
              }

cell_data = {"scalars": {"temp": cell_scalars}
             }


# --8<-- [end:create_multicell_data]

# --8<-- [start:create_multicell_topology]

cell_types = [VTK_Hexahedron, VTK_Voxel, VTK_Tetra, VTK_Pixel, VTK_Polygon.set_num_points(6),
              VTK_TriangleStrip.set_num_triangles(1), VTK_Quad, VTK_Triangle,
              VTK_PolyLine.set_num_points(3), VTK_Line, VTK_Vertex]

# create cell topology
cell_type = []
num_cell_nodes = []
for cell in cell_types:
    cell_type.append(cell.type_id)
    num_cell_nodes.append(cell.num_points)

connectivity = [0, 1, 4, 3, 6, 7, 10, 9,
                1, 2, 4, 5, 7, 8, 10, 11,
                6, 10, 9, 12,
                11, 14, 10, 13,
                15, 16, 17, 14, 13, 12,
                18, 15, 19, 16, 20, 17,
                22, 23, 20, 19,
                21, 22, 18,
                22, 19, 18,
                26, 25,
                24]

offsets = np.cumsum(num_cell_nodes)

# --8<-- [end:create_multicell_topology]


# --8<-- [start:write_multicell_vtu]
# Write the unstructured grid to a vtu file with multiple cell types
from vtkio.writer.xml import XMLUnstructuredGridWriter

# Write the file using the xml writer class
file = XMLUnstructuredGridWriter('multi_cell_type_example',
                                 nodes=points,
                                 cell_type=cell_type,
                                 connectivity=connectivity,
                                 offsets=offsets,
                                 point_data=point_data,
                                 cell_data=cell_data,
                                 field_data=None,
                                 encoding='ascii')

file.write_xml_file()

# --8<-- [end:write_multicell_vtu]

# --8<-- [start:write_multicell_vtu_binary]

# Write the file using the xml writer class
file = XMLUnstructuredGridWriter('multi_cell_type_example',
                                 nodes=points,
                                 cell_type=cell_type,
                                 connectivity=connectivity,
                                 offsets=offsets,
                                 point_data=point_data,
                                 cell_data=cell_data,
                                 field_data=None,
                                 encoding='binary')

file.write_xml_file()

# --8<-- [end:write_multicell_vtu_binary]

# --8<-- [start:write_multicell_vtu_appended_encoded]
# Write the file using the xml writer class
file = XMLUnstructuredGridWriter('multi_cell_type_example',
                                 nodes=points,
                                 cell_type=cell_type,
                                 connectivity=connectivity,
                                 offsets=offsets,
                                 point_data=point_data,
                                 cell_data=cell_data,
                                 field_data=None,
                                 encoding='appended')

file.write_xml_file()

# --8<-- [end:write_multicell_vtu_appended_encoded]

# --8<-- [start:write_multicell_vtu_appended_raw]
# Write the file using the xml writer class
file = XMLUnstructuredGridWriter('multi_cell_type_example',
                                 nodes=points,
                                 cell_type=cell_type,
                                 connectivity=connectivity,
                                 offsets=offsets,
                                 point_data=point_data,
                                 cell_data=cell_data,
                                 field_data=None,
                                 encoding='appended',
                                 appended_encoding='raw')

file.write_xml_file()

# --8<-- [end:write_multicell_vtu_appended_raw]

# --8<-- [start:write_multicell_vtkhdf]
from vtkio.writer.vtkhdf import VTKHDFUnstructuredGridWriter

# Write the file using the xml writer class
file = VTKHDFUnstructuredGridWriter('multi_cell_type_example',
                                 nodes=points,
                                 cell_types=cell_type,
                                 connectivity=connectivity,
                                 offsets=offsets,
                                 point_data=point_data,
                                 cell_data=cell_data,
                                 field_data=None,
                                 additional_metadata=None)

file.write_vtkhdf_file()

# --8<-- [end:write_multicell_vtkhdf]

# --8<-- [start:write_multicell_write_vtu_api_xml]

# Write the unstructured grid to a vtu file
write_vtu('multi_cell_type_example_new', nodes=points,
          cell_type=cell_type, connectivity=connectivity, offsets=offsets,
          point_data=point_data,
          cell_data=cell_data,
          field_data=None,
          encoding='ascii')

# --8<-- [end:write_multicell_write_vtu_api_xml]

# --8<-- [start:write_points_writer_api_vtkhdf]

# Write the unstructured grid to a vtu file
write_vtu('multi_cell_type_example_new', nodes=points,
          cell_type=cell_type, connectivity=connectivity, offsets=offsets,
          point_data=point_data,
          cell_data=cell_data,
          field_data=None,
          file_format='vtkhdf')

# --8<-- [end:write_points_writer_api_vtkhdf]


#%% Unstructured points
# --8<-- [start:generate_unstructured_points]
# set numpy seed value so that all arrays contain repeatable numbers
np.random.seed(77)

# set number of points
npoints = 20

# generate dataset
random_sample = np.random.random(npoints)
temp = random_sample
multi_component2 = np.random.random((npoints, 2))
multi_component3 = np.random.random((npoints, 3))
multi_component4 = np.random.random((npoints, 4))
force = np.random.random((npoints, 3)) * 20
stress = np.random.random([npoints, 9]) * 1000
norms = np.random.random([npoints, 3])
norms /= np.linalg.norm(norms, axis=1)[:, np.newaxis]

# add to point data dictionary
point_data = {"scalars": {"temp": temp, "2-components": multi_component2,
                          "3-components": multi_component3, "4-components": multi_component4},
              "vectors": {"force": force},
              "tensors": {"stress": stress},
              "normals": {"normals": norms},
              }

fielddata = {'TimeValue': 0.122654987}

positions = np.random.random((npoints, 3))

# --8<-- [end:generate_unstructured_points]

# %% Set file path

# --8<-- [start:write_unstructured_points]

unstructured_points('test', positions, pointData=point_data, fieldData=fielddata, encoding='ascii')

unstructured_points('test_binary', positions, pointData=point_data, fieldData=fielddata, encoding='binary')

unstructured_points('test_appended', positions, pointData=point_data, fieldData=fielddata, encoding='appended')

# --8<-- [end:write_unstructured_points]

#%% Unstructured triangular mesh
# --8<-- [end:generate_unstructured_triangular_mesh_topology]

import pygmsh

with pygmsh.geo.Geometry() as geom:
    poly = geom.add_polygon(
        [
            [0.0, 0.25, 0.0],
            [0.0, 1.25, 0.0],
            [0.0, 1.25, 1.0],
        ],
        mesh_size=0.25,
    )
    geom.revolve(poly, [0.0, 0.0, 1.0], [0.0, 0.0, 0.0], 0.8 * np.pi)
    mesh = geom.generate_mesh()

# Calculate vtk information
connectivity = []
size = []
for _key, data in mesh.cells_dict.items():
    connectivity.append(data.flatten())
    size.append(data.shape[0])
connectivity = np.hstack(connectivity)

# get the cell type
cell_type = [np.tile(VTK_Line.type_id, size[0]), np.tile(VTK_Triangle.type_id, size[1]),
                   np.tile(VTK_Tetra.type_id, size[2]), np.tile(VTK_Vertex.type_id, size[3])]
cell_type = np.hstack(cell_type)

# get offsets from number of nodes
num_cells_nodes = [np.tile(VTK_Line.num_points, size[0]), np.tile(VTK_Triangle.num_points, size[1]),
                   np.tile(VTK_Tetra.num_points, size[2]), np.tile(VTK_Vertex.num_points, size[3])]
num_cells_nodes = np.hstack(num_cells_nodes)
offsets = np.cumsum(num_cells_nodes)
# --8<-- [end:generate_unstructured_triangular_mesh_topology]

# --8<-- [start:generate_unstructured_triangular_mesh_data]

# create variables
npoints = len(mesh.points)

random_sample = np.random.random(npoints)
temp = random_sample
multi_component2 = np.random.random((npoints, 2))
multi_component3 = np.random.random((npoints, 3))
multi_component4 = np.random.random((npoints, 4))
force = np.random.random((npoints, 3)) * 20
stress = np.random.random([npoints, 9]) * 1000
norms = np.random.random([npoints, 3])
norms /= np.linalg.norm(norms, axis=1)[:, np.newaxis]


point_data = {"scalars": {"temp": temp, "2-components": multi_component2,
                          "3-components": multi_component3, "4-components": multi_component4},
              "vectors": {"force": force},
              "tensors": {"stress": stress},
              "normals": {"normals": norms},
              }
# Note that writing "normals" to the xml file will affect the default rendering in paraview as it will turn normal
# data on

cell_scalars = np.arange(len(num_cells_nodes))
cell_data = {"scalars": {"temp": cell_scalars}
             }

fielddata = {'TimeValue': 0.122654987,
             'TMSTEP': np.arange(35),
             'Energy': np.random.random(35)}

# --8<-- [start:generate_unstructured_triangular_mesh_data]

# --8<-- [start:write_unstructured_triangular_mesh]

write_vtu('revolution_triangular_mesh_test_new', nodes=mesh.points,
          cell_type=cell_type, connectivity=connectivity, offsets=offsets,
         point_data=point_data, cell_data=cell_data, field_data=fielddata, encoding='ascii')

# --8<-- [end:write_unstructured_triangular_mesh]

#%% write vtkhdf file
# --8<-- [start:write_points_writer_api_vtkhdf_additional_metadata]

testdata = {
    "group1": {
        "dataset1": np.array([1, 2, 3, 4, 5]),
        "dataset2": np.random.random((3, 3)),
        "scalar": 42,
        "attrs": {
            "description": "Test data",
            "time": 1.456436,
            "timestep_index": 1,
            "simulation_timestep": 1e-6,
            "domain": np.array([0, 0, 0, 1, 1, 1])
        }
    },
    "group2": {
        "subgroup1": {
            "dataset3": np.zeros((10, 10)),
            "text": "Hello HDF5"
        },
        "flags": {
            "active": True,
            "mode": "standard"
        }
    },
    "additional_metadata": {
        "author": "User",
        "date": "2023-05-15"
    }
}

# Write the unstructured grid to a vtkhdf file
test = VTKHDFUnstructuredGridWriter('revolution_triangular_mesh_test_new_hdf5', nodes=mesh.points,
                                    cell_types=cell_type, connectivity=connectivity, offsets=offsets,
                                    point_data=point_data, cell_data=cell_data, field_data=fielddata,
                                    additional_metadata=testdata)

test.write_vtkhdf_file()

# --8<-- [end:write_points_writer_api_vtkhdf_additional_metadata]

#%% write vtkhdf file with additional metadata
from vtkio.reader import read_vtkxml_data

cube_tensors_data = read_vtkxml_data('../TestData/vtu/cube_tensors.vtu')
disc_quads_data = read_vtkxml_data('../TestData/vtu/disc_quads.vtu')
fire_data = read_vtkxml_data('../TestData/vtu/fire.vtu')
single_plane_data = read_vtkxml_data('../TestData/vtu/single_plane.vtu')
multiple_tetra_data = read_vtkxml_data('../TestData/vtu/multiple_tetra.vtu')

# --8<-- [start:write_points_writer_api_vtkhdf_additional_metadata]
from vtkio.writer.vtkhdf import VTKHDFMultiBlockWriter

blocks = {'block1': cube_tensors_data, 'block2': disc_quads_data, 'block3': fire_data,
          'block4': single_plane_data,'block5': multiple_tetra_data,}

writer = VTKHDFMultiBlockWriter('hdf_multiblock_test_unstructured', blocks)
writer.write_vtkhdf_file()

# --8<-- [end:write_points_writer_api_vtkhdf_additional_metadata]
