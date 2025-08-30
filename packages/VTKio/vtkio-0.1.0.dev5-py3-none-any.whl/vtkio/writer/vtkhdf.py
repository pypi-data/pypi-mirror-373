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
from abc import ABCMeta, abstractmethod
from pathlib import Path

# Imports
import h5py
import numpy as np

# Local imports
from ..utilities import flatten

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


class VTKHDFWriterBase(metaclass=ABCMeta):
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

    def __init__(self, filename, version=(2, 2), additional_metadata=None):
        self.field_data = None
        self.point_data = None
        self.cell_data = None
        self.hdf5_root = None
        self.path = Path(filename).with_suffix(self.extension)

        if version not in VTKHDFWriterBase.supported_versions:
            raise ValueError("Unsupported VTKHDF version. Supported versions are (2, 2), (2, 3), and (2, 4).")
        self.version = version

        # set data attributes
        # num points and cells can be calculated from the extents for ImageData, StructuredGrid and RectilinearGrid
        self.npoints = 0
        self.ncells = 0

        # needs to be calculated from the data first and passed at instantiation
        self.nverts = 0
        self.nlines = 0
        self.nstrips = 0
        self.npolys = 0

        self.additional_metadata = additional_metadata

    def write_additional_metadata(self, dictionary, group_path: str = '/VTKHDF'):
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

        # Create group if it doesn't exist
        # Handle case where group_path is an h5py.Group
        if isinstance(group_path, h5py.Group):
            current_group = self.hdf5_root.create_group(
                'additional_data') if self.hdf5_root.name == '/VTKHDF' else group_path

            group_path = current_group.name
        else:
            if group_path == '/VTKHDF':
                group_path = 'additional_data'
                current_group = self.hdf5_root.create_group(group_path)
            else:
                # Create group if it doesn't exist
                try:
                    current_group = self.hdf5_root[group_path]
                except KeyError:
                    current_group = self.hdf5_root.create_group(group_path)

        # Iterate through dictionary items
        for key, value in dictionary.items():
            # Ensure key is a string
            key = str(key)

            # Handle different types of values
            if isinstance(value, dict):
                if key == 'attrs':
                    # If the key is 'attrs', treat it as attributes
                    for attr_key, attr_value in value.items():
                        current_group.attrs[attr_key] = attr_value
                else:
                    # For nested dictionaries, create a new group and recurse
                    new_group_path = f"{group_path}/{key}"
                    self.write_additional_metadata(value, new_group_path)

            elif isinstance(value, (np.ndarray, list, tuple)):
                # Convert lists/tuples to numpy arrays
                if not isinstance(value, np.ndarray):
                    value = np.array(value)

                # Create dataset
                current_group.create_dataset(key, data=value)

            elif isinstance(value, (int, float, str, bool, np.number)):
                # Store simple scalar types as attributes
                current_group.attrs[key] = value

            else:
                # Try to convert to string or numpy array for other types
                try:
                    current_group.attrs[key] = str(value)
                except:
                    try:
                        current_group.create_dataset(key, data=np.array(value))
                    except:
                        print(f"Warning: Could not store value for key {key} of type {type(value)}")

    @abstractmethod
    def write_topology(self):
        pass

    def write_vtkhdf_file(self):
        """
        Write the VTKHDF dataset to the specified file.

        This method creates the root group in the HDF5 file, initialises the CellData, PointData, and FieldData groups,
        and calls the write_topology method to write the dataset topology. It then writes the data arrays for structured
        grids (ImageData, StructuredGrid, RectilinearGrid) or unstructured grids (UnstructuredGrid, PolyData) based on
        the type of dataset being written. Finally, it writes any additional metadata to the file.
        
        """
        with h5py.File(self.path, 'w') as f:
            self.hdf5_root = f.create_group('VTKHDF')
            self.CellData_Group = self.hdf5_root.create_group("CellData")
            self.PointData_Group = self.hdf5_root.create_group("PointData")
            self.FieldData_Group = self.hdf5_root.create_group("FieldData")
            self.write_topology()
            if self.hdf5_root.attrs['Type'].decode('utf8') == 'ImageData':
                self.write_grid_data_arrays()
            else:
                self.write_nongrid_data_arrays()
            self.write_additional_metadata(self.additional_metadata)

    def write_vtkhdf_multiblock_data(self, root, block_name):
        """
        Write the VTKHDF datasets to the specified file as a MultiBlock dataset.

        This method creates the root group in the HDF5 file, initialises the CellData, PointData, and FieldData groups,
        and calls the write_topology method to write the dataset topology. It then writes the data arrays for structured
        grids (ImageData, StructuredGrid, RectilinearGrid) or unstructured grids (UnstructuredGrid, PolyData) based on
        the type of dataset being written. Finally, it writes any additional metadata to the file.

        """
        # set hdf5 root for writing block
        self.hdf5_root = root.create_group(block_name, track_order=True)

        self.CellData_Group = self.hdf5_root.create_group("CellData")
        self.PointData_Group = self.hdf5_root.create_group("PointData")
        self.FieldData_Group = self.hdf5_root.create_group("FieldData")

        self.write_topology()
        if self.hdf5_root.attrs['Type'].decode('utf8') == 'ImageData':
            self.write_grid_data_arrays()
        else:
            self.write_nongrid_data_arrays()

        # add to assembly
        assembly_blk = root['Assembly'].create_group(block_name, track_order=True)
        assembly_blk[block_name] = h5py.SoftLink(f'/VTKHDF/{block_name}')

    def add_structured_data_to_group(self, group, data_shape, dname, darray):
        """
        Add a data array to an HDF5 group as a dataset.

        Adds a data array to an HDF5 group as a dataset, reshaping it to match the specified data shape and
        accounting for VTK's Fortran-style axis order.
        root : h5py.Group
            The HDF5 group to which the dataset will be added.
        data_shape : tuple or list of int
            The shape of the data (excluding the number of components).
        dname : str
            The name of the dataset to be created within the group.
        darray : numpy.ndarray
            The data array to be stored. Should have shape (N, n_comp) or (N,) if single component.


        Notes
        -----
        The function attempts to determine the number of components in the data array. If the array is 1D,
        it assumes a single component. The data is reshaped to match the reversed data shape (to account for
        VTK's Fortran axis order) with the number of components as the last dimension.
        """
        try:
            n_comp = darray.shape[1]
        except:
            n_comp = 1

        # root.create_dataset(dname, data=darray.reshape([*data_shape, n_comp], order='F'))
        # reverse order of dimensions to account for VTK fortran axis order
        group.create_dataset(dname, data=darray.reshape([*data_shape[::-1], n_comp]))

    def add_unstructured_group_data(self, group, name, data):
        """
        Add a data array to an HDF5 group as a dataset for unstructured grids.

        Adds a data array to an HDF5 group as a dataset. If the data is a dictionary, it assumes that
        the dictionary contains data grouped by data array type and creates datasets for each type.
        If the data is not a dictionary, it assumes that it is a single data array and creates a dataset
        with the specified name.

        Parameters
        ----------
        group : h5py.Group
            The HDF5 group to which the dataset will be added.
        name : str  
            The name of the dataset to be created within the group.
        data : numpy.ndarray or dict
            The data array to be stored. If a dictionary, it should contain data grouped by data array type.

        Notes
        -----
        This method is used for unstructured grids, where the data arrays do not require reshaping like
        structured grids. The data is stored directly in the group as datasets without reshaping.
        
        """
        if isinstance(data, dict):
            # if data is a dict, we assume it contains data grouped by data array type
            for darray_name, darray in data.items():
                group.create_dataset(darray_name, data=darray)
        else:
            # if data is not a dict, we assume it is a single data array
            group.create_dataset(name, data=data)

    def add_structured_group_data(self, group, name, data, datasize):
        """
        Add a data array to an HDF5 group as a dataset for structured grids.
        
        Adds a data array to an HDF5 group as a dataset. If the data is a dictionary, it assumes that
        the dictionary contains data grouped by data array type and creates datasets for each type.
        If the data is not a dictionary, it assumes that it is a single data array and creates a dataset
        with the specified name.

        Parameters
        ----------
        group : h5py.Group
            The HDF5 group to which the dataset will be added.
        name : str
            The name of the dataset to be created within the group.
        data : numpy.ndarray or dict
            The data array to be stored. If a dictionary, it should contain data grouped by data array type.
        datasize : tuple(ints)
            The size of the data array, which is used to reshape the data correctly for structured grids.

        Notes
        -----
        This method is used for structured grids (ImageData, StructuredGrid, RectilinearGrid), where the data
        arrays need to be reshaped to match the grid structure. The reshaping accounts for VTK's Fortran-style
        axis order. The data is stored in the group as datasets, reshaped to the specified data size.
        
        
        """
        if isinstance(data, dict):
            # if data is a dict, we assume it contains data grouped by data array type
            for darray_name, darray in data.items():
                self.add_structured_data_to_group(group, datasize, darray_name, darray)
        else:
            # if data is not a dict, we assume it is a single data array
            self.add_structured_data_to_group(group, datasize, name, data)

    def write_grid_data_arrays(self):
        """
        Write data arrays for structured grids (ImageData, StructuredGrid, RectilinearGrid).
        
        This method writes point data, cell data, and field data to the HDF5 file in the appropriate groups.
        It handles the structured nature of the data, ensuring that the data arrays are reshaped correctly
        to match the grid structure. The reshaping accounts for VTK's Fortran-style axis order.
        
        The method assumes that the data arrays are provided in a dictionary format, where keys are the names
        of the data arrays and values are the corresponding numpy arrays. If the data arrays are not provided,
        the method will skip writing that type of data.
        """

        # write cell data if present
        if self.cell_data is not None:
            for name, data in self.cell_data.items():
                self.add_structured_group_data(self.CellData_Group, name, data, self.num_cells)

        # write point data if present
        if self.point_data is not None:
            for name, data in self.point_data.items():
                self.add_structured_group_data(self.PointData_Group, name, data, self.num_points)

        # write field data if present
        if self.field_data is not None:
            # field data can be any shape, so we store it directly
            for name, darray in self.field_data.items():
                if isinstance(darray, np.ndarray):
                    self.FieldData_Group.create_dataset(name, data=darray)
                else:
                    self.FieldData_Group.create_dataset(name, data=np.array([darray]))

    def write_nongrid_data_arrays(self):
        """
        Write data arrays for unstructured grids (UnstructuredGrid, PolyData).
        
        This method writes point data, cell data, and field data to the HDF5 file in the appropriate groups.
        It handles the unstructured nature of the data, ensuring that the data arrays are stored correctly - unstructured data does not require reshaping like structured data.
        
        The method assumes that the data arrays are provided in a dictionary format, where keys are the names
        of the data arrays and values are the corresponding numpy arrays. If the data arrays are not provided,
        the method will skip writing that type of data.
        """

        # write cell data if present
        if self.cell_data is not None:
            for name, data in self.cell_data.items():
                self.add_unstructured_group_data(self.CellData_Group, name, data)

        # write point data if present
        if self.point_data is not None:
            for name, data in self.point_data.items():
                self.add_unstructured_group_data(self.PointData_Group, name, data)

        # write field data if present
        if self.field_data is not None:
            # field data can be any shape, so we store it directly
            for name, darray in self.field_data.items():
                if isinstance(darray, np.ndarray):
                    self.FieldData_Group.create_dataset(name, data=darray)
                else:
                    self.FieldData_Group.create_dataset(name, data=np.array([darray]))

    @staticmethod
    def _check_array_sizes(array_data):
        """
        Check the size of all data arrays to be written to ensure they are all the same length.

        Parameters
        ----------
        array_data : dictionary of data arrays to be written.

        Returns
        -------
        Array Size : Int

        Raises
        ------
        ValueError : If the sizes of the arrays are not all equal.

        """
        # flatten dictionary to check sizes more easily
        flattened_arrays = flatten(array_data, parent_key='', separator='_')

        sizes = []
        for _key, val in flattened_arrays.items():
            try:
                if val.ndim == 1:
                    sizes.append(val.size)
                else:
                    sizes.append(val.shape[0])
            except AttributeError:
                sizes.append(len(val))

        all_equal = all(sizes)

        if all_equal:
            return sizes[0]
        else:
            raise ValueError("Warning: Arrays provided are not all the same length. Data not written to file.")

    # Keep specialised methods for regular XML writing:
    def check_array_sizes_for_cell_data(self, cell_data):
        """
        Compare size of cell data with the number of cells in the file.
        
        Parameters
        ----------
        cell_data : dict
            Dictionary containing cell data arrays to be checked.
        
        Raises
        -------
        ValueError : If the size of cell data does not match the number of cells.
        
        """
        if cell_data is not None:
            cell_data_size = self._check_array_sizes(cell_data)
            if cell_data_size != self.ncells:
                raise ValueError('Cells and cell data sizes do not match')

    def check_array_sizes_for_point_data(self, point_data):
        """
        Compare size of point data with the number of points in the file.

        Parameters
        ----------
        point_data : dict
            Dictionary containing point data arrays to be checked.

        Raises
        -------
        ValueError : If the size of point data does not match the number of points.
        """
        if point_data is not None:
            point_data_size = self._check_array_sizes(point_data)
            if point_data_size != self.npoints:
                raise ValueError('Points and point data sizes do not match')


