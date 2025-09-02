"""DoRoute types."""

from contextlib import suppress
from typing import Annotated, Any, Literal, NotRequired, TypeAlias, TypedDict

import kfactory as kf
import numpy as np
from kfactory.layer import LayerEnum

try:
    from gdsfactory import kcl as gf_kcl  # type: ignore[reportMissingImports]
    from gdsfactory import pdk as gf_pdk  # type: ignore[reportMissingImports]
except ImportError:
    gf_kcl = None
    gf_pdk = None

__all__ = [
    "Dbu",
    "DirectivePointsDbu",
    "Float",
    "Int",
    "Layer",
    "LayerLike",
    "Number",
    "OrientationChar",
    "OrientationDegree",
    "OrientationLike",
    "OrientationTransition",
    "OrientationWord",
    "PointsDbu",
    "PointsUm",
    "PointsWgu",
    "PortLike",
    "PositionAny",
    "PositionDbu",
    "PositionUm",
    "PositionWithDirectionDbu",
    "PositionWithDirectionUm",
    "StepDbu",
    "Um",
    "Wgu",
]

Int: TypeAlias = int | np.int_
Float: TypeAlias = float | np.float64
Number: TypeAlias = Int | Float
Wgu: TypeAlias = Annotated[Int, "value in 'wg width units'"]
Dbu: TypeAlias = Annotated[Int, "value in database units"]
Um: TypeAlias = Annotated[Float, "value in micrometer"]
PositionUm: TypeAlias = Annotated[tuple[Um, Um], "x, y position in micrometer"]
PositionDbu: TypeAlias = Annotated[tuple[Dbu, Dbu], "x, y position in database units"]
PositionAny: TypeAlias = PositionUm | PositionDbu
OrientationChar: TypeAlias = Literal["n", "e", "s", "w", "o"]
OrientationWord: TypeAlias = Literal["north", "east", "south", "west", "none"]
OrientationDegree: TypeAlias = Literal[0, 90, 180, 270, -90]
PositionWithDirectionUm: TypeAlias = Annotated[
    tuple[Um, Um, OrientationChar], "x[um] y[um] d[neswo]"
]
PositionWithDirectionDbu: TypeAlias = Annotated[
    tuple[Dbu, Dbu, OrientationChar], "x[dbu] y[dbu] d[n|e|s|w|o]"
]
OrientationLike: TypeAlias = (
    OrientationChar | OrientationWord | OrientationDegree | Int | Float | None
)
PortLike: TypeAlias = (
    PositionDbu | tuple[Dbu, Dbu, OrientationLike] | kf.Port | kf.DPort
)
OrientationTransition: TypeAlias = tuple[OrientationChar, OrientationChar]
LayerLike: TypeAlias = tuple[Int, Int] | LayerEnum | str
Layer: TypeAlias = tuple[int, int]
PointsDbu: TypeAlias = list[PositionDbu]
PointsWgu: TypeAlias = list[tuple[Wgu, Wgu]]
PointsUm: TypeAlias = list[tuple[Float, Float]]
DirectivePointsDbu: TypeAlias = list[PositionWithDirectionDbu]


class StepDbu(TypedDict):  # noqa: D101
    x: NotRequired[Dbu]
    dx: NotRequired[Dbu]
    y: NotRequired[Dbu]
    dy: NotRequired[Dbu]


def validate_position(p: Any) -> PositionDbu:
    if isinstance(p, kf.DPort):
        _p = kf.Port(base=p._base)
        x, y = _p.center
        return (x, y)

    if isinstance(p, kf.Port):
        x, y = p.center
        return (x, y)

    try:
        p = tuple(p)
    except Exception as e:
        msg = f"Unable to parse {p} as position"
        raise ValueError(msg) from e

    match p:
        case (x, y):
            return (x, y)
        case (x, y, _):
            return (x, y)
    msg = f"Unable to parse {p} as position"
    raise ValueError(msg)


def validate_position_with_orientation(
    p: Any, *, invert_orientation: bool = False
) -> PositionWithDirectionDbu:
    from . import util

    def maybe_invert_orientation(o: OrientationChar) -> OrientationChar:
        if invert_orientation:
            return util.invert_orientation(o)
        return o

    if isinstance(p, kf.DPort):
        _p = kf.Port(base=p._base)
        x, y = _p.center
        o = validate_orientation(p.orientation)
        return (x, y, maybe_invert_orientation(o))

    if isinstance(p, kf.Port):
        x, y = p.center
        o = validate_orientation(p.orientation)
        return (x, y, maybe_invert_orientation(o))

    try:
        p = tuple(p)
    except Exception as e:
        msg = f"Unable to parse {p} as position with orientation"
        raise ValueError(msg) from e
    match p:
        case (x, y):
            return (int(x), int(y), maybe_invert_orientation("o"))
        case (x, y, o):
            return (int(x), int(y), maybe_invert_orientation(validate_orientation(o)))

    msg = f"Unable to parse {p} as position with orientation"
    raise ValueError(msg)


def validate_orientation(o: Any) -> OrientationChar:  # noqa: PLR0911
    given = o

    if given is None:
        return "o"

    if isinstance(given, str):
        o = o.lower().strip()
        if o == "none":
            return "o"
        o = o[:1]
        if o in "nesw":
            return o
        # if none of these cases match, try to validate as integer below:

    o = _try_int(given)

    if o is None:
        msg = f"Could not parse orientation from {given}."
        raise ValueError(msg)

    o = o % 360
    match o:
        case 0:
            return "e"
        case 90:
            return "n"
        case 180:
            return "w"
        case 270:
            return "s"

    msg = f"Could not parse orientation from {given}."
    raise ValueError(msg)


def validate_layer(kcl: kf.KCLayout, layer: Any) -> Layer:
    if isinstance(layer, LayerEnum):
        return (layer.layer, layer.datatype)

    if isinstance(layer, str):
        if kcl == gf_kcl and gf_pdk is not None:
            return gf_pdk.get_layer_tuple(layer)
        return kcl.layer_stack.layers[layer].layer

    layer_tuple = tuple(layer)
    return (int(layer_tuple[0]), int(layer_tuple[1]))


def _try_int(s: Any) -> int | None:
    with suppress(Exception):
        return int(s)
    return None
