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
import contextlib

# Imports
import numpy as np

# Local Sources
from vtkio import structured_grid
from vtkio.writer import write_vts


#%% Set some constants


#%% Structured
print("Running structured...")

# write blank vts file
with contextlib.suppress(TypeError):
    write_vts('test_blank_vts_new', np.array([]), whole_extent=[0, 1, 0, 1, 0, 1],
         piece_extent=[0, 1, 0, 1, 0, 1])

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
nx, ny, nz = num_cells
spacing = (max_extent - origin) / num_cells

# Coordinates
x, x_step = np.linspace(origin[0], max_extent[0], num_cells[0]+1,
                        retstep=True, dtype='float64')
y, y_step = np.linspace(origin[1], max_extent[1], num_cells[1]+1,
                        retstep=True, dtype='float64')
z, z_step = np.linspace(origin[2], max_extent[2], num_cells[2]+1,
                        retstep=True, dtype='float64')

xx, yy, zz = np.array(np.meshgrid(x, y, z))
points = np.vstack((xx.ravel(), yy.ravel(), zz.ravel())).T

#sort points in correct order (x, then, y, then z)
sort_index_F = np.lexsort((points[:, 0], points[:, 1], points[:, 2]))
sorted_points = points[sort_index_F]

# distort the grid with some random noise at each node
x_noise = (np.random.random(npoints) - 0.5) * x_step*0.35
y_noise = (np.random.random(npoints) - 0.5) * y_step*0.35
z_noise = (np.random.random(npoints) - 0.5) * z_step*0.25

# update positions with noise
sorted_points[:, 0] += x_noise
sorted_points[:, 1] += y_noise
sorted_points[:, 2] += z_noise

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

point_data = {"scalars": {"temp": temp,
                          "2-components": multi_component2,
                          "3-components": multi_component3,
                          "4-components": multi_component4},
              "vectors": {"force": force},
              "tensors": {"stress": stress},
              "normals": {"normals": norms},
}

pressure = np.arange(ncells)
cell_data = {"scalars": {"pressure": pressure}}

field_data = {'TimeValue': 0.122654987}

# --8<-- [end:create_grid_data]

# --8<-- [start:write_structuredgrid_data_writer_ascii]
from vtkio.writer.xml import XMLStructuredGridWriter


file = XMLStructuredGridWriter('test_distorted_grid',
                                sorted_points,
                                whole_extent,
                                point_data=point_data,
                                cell_data=cell_data,
                                field_data=field_data,
                                encoding='ascii')

file.write_xml_file()

# --8<-- [end:write_structuredgrid_data_writer_ascii]

# --8<-- [start:write_structuredgrid_data_writer_binary]
file = XMLStructuredGridWriter('test_distorted_grid',
                                sorted_points,
                                whole_extent,
                                point_data=point_data,
                                cell_data=cell_data,
                                field_data=field_data,
                                encoding='ascii')

file.write_xml_file()

# --8<-- [end:write_structuredgrid_data_writer_binary]

# --8<-- [start:write_structuredgrid_data_writer_appended_encoded]
file = XMLStructuredGridWriter('test_distorted_grid',
                                sorted_points,
                                whole_extent,
                                point_data=point_data,
                                cell_data=cell_data,
                                field_data=field_data,
                                encoding='appended')

file.write_xml_file()

# --8<-- [end:write_structuredgrid_data_writer_appended_encoded]

# --8<-- [start:write_structuredgrid_data_writer_appended_raw]
file = XMLStructuredGridWriter('test_distorted_grid',
                                sorted_points,
                                whole_extent,
                                point_data=point_data,
                                cell_data=cell_data,
                                field_data=field_data,
                                encoding='appended',
                                appended_encoding='raw')

file.write_xml_file()

# --8<-- [end:write_structuredgrid_data_writer_appended_raw]


# --8<-- [start:write_StructuredGrid_writer_vtkhdf]
from vtkio.writer.vtkhdf import VTKHDFStructuredGridWriter

file = VTKHDFStructuredGridWriter('test_distorted_grid',
                                    sorted_points,
                                    num_cells=num_cells,
                                    point_data=point_data,
                                    cell_data=cell_data,
                                    field_data=field_data
                                  )

