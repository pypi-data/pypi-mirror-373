"""Shared utilities for the library."""

from collections.abc import Iterable
from types import SimpleNamespace

import numpy as np
import shapely.geometry as sg
from kfactory import kdb
from kfactory.instance import Instance
from kfactory.kcell import KCell, ProtoTKCell
from kfactory.layout import KCLayout
from kfactory.typings import KCellSpec
from numpy.typing import NDArray

from .types import (
    Dbu,
    DirectivePointsDbu,
    Int,
    Layer,
    OrientationChar,
    OrientationTransition,
    PointsDbu,
    PointsUm,
    PointsWgu,
    PositionAny,
    PositionDbu,
    PositionWithDirectionDbu,
    StepDbu,
    validate_orientation,
    validate_position_with_orientation,
)

# all the functions in this submodule are internal to the module.
__all__ = []


def as_kcell(c: ProtoTKCell) -> KCell:
    return KCell(base=c._base)  # noqa: SLF001


def extract_orientation(p0: PositionAny, p1: PositionAny) -> OrientationChar:
    dp = np.asarray(p1) - np.asarray(p0)
    is_east, is_north = dp > 0
    is_west, is_south = dp < 0
    match (bool(is_north), bool(is_east), bool(is_south), bool(is_west)):
        case (True, False, False, False):
            d = "n"
        case (False, True, False, False):
            d = "e"
        case (False, False, True, False):
            d = "s"
        case (False, False, False, True):
            d = "w"
        case _:
            msg = (
                f"Corner {p1} not in vertical or horizontal "
                f"line with previous corner {p0}."
            )
            raise RuntimeError(msg)
    return d


def invert_orientation(o: OrientationChar) -> OrientationChar:
    match o:
        case "n":
            return "s"
        case "s":
            return "n"
        case "e":
            return "w"
        case "w":
            return "e"
        case "o":
            return "o"
    return o


def subtract_bend_radius(p: PositionDbu, d: OrientationChar, br: Dbu) -> PositionDbu:
    x, y = p
    match d:
        case "n":
            y = y - br
        case "e":
            x = x - br
        case "s":
            y = y + br
        case "w":
            x = x + br
    return (x, y)


def add_bend_radius(p: PositionDbu, d: OrientationChar, br: Dbu) -> PositionDbu:
    x, y = p
    match d:
        case "n":
            y = y + br
        case "e":
            x = x + br
        case "s":
            y = y - br
        case "w":
            x = x - br
    return (x, y)


def orient_east_at_origin(straight_ref: Instance) -> Instance:
    inv_dbu = get_inv_dbu(straight_ref.kcl)
    # bundles of straights have more than 2 ports
    o1, o2, *_ = [p.name for p in straight_ref.ports]
    d = extract_orientation(
        straight_ref.ports[o1].center, straight_ref.ports[o2].center
    )
    x0, y0 = straight_ref.ports[o1].center
    straight_ref.dmove((float(-x0 / inv_dbu), float(-y0 / inv_dbu)))
    match d:
        case "n":
            straight_ref.drotate(90)
        case "e":
            pass
        case "s":
            straight_ref.drotate(-90)
        case "w":
            straight_ref.drotate(180)
    return straight_ref


def orient_east_to_north_at_origin(bend_ref: Instance) -> Instance:
    inv_dbu = get_inv_dbu(bend_ref.kcl)
    o1, o2 = [p.name for p in bend_ref.ports]
    x0, y0 = bend_ref.ports[o1].center
    bend_ref.dmove((float(-x0 / inv_dbu), float(-y0 / inv_dbu)))
    o_in = int(bend_ref.ports[o1].orientation) % 360
    o_out = int(bend_ref.ports[o2].orientation) % 360
    x0, y0 = bend_ref.ports[o1].center

    match (o_in, o_out):
        case (180, 90):  # e->n
            pass
        case (180, 270):  # e->s
            bend_ref.drotate(180)
            bend_ref.dmirror()
        case (90, 0):  # s->e
            bend_ref.drotate(90)
        case (90, 180):  # s->w
            bend_ref.drotate(270)
            bend_ref.dmirror()
        case (0, 90):  # w->n
            bend_ref.dmirror()
        case (0, 270):  # w->s
            bend_ref.drotate(180)
        case (270, 0):  # n->e
            bend_ref.drotate(90)
            bend_ref.dmirror()
        case (270, 180):  # n->w
            bend_ref.drotate(270)
    return bend_ref


def orient_at_origin(straight_ref: Instance, direction: OrientationChar) -> Instance:
    straight_ref = orient_east_at_origin(straight_ref)
    match direction:
        case "n":
            straight_ref.drotate(90)
        case "e":
            pass
        case "s":
            straight_ref.drotate(-90)
        case "w":
            straight_ref.drotate(180)
    return straight_ref


