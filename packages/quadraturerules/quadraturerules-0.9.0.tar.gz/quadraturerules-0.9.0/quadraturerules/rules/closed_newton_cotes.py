"""closed Newton--Cotes quadrature rule."""

import numpy as np
import numpy.typing as npt
from quadraturerules.domain import Domain
import typing


def closed_newton_cotes(
    domain: Domain,
    order: int,
) -> typing.Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Get a closed Newton--Cotes quadrature rule."""
    match domain:
        case Domain.Interval:
            match order:
                case 1:
                    return np.array([[1.0, 0.0], [0.0, 1.0]]), np.array([0.5, 0.5])
                case 2:
                    return np.array([[1.0, 0.0], [0.5, 0.5], [0.0, 1.0]]), np.array(
                        [0.16666666666666666, 0.6666666666666666, 0.16666666666666666]
                    )
                case 3:
                    return np.array(
                        [
                            [1.0, 0.0],
                            [0.6666666666666666, 0.3333333333333333],
                            [0.3333333333333333, 0.6666666666666666],
                            [0.0, 1.0],
                        ]
                    ), np.array([0.125, 0.375, 0.375, 0.125])
                case 4:
                    return np.array(
                        [[1.0, 0.0], [0.75, 0.25], [0.5, 0.5], [0.25, 0.75], [0.0, 1.0]]
                    ), np.array(
                        [
                            0.07777777777777778,
                            0.35555555555555557,
                            0.13333333333333333,
                            0.35555555555555557,
                            0.07777777777777778,
                        ]
                    )
                case 5:
                    return np.array(
                        [[1.0, 0.0], [0.8, 0.2], [0.6, 0.4], [0.4, 0.6], [0.2, 0.8], [0.0, 1.0]]
                    ), np.array(
                        [
                            0.06597222222222222,
                            0.2604166666666667,
                            0.1736111111111111,
                            0.1736111111111111,
                            0.2604166666666667,
                            0.06597222222222222,
                        ]
                    )
                case 6:
                    return np.array(
                        [
                            [1.0, 0.0],
                            [0.8333333333333334, 0.16666666666666666],
                            [0.6666666666666667, 0.3333333333333333],
                            [0.5, 0.5],
                            [0.33333333333333337, 0.6666666666666666],
                            [0.16666666666666663, 0.8333333333333334],
                            [0.0, 1.0],
                        ]
                    ), np.array(
                        [
                            0.04880952380952381,
                            0.2571428571428571,
                            0.03214285714285714,
                            0.3238095238095238,
                            0.03214285714285714,
                            0.2571428571428571,
                            0.04880952380952381,
                        ]
                    )
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.Quadrilateral:
            match order:
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
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.Tetrahedron:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.SquareBasedPyramid:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.TriangularPrism:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
