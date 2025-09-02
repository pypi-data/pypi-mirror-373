#!/usr/bin/env python
"""
Example usage of refactored VTK writers showing the improved API.

Demonstrates how the shared base classes and mixins reduce code duplication
while maintaining clean, consistent interfaces.
"""

import numpy as np
from vtk_writers.xml import XMLImageDataWriter, XMLUnstructuredGridWriter
from vtk_writers.vtkhdf_refactored import (
    VTKHDFImageDataWriter,
    VTKHDFUnstructuredGridWriter,
    VTKHDFMultiBlockWriter
)


def create_sample_data():
    """Create sample data for demonstrations."""
    # Sample ImageData
    extent = [0, 10, 0, 10, 0, 5]
    origin = [0.0, 0.0, 0.0]
    spacing = [1.0, 1.0, 1.0]

    # Sample point and cell data
    npoints = 11 * 11 * 6  # (extent[1]+1) * (extent[3]+1) * (extent[5]+1)
    ncells = 10 * 10 * 5  # extent[1] * extent[3] * extent[5]

    point_data = {
        'temperature': np.random.random(npoints),
        'velocity': np.random.random((npoints, 3))
    }

    cell_data = {
        'pressure': np.random.random(ncells),
        'density': np.random.random(ncells)
    }

    # Sample UnstructuredGrid
    points = np.random.random((100, 3)) * 10
    connectivity = np.arange(400)  # 100 tetrahedra
    offsets = np.arange(4, 401, 4)  # Each tetrahedron has 4 points
    cell_types = np.full(100, 10)  # VTK_TETRA = 10

    unstruct_point_data = {
        'values': np.random.random(100)
    }

    unstruct_cell_data = {
        'material_id': np.random.randint(1, 5, 100)
    }

    return {
        'image_data': {
            'extent': extent,
            'origin': origin,
            'spacing': spacing,
            'point_data': point_data,
            'cell_data': cell_data
        },
        'unstructured_grid': {
            'points': points,
            'connectivity': connectivity,
            'offsets': offsets,
            'cell_types': cell_types,
            'point_data': unstruct_point_data,
            'cell_data': unstruct_cell_data
        }
    }


def example_xml_writers():
    """Example using XML writers with shared validation."""
    print("=== XML Writers Example ===")
    data = create_sample_data()

    # ImageData XML
    xml_img_writer = XMLImageDataWriter(
        filepath='output_image.vti',
        whole_extent=data['image_data']['extent'],
        spacing=data['image_data']['spacing'],
        origin=data['image_data']['origin'],
        point_data=data['image_data']['point_data'],
        cell_data=data['image_data']['cell_data']
    )
    xml_img_writer.write_xml_file()
    print(f"Written XML ImageData: {xml_img_writer.path}")

    # UnstructuredGrid XML
    xml_unstruct_writer = XMLUnstructuredGridWriter(
        filepath='output_unstructured.vtu',
        nodes=data['unstructured_grid']['points'],
        cell_type=data['unstructured_grid']['cell_types'],
        connectivity=data['unstructured_grid']['connectivity'],
        offsets=data['unstructured_grid']['offsets'],
        point_data=data['unstructured_grid']['point_data'],
        cell_data=data['unstructured_grid']['cell_data']
    )
    xml_unstruct_writer.write_xml_file()
    print(f"Written XML UnstructuredGrid: {xml_unstruct_writer.path}")


def example_vtkhdf_writers():
    """Example using refactored VTKHDF writers."""
    print("\n=== VTKHDF Writers Example ===")
    data = create_sample_data()

    # ImageData VTKHDF
    hdf_img_writer = VTKHDFImageDataWriter(
        filename='output_image.vtkhdf',
        whole_extent=data['image_data']['extent'],
        origin=data['image_data']['origin'],
        spacing=data['image_data']['spacing'],
        point_data=data['image_data']['point_data'],
        cell_data=data['image_data']['cell_data']
    )
    hdf_img_writer.write_file()
    print(f"Written VTKHDF ImageData: {hdf_img_writer.path}")

    # UnstructuredGrid VTKHDF
    hdf_unstruct_writer = VTKHDFUnstructuredGridWriter(
        filename='output_unstructured.vtkhdf',
        points=data['unstructured_grid']['points'],
        cell_types=data['unstructured_grid']['cell_types'],
        connectivity=data['unstructured_grid']['connectivity'],
        offsets=data['unstructured_grid']['offsets'],
        point_data=data['unstructured_grid']['point_data'],
        cell_data=data['unstructured_grid']['cell_data']
    )
    hdf_unstruct_writer.write_file()
    print(f"Written VTKHDF UnstructuredGrid: {hdf_unstruct_writer.path}")