class VTKHDFMultiBlockWriter(VTKHDFWriterBase):
    """
    A class for writing multiblock datasets in VTKHDF format.
    
    This class allows for the creation of a multiblock dataset where each block can be
    a different type of VTK dataset (e.g., UnstructuredGrid, ImageData, PolyData).
    Each block is written as a separate group within the main VTKHDF group, and an assembly
    group is created to link these blocks together.

    The class inherits from VTKHDFWriterBase and implements the write_vtkhdf_file method to handle
    the specifics of writing multiple blocks to a single VTKHDF file.
    """

    def __init__(self, filename, blocks, additional_metadata=None, version=(2, 2)):
        """
        Initialise the VTKHDFMultiBlockWriter with a path and a dictionary of blocks.
        
        Parameters
        ----------
        filename : str
            The name of the file to write the multiblock dataset to. Should end with '.vtkhdf'.
        blocks : dict
            A dictionary where keys are block names and values are instances of VTKHDFWriterBase
            (e.g., VTKHDFUnstructuredGridWriter, VTKHDFImageDataWriter, etc.) that will be written as blocks.
        additional_metadata : dict, optional
            Additional metadata to be written to the VTKHDF file. Default is None.
            
        """
        super().__init__(filename, additional_metadata=additional_metadata, version=version)
        self.blocks = blocks  # dict: name -> writer instance

    def write_vtkhdf_file(self):
        """
        Write the multiblock dataset to the VTKHDF file.
        
        This method creates the main VTKHDF group, writes the metadata, and iterates over the blocks
        to write each one as a separate group. It also creates an assembly group that links the blocks
        together using soft links.
        """
        with h5py.File(self.path, 'w', track_order=True) as f:

            root = f.create_group('VTKHDF', track_order=True)
            root.attrs['Version'] = self.version
            ascii_type = 'PartitionedDataSetCollection'.encode('ascii')
            root.attrs.create('Type', ascii_type, dtype=h5py.string_dtype('ascii', len(ascii_type)))
            root.create_group('Assembly', track_order=True)

            if self.additional_metadata is not None:
                self.write_additional_metadata(root)

            for blk_indx, (blk_name, blk_data) in enumerate(self.blocks.items()):
                class_names = [t.__name__ for t in type(blk_data).__mro__]
                if 'PolyData' in class_names:
                    writer = VTKHDFPolyDataWriter(self.path, blk_data.points, verts=blk_data.verts,
                                                  lines=blk_data.lines,
                                                  polys=blk_data.polys, strips=blk_data.strips,
                                                  cell_data=blk_data.cell_data, point_data=blk_data.point_data,
                                                  field_data=blk_data.field_data, multiblock_index=blk_indx)
                    writer.write_vtkhdf_multiblock_data(root, block_name=blk_name)

                elif 'UnstructuredGrid' in class_names:
                    writer = VTKHDFUnstructuredGridWriter(self.path, blk_data.points, blk_data.cells.types,
                                                          blk_data.cells.connectivity, blk_data.cells.offsets,
                                                          cell_data=blk_data.cell_data, point_data=blk_data.point_data,
                                                          field_data=blk_data.field_data, multiblock_index=blk_indx)
                    writer.write_vtkhdf_multiblock_data(root, block_name=blk_name)
                elif 'ImageData' in class_names:
                    writer = VTKHDFImageDataWriter(self.path, blk_data.grid.whole_extents, blk_data.grid.origin,
                                                   blk_data.grid.spacing, direction=blk_data.grid.direction,
                                                   cell_data=blk_data.cell_data, point_data=blk_data.point_data,
                                                  field_data=blk_data.field_data, multiblock_index=blk_indx)
                    writer.write_vtkhdf_multiblock_data(root, block_name=blk_name)


    def write_topology(self):
        """ There is no topology in the multiblock dataset. It is written by the specific writer."""
        raise NotImplementedError


