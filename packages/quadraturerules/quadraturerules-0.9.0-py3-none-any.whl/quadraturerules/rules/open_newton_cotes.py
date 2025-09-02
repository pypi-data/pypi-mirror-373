"""open Newton--Cotes quadrature rule."""

import numpy as np
import numpy.typing as npt
from quadraturerules.domain import Domain
import typing


def open_newton_cotes(
    domain: Domain,
    order: int,
) -> typing.Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Get a open Newton--Cotes quadrature rule."""
    match domain:
        case Domain.Interval:
            match order:
                case 0:
                    return np.array([[0.5, 0.5]]), np.array([1.0])
                case 1:
                    return np.array(
                        [
                            [0.6666666666666667, 0.3333333333333333],
                            [0.33333333333333337, 0.6666666666666666],
                        ]
                    ), np.array([0.5, 0.5])
                case 2:
                    return np.array([[0.75, 0.25], [0.5, 0.5], [0.25, 0.75]]), np.array(
                        [0.6666666666666666, -0.3333333333333333, 0.6666666666666666]
                    )
                case 3:
                    return np.array([[0.8, 0.2], [0.6, 0.4], [0.4, 0.6], [0.2, 0.8]]), np.array(
                        [
                            0.4583333333333333,
                            0.041666666666666664,
                            0.041666666666666664,
                            0.4583333333333333,
                        ]
                    )
                case 4:
                    return np.array(
                        [
                            [0.8333333333333334, 0.16666666666666666],
                            [0.6666666666666667, 0.3333333333333333],
                            [0.5, 0.5],
                            [0.33333333333333337, 0.6666666666666666],
                            [0.16666666666666663, 0.8333333333333334],
                        ]
                    ), np.array([0.55, -0.7, 1.3, -0.7, 0.55])
                case 5:
                    return np.array(
                        [
                            [0.8571428571428572, 0.14285714285714285],
                            [0.7142857142857143, 0.2857142857142857],
                            [0.5714285714285714, 0.42857142857142855],
                            [0.4285714285714286, 0.5714285714285714],
                            [0.2857142857142857, 0.7142857142857143],
                            [0.1428571428571429, 0.8571428571428571],
                        ]
                    ), np.array(
                        [
                            0.42430555555555555,
                            -0.3145833333333333,
                            0.3902777777777778,
                            0.3902777777777778,
                            -0.3145833333333333,
                            0.42430555555555555,
                        ]
                    )
                case 6:
                    return np.array(
                        [
                            [0.875, 0.125],
                            [0.75, 0.25],
                            [0.625, 0.375],
                            [0.5, 0.5],
                            [0.375, 0.625],
                            [0.25, 0.75],
                            [0.125, 0.875],
                        ]
                    ), np.array(
                        [
                            0.48677248677248675,
                            -1.0095238095238095,
                            2.323809523809524,
                            -2.602116402116402,
                            2.323809523809524,
                            -1.0095238095238095,
                            0.48677248677248675,
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
