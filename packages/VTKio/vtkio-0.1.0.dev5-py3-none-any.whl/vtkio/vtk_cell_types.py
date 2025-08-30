#!/usr/bin/env python
"""
VTKWriter Class for creating VTK's XML based format.

Supports ASCII, Base64 and Appended Raw encoding of data.

Created at 13:01, 24 Feb, 2022
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard Library
from dataclasses import dataclass


@dataclass
class VTK_CellType:
    """Generic Class for storing the various different vtk cell types."""

    name: str
    type_id: int
    num_points: int
    dimensionality: int
    structure: str
    interpolation: str

    def set_num_points(self, num_points: int):
        """
        Set the number of points for the cell type.

        This is used for the PolyLine, Polygon and PolyVertex cell types.
        The number of points is set to the number of points in the cell.

        Parameters
        ----------
        num_points : int
            The number of points in the cell.
        """
        if self.name in ["PolyLine", "Polygon", "PolyVertex"]:
            self.num_points = num_points
        else:
            raise ValueError(f"Cannot set number of points for {self.name} cell type.")

        return self

    def set_num_triangles(self, num_triangles: int):
        """
        Set the number of triangles and points for the Triangle Strip cell type.

        Parameters
        ----------
        num_triangles : int
            The number of triangles in the cell.

        """
        if self.name == "TriangleStrip":
            # The number of points in a triangle strip is the number of triangles + 2
            self.num_points = num_triangles + 2
        else:
            raise ValueError(f"Cannot set number of triangles for {self.name} cell type.")

        return self


VTK_Vertex = VTK_CellType("Vertex", 1, 1, 0, "Primary", "Linear")
VTK_PolyVertex = VTK_CellType("PolyVertex", 1, "n", 0, "Composite", "Linear")
VTK_Line = VTK_CellType("Line", 3, 2, 1, "Primary", "Linear")
VTK_PolyLine = VTK_CellType("PolyLine", 4, "n", 1, "Composite", "Linear")
VTK_Triangle = VTK_CellType("Triangle", 5, 3, 2, "Primary", "Linear")
VTK_TriangleStrip = VTK_CellType("TriangleStrip", 6, "n+2", 2, "Composite", "Linear")
VTK_Polygon = VTK_CellType("Polygon", 7, "n", 2, "Primary", "Linear")
VTK_Pixel = VTK_CellType("Pixel", 8, 4, 2, "Primary", "Linear")
VTK_Quad = VTK_CellType("Quad", 9, 4, 3, "Primary", "Linear")
VTK_Tetra = VTK_CellType("Tetra", 10, 4, 3, "Primary", "Linear")
VTK_Voxel = VTK_CellType("Voxel", 11, 8, 3, "Primary", "Linear")
VTK_Hexahedron = VTK_CellType("Hexahedron", 12, 8, 3, "Primary", "Linear")
VTK_Wedge = VTK_CellType("Wedge", 13, 6, 3, "Primary", "Linear")
VTK_Pyramid = VTK_CellType("Pyramid", 14, 5, 3, "Primary", "Linear")
VTK_Pentagonal_Prism = VTK_CellType("Pentagonal_Prism", 15, 10, 3, "Primary", "Linear")
VTK_Hexagonal_Prism = VTK_CellType("Hexagonal_Prism", 16, 12, 3, "Primary", "Linear")
VTK_Quadratic_Edge = VTK_CellType("Quadratic_Edge", 21, 3, 1, "Primary", "NonLinear")
VTK_Quadratic_Triangle = VTK_CellType("Quadratic_Triangle", 22, 6, 2, "Primary", "NonLinear")
VTK_Quadratic_Quad = VTK_CellType("Quadratic_Quad", 23, 8, 2, "Primary", "NonLinear")
VTK_Quadratic_Tetra = VTK_CellType("Quadratic_Tetra", 24, 10, 3, "Primary", "NonLinear")
VTK_Quadratic_Hexahedron = VTK_CellType("Quadratic_Hexahedron", 25, 20, 3, "Primary", "NonLinear")
VTK_Quadratic_Wedge = VTK_CellType("Quadratic_Wedge", 26, 12, 3, "Primary", "NonLinear")
VTK_Quadratic_Pyramid = VTK_CellType("Quadratic_Pyramid", 27, 13, 3, "Primary", "NonLinear")
VTK_BiQuadratic_Quad = VTK_CellType("BiQuadratic_Quad", 28, 9, 2, "Primary", "NonLinear")
VTK_TriQuadratic_Hexahedron = VTK_CellType("TriQuadratic_Hexahedron", 29, 27, 3, "Primary", "NonLinear")
VTK_Quadratic_Linear_Quad = VTK_CellType("Quadratic_Linear_Quad", 30, 6, 3, "Primary", "NonLinear")
VTK_Quadratic_Linear_Wedge = VTK_CellType("Quadratic_Linear_Wedge", 31, 12, 3, "Primary", "NonLinear")
VTK_BiQuadratic_Quadratic_Wedge= VTK_CellType("BiQuadratic_Quadratic_Wedge", 32, 18, 3, "Primary", "NonLinear")
VTK_BiQuadratic_Quadratic_Hexahedron = VTK_CellType("BiQuadratic_Quadratic_Hexahedron", 33, 24, 3, "Primary", "NonLinear")
VTK_BiQuadratic_Triangle = VTK_CellType("BiQuadratic_Triangle", 34, 7, 2, "Primary", "NonLinear")
