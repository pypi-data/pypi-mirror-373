import os
from pathlib import Path

import pytest
from vtkio.reader.hdf5 import read_vtkhdf_data
from vtkio.vtk_structures import ImageData, PolyData, UnstructuredGrid, StructuredData, RectilinearData

TEST_DATA_PATH = Path(__file__).parent.parent / "TestData" / "vtkhdf"


@pytest.mark.parametrize("filename,expected_type", [
    ("image_data.vtkhdf", ImageData),
    ("poly_data.vtkhdf", PolyData),
    ("unstructured_grid.vtkhdf", UnstructuredGrid),
    ("structured_grid.vtkhdf", StructuredData),
    ("rectilinear_grid.vtkhdf", RectilinearData),
])


def test_read_vtkhdf_data_types(filename, expected_type):
    """
    Test the read_vtkhdf_data function.
    
    Test the read_vtkhdf_data function to ensure it correctly identifies the
    data type of the VTKHDF file. The test checks if the result is an instance 
    of the expected type (ImageData, PolyData, UnstructuredGrid, StructuredData,
    or RectilinearData) and verifies that the data structure contains the expected  
    attributes.

    The test uses pytest's parameterisation feature to run the test
    for multiple file types and their corresponding expected data structures.
    The test also includes assertions to check the presence of specific attributes
    in the resulting data structure, ensuring that the data has been read correctly
    and contains the expected information.

    The test is designed to be run with pytest
    and will fail if the read_vtkhdf_data function does not return the expected data    
    structure or if the attributes are not present. The test is useful for validating
    the functionality of the read_vtkhdf_data function and ensuring that it can handle
    different types of VTKHDF files correctly. 
    

    Parameters
    ----------
    filename : _type_
        _description_
    expected_type : _type_
        _description_
    """
    # Adjust the path as needed for your test data location
    filepath = TEST_DATA_PATH / filename
    result = read_vtkhdf_data(filepath)
    assert isinstance(result, expected_type)

     # Additional content checks
    if isinstance(result, ImageData):
        assert hasattr(result, "point_data")
        assert result.point_data is not None
        assert hasattr(result, "cell_data")
        assert result.cell_data is not None

    if isinstance(result, PolyData):
        assert hasattr(result, "points")
        assert result.points is not None
        assert result.points.size > 0

    if isinstance(result, UnstructuredGrid):
        assert hasattr(result, "points")
        assert result.points is not None
        assert hasattr(result, "cells")
        assert result.cells is not None

    if isinstance(result, StructuredData):
        assert hasattr(result, "coordinates")
        assert result.coordinates is not None

    if isinstance(result, RectilinearData):
        assert hasattr(result, "coordinates")
        assert result.coordinates is not None