"""Hammer--Marlowe--Stroud quadrature rule."""

import numpy as np
import numpy.typing as npt
from quadraturerules.domain import Domain
import typing


def hammer_marlowe_stroud(
    domain: Domain,
    order: int,
) -> typing.Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Get a Hammer--Marlowe--Stroud quadrature rule."""
    match domain:
        case Domain.Interval:
            match order:
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
                case 4:
                    return np.array(
                        [
                            [0.13005607921683443, 0.009703785126946106, 0.8602401356562195],
                            [0.009703785126946106, 0.13005607921683443, 0.8602401356562195],
                            [0.0936377844373285, 0.04612207990645205, 0.8602401356562195],
                            [0.04612207990645205, 0.0936377844373285, 0.8602401356562195],
                            [0.38749748340669415, 0.028912084224389012, 0.5835904323689168],
                            [0.028912084224389012, 0.38749748340669415, 0.5835904323689168],
                            [0.2789904634965088, 0.13741910413457437, 0.5835904323689168],
                            [0.13741910413457437, 0.2789904634965088, 0.5835904323689168],
                            [0.6729468631505064, 0.050210123211369806, 0.2768430136381237],
                            [0.050210123211369806, 0.6729468631505064, 0.2768430136381237],
                            [0.4845083266304333, 0.23864865973144297, 0.2768430136381237],
                            [0.23864865973144297, 0.4845083266304333, 0.2768430136381237],
                            [0.8774288093304679, 0.06546699455501448, 0.05710419611451767],
                            [0.06546699455501448, 0.8774288093304679, 0.05710419611451767],
                            [0.6317312516411253, 0.311164552244357, 0.05710419611451767],
                            [0.311164552244357, 0.6317312516411253, 0.05710419611451767],
                        ]
                    ), np.array(
                        [
                            0.010846451821050509,
                            0.010846451821050509,
                            0.020334519128957573,
                            0.020334519128957573,
                            0.04516809856473986,
                            0.04516809856473986,
                            0.08467944904349257,
                            0.08467944904349257,
                            0.07077613579617188,
                            0.07077613579617188,
                            0.13268843221409946,
                            0.13268843221409946,
                            0.047136736386764674,
                            0.047136736386764674,
                            0.08837017704472347,
                            0.08837017704472347,
                        ]
                    )
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