class VTKHDFImageDataWriter(VTKHDFWriterBase):
    """
    Write ImageData to a file in the VTKHDF format.

    This class allows for the creation of ImageData datasets, which are structured grids
    defined by their whole extent, origin, spacing, and direction. It inherits from
    VTKHDFWriterBase and implements the write_vtkhdf_file method to handle the specifics of writing
    ImageData to a VTKHDF file.

    Parameters
    ----------
    filename : str
        The name of the file to write the ImageData to. Should end with '.vtkhdf'.
    whole_extent : list or array-like
        The whole extent of the ImageData, defined as [xmin, xmax, ymin, ymax, zmin, zmax].
    origin : list or array-like
        The origin of the ImageData, defined as [x_origin, y_origin, z_origin].
    spacing : list or array-like
        The spacing of the ImageData, defined as [x_spacing, y_spacing, z_spacing].
    direction : list or array-like, optional
        The direction cosines of the ImageData, defined as a flattened 3x3 matrix.
        If not provided, defaults to the identity matrix (no rotation).
    version : tuple, optional
        The version of the VTKHDF format to use. Default is (2, 2).
    point_data : dict, optional
        A dictionary containing point data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    cell_data : dict, optional
        A dictionary containing cell data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    field_data : dict, optional
        A dictionary containing field data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    additional_metadata : dict, optional
        Additional metadata to be written to the VTKHDF file. This can include any additional information
        that should be stored in the file, such as attributes or custom data.
    multiblock_index : int, optional
        An index for the multiblock dataset, if this ImageData is part of a larger multiblock dataset.
        If not provided, defaults to None.
    """

    def __init__(self, filename, whole_extent, origin, spacing, direction=None, version=(2, 2),
                 point_data=None, cell_data=None, field_data=None, additional_metadata=None, multiblock_index=None):
        """
        Initialise the VTKHDFImageDataWriter with the necessary parameters for ImageData.

        Parameters
        ----------
        filename : str
            The name of the file to write the ImageData to. Should end with '.vtkhdf'.
        whole_extent : list or array-like
            The whole extent of the ImageData, defined as [xmin, xmax, ymin, ymax, zmin, zmax].
        origin : list or array-like
            The origin of the ImageData, defined as [x_origin, y_origin, z_origin].
        spacing : list or array-like
            The spacing of the ImageData, defined as [x_spacing, y_spacing, z_spacing].
        direction : list or array-like, optional
            The direction cosines of the ImageData, defined as a flattened 3x3 matrix.
            If not provided, defaults to the identity matrix (no rotation).
        version : tuple, optional
            The version of the VTKHDF format to use. Default is (2, 2).
        point_data : dict, optional
            A dictionary containing point data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        cell_data : dict, optional
            A dictionary containing cell data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        field_data : dict, optional
            A dictionary containing field data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        additional_metadata : dict, optional
            Additional metadata to be written to the VTKHDF file. This can include any additional information
            that should be stored in the file, such as attributes or custom data.
        multiblock_index : int, optional
            An index for the multiblock dataset, if this ImageData is part of a larger multiblock dataset.
            If not provided, defaults to None.
        """
        super().__init__(filename, additional_metadata=additional_metadata, version=version)
        self.whole_extent = np.asarray(whole_extent)
        if len(self.whole_extent) != 6:
            raise ValueError("whole_extent must be a list or array of length 6.")

        self.origin = np.asarray(origin)
        self.spacing = np.asarray(spacing)
        self.direction = np.asarray(direction) if direction is not None else np.eye(3).flatten()
        self.multiblock_index = multiblock_index

        self.num_cells = (self.whole_extent[1::2] - self.whole_extent[0::2])
        self.num_points = self.num_cells + 1
        self.ncells = np.prod(self.num_cells)
        self.npoints = np.prod(self.num_cells + 1)

        # do check on provided data sizes before attempting to write
        self.check_array_sizes_for_point_data(point_data)
        self.check_array_sizes_for_cell_data(cell_data)

        self.point_data = point_data
        self.cell_data = cell_data
        self.field_data = field_data

    def write_topology(self):
        """
        Write the topology of the ImageData to the HDF5 file.

        This method creates the necessary attributes and datasets in the HDF5 file to represent
        the ImageData topology, including whole extent, origin, spacing, and direction.
        If a multiblock index is provided, it is stored as an attribute. The version and type of the dataset
        are also set as attributes. The whole extent, origin, spacing, and direction are stored as attributes
        within the root group of the HDF5 file.

        """
        if self.multiblock_index is not None:
            self.hdf5_root.attrs.create('Index', self.multiblock_index, dtype=idType)
        self.hdf5_root.attrs['Version'] = self.version
        ascii_type = 'ImageData'.encode('ascii')
        self.hdf5_root.attrs.create('Type', ascii_type, dtype=h5py.string_dtype('ascii', len(ascii_type)))
        self.hdf5_root.attrs.create('WholeExtent', self.whole_extent, dtype=idType)
        self.hdf5_root.attrs.create('Origin', self.origin, dtype=fType)
        self.hdf5_root.attrs.create('Spacing', self.spacing, dtype=fType)
        self.hdf5_root.attrs.create('Direction', self.direction, dtype=fType)