def example_multiblock_writer():
    """Example using multiblock writer."""
    print("\n=== MultiBlock Writer Example ===")
    data = create_sample_data()

    # Create individual dataset writers (but don't write them yet)
    img_writer = VTKHDFImageDataWriter(
        filename='temp.vtkhdf',  # Filename not used in multiblock context
        whole_extent=data['image_data']['extent'],
        origin=data['image_data']['origin'],
        spacing=data['image_data']['spacing'],
        point_data=data['image_data']['point_data'],
        cell_data=data['image_data']['cell_data']
    )

    unstruct_writer = VTKHDFUnstructuredGridWriter(
        filename='temp.vtkhdf',  # Filename not used in multiblock context
        points=data['unstructured_grid']['points'],
        cell_types=data['unstructured_grid']['cell_types'],
        connectivity=data['unstructured_grid']['connectivity'],
        offsets=data['unstructured_grid']['offsets'],
        point_data=data['unstructured_grid']['point_data'],
        cell_data=data['unstructured_grid']['cell_data']
    )

    # Create multiblock writer
    multiblock_writer = VTKHDFMultiBlockWriter(
        filename='multiblock_output.vtkhdf',
        blocks={
            'ImageData_Block': img_writer,
            'UnstructuredGrid_Block': unstruct_writer
        },
        additional_metadata={
            'simulation_info': {
                'time_step': 42,
                'solver': 'custom_solver_v1.0',
                'attrs': {
                    'creation_date': '2025-01-01',
                    'author': 'simulation_user'
                }
            }
        }
    )

    multiblock_writer.write_file()
    print(f"Written MultiBlock dataset: {multiblock_writer.path}")


def demonstrate_validation_benefits():
    """Show how shared validation catches errors consistently."""
    print("\n=== Validation Benefits Example ===")

    try:
        # This should fail with clear error message
        bad_extent = [0, 10, 5, 3, 0, 2]  # ymin > ymax
        VTKHDFImageDataWriter(
            filename='bad_extent.vtkhdf',
            whole_extent=bad_extent,
            origin=[0, 0, 0],
            spacing=[1, 1, 1]
        )
    except ValueError as e:
        print(f"✓ Validation caught bad extent: {e}")

    try:
        # This should fail - mismatched data sizes
        VTKHDFImageDataWriter(
            filename='bad_data.vtkhdf',
            whole_extent=[0, 2, 0, 2, 0, 2],  # Should have 27 points
            origin=[0, 0, 0],
            spacing=[1, 1, 1],
            point_data={'temp': np.random.random(10)}  # Wrong size!
        )
    except ValueError as e:
        print(f"✓ Validation caught data size mismatch: {e}")

    try:
        # This should fail - invalid coordinates
        VTKHDFRectilinearGridWriter(
            filename='bad_coords.vtkhdf',
            x_coords=[1, 2, np.nan, 4],  # Contains NaN
            y_coords=[0, 1, 2],
            z_coords=[0, 1]
        )
    except ValueError as e:
        print(f"✓ Validation caught invalid coordinates: {e}")


if __name__ == '__main__':
    example_xml_writers()
    example_vtkhdf_writers()
    example_multiblock_writer()
    demonstrate_validation_benefits()

    print("\n=== Summary ===")
    print("✓ All writers use shared validation logic")
    print("✓ Consistent error handling across XML and VTKHDF formats")
    print("✓ Mixin pattern allows flexible combination of features")
    print("✓ Reduced code duplication while maintaining clean APIs")