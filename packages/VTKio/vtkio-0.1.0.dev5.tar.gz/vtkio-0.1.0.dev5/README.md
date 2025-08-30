# VTKio
![](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)  
A simple python package for reading and writing Visualization Tool Kit (VTK) files.



## Supported features
Legacy ascii `.vtk` files are not supported and only the newer **XML** and **HDF5** based formats are supported.

XML files can be written in `ascii`, `base64` binary and appended `base64` binary formats. 
This means all files remain valid `XML` documents. 
Support for reading and writing `raw` appended data is provided, but discouraged.

XML and VTKHDF files can also be read using the associated file readers. 

Data is returned in appropriate VTK classes with arrays stored in `numpy` formats. 

> [!WARNING]
> VTKHDF files can only be opened in supported software.  
> For example, ParaView has full VTKHDF support in 5.13 and above.


## VTK File Formats
All file formats have been developed based on VTK's [documentation](https://docs.vtk.org/en/latest/index.html) where 
the [XML](https://docs.vtk.org/en/latest/design_documents/VTKFileFormats.html#xml-file-formats) formats and newer [VTKHDF](https://docs.vtk.org/en/latest/design_documents/VTKFileFormats.html#vtkhdf-file-format) formats are described in detail.
Additional information can be found in [Chapter 5](https://book.vtk.org/en/latest/VTKBook/05Chapter5.html#) of the **VTK Book**.

Further information regarding the VTK data model can be found in the [ParaView documentation](https://docs.paraview.org/en/latest/UsersGuide/understandingData.html#vtk-data-model).

Example datafiles can be found for various filetypes at the [VTK Examples Repository](https://gitlab.kitware.com/vtk/vtk-examples/-/tree/master/src/Testing/Data?ref_type=heads).

## Documentation
For full documentation visit [jpmorr.gitlab.io/vtkio](https://jpmorr.gitlab.io/vtkio).

## Related packages
The following packages have some overlap in functionality with VTKio: 
 - [PyEVTK](https://github.com/paulo-herrera/PyEVTK)
 - [meshio](https://github.com/nschloe/meshio)
 - [uvw](https://github.com/prs513rosewood/uvw)
 - [vtk-hdf](https://github.com/jmag722/vtk-hdf)