class VTKHDFUnstructuredGridWriter(VTKHDFWriterBase):
    """
    Write UnstructuredGrid datasets to a file in VTKHDF format.

    This class allows for the creation of UnstructuredGrid datasets, which are defined by their nodes,
    cell types, connectivity, and offsets. It inherits from VTKHDFWriterBase and implements the
    write_vtkhdf_file method to handle the specifics of writing UnstructuredGrid data to a VTKHDF file.

    Parameters
    ----------
    filename : str
        The name of the file to write the UnstructuredGrid to. Should end with '.vtkhdf'.
    nodes : numpy.ndarray
        An array of nodes defining the vertices of the UnstructuredGrid. Should be of shape (N, 3),
        where N is the number of nodes.
    cell_types : numpy.ndarray
        An array of cell types for the UnstructuredGrid. Should be a 1D array of integers representing
        the types of cells (e.g., VTK_TRIANGLE, VTK_QUAD, etc.).
    connectivity : numpy.ndarray
        An array of connectivity indices for the UnstructuredGrid. Should be a 1D array of integers
        representing the indices of nodes that form each cell.
    offsets : list or numpy.ndarray
        An array of offsets for the connectivity array. Should be a 1D array of integers indicating
        the start of each cell in the connectivity array. The length of this array should be equal to
        the number of cells plus one (to account for the end of the last cell).
    version : tuple, optional
        The version of the VTKHDF format to use. Default is (2, 2).
    point_data : dict, optional
        A dictionary containing point data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    cell_data : dict, optional
        A dictionary containing cell data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    field_data : dict, optional
        A dictionary containing field data arrays to be written. Keys and values
        should match the desired metadata structure.
    additional_metadata : dict, optional
        Additional metadata to be written to the VTKHDF file. This can include any additional information
        that should be stored in the file, such as attributes or custom data.
    multiblock_index : int, optional
        An index for the multiblock dataset, if this UnstructuredGrid is part of a larger multiblock dataset.
        If not provided, defaults to None.
    """

    def __init__(self, filename, nodes, cell_types, connectivity, offsets, version=(2, 2),
                 point_data=None, cell_data=None, field_data=None, additional_metadata=None, multiblock_index=None):
        super().__init__(filename, additional_metadata=additional_metadata, version=version)
        self.nodes = np.asarray(nodes)
        self.cell_types = np.asarray(cell_types)
        self.connectivity = np.asarray(connectivity)
        self.offsets = self._correct_offsets(offsets, self.cell_types)
        self.point_data = point_data or {}
        self.cell_data = cell_data or {}
        self.field_data = field_data or {}
        self.multiblock_index = multiblock_index

    @staticmethod
    def _correct_offsets(offsets, cell_types):
        """
        Correct the offsets array to ensure it is in the correct format for VTKHDF.
        
        Parameters
        ----------
        offsets : list or array-like
            The offsets for the connectivity array. Can be a list or array of integers.
        cell_types : list or array-like
            The types of cells in the unstructured grid. Used to determine the number of cells.
            
        Returns
        -------
        offsets : numpy.ndarray
            A numpy array of offsets, corrected to ensure it starts with 0 and has the correct length.
        
        Raises
        -------
        ValueError : If the offsets array is not of the correct length.
        """

        offsets = np.asarray(offsets)
        ncells = len(cell_types)
        if len(offsets) == ncells:
            offsets = np.hstack([0, offsets])
        elif len(offsets) != ncells + 1:
            raise ValueError("Offsets must be length ncells+1 or ncells (will prepend 0 if needed).")
        if offsets[0] != 0:
            offsets = offsets - offsets[0]
        return offsets

    def write_topology(self):
        """
        Write the topology of the unstructured grid to the HDF5 file.
        
        This method creates the necessary attributes and datasets in the HDF5 file to represent
        the unstructured grid topology, including nodes, connectivity, offsets, cell types, and counts.
        
        If a multiblock index is provided, it is stored as an attribute. The version and type of the dataset
        are also set as attributes. The nodes, connectivity, offsets, and cell types are stored as datasets
        within the root group of the HDF5 file.
        """
        if self.multiblock_index is not None:
            self.hdf5_root.attrs.create('Index', self.multiblock_index, dtype=idType)
        self.hdf5_root.attrs['Version'] = (2, 2)
        ascii_type = 'UnstructuredGrid'.encode('ascii')
        self.hdf5_root.attrs.create('Type', ascii_type, dtype=h5py.string_dtype('ascii', len(ascii_type)))
        self.hdf5_root.create_dataset('Points', data=self.nodes, maxshape=(None, 3), dtype=fType)
        self.hdf5_root.create_dataset('Connectivity', data=self.connectivity, maxshape=(None,), dtype=idType)
        self.hdf5_root.create_dataset('Offsets', data=self.offsets, maxshape=(None,), dtype=idType)
        self.hdf5_root.create_dataset('Types', data=self.cell_types, maxshape=(None,), dtype=charType)
        self.hdf5_root.create_dataset('NumberOfPoints', data=np.array([len(self.nodes)]), dtype=idType)
        self.hdf5_root.create_dataset('NumberOfConnectivityIds', data=np.array([len(self.connectivity)]), dtype=idType)
        self.hdf5_root.create_dataset('NumberOfCells', data=np.array([len(self.cell_types)]), dtype=idType)