file.write_vtkhdf_file()

# --8<-- [end:write_StructuredGrid_writer_vtkhdf]

# --8<-- [start:write_structuredgrid_data_writer_api]
from vtkio.writer import write_vts

write_vts('distorted_grid_api', sorted_points,
          num_cells=num_cells,
          point_data=point_data,
          cell_data=cell_data,
          field_data=field_data,
          encoding='ascii')


write_vts('distorted_grid_binary_api', sorted_points,
          num_cells=num_cells,
          point_data=point_data,
          cell_data=cell_data,
          field_data=field_data,
          encoding='binary')

write_vts('distorted_grid_appended_api',
          sorted_points,
          num_cells=num_cells,
          point_data=point_data,
          cell_data=cell_data,
          field_data=field_data,
          encoding='appended')


# --8<-- [end:write_structuredgrid_data_writer_api]


# --8<-- [start:write_structuredgrid_data_writer_api_vtkhdf]

write_vts('distorted_grid_api',
          sorted_points, num_cells=num_cells,
          point_data=point_data,
          cell_data=cell_data,
          field_data=field_data,
          file_format='vtkhdf')

# --8<-- [end:write_structuredgrid_data_writer_api_vtkhdf]


structured_grid('distorted_grid', sorted_points, num_cells=num_cells,
                point_data=point_data, cell_data=cell_data, field_data=field_data, encoding='ascii')



structured_grid('distorted_grid_binary', sorted_points, num_cells=num_cells,
                point_data=point_data, cell_data=cell_data, field_data=field_data, encoding='binary')

structured_grid('distorted_grid_appended', sorted_points, num_cells=num_cells,
                point_data=point_data, cell_data=cell_data, field_data=field_data, encoding='appended')



#%% Cylindrical mesh

# --8<-- [start:write_structuredgrid_data_cylindrical_mesh_functions]

def generate_circular_points(centre, radius, num_points=20, range=360):
    """
    Generate points on a circle in 3D space.

    The circle is defined by its centre and radius, and the points
    are generated equally spaced around the circle. The angle has
    a range of 0 to 360 degrees.

    Parameters
    ----------
    centre: array-like
        Centre of the circle, given as a 3-element array-like
        object (x, y, z).
    radius: float
        Radius of the circle.
    num_points: int
        Number of points to generate on the circle, default is 20.
    range: int
        Number of degrees to cover in the circle, default is 360 degrees.

    Returns
    -------
    np.ndarray
        An array of shape (num_points, 3) containing the (x, y, z)
        coordinates of the points on the circle.

    """

    theta = np.linspace(0, np.deg2rad(range), num_points)

    # Convert angles to Cartesian coordinates (x, y, z)
    x = radius * np.cos(theta) + centre[0]
    y = radius * np.sin(theta) + centre[1]
    z = np.ones(num_points) * centre[2]

    return np.vstack([x, y, z]).T

def generate_cylindrical_grid(centre, height, inner_radius, radius,
                              nx=6, ny=3, nz=3, radial_range=360):
    """
    Generate a structured grid in cylindrical coordinates.

    This function creates a grid of points in a cylindrical segment
    defined by the given centre, height, inner radius, and outer radius.
    The grid is structured such that it has `nx` points along the radial
    direction, `ny` points along the circumferential direction, and `nz`
    points along the height of the cylinder.

    The points are generated in a way that they are evenly distributed in the
    radial direction from the inner radius to the outer radius, and in the
    circumferential direction they are evenly spaced around the cylinder.

    Parameters
    ----------
    centre: array-like
        Centre of the cylindrical segment, given as a 3-element array-like
        object (x, y, z).
    height: float
        Height of the cylindrical segment.
    inner_radius: float
        Inner radius of the cylindrical segment.
    radius: float
        Outer radius of the cylindrical segment.
    nx: int
        Number of points along the radial direction. Default is 6.
    ny: int
        Number of points along the circumferential direction. Default is 3.
    nz: int
        Number of points along the height of the cylinder. Default is 3.
    radial_range: int
        The range of the circumferential angle in degrees. Default is
        360 degrees.

    Returns
    -------

    """
    points = []

    # get z coordinates
    z_coords = np.linspace(centre[2], height, nz)

    for h in z_coords:
        row_centre = np.array([centre[0], centre[1], h])
        x = np.linspace(inner_radius, radius, nx)
        for r in x:
            points.append(generate_circular_points(row_centre, r,
                                                   num_points=ny,
                                                   range=radial_range))

    # create array
    points = np.vstack(points)

    # sort points
    indxs = np.arange(nx * ny).reshape(nx, -1).T.flatten()
    all_indx = (indxs * np.ones(nz)[:, None] +
                (np.arange(nz) * (nx * ny))[:, None]).flatten().astype(int)
    points = points[all_indx, :]

    return points
