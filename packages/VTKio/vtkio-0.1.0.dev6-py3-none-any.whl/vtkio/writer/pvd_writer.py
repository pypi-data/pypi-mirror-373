#!/usr/bin/env python
"""
PVDWriter Class for creating PAraViews's XML based format for multiple files.

Created at 13:01, 24 Feb, 2022
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard Library
import sys

# Imports
from ..vtk_cell_types import *


class PVDWriter:
    _text_encoding = 'utf-8'

    def __init__(self, filepath, declaration=True):

        self.file = open(filepath + '.pvd', "wb")
        self.filetype = "Collection"
        self._add_declaration = declaration


        self._byteorder = 'LittleEndian' if sys.byteorder == "little" else 'BigEndian'
        self._byteorder_char = '<' if sys.byteorder == "little" else '>'

        if self._add_declaration:
            self.add_declaration()

        self.add_filetype()


    def add_declaration(self):
        """
        Add an XML declaration to start of file.

        This can be included in all files.
        However, it should be noted that XML files with an encoding of `appended` may be considered invalid XML.

        """
        self.file.write(b'<?xml version="1.0"?>\n')


    def add_filetype(self, header_type="UInt64"):
        """
        Add XML root node and file type node.

        Parameters
        ----------
        header_type : str

        """
        # add vtk root node
        vtk_filestr = (f'<VTKFile type="{self.filetype}" version="1.0" '
                       f'byte_order="{self._byteorder}" header_type="{self.header_type}">')
        self.file.write((vtk_filestr + "\n").encode(self._text_encoding))


    def open_collection(self):
        self.file.write(f'  <{self.filetype}>\n'.encode(self._text_encoding))


    def close_collection(self):
        self.file.write(f'  </{self.filetype}>\n'.encode(self._text_encoding))


    def close_file(self):
        """
        Close file after writing data to it.

        Returns
        -------
        None

        """
        self.file.write("</VTKFile>\n".encode(self._text_encoding))
        self.file.close()
        # print('  File successfully written.')

    def add_dataset(self, file, timestep, group="", part=0, name="" ,indent_lvl=2,):

        element = '  ' * indent_lvl + f'<DataSet timestep="{timestep}" group="{group}" part="{part}" name="{name}" file="{file}"/>\n'
        self.file.write(element.encode(self._text_encoding))


# test pvd writer
def write_pvd_file(filename, timestep_list, file_list, group_list=None, part_list=None, names_list=None):
    """
    Write a PVD file for a list of files and timesteps. The lists need to be in the correct order.

    Parameters
    ----------
    filename :
    timestep_list :
    file_list :
    group_list :
    part_list :

    Returns
    -------
    PVD file

    """
    #open file
    file = PVDWriter(filename)
    file.open_collection()

    # handle nones
    if group_list is None:
        group_list = ["" for x in range(len(timestep_list))]

    if part_list is None:
        part_list = [0 for x in range(len(timestep_list))]

    if names_list is None:
        names_list = ["" for x in range(len(timestep_list))]


    # zip and loop to write datasets
    for file, timestep, group, part, name in zip(file_list, timestep_list, group_list, part_list, names_list):
        file.add_dataset(file, timestep=timestep, group=group, part=part, name=name)

    # close out file
    file.close_collection()
    file.close_file()