class VTKHDFPolyDataWriter(VTKHDFWriterBase):
    """
    Write PolyData datasetes to a file in VTKHDF format.

    This class allows for the creation of PolyData datasets, which are unstructured grids
    defined by their points, vertices, lines, polygons, and strips. It inherits from
    VTKHDFWriterBase and implements the write_vtkhdf_file method to handle the specifics of writing
    PolyData to a VTKHDF file.

    Parameters
    ----------
    filename : str
        The name of the file to write the PolyData to. Should end with '.vtkhdf'.
    points : numpy.ndarray
        An array of points defining the vertices of the PolyData. Should be of shape (N, 3),
        where N is the number of points.
    verts : tuple, optional
        A tuple containing the connectivity and offsets for vertices in the PolyData.
        Should be of the form (connectivity, offsets), where connectivity is a 1D array
        of vertex indices and offsets is a 1D array indicating the start of each vertex.
    lines : tuple, optional
        A tuple containing the connectivity and offsets for lines in the PolyData.
        Should be of the form (connectivity, offsets), where connectivity is a 1D array
        of line indices and offsets is a 1D array indicating the start of each line.
    polys : tuple, optional
        A tuple containing the connectivity and offsets for polygons in the PolyData.
        Should be of the form (connectivity, offsets), where connectivity is a 1D array
        of polygon indices and offsets is a 1D array indicating the start of each polygon.
    strips : tuple, optional
        A tuple containing the connectivity and offsets for strips in the PolyData.
        Should be of the form (connectivity, offsets), where connectivity is a 1D array
        of strip indices and offsets is a 1D array indicating the start of each strip.
    version : tuple, optional
        The version of the VTKHDF format to use. Default is (2, 2).
    point_data : dict, optional
        A dictionary containing point data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    cell_data : dict, optional
        A dictionary containing cell data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    field_data : dict, optional
        A dictionary containing field data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    additional_metadata : dict, optional
        Additional metadata to be written to the VTKHDF file. This can include any additional information
        that should be stored in the file, such as attributes or custom data.
    multiblock_index : int, optional
        An index for the multiblock dataset, if this PolyData is part of a larger multiblock dataset.
        If not provided, defaults to None.
    
    """

    def __init__(self, filename, points, verts=None, lines=None, polys=None, strips=None,
                 point_data=None, cell_data=None, field_data=None,
                 additional_metadata=None, multiblock_index=None, version=(2, 2)):
        """
        Initialise the VTKHDFPolyDataWriter with the necessary parameters for PolyData.

        Parameters
        ----------
        filename : str
            The name of the file to write the PolyData to. Should end with '.vtkhdf'.   
        points : numpy.ndarray
            An array of points defining the vertices of the PolyData. Should be of shape (N, 3),
            where N is the number of points.
        verts : tuple, optional
            A tuple containing the connectivity and offsets for vertices in the PolyData.
            Should be of the form (connectivity, offsets), where connectivity is a 1D array
            of vertex indices and offsets is a 1D array indicating the start of each vertex.
        lines : tuple, optional
            A tuple containing the connectivity and offsets for lines in the PolyData.
            Should be of the form (connectivity, offsets), where connectivity is a 1D array
            of line indices and offsets is a 1D array indicating the start of each line.
        polys : tuple, optional
            A tuple containing the connectivity and offsets for polygons in the PolyData.
            Should be of the form (connectivity, offsets), where connectivity is a 1D array
            of polygon indices and offsets is a 1D array indicating the start of each polygon.
        strips : tuple, optional
            A tuple containing the connectivity and offsets for strips in the PolyData.
            Should be of the form (connectivity, offsets), where connectivity is a 1D array
            of strip indices and offsets is a 1D array indicating the start of each strip.
        version : tuple, optional
            The version of the VTKHDF format to use. Default is (2, 2).
        point_data : dict, optional
            A dictionary containing point data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        cell_data : dict, optional
            A dictionary containing cell data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        field_data : dict, optional
            A dictionary containing field data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        additional_metadata : dict, optional
            Additional metadata to be written to the VTKHDF file. This can include any additional information
            that should be stored in the file, such as attributes or custom data.
        multiblock_index : int, optional
            An index for the multiblock dataset, if this PolyData is part of a larger multiblock dataset.
            If not provided, defaults to None.
        
        """

        super().__init__(filename, version=version, additional_metadata=additional_metadata)

        self.points = points
        self.verts = verts
        self.lines = lines
        self.strips = strips
        self.polys = polys

        self.point_data = point_data
        self.cell_data = cell_data
        self.field_data = field_data

        # set topology attributes
        if self.points is not None:
            self.npoints = len(points)
        if self.verts is not None:
            if type(self.verts).__name__ == 'PolyDataTopology':
                self.nverts = len(verts.offsets)
            else:
                self.nverts = len(verts[1])
        if self.lines is not None:
            if type(self.lines).__name__ == 'PolyDataTopology':
                self.nlines = len(lines.offsets)
            else:
                self.nlines = len(lines[1])
        if self.strips is not None:
            if type(self.strips).__name__ == 'PolyDataTopology':
                self.nstrips = len(strips.offsets)
            else:
                self.nstrips = len(strips[1])
        if self.polys is not None:
            if type(polys).__name__ == 'PolyDataTopology':
                self.npolys = len(polys.offsets)
            else:
                self.npolys = len(polys[1])

        if self.cell_data:
            self.ncells = self.nverts + self.nlines + self.nstrips + self.npolys

        self.multiblock_index = multiblock_index

        # data size checks
        self.check_array_sizes_for_point_data(point_data)
        self.check_array_sizes_for_cell_data(cell_data)

    def write_topology(self):
        """
        Write the topology of the PolyData to the HDF5 file.

        This method creates the necessary attributes and datasets in the HDF5 file to represent
        the PolyData topology, including points, vertices, lines, polygons, and strips.
        If a multiblock index is provided, it is stored as an attribute. The version and type of the dataset
        are also set as attributes. The points, vertices, lines, polygons, and strips are stored as datasets
        within the root group of the HDF5 file.
        
        """
        if self.multiblock_index is not None:
            self.hdf5_root.attrs.create('Index', self.multiblock_index, dtype=idType)

        self.hdf5_root.attrs['Version'] = self.version
        ascii_type = 'PolyData'.encode('ascii')
        self.hdf5_root.attrs.create('Type', ascii_type, dtype=h5py.string_dtype('ascii', len(ascii_type)))
        self.hdf5_root.create_dataset('Points', data=self.points, maxshape=(None, 3), dtype=fType)
        self.hdf5_root.create_dataset('NumberOfPoints', data=np.array([len(self.points)]), dtype=idType)
        for name, topo in zip(['Vertices', 'Lines', 'Polygons', 'Strips'],
                              [self.verts, self.lines, self.polys, self.strips]):
            group = self.hdf5_root.create_group(name)
            if topo is not None:
                if type(topo).__name__ == 'PolyDataTopology':
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
                group.create_dataset('NumberOfConnectivityIds', data=np.array([0]), maxshape=(None,), dtype=idType)
                group.create_dataset('NumberOfCells', data=np.array([0]), maxshape=(None,), dtype=idType)
                group.create_dataset('Offsets', data=np.array([0]), maxshape=(None,), dtype=idType)
                group.create_dataset('Connectivity', (0,), maxshape=(None,), dtype=idType)