def orient_as_transition_at_origin(
    bend_ref: Instance, transition: OrientationTransition
) -> Instance:
    orient_east_to_north_at_origin(bend_ref)
    match transition:
        case ("e", "n"):
            pass
        case ("e", "s"):
            bend_ref.dmirror()
            bend_ref.drotate(180)
        case ("s", "e"):
            bend_ref.drotate(-90)
        case ("s", "w"):
            bend_ref.dmirror()
            bend_ref.drotate(90)
        case ("w", "n"):
            bend_ref.dmirror()
        case ("w", "s"):
            bend_ref.drotate(180)
        case ("n", "e"):
            bend_ref.dmirror()
            bend_ref.drotate(-90)
        case ("n", "w"):
            bend_ref.drotate(90)

    inv_dbu = get_inv_dbu(bend_ref.kcl)
    o1, _ = [p.name for p in bend_ref.ports]
    x0, y0 = bend_ref.ports[o1].center
    bend_ref.dmove((float(-x0 / inv_dbu), float(-y0 / inv_dbu)))

    return bend_ref


def extract_polys(
    c: KCell,
    layers: Iterable[Layer],
) -> list[NDArray[np.int64]]:
    if not layers:
        layers = [
            (info.layer, info.datatype)
            for info in c.kcl.layer_infos()
            if not c.bbox(c.kcl.layer(info)).empty()
        ]

    polys = []
    for layer in layers:
        layer_idx = c.kcl.layer(*layer)
        r = kdb.Region(c.begin_shapes_rec(layer_idx))
        polys += list(r.each())
    return [_poly2np(poly) for poly in polys]


def straight_length(kcl: KCLayout, straight_points: PointsDbu) -> PointsUm:
    inv_dbu = get_inv_dbu(kcl)
    return (
        np.sqrt(
            ((np.array(straight_points[0]) - np.array(straight_points[-1])) ** 2).sum()
        )
        / inv_dbu
    )


def discretize_bend(
    kcl: KCLayout, bend: KCellSpec, grid_unit: Dbu, layers: Iterable[Layer]
) -> PointsWgu:
    c = KCell(kcl=kcl)
    r = c << kcl.get_component(bend, output_type=KCell)
    orient_east_to_north_at_origin(r)
    c.flatten()

    bend_points = extract_polys(c, layers)
    mp = sg.MultiPolygon([sg.Polygon(bp) for bp in bend_points])

    bbox = c.bbox()
    bbox = SimpleNamespace(
        north=bbox.top, east=bbox.right, south=bbox.bottom, west=bbox.left
    )
    m = (bbox.east - bbox.west) // grid_unit + 1
    n = (bbox.north - bbox.south) // grid_unit + 1
    xc = np.arange(0, m) * grid_unit + bbox.west // grid_unit * grid_unit
    yc = np.arange(0, n) * grid_unit + bbox.south // grid_unit * grid_unit
    ic = xc // grid_unit
    jc = yc // grid_unit
    J, I = np.meshgrid(jc, ic)

    grid = np.zeros((m, n), dtype=int)
    for i, x in enumerate(xc):
        for j, y in enumerate(yc):
            cell = sg.Polygon(
                [
                    (x - grid_unit / 2, y - grid_unit / 2),
                    (x - grid_unit / 2, y + grid_unit / 2),
                    (x + grid_unit / 2, y + grid_unit / 2),
                    (x + grid_unit / 2, y - grid_unit / 2),
                ]
            )
            grid[i, j] = cell.intersects(mp)

    _i, _j = np.where(grid)
    return [(x + 1, y) for (x, y) in zip(I[_i, _j], J[_i, _j], strict=False)]


def steps_to_corners(c: KCell, steps: list[StepDbu], start: PositionDbu) -> PointsDbu:
    corners = []
    prev = start
    for step in steps:
        x = step.get("x", None)
        y = step.get("y", None)
        dx = step.get("dx", None)
        dy = step.get("dy", None)
        match (x, y, dx, dy):
            case (x, None, dx, None):
                if isinstance(x, str):
                    x = get_port_position(c, x)[0]
                x = (prev[0] if x is None else x) + (dx or 0.0)
                y = prev[1]
            case (None, y, None, dy):
                if isinstance(y, str):
                    y = get_port_position(c, y)[1]
                x = prev[0]
                y = (prev[1] if y is None else y) + (dy or 0.0)
            case _:
                msg = (
                    f"Step {step} is a diagonal step! "
                    "A manhattan route can only move in x+dx OR y+dy per step."
                )
                raise ValueError(msg)
        prev = (x, y)
        corners.append(prev)
    return corners


