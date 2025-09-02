"""Fan in and fan out."""

import numpy as np
from kfactory.kcell import KCell, ProtoTKCell
from kfactory.layout import KCLayout
from kfactory.typings import KCellSpec
from numpy.typing import NDArray

from . import util
from .routing import add_route_from_steps
from .types import (
    Dbu,
    OrientationChar,
    PointsDbu,
    PortLike,
    StepDbu,
    validate_orientation,
    validate_position_with_orientation,
)

__all__ = ["add_fan_in"]


def add_fan_in(
    c: ProtoTKCell,
    inputs: list[PortLike],
    straight: KCellSpec,
    bend: KCellSpec,
    x_bundle_dbu: Dbu | None = None,
    y_bundle_dbu: Dbu | None = None,
    spacing_dbu: Dbu | None = None,
    start_dir: OrientationChar | None = None,
) -> NDArray[np.int64]:
    """Add a fan-in to a parent component.

    Args:
        c: the component to add the fan-in to
        inputs: the list of ports to start from
        straight: the straight-spec to create straights from
        bend: the bend-spec to create bends from
        x_bundle_dbu: the x-location where to form the confluence of the bundle
            will be two bend radiuses from the inputs if not given.
        y_bundle_dbu: the y-location where to form the confluence of the bundle
            will be somewhere in the middle if not given.
        spacing_dbu: the spacing between waveguides in the bundle
        start_dir: the start direction of the bundle (derived from ports if not given)

    """
    kc: KCell = util.as_kcell(c)
    invert_direction = False
    starts = [validate_position_with_orientation(p) for p in inputs]
    ds = [d for _, _, d in starts]
    if any(d != ds[0] for d in ds):
        msg = "start ports all need to have the same orientation."
        raise ValueError(msg)
    d0 = ds[0]
    start_dir = validate_orientation(start_dir)
    if d0 == "o":
        if start_dir == "o":
            msg = (
                "Please specify a start direction if your "
                "inputs don't have an orientation."
            )
            raise ValueError(msg)
        d0 = start_dir
    elif start_dir in ("o", d0):
        pass
    # elif d0 == util.invert_orientation(start_dir):
    #    invert_direction = True  # yes, that's allowed!
    else:
        msg = "Invalid start direction."
        raise ValueError(msg)

    # at this point d0 is guaranteed to be in "nesw"
    coord = 1 if d0 in "ew" else 0
    starts = np.array(sorted([(x, y) for x, y, _ in starts], key=lambda xy: xy[coord]))  # type: ignore[reportCallIssue]
    fan_ins = {
        "n": _fan_in_north_steps,
        "e": _fan_in_east_steps,
        "s": _fan_in_south_steps,
        "w": _fan_in_west_steps,
    }
    fan_in = fan_ins[d0]

    stepses, stops = fan_in(
        kc.kcl,
        [(x, y) for x, y in starts],
        straight,
        bend,
        x_bundle_dbu,
        y_bundle_dbu,
        spacing_dbu,
        invert_direction=invert_direction,
    )
    for start, stop, steps in zip(starts, stops, stepses, strict=False):
        add_route_from_steps(
            c=kc,
            start=start,
            stop=stop,
            steps=steps,
            straight=straight,
            bend=bend,
        )
    return stops