class VTKHDFRectilinearGridWriter(VTKHDFWriterBase):
    """
    Write RectilinearGrid dtasets to a file in VTKHDF format.

    This class allows for the creation of RectilinearGrid datasets, which are structured grids
    defined by their points along each axis. It inherits from VTKHDFWriterBase and implements the
    write_vtkhdf_file method to handle the specifics of writing RectilinearGrid to a VTKHDF file.

    Parameters
    ----------
    filename : str
        The name of the file to write the RectilinearGrid to. Should end with '.vtkhdf'.
    x_coords : numpy.ndarray
        An array of x-coordinates defining the points along the x-axis.
    y_coords : numpy.ndarray
        An array of y-coordinates defining the points along the y-axis.
    z_coords : numpy.ndarray
        An array of z-coordinates defining the points along the z-axis.
    version : tuple, optional
        The version of the VTKHDF format to use. Default is (2, 2).
    point_data : dict, optional
        A dictionary containing point data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    cell_data : dict, optional
        A dictionary containing cell data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    field_data : dict, optional
        A dictionary containing field data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    additional_metadata : dict, optional
        Additional metadata to be written to the VTKHDF file. This can include any additional information
        that should be stored in the file, such as attributes or custom data.
    multiblock_index : int, optional
        An index for the multiblock dataset, if this RectilinearGrid is part of a larger multiblock dataset.
        If not provided, defaults to None.

    """

    def __init__(self, filename, x_coords, y_coords, z_coords, version=(2, 2),
                 point_data=None, cell_data=None, field_data=None,
                 additional_metadata=None, multiblock_index=None):
        """
        Initialize the VTKHDFRectilinearGridWriter with the necessary parameters for RectilinearGrid.

        Parameters
        ----------
        filename : str
            The name of the file to write the RectilinearGrid to. Should end with '.vtkhdf'.
        x_coords : numpy.ndarray
            An array of x-coordinates defining the points along the x-axis.
        y_coords : numpy.ndarray
            An array of y-coordinates defining the points along the y-axis.
        z_coords : numpy.ndarray
            An array of z-coordinates defining the points along the z-axis.
        version : tuple, optional
            The version of the VTKHDF format to use. Default is (2, 2).
        point_data : dict, optional
            A dictionary containing point data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        cell_data : dict, optional
            A dictionary containing cell data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        field_data : dict, optional
            A dictionary containing field data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        additional_metadata : dict, optional
            Additional metadata to be written to the VTKHDF file. This can include any additional information
            that should be stored in the file, such as attributes or custom data.
        multiblock_index : int, optional
            An index for the multiblock dataset, if this RectilinearGrid is part of a larger multiblock dataset.
            If not provided, defaults to None.

        """
        # simple check on coordinates - must first be a list or array
        if not (isinstance(x_coords, (np.ndarray, list, tuple))):
            raise TypeError("x must be a numpy array, tuple or list")
        if not (isinstance(y_coords, (np.ndarray, list, tuple))):
            raise TypeError("y must be a numpy array, tuple or list")
        if not (isinstance(z_coords, (np.ndarray, list, tuple))):
            raise TypeError("z must be a numpy array, tuple or list")

        # check if list or array is numeric
        x = np.asarray(x_coords)
        y = np.asarray(y_coords)
        z = np.asarray(z_coords)
        if not (np.issubdtype(x.dtype, np.number)):
            raise TypeError("x must be a numeric numpy array or list")
        if not (np.issubdtype(y.dtype, np.number)):
            raise TypeError("y must be a numeric numpy array or list")
        if not (np.issubdtype(z.dtype, np.number)):
            raise TypeError("z must be a numeric numpy array or list")

        super().__init__(filename, additional_metadata=additional_metadata, version=version)

        self.x = x
        self.y = y
        self.z = z

        self.whole_extent = np.array([np.zeros(3), np.array([len(x), len(y), len(z)]) - 1]).T.flatten()

        self.num_cells = (len(x_coords) - 1, len(y_coords) - 1, len(z_coords) - 1)
        self.num_points = (len(x_coords), len(y_coords), len(z_coords))
        self.ncells = np.prod(self.num_cells)
        self.npoints = np.prod(self.num_points)

        self.multiblock_index = multiblock_index

        # do check on provided data sizes before attempting to write
        self.check_array_sizes_for_cell_data(cell_data)
        self.check_array_sizes_for_point_data(point_data)

        self.point_data = point_data
        self.cell_data = cell_data
        self.field_data = field_data

    def write_topology(self):
        """
        Write the topology of the RectilinearGrid to the HDF5 file.

        This method creates the necessary attributes and datasets in the HDF5 file to represent
        the RectilinearGrid topology, including x-coordinates, y-coordinates, z-coordinates,
        number of cells, and number of points. If a multiblock index is provided, it is stored as an attribute.
        The version and type of the dataset are also set as attributes. The x-coordinates, y-coordinates,
        and z-coordinates are stored as datasets within the root group of the HDF5 file.

        Notes
        -----
        This is experimental and may not be fully functional yet. It is currently not supported by VTKHDF.

        """
        if self.multiblock_index is not None:
            self.hdf5_root.attrs.create('Index', self.multiblock_index, dtype=idType)
        self.hdf5_root.attrs['Version'] = self.version
        ascii_type = 'RectilinearGrid'.encode('ascii')
        self.hdf5_root.attrs.create('Type', ascii_type, dtype=h5py.string_dtype('ascii', len(ascii_type)))

        self.hdf5_root.attrs.create('WholeExtent', self.whole_extent, dtype=fType)