def corners_to_directive_path(
    start: PositionDbu, stop: PositionDbu, corners: PointsDbu, radius_dbu: Dbu
) -> DirectivePointsDbu:
    x0, y0 = (int(x) for x in start)
    x1, y1 = (int(x) for x in stop)
    if len(corners) > 0:
        _corners = np.concatenate([np.asarray(corners), [(x1, y1)]])
    else:
        _corners = np.asarray([(x1, y1)])
    directive_path: DirectivePointsDbu = [
        (x0, y0, extract_orientation(start, _corners[0]))
    ]
    for i in range(_corners.shape[0] - 1):
        _, _, d0 = directive_path[-1]
        d0 = validate_orientation(d0)
        x0, y0 = subtract_bend_radius(_corners[i], d0, radius_dbu)
        directive_path.append((x0, y0, d0))
        d1 = extract_orientation(_corners[i], _corners[i + 1])
        x1, y1 = add_bend_radius(_corners[i], d1, radius_dbu)
        xc, yc = (int(x) for x in _corners[i])
        directive_path.append((xc, yc, "o"))
        directive_path.append((x1, y1, d1))

    _, _, d0 = directive_path[-1]
    x0, y0 = _corners[-1]
    directive_path.append((x0, y0, d0))
    return directive_path


def directive_path_to_sdbt(
    directive_path: DirectivePointsDbu,
) -> tuple[
    list[PointsDbu], list[OrientationChar], list[PointsDbu], list[OrientationTransition]
]:
    dirs: list[OrientationChar] = [d for (_, _, d) in directive_path]
    path = [(x, y) for (x, y, _) in directive_path]
    mask = np.array([d == "o" for d in dirs])
    if mask.any():
        idxs = np.where(mask)[0]
        _didxs = np.concatenate([[0], 1 + np.where((idxs[1:] - idxs[:-1]) > 1)[0]])
        didxs_ = np.concatenate([np.where((idxs[1:] - idxs[:-1]) > 1)[0], [-1]])
        _idxs = idxs[_didxs]
        idxs_ = idxs[didxs_] + 1
        transitions = [
            (dirs[i - 1], dirs[j]) for i, j in zip(_idxs, idxs_, strict=False)
        ]
        bends = [path[i - 1 : j + 1] for i, j in zip(_idxs, idxs_, strict=False)]
        straights = [
            [path[i], path[j]]
            for i, j in zip(
                np.concatenate([[0], idxs_]),
                np.concatenate([_idxs - 1, [-1]]),
                strict=False,
            )
        ]
        dirs = [dirs[i] for i in np.concatenate([[0], idxs_])]
    else:
        bends = []
        straights = [[path[0], path[-1]]]
        transitions = []
        dirs = [dirs[0]]
    return straights, dirs, bends, transitions


def corners_to_sdbt(
    start: PositionDbu, stop: PositionDbu, corners: PointsDbu, radius_dbu: Dbu
) -> tuple[
    list[PointsDbu], list[OrientationChar], list[PointsDbu], list[OrientationTransition]
]:
    directive_path = corners_to_directive_path(start, stop, corners, radius_dbu)
    return directive_path_to_sdbt(directive_path)


def extract_bend_radius(kcl: KCLayout, bend: KCellSpec) -> Dbu:
    c = kcl.get_component(bend, output_type=KCell)
    o1, o2 = [p.name for p in c.ports]
    x0, y0 = c.ports[o1].center
    x1, y1 = c.ports[o2].center
    br1 = max(x0, x1) - min(x0, x1)
    br2 = max(y0, y1) - min(y0, y1)
    if br1 != br2:
        msg = "Given bend is not a 90° bend!"
        raise ValueError(msg)
    return br1


def extract_waveguide_width(kcl: KCLayout, straight: KCellSpec) -> Dbu:
    c = KCell(kcl=kcl)
    r = c << kcl.get_component(straight, output_type=KCell)
    orient_east_at_origin(r)
    bbox = r.bbox()
    return bbox.top - bbox.bottom


def get_inv_dbu(kcl: KCLayout) -> Int:
    return int(1 / kcl.dbu)


def get_port_position(c: KCell, port_name: str) -> PositionWithDirectionDbu:
    port_name = str(port_name)
    if port_name.count(",") != 1:
        msg = f"port_name should be of format 'inst,port'. Got: {port_name}."
        raise ValueError(msg)
    inst_name, port_name = port_name.split(",")
    try:
        inst = c.insts[inst_name]
    except Exception as e:
        msg = f"KCell does not have an instance named '{inst_name}'."
        raise ValueError(msg) from e
    try:
        port = inst.ports[port_name]
    except Exception as e:
        msg = f"Instance '{inst_name}' does not have a port named '{port_name}'"
        raise ValueError(msg) from e
    return validate_position_with_orientation(port)


def _poly2np(poly: kdb.Polygon) -> NDArray[np.int64]:
    return np.array([(p.x, p.y) for p in poly.each_point_hull()], dtype=np.int64)
