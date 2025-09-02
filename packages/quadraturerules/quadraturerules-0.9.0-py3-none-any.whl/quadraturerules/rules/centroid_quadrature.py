"""centroid quadrature quadrature rule."""

import numpy as np
import numpy.typing as npt
from quadraturerules.domain import Domain
import typing


def centroid_quadrature(
    domain: Domain,
    order: int,
) -> typing.Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Get a centroid quadrature quadrature rule."""
    match domain:
        case Domain.Interval:
            match order:
                case 1:
                    return np.array([[0.5, 0.5]]), np.array([1.0])
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.Quadrilateral:
            match order:
                case 1:
                    return np.array([[0.25, 0.25, 0.25, 0.25]]), np.array([1.0])
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.EdgeAdjacentQuadrilaterals:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.VertexAdjacentQuadrilaterals:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.Triangle:
            match order:
                case 1:
                    return np.array(
                        [[0.3333333333333333, 0.3333333333333333, 0.3333333333333333]]
                    ), np.array([1.0])
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.EdgeAdjacentTriangleAndQuadrilateral:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.VertexAdjacentTriangleAndQuadrilateral:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.EdgeAdjacentTriangles:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.VertexAdjacentTriangles:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.Hexahedron:
            match order:
                case 1:
                    return np.array(
                        [[0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]]
                    ), np.array([1.0])
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.Tetrahedron:
            match order:
                case 1:
                    return np.array([[0.25, 0.25, 0.25, 0.25]]), np.array([1.0])
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.SquareBasedPyramid:
            match order:
                case 1:
                    return np.array([[0.2, 0.2, 0.2, 0.2, 0.2]]), np.array([1.0])
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.TriangularPrism:
            match order:
                case 1:
                    return np.array(
                        [
                            [
                                0.16666666666666666,
                                0.16666666666666666,
                                0.16666666666666666,
                                0.16666666666666666,
                                0.16666666666666666,
                                0.16666666666666666,
                            ]
                        ]
                    ), np.array([1.0])
                case _:
                    raise ValueError(f"Invalid order: {order}")