class VTKHDFStructuredGridWriter(VTKHDFWriterBase):
    """
    Write StructuredGrid datasets to a file in VTKHDF format.

    This class allows for the creation of StructuredGrid datasets, which are structured grids
    defined by their points along each axis. It inherits from VTKHDFWriterBase and implements the
    write_vtkhdf_file method to handle the specifics of writing StructuredGrid to a VTKHDF file.

    Parameters
    ----------
    filename : str
        The name of the file to write the StructuredGrid to. Should end with '.vtkhdf'.
    points : numpy.ndarray
        An array of points defining the vertices of the StructuredGrid. Should be of shape (N, 3),
        where N is the number of points.
    num_cells : list or tuple
        A list or tuple defining the number of cells along each axis of the StructuredGrid.
        Should be of length 3, representing the number of cells in the x, y, and z directions.
    version : tuple, optional
        The version of the VTKHDF format to use. Default is (2, 2).
    point_data : dict, optional
        A dictionary containing point data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    cell_data : dict, optional
        A dictionary containing cell data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    field_data : dict, optional
        A dictionary containing field data arrays to be written. Keys are the names of the data arrays,
        and values are the corresponding numpy arrays.
    additional_metadata : dict, optional
        Additional metadata to be written to the VTKHDF file. This can include any additional information
        that should be stored in the file, such as attributes or custom data.
    multiblock_index : int, optional
        An index for the multiblock dataset, if this StructuredGrid is part of a larger multiblock dataset.
        If not provided, defaults to None.

    """

    def __init__(self, filename, points, num_cells, version=(2, 2),
                 point_data=None, cell_data=None, field_data=None, additional_metadata=None, multiblock_index=None):
        """
        Initialise the VTKHDFStructuredGridWriter with the necessary parameters for StructuredGrid.

        Parameters
        ----------
        filename : str
            The name of the file to write the StructuredGrid to. Should end with '.vtkhdf'.
        points : numpy.ndarray
            An array of points defining the vertices of the StructuredGrid. Should be of shape (N, 3),
            where N is the number of points.
        version : tuple, optional
            The version of the VTKHDF format to use. Default is (2, 2).
        point_data : dict, optional
            A dictionary containing point data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        cell_data : dict, optional
            A dictionary containing cell data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        field_data : dict, optional
            A dictionary containing field data arrays to be written. Keys are the names of the data arrays,
            and values are the corresponding numpy arrays.
        additional_metadata : dict, optional
            Additional metadata to be written to the VTKHDF file. This can include any additional information
            that should be stored in the file, such as attributes or custom data.
        multiblock_index : int, optional
            An index for the multiblock dataset, if this StructuredGrid is part of a larger multiblock dataset.
            If not provided, defaults to None.

        """

        super().__init__(filename, additional_metadata=additional_metadata, version=version)

        self.points = np.asarray(points)

        if not (np.issubdtype(points.dtype, np.number)):
            raise TypeError("points must be a numeric numpy array")

        if len(self.points.shape) != 2 or self.points.shape[1] != 3:
            raise ValueError("Points must be a 2D array with shape (N, 3) where N is the number of points.")

        self.npoints = len(self.points)

        self.num_cells = np.asarray(num_cells)
        self.num_points = self.num_cells + 1
        self.ncells = np.prod(self.num_cells)

        self.multiblock_index = multiblock_index

        self.whole_extent = np.array([np.zeros(3), num_cells]).T.flatten()
        self.piece_extent = self.whole_extent

        # do check on provided data sizes before attempting to write
        self.check_array_sizes_for_point_data(point_data)
        self.check_array_sizes_for_cell_data(cell_data)

        self.point_data = point_data
        self.cell_data = cell_data
        self.field_data = field_data

    def write_topology(self):
        """
        Write the topology of the StructuredGrid to the HDF5 file.

        This method creates the necessary attributes and datasets in the HDF5 file to represent
        the StructuredGrid topology, including points, number of points, and optionally
        multiblock index, version, and type. The points are stored as a dataset within the root group
        of the HDF5 file.

        If a multiblock index is provided, it is stored as an attribute.

        Notes
        -----
        This is experimental and may not be fully functional yet. It is currently not supported by VTKHDF.

        """

        if self.multiblock_index is not None:
            self.hdf5_root.attrs.create('Index', self.multiblock_index, dtype=idType)

        self.hdf5_root.attrs['Version'] = self.version
        ascii_type = 'StructuredGrid'.encode('ascii')
        self.hdf5_root.attrs.create('Type', ascii_type, dtype=h5py.string_dtype('ascii', len(ascii_type)))
        self.hdf5_root.create_dataset('Points', data=self.points, maxshape=(None, 3), dtype=fType)
        self.hdf5_root.create_dataset('NumberOfPoints', data=np.array([self.npoints]), dtype=idType)
        self.hdf5_root.attrs.create('WholeExtent', self.whole_extent, dtype=fType)
        self.hdf5_root.attrs.create('PieceExtent', self.piece_extent, dtype=fType)
