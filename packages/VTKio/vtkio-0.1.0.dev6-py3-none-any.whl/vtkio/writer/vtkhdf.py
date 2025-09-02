#!/usr/bin/env python
"""
VTKHDF Writer Module.

Includes all functions for writing VTKHDF files, including image data, poly data,
unstructured grid, structured grid, and rectilinear grid. Also includes functions
for writing additional metadata and creating multiblock datasets.

Note: This module writes structured grids and rectilinear grids in a VTKHDF format
although the definition is not yet formally included in the VTKHDF specification.

"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard library
from abc import abstractmethod
from pathlib import Path

# Imports
import h5py
import numpy as np

# Local imports
from .base_writer import (VTKWriterBase, StructuredGridMixin, ImageDataMixin,
                          RectilinearGridMixin, UnstructuredGridMixin, PolyDataMixin)

# Global metadata
fType = 'f'
idType = 'i8'
charType = 'uint8'

__all__ = [
    'VTKHDFMultiBlockWriter',
    'VTKHDFImageDataWriter',
    'VTKHDFUnstructuredGridWriter',
    'VTKHDFPolyDataWriter',
    'VTKHDFStructuredGridWriter',
    'VTKHDFRectilinearGridWriter'
]


class VTKHDFWriterBase(VTKWriterBase):
    """
    Base class for writing VTKHDF files.

    This class provides the basic structure and methods for writing VTKHDF files,
    including methods for writing metadata, topology, and data arrays. It is intended
    to be subclassed for specific VTKHDF dataset types such as ImageData, PolyData,
    UnstructuredGrid, and StructuredGrid.

    Parameters
    ----------
    filename : str
        The name of the file to write the VTKHDF dataset to. Should end with '.vtkhdf'.
    version : tuple, optional
        The version of the VTKHDF format to use. Default is (2, 2).
    additional_metadata : dict, optional
        Additional metadata to be written to the VTKHDF file. This can include any additional information
        that should be stored in the file, such as attributes or custom data.

    Attributes
    ----------
    field_data : dict
        A dictionary containing field data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    point_data : dict
        A dictionary containing point data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    cell_data : dict
        A dictionary containing cell data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    root : h5py.Group
        The root group of the HDF5 file where the VTKHDF dataset will be written.
    path : str
        The name of the file to write the VTKHDF dataset to, including the '.vtkhdf' extension.
    version : tuple 
        The version of the VTKHDF format being used.
    npoints : int
        The number of points in the dataset, calculated from the extents for structured grids.
    ncells : int
        The number of cells in the dataset, calculated from the extents for structured grids.
    nverts : int
        The number of vertices in the dataset, to be calculated from the data.
    nlines : int
        The number of lines in the dataset, to be calculated from the data.
    nstrips : int
        The number of strips in the dataset, to be calculated from the data.
    npolys : int
        The number of polygons in the dataset, to be calculated from the data.
    additional_metadata : dict
        Additional metadata to be written to the VTKHDF file. This can include any additional information
        that should be stored in the file, such as attributes or custom data.
    
    """

    supported_versions = [(2, 2), (2, 3), (2, 4)]
    extension = '.vtkhdf'

    def __init__(self, filename, version=(2, 2), additional_metadata=None, **kwargs):
        """Initialize VTKHDF writer with HDF5-specific settings."""
        super().__init__(filename, **kwargs)
        self.path = self.path.with_suffix(self.extension)

        if version not in self.supported_versions:
            raise ValueError(f"Unsupported VTKHDF version {version}. "
                             f"Supported versions are {self.supported_versions}.")
        self.version = version
        self.additional_metadata = additional_metadata
        self.hdf5_root = None

    def write_file(self):
        """Main entry point for writing VTKHDF files."""
        self.write_vtkhdf_file()

    def write_vtkhdf_file(self):
        """Write the VTKHDF dataset to file."""
        with h5py.File(self.path, 'w') as f:
            self.hdf5_root = f.create_group('VTKHDF')
            self._create_data_groups()
            self.write_topology()
            self._write_data_arrays()
            self.write_additional_metadata(self.additional_metadata)

    def write_vtkhdf_multiblock_data(self, root, block_name):
        """Write as part of a multiblock dataset."""
        self.hdf5_root = root.create_group(block_name, track_order=True)
        self._create_data_groups()
        self.write_topology()
        self._write_data_arrays()

        # Add to assembly
        assembly_blk = root['Assembly'].create_group(block_name, track_order=True)
        assembly_blk[block_name] = h5py.SoftLink(f'/VTKHDF/{block_name}')

    def _create_data_groups(self):
        """Create standard VTKHDF data groups."""
        self.CellData_Group = self.hdf5_root.create_group("CellData")
        self.PointData_Group = self.hdf5_root.create_group("PointData")
        self.FieldData_Group = self.hdf5_root.create_group("FieldData")

    def _write_data_arrays(self):
        """Write data arrays using appropriate method based on dataset type."""
        dataset_type = self.hdf5_root.attrs['Type'].decode('utf8')
        if dataset_type == 'ImageData':
            self._write_structured_data_arrays()
        else:
            self._write_unstructured_data_arrays()

    def _write_structured_data_arrays(self):
        """Write data arrays for structured grids with proper reshaping."""
        if self.cell_data is not None:
            for name, data in self.cell_data.items():
                self._add_structured_data_to_group(self.CellData_Group, name, data, self.num_cells)

        if self.point_data is not None:
            for name, data in self.point_data.items():
                self._add_structured_data_to_group(self.PointData_Group, name, data, self.num_points)

        self._write_field_data()

    def _write_unstructured_data_arrays(self):
        """Write data arrays for unstructured grids."""
        if self.cell_data is not None:
            for name, data in self.cell_data.items():
                self._add_unstructured_data_to_group(self.CellData_Group, name, data)

        if self.point_data is not None:
            for name, data in self.point_data.items():
                self._add_unstructured_data_to_group(self.PointData_Group, name, data)

        self._write_field_data()

    def _write_field_data(self):
        """Write field data arrays."""
        if self.field_data is not None:
            for name, darray in self.field_data.items():
                if isinstance(darray, np.ndarray):
                    self.FieldData_Group.create_dataset(name, data=darray)
                else:
                    self.FieldData_Group.create_dataset(name, data=np.array([darray]))

    def _add_structured_data_to_group(self, group, name, data, data_shape):
        """Add structured data with proper reshaping."""
        if isinstance(data, dict):
            for darray_name, darray in data.items():
                self._add_single_structured_array(group, darray_name, darray, data_shape)
        else:
            self._add_single_structured_array(group, name, data, data_shape)

    def _add_single_structured_array(self, group, name, darray, data_shape):
        """Add a single structured data array with reshaping."""
        try:
            n_comp = darray.shape[1] if darray.ndim > 1 else 1
        except IndexError:
            n_comp = 1
        # Reshape with reversed dimensions for VTK Fortran ordering
        group.create_dataset(name, data=darray.reshape([*data_shape[::-1], n_comp]))

    def _add_unstructured_data_to_group(self, group, name, data):
        """Add unstructured data without reshaping."""
        if isinstance(data, dict):
            for darray_name, darray in data.items():
                group.create_dataset(darray_name, data=darray)
        else:
            group.create_dataset(name, data=data)

    def write_additional_metadata(self, dictionary, group_path='/VTKHDF'):
        """
        Recursively write a nested dictionary to an HDF5 file group.

        Parameters
        ----------
        dictionary : dict
            The dictionary to write to the HDF5 file. It can contain nested dictionaries, lists, numpy arrays,
            or simple scalar values (int, float, str, bool).
        group_path : str, optional
            The path within the HDF5 file where the dictionary should be written.
            Default is '/VTKHDF'.
        """
        if dictionary is None:
            return

        if group_path == '/VTKHDF':
            group_path = 'additional_data'
            current_group = self.hdf5_root.create_group(group_path)
        else:
            try:
                current_group = self.hdf5_root[group_path]
            except KeyError:
                current_group = self.hdf5_root.create_group(group_path)

        self._write_metadata_recursive(dictionary, current_group, group_path)

    def _write_metadata_recursive(self, dictionary, current_group, group_path):
        """Recursively write metadata dictionary."""
        for key, value in dictionary.items():
            key = str(key)

            if isinstance(value, dict):
                if key == 'attrs':
                    # Handle attributes specially
                    for attr_key, attr_value in value.items():
                        current_group.attrs[attr_key] = attr_value
                else:
                    # Create new group for nested dictionaries
                    new_group_path = f"{group_path}/{key}"
                    self.write_additional_metadata(value, new_group_path)

            elif isinstance(value, (np.ndarray, list, tuple)):
                if not isinstance(value, np.ndarray):
                    value = np.array(value)
                current_group.create_dataset(key, data=value)

            elif isinstance(value, (int, float, str, bool, np.number)):
                current_group.attrs[key] = value

            else:
                # Fallback for other types
                try:
                    current_group.attrs[key] = str(value)
                except:
                    try:
                        current_group.create_dataset(key, data=np.array(value))
                    except:
                        print(f"Warning: Could not store value for key {key} of type {type(value)}")

    @abstractmethod
    def write_topology(self):
        """Write dataset topology. Must be implemented by subclasses."""
        pass


# Concrete writer classes using mixins
class VTKHDFImageDataWriter(ImageDataMixin, VTKHDFWriterBase):
    """VTKHDF writer for ImageData using mixin pattern."""

    def __init__(self, filename, whole_extent, origin, spacing, direction=None,
                 version=(2, 2), multiblock_index=None, **kwargs):
        super().__init__(
            filename=filename,
            whole_extent=whole_extent,
            origin=origin,
            spacing=spacing,
            direction=direction or np.eye(3).flatten(),
            version=version,
            **kwargs
        )
        self.multiblock_index = multiblock_index
        self.check_data_consistency()

    def write_topology(self):
        """Write ImageData topology to HDF5."""
        if self.multiblock_index is not None:
            self.hdf5_root.attrs.create('Index', self.multiblock_index, dtype=idType)

        self.hdf5_root.attrs['Version'] = self.version
        ascii_type = 'ImageData'.encode('ascii')
        self.hdf5_root.attrs.create('Type', ascii_type,
                                    dtype=h5py.string_dtype('ascii', len(ascii_type)))
        self.hdf5_root.attrs.create('WholeExtent', self.whole_extent, dtype=idType)
        self.hdf5_root.attrs.create('Origin', self.origin, dtype=fType)
        self.hdf5_root.attrs.create('Spacing', self.grid_spacing, dtype=fType)
        self.hdf5_root.attrs.create('Direction', self.direction, dtype=fType)


class VTKHDFUnstructuredGridWriter(UnstructuredGridMixin, VTKHDFWriterBase):
    """VTKHDF writer for UnstructuredGrid using mixin pattern."""

    def __init__(self, filename, points, cell_types, connectivity, offsets,
                 version=(2, 2), multiblock_index=None, **kwargs):
        super().__init__(
            filename=filename,
            points=points,
            cell_types=cell_types,
            connectivity=connectivity,
            offsets=offsets,
            version=version,
            **kwargs
        )
        self.multiblock_index = multiblock_index
        self.check_data_consistency()

    def write_topology(self):
        """Write UnstructuredGrid topology to HDF5."""
        if self.multiblock_index is not None:
            self.hdf5_root.attrs.create('Index', self.multiblock_index, dtype=idType)

        self.hdf5_root.attrs['Version'] = self.version
        ascii_type = 'UnstructuredGrid'.encode('ascii')
        self.hdf5_root.attrs.create('Type', ascii_type,
                                    dtype=h5py.string_dtype('ascii', len(ascii_type)))

        self.hdf5_root.create_dataset('Points', data=self.points, maxshape=(None, 3), dtype=fType)
        self.hdf5_root.create_dataset('Connectivity', data=self.connectivity, maxshape=(None,), dtype=idType)
        self.hdf5_root.create_dataset('Offsets', data=self.offsets, maxshape=(None,), dtype=idType)
        self.hdf5_root.create_dataset('Types', data=self.cell_types, maxshape=(None,), dtype=charType)
        self.hdf5_root.create_dataset('NumberOfPoints', data=np.array([len(self.points)]), dtype=idType)
        self.hdf5_root.create_dataset('NumberOfConnectivityIds', data=np.array([len(self.connectivity)]), dtype=idType)
        self.hdf5_root.create_dataset('NumberOfCells', data=np.array([len(self.cell_types)]), dtype=idType)


class VTKHDFPolyDataWriter(PolyDataMixin, VTKHDFWriterBase):
    """VTKHDF writer for PolyData using mixin pattern."""

    def __init__(self, filename, points, verts=None, lines=None, polys=None, strips=None,
                 version=(2, 2), multiblock_index=None, **kwargs):
        super().__init__(
            filename=filename,
            points=points,
            verts=verts,
            lines=lines,
            strips=strips,
            polys=polys,
            version=version,
            **kwargs
        )
        self.multiblock_index = multiblock_index
        self.check_data_consistency()

    def write_topology(self):
        """Write PolyData topology to HDF5."""
        if self.multiblock_index is not None:
            self.hdf5_root.attrs.create('Index', self.multiblock_index, dtype=idType)

        self.hdf5_root.attrs['Version'] = self.version
        ascii_type = 'PolyData'.encode('ascii')
        self.hdf5_root.attrs.create('Type', ascii_type,
                                    dtype=h5py.string_dtype('ascii', len(ascii_type)))
        self.hdf5_root.create_dataset('Points', data=self.points, maxshape=(None, 3), dtype=fType)
        self.hdf5_root.create_dataset('NumberOfPoints', data=np.array([len(self.points)]), dtype=idType)

        # Write topology for each primitive type
        for name, topo in zip(['Vertices', 'Lines', 'Polygons', 'Strips'],
                              [self.verts, self.lines, self.polys, self.strips]):
            group = self.hdf5_root.create_group(name)
            if topo is not None:
                if hasattr(topo, 'connectivity'):  # PolyDataTopology object
                    connectivity = topo.connectivity
                    offsets = topo.offsets
                else:
                    connectivity, offsets = topo

                if len(offsets) > 0 and offsets[0] != 0:
                    offsets = np.hstack([0, offsets])

                group.create_dataset('Connectivity', data=connectivity, maxshape=(None,), dtype=idType)
                group.create_dataset('Offsets', data=offsets, maxshape=(None,), dtype=idType)
                group.create_dataset('NumberOfConnectivityIds', data=np.array([len(connectivity)]), dtype=idType)
                group.create_dataset('NumberOfCells', data=np.array([len(offsets) - 1]), dtype=idType)
            else:
                # Create empty datasets for missing topology
                group.create_dataset('NumberOfConnectivityIds', data=np.array([0]), dtype=idType)
                group.create_dataset('NumberOfCells', data=np.array([0]), dtype=idType)
                group.create_dataset('Offsets', data=np.array([0]), maxshape=(None,), dtype=idType)
                group.create_dataset('Connectivity', (0,), maxshape=(None,), dtype=idType)


class VTKHDFStructuredGridWriter(StructuredGridMixin, VTKHDFWriterBase):
    """VTKHDF writer for StructuredGrid using mixin pattern."""

    def __init__(self, filename, points, whole_extent, piece_extent=None,
                 version=(2, 2), multiblock_index=None, **kwargs):
        # Validate points first
        points = self.validator.validate_points_array(points) if hasattr(self, 'validator') else np.asarray(points)

        super().__init__(
            filename=filename,
            whole_extent=whole_extent,
            piece_extent=piece_extent,
            version=version,
            **kwargs
        )

        self.points = points
        self.npoints = len(self.points)
        self.multiblock_index = multiblock_index

        # Validate consistency
        expected_npoints = np.prod(self.num_cells + 1)
        if self.points.shape[0] != expected_npoints:
            raise ValueError(
                f"Number of points ({self.points.shape[0]}) doesn't match extent. "
                f"Expected {expected_npoints} points for extent {self.piece_extent}"
            )

        self.check_data_consistency()

    def write_topology(self):
        """Write StructuredGrid topology to HDF5."""
        if self.multiblock_index is not None:
            self.hdf5_root.attrs.create('Index', self.multiblock_index, dtype=idType)

        self.hdf5_root.attrs['Version'] = self.version
        ascii_type = 'StructuredGrid'.encode('ascii')
        self.hdf5_root.attrs.create('Type', ascii_type,
                                    dtype=h5py.string_dtype('ascii', len(ascii_type)))
        self.hdf5_root.create_dataset('Points', data=self.points, maxshape=(None, 3), dtype=fType)
        self.hdf5_root.create_dataset('NumberOfPoints', data=np.array([self.npoints]), dtype=idType)
        self.hdf5_root.attrs.create('WholeExtent', self.whole_extent, dtype=fType)
        self.hdf5_root.attrs.create('PieceExtent', self.piece_extent, dtype=fType)


class VTKHDFRectilinearGridWriter(RectilinearGridMixin, VTKHDFWriterBase):
    """VTKHDF writer for RectilinearGrid using mixin pattern."""

    def __init__(self, filename, x_coords, y_coords, z_coords, version=(2, 2),
                 multiblock_index=None, **kwargs):
        super().__init__(
            filename=filename,
            x=x_coords,
            y=y_coords,
            z=z_coords,
            version=version,
            **kwargs
        )
        self.multiblock_index = multiblock_index
        self.check_data_consistency()

    def write_topology(self):
        """Write RectilinearGrid topology to HDF5."""
        if self.multiblock_index is not None:
            self.hdf5_root.attrs.create('Index', self.multiblock_index, dtype=idType)

        self.hdf5_root.attrs['Version'] = self.version
        ascii_type = 'RectilinearGrid'.encode('ascii')
        self.hdf5_root.attrs.create('Type', ascii_type,
                                    dtype=h5py.string_dtype('ascii', len(ascii_type)))
        self.hdf5_root.attrs.create('WholeExtent', self.whole_extent, dtype=fType)

        # Note: This is experimental - coordinate arrays would be added here
        # when VTKHDF specification supports RectilinearGrid fully


class VTKHDFMultiBlockWriter(VTKHDFWriterBase):
    """
    VTKHDF writer for multiblock datasets.

    Allows creation of multiblock datasets where each block can be
    a different type of VTK dataset.
    """

    def __init__(self, filename, blocks, version=(2, 2), additional_metadata=None):
        """
        Initialize multiblock writer.

        Parameters
        ----------
        filename : str
            Output file path
        blocks : dict
            Dictionary mapping block names to writer instances
        version : tuple, optional
            VTKHDF version
        additional_metadata : dict, optional
            Additional metadata
        """
        super().__init__(filename, version=version, additional_metadata=additional_metadata)
        self.blocks = blocks

    def write_topology(self):
        """No topology for multiblock - written by individual writers."""
        pass

    def write_vtkhdf_file(self):
        """Write multiblock dataset to VTKHDF file."""
        with h5py.File(self.path, 'w', track_order=True) as f:
            root = f.create_group('VTKHDF', track_order=True)
            root.attrs['Version'] = self.version
            ascii_type = 'PartitionedDataSetCollection'.encode('ascii')
            root.attrs.create('Type', ascii_type, dtype=h5py.string_dtype('ascii', len(ascii_type)))
            root.create_group('Assembly', track_order=True)

            if self.additional_metadata is not None:
                # Temporarily set hdf5_root for metadata writing
                self.hdf5_root = root
                self.write_additional_metadata(self.additional_metadata)

            # Write each block
            for blk_indx, (blk_name, blk_data) in enumerate(self.blocks.items()):
                self._write_block(root, blk_name, blk_data, blk_indx)

    def _write_block(self, root, blk_name, blk_data, blk_indx):
        """Write a single block to the multiblock dataset."""
        class_names = [t.__name__ for t in type(blk_data).__mro__]

        if 'PolyData' in class_names:
            writer = VTKHDFPolyDataWriter(
                self.path, blk_data.points, verts=blk_data.verts,
                lines=blk_data.lines, polys=blk_data.polys, strips=blk_data.strips,
                cell_data=blk_data.cell_data, point_data=blk_data.point_data,
                field_data=blk_data.field_data, multiblock_index=blk_indx
            )
        elif 'UnstructuredGrid' in class_names:
            writer = VTKHDFUnstructuredGridWriter(
                self.path, blk_data.points, blk_data.cells.types,
                blk_data.cells.connectivity, blk_data.cells.offsets,
                cell_data=blk_data.cell_data, point_data=blk_data.point_data,
                field_data=blk_data.field_data, multiblock_index=blk_indx
            )
        elif 'ImageData' in class_names:
            writer = VTKHDFImageDataWriter(
                self.path, blk_data.grid.whole_extents, blk_data.grid.origin,
                blk_data.grid.spacing, direction=blk_data.grid.direction,
                cell_data=blk_data.cell_data, point_data=blk_data.point_data,
                field_data=blk_data.field_data, multiblock_index=blk_indx
            )
        else:
            raise ValueError(f"Unsupported block type: {class_names}")

        writer.write_vtkhdf_multiblock_data(root, block_name=blk_name)