def _fan_in_east_steps(
    kcl: KCLayout,
    starts: PointsDbu,
    straight: KCellSpec,
    bend: KCellSpec,
    x_bundle_dbu: Dbu | None = None,
    y_bundle_dbu: Dbu | None = None,
    spacing_dbu: Dbu | None = None,
    *,
    invert_direction: bool = False,
) -> tuple[list[list[StepDbu]], np.ndarray]:
    # FIXME: invert direction not working properly.
    _starts = np.asarray(starts, dtype=np.int_)
    num_links = _starts.shape[0]
    wg_width_dbu = util.extract_waveguide_width(kcl, straight)
    _spacing_dbu = spacing_dbu or 2 * wg_width_dbu

    xs_start = _starts[:, 0]
    ys_start = _starts[:, 1]

    if y_bundle_dbu is None:
        _y_bundle_dbu = ys_start.mean()
        if num_links % 2:
            i = int(np.argmin(np.abs(ys_start - _y_bundle_dbu)))
            dys_start = ys_start[1:] - ys_start[:-1]
            dy = dys_start[min(i, dys_start.shape[0] - 1)]
            _y_bundle_dbu += dy / 2
    else:
        _y_bundle_dbu = int(y_bundle_dbu)

    if (xs_start[:] != xs_start[0]).any():
        msg = "start ports need to be vertically or horizontally aligned."
        raise ValueError(msg)

    ys_stop = np.sort(
        np.asarray(
            [
                _y_bundle_dbu - (i + 1) // 2 * _spacing_dbu * (2 * (i % 2) - 1)
                for i in range(num_links)
            ],
            dtype=np.int_,
        )
    )
    above = ((ys_start - ys_stop) > 0).sum()
    below = num_links - above
    radius_dbu = util.extract_bend_radius(kcl, bend)
    sign = 1 - 2 * invert_direction
    _x_bundle_dbu = x_bundle_dbu or (
        xs_start[0]
        + (1 - invert_direction)
        * (sign * 2 * radius_dbu + (max(above, below) - 1) * _spacing_dbu)
    )
    xs_stop = np.broadcast_to(np.int_(_x_bundle_dbu), ys_stop.shape)
    stops = np.stack([xs_stop, ys_stop], 1)

    steps = []
    for i, stop in enumerate(stops):
        steps.append(
            [
                {"dx": radius_dbu + max((below - i - 1), (i - below)) * _spacing_dbu},
                {"y": stop[1]},
            ]
        )
    return steps, stops


def _fan_in_west_steps(
    kcl: KCLayout,
    starts: PointsDbu,
    straight: KCellSpec,
    bend: KCellSpec,
    x_bundle_dbu: Dbu | None = None,
    y_bundle_dbu: Dbu | None = None,
    spacing_dbu: Dbu | None = None,
    *,
    invert_direction: bool = False,
) -> tuple[list[list[StepDbu]], np.ndarray]:
    # strategy: calculate east and adjust coordinates accordingly
    steps, stops = _fan_in_east_steps(
        kcl,
        starts,
        straight,
        bend,
        x_bundle_dbu,
        y_bundle_dbu,
        spacing_dbu,
        invert_direction=invert_direction,
    )
    stops[:, 0] = 2 * np.asarray(starts, dtype=np.int_)[:, 0] - stops[:, 0]
    for _steps in steps:
        for step in _steps:
            if "dx" in step:
                step["dx"] = -(step["dx"] or 0)
    return steps, stops


def _fan_in_north_steps(
    kcl: KCLayout,
    starts: PointsDbu,
    straight: KCellSpec,
    bend: KCellSpec,
    x_bundle_dbu: Dbu | None = None,
    y_bundle_dbu: Dbu | None = None,
    spacing_dbu: Dbu | None = None,
    *,
    invert_direction: bool = False,
) -> tuple[list[list[StepDbu]], np.ndarray]:
    # strategy: calculate east and adjust coordinates accordingly
    steps, stops = _fan_in_east_steps(
        kcl,
        [(y, x) for (x, y) in starts],
        straight,
        bend,
        y_bundle_dbu,
        x_bundle_dbu,
        spacing_dbu,
        invert_direction=invert_direction,
    )
    stops = np.stack([stops[:, 1], stops[:, 0]], 1)
    for _steps in steps:
        for step in _steps:
            if "dx" in step:
                step["dy"] = step.pop("dx")
            if "y" in step:
                step["x"] = step.pop("y")
    return steps, stops


def _fan_in_south_steps(
    kcl: KCLayout,
    starts: PointsDbu,
    straight: KCellSpec,
    bend: KCellSpec,
    x_bundle_dbu: Dbu | None = None,
    y_bundle_dbu: Dbu | None = None,
    spacing_dbu: Dbu | None = None,
    *,
    invert_direction: bool = False,
) -> tuple[list[list[StepDbu]], np.ndarray]:
    # strategy: calculate north and adjust coordinates accordingly
    steps, stops = _fan_in_north_steps(
        kcl,
        starts,
        straight,
        bend,
        x_bundle_dbu,
        y_bundle_dbu,
        spacing_dbu,
        invert_direction=invert_direction,
    )
    stops[:, 1] = 2 * np.asarray(starts, dtype=np.int_)[:, 1] - stops[:, 1]
    for _steps in steps:
        for step in _steps:
            if "dy" in step:
                step["dy"] = -(step["dy"] or 0)
    return steps, stops
