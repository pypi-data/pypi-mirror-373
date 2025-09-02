"""Routing functions."""

from collections.abc import Iterable

from kfactory.kcell import KCell, ProtoTKCell
from kfactory.port import DPort, Port
from kfactory.typings import KCellSpec

from . import doroutes as _doroutes  # type: ignore[reportAttributeAccess]
from . import util
from .types import (
    Dbu,
    DirectivePointsDbu,
    LayerLike,
    OrientationChar,
    OrientationTransition,
    PointsDbu,
    PortLike,
    StepDbu,
    validate_layer,
    validate_position,
    validate_position_with_orientation,
)

__all__ = [
    "add_route_astar",
    "add_route_from_corners",
    "add_route_from_steps",
    "find_route_astar",
]


def add_route_astar(
    c: ProtoTKCell,
    start: PortLike,
    stop: PortLike,
    straight: KCellSpec,
    bend: KCellSpec,
    layers: Iterable[LayerLike],
    grid_unit: Dbu,
) -> None:
    """Add an a-star route to a component.

    Args:
        c: the component to add the route to
        start: the start port
        stop: the stop port
        straight: the straight-spec to create straights from
        bend: the bend-spec to create bends from
        layers: the layers to avoid
        grid_unit: the discretization unit for the a-star algorithm

    """
    corners = find_route_astar(c, start, stop, straight, bend, layers, grid_unit)
    _start = validate_position_with_orientation(start)
    _stop = validate_position_with_orientation(stop)
    add_route_from_corners(
        c=c,
        start=(_start[0], _start[1]),
        stop=(_stop[0], _stop[1]),
        corners=corners,
        straight=straight,
        bend=bend,
    )


def add_route_from_steps(
    c: ProtoTKCell,
    start: PortLike,
    stop: PortLike,
    steps: list[StepDbu],
    straight: KCellSpec,
    bend: KCellSpec,
) -> None:
    """Add a steps-based route to a component.

    Args:
        c: the component to add the route to
        start: the start port
        stop: the stop port
        steps: the steps in between start and stop.
        straight: the straight-spec to create straights from
        bend: the bend-spec to create bends from

    """
    _start = validate_position(start)
    _stop = validate_position(stop)
    corners = util.steps_to_corners(util.as_kcell(c), steps, _start)
    add_route_from_corners(c, _start, _stop, corners, straight, bend)


def add_route_from_corners(
    c: ProtoTKCell,
    start: PortLike,
    stop: PortLike,
    corners: PointsDbu,
    straight: KCellSpec,
    bend: KCellSpec,
) -> None:
    """Add a corners-based route to a component.

    Args:
        c: the component to add the route to
        start: the start port
        stop: the stop port
        corners: the corners in between start and stop.
        straight: the straight-spec to create straights from
        bend: the bend-spec to create bends from

    """
    _start = validate_position(start)
    _stop = validate_position(stop)
    radius_dbu = util.extract_bend_radius(c.kcl, bend)
    directive_path = util.corners_to_directive_path(_start, _stop, corners, radius_dbu)
    _add_route_from_directive_path(c, directive_path, straight, bend)


def _add_route_from_directive_path(
    c: ProtoTKCell,
    directive_path: DirectivePointsDbu,
    straight: KCellSpec,
    bend: KCellSpec,
) -> None:
    straights, dirs, bends, transitions = util.directive_path_to_sdbt(directive_path)
    _add_route(util.as_kcell(c), straights, dirs, bends, transitions, straight, bend)


def _add_route(
    c: KCell,
    straights: list[PointsDbu],
    directions: list[OrientationChar],
    bends: list[PointsDbu],
    transitions: list[OrientationTransition],
    straight: KCellSpec,
    bend: KCellSpec,
) -> None:
    inv_dbu = util.get_inv_dbu(c.kcl)
    for d, path in zip(directions, straights, strict=False):
        if path[0] == path[-1]:
            continue
        s = c.kcl.get_component(
            straight, output_type=KCell, length=util.straight_length(c.kcl, path)
        )
        r = c << s
        util.orient_at_origin(r, d)
        r.dmove((float(path[0][0] / inv_dbu), float(path[0][1] / inv_dbu)))
    for tran, path in zip(transitions, bends, strict=False):
        r = c << c.kcl.get_component(bend, output_type=KCell)
        util.orient_as_transition_at_origin(r, tran)
        r.dmove((float(path[0][0] / inv_dbu), float(path[0][1] / inv_dbu)))


def find_route_astar(
    c: ProtoTKCell,
    start: PortLike,
    stop: PortLike,
    straight: KCellSpec,
    bend: KCellSpec,
    layers: Iterable[LayerLike],
    grid_unit: Dbu,
) -> PointsDbu:
    """Find an a-star route without adding it to the component.

    Args:
        c: the component to find the route in
        start: the start port
        stop: the stop port
        straight: the straight-spec to create straights from
        bend: the bend-spec to create bends from
        layers: the layers to avoid
        grid_unit: the discretization unit for the a-star algorithm

    Returns:
        The corners of the route as a list of points in dbu.

    """
    kc: KCell = util.as_kcell(c)
    _layers = [validate_layer(kc.kcl, layer) for layer in layers]
    width_dbu = util.extract_waveguide_width(kc.kcl, straight)
    radius_dbu = util.extract_bend_radius(kc.kcl, bend)
    if grid_unit > 0.5 * radius_dbu:
        msg = "bend radius should at least be twice the grid unit."
        raise ValueError(msg)
    _grid_unit = int(radius_dbu / int(radius_dbu / grid_unit))
    bbox = kc.bbox()
    straight_width = width_dbu // grid_unit + 1
    straight_width += (straight_width + 1) % 2
    _bend = util.discretize_bend(kc.kcl, bend, _grid_unit, _layers)
    _start = validate_position_with_orientation(start)
    _stop = validate_position_with_orientation(
        stop, invert_orientation=isinstance(stop, Port | DPort)
    )
    return _doroutes.show(
        polys=util.extract_polys(kc, _layers),
        bbox=(
            bbox.top + 2 * radius_dbu,
            bbox.right + 2 * radius_dbu,
            bbox.bottom - 2 * radius_dbu,
            bbox.left - 2 * radius_dbu,
        ),
        start=_start,
        stop=_stop,
        grid_unit=_grid_unit,
        straight_width=straight_width,
        discretized_bend_east_to_north=_bend,
    )
