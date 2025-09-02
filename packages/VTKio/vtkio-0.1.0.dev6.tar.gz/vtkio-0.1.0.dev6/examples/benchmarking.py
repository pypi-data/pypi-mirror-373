"""
Simple Performance check against other packages for a rectilinear grid.

Compares vtkio and xml and vtkhdf writing performance.
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard Library
import time

import numpy as np
from pyevtk.hl import gridToVTK
from uvw import DataArray, RectilinearGrid

from vtkio import rectilinear_grid
from vtkio.writer import write_rectilinear_grid

# create points array
nx = 5*10**2
ny = 5*10**2
nz = 10**2
x = np.linspace(0, 1, nx)
y = np.linspace(0, 1, ny)
z = np.linspace(0, 1, nz)

xx, yy, zz = np.meshgrid(x, y, z, indexing='xy', sparse=True)

# create point data
r = np.sqrt(xx**2 + yy**2 + zz**2)

def write_pyevtk():
    gridToVTK('pyevtk', x, y, z, pointData={'': r})


tok = time.time()
write_pyevtk()
print("pyevtk:", time.time() - tok)


def write_uvw():
    f = RectilinearGrid('uvw.vtr', (x, y, z), compression=False)
    f.addPointData(DataArray(r, range(r.ndim), ''), vtk_format='append')
    f.write()


tik = time.time()
write_uvw()
print("uvw:", time.time() - tik)


tik = time.time()
rectilinear_grid('vtkio_binary', x, y, z, point_data={'scalars': r.flatten()}, encoding='binary')
print("vtkio - binary:", time.time() - tik)


tik = time.time()
rectilinear_grid('vtkio', x, y, z, point_data={'scalars': r.flatten()})
print("vtkio - appended:", time.time() - tik)


tik = time.time()
rectilinear_grid('vtkio_ascii', x, y, z, point_data={'scalars': r.flatten()}, encoding='ascii')
print("vtkio - ascii:", time.time() - tik)

# although this is a good comparison on write speeds, this format is not currently officially supported - there is no
# vtk reader implemented yet
tik = time.time()
write_rectilinear_grid('vtkio_hdf', x, y, z, point_data={'scalars': r.flatten()})
print("vtkio - vtkhdf:", time.time() - tik)
