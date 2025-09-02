"""Quadrature rules."""

from enum import Enum as _Enum
import typing as _typing
import numpy.typing as _npt
import numpy as _np

from quadraturerules import rules
from quadraturerules.domain import Domain


class QuadratureRule(_Enum):
    """A quadrature rule family."""

    GaussLegendre = 1
    GaussLobattoLegendre = 3
    HammerMarloweStroud = 6
    SauterSchwab = 7
    XiaoGimbutas = 2
    CentroidQuadrature = 5
    ClosedNewtonCotes = 8
    OpenNewtonCotes = 9
    VertexQuadrature = 4


def single_integral_quadrature(
    rtype: QuadratureRule,
    domain: Domain,
    order: int,
) -> _typing.Tuple[_npt.NDArray[_np.float64], _npt.NDArray[_np.float64]]:
    """Get a quadrature rule for a single integral."""
    match rtype:
        case QuadratureRule.GaussLegendre:
            return rules.gauss_legendre(domain, order)
        case QuadratureRule.GaussLobattoLegendre:
            return rules.gauss_lobatto_legendre(domain, order)
        case QuadratureRule.HammerMarloweStroud:
            return rules.hammer_marlowe_stroud(domain, order)
        case QuadratureRule.XiaoGimbutas:
            return rules.xiao_gimbutas(domain, order)
        case QuadratureRule.CentroidQuadrature:
            return rules.centroid_quadrature(domain, order)
        case QuadratureRule.ClosedNewtonCotes:
            return rules.closed_newton_cotes(domain, order)
        case QuadratureRule.OpenNewtonCotes:
            return rules.open_newton_cotes(domain, order)
        case QuadratureRule.VertexQuadrature:
            return rules.vertex_quadrature(domain, order)
        case _:
            raise ValueError(f"Unsupported rule for single integral: {rtype}")


def double_integral_quadrature(
    rtype: QuadratureRule,
    domain: Domain,
    order: int,
) -> _typing.Tuple[_npt.NDArray[_np.float64], _npt.NDArray[_np.float64], _npt.NDArray[_np.float64]]:
    """Get a quadrature rule for a double integral."""
    match rtype:
        case QuadratureRule.SauterSchwab:
            return rules.sauter_schwab(domain, order)
        case _:
            raise ValueError(f"Unsupported rule for double integral: {rtype}")
