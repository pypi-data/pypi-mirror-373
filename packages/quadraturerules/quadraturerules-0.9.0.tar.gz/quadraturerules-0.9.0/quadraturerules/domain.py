"""Integral domains."""

from enum import Enum


class Domain(Enum):
    """A domain of an integral."""

    Interval = 0
    Quadrilateral = 1
    EdgeAdjacentQuadrilaterals = 2
    VertexAdjacentQuadrilaterals = 3
    Triangle = 4
    EdgeAdjacentTriangleAndQuadrilateral = 5
    VertexAdjacentTriangleAndQuadrilateral = 6
    EdgeAdjacentTriangles = 7
    VertexAdjacentTriangles = 8
    Hexahedron = 9
    Tetrahedron = 10
    SquareBasedPyramid = 11
    TriangularPrism = 12