# --8<-- [end:write_structuredgrid_data_cylindrical_mesh_functions]

# --8<-- [start:write_structuredgrid_data_cylindrical_mesh_generation]

# generate cylindrical grid
centre = np.array([0.0, 0.0, 0.0])
radius = 2
inner_radius = 0.4
height = 1
num_points = np.array((10, 15, 5))
num_cells = num_points - 1

nx, ny, nz = num_points

points = generate_cylindrical_grid(centre, height, inner_radius, radius,
                                   nx, ny, nz, radial_range=60)
# --8<-- [end:write_structuredgrid_data_cylindrical_mesh_generation]

# --8<-- [start:write_structuredgrid_data_cylindrical_mesh_data]

# Create Variables
npoints = np.prod(num_points)
ncells = np.prod(num_points-1)

random_sample = np.random.random(npoints)
temp = random_sample
multi_component2 = np.random.random((npoints, 2))
multi_component3 = np.random.random((npoints, 3))
multi_component4 = np.random.random((npoints, 4))
force = np.random.random((npoints, 3)) * 20
stress = np.random.random([npoints, 9]) * 1000
norms = np.random.random([npoints, 3])
norms /= np.linalg.norm(norms, axis=1)[:, np.newaxis]

point_data = {"scalars": {"temp": temp,
                          "2-components": multi_component2,
                          "3-components": multi_component3,
                          "4-components": multi_component4},
              "vectors": {"force": force},
              "tensors": {"stress": stress},
              "normals": {"normals": norms},
}

pressure = np.arange(ncells)
cell_data = {"scalars": {"pressure": pressure}}

# --8<-- [end:write_structuredgrid_data_cylindrical_mesh_data]

# --8<-- [start:write_structuredgrid_data_cylindrical_mesh_data_api]
write_vts('cylinder_segment', points, num_cells=num_cells,
          point_data=point_data,
          cell_data=cell_data,
          field_data=None,
          encoding='ascii')

write_vts('cylinder_segment_binary', points, num_cells=num_cells,
          point_data=point_data,
          cell_data=cell_data,
          field_data=None,
          encoding='binary')

write_vts('cylinder_segment_appended', points, num_cells=num_cells,
          point_data=point_data,
          cell_data=cell_data,
          field_data=None,
          encoding='appended')


# --8<-- [end:write_structuredgrid_data_cylindrical_mesh_data_api]


# --8<-- [start:write_structuredgrid_data_cylindrical_mesh_data_hls]

# write data
structured_grid('cylinder_segment', points, num_cells=num_cells,
                point_data=point_data,
                cell_data=cell_data,
                field_data=None,
                encoding='ascii')


structured_grid('cylinder_segment_binary', points, num_cells=num_cells,
                point_data=point_data,
                cell_data=cell_data,
                field_data=None,
                encoding='binary')


structured_grid('cylinder_segment_appended', points, num_cells=num_cells,
                point_data=point_data,
                cell_data=cell_data,
                field_data=None, encoding='appended')

# --8<-- [end:write_structuredgrid_data_cylindrical_mesh_data_hls]



#%% write VTKHDF data
whole_extent = np.array([np.zeros(3), num_cells]).T.flatten()

test = VTKHDFStructuredGridWriter('cylinder_segment_new_hdf5', points, num_cells,
                      point_data=point_data, cell_data=cell_data, field_data=None)

test.write_vtkhdf_file()

