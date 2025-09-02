"""Bundle routing."""

from collections.abc import Iterable
from functools import partial

import numpy as np
from kfactory.kcell import ProtoTKCell
from kfactory.typings import KCellSpec

from . import pcells, util
from .fanin import add_fan_in
from .routing import add_route_astar
from .types import (
    Int,
    LayerLike,
    PortLike,
    Um,
    validate_orientation,
    validate_position_with_orientation,
)


def add_bundle_astar(
    component: ProtoTKCell,
    ports1: list[PortLike],
    ports2: list[PortLike],
    spacing: Um,
    bend: KCellSpec,
    straight: KCellSpec,
    layers: Iterable[LayerLike],
    grid_unit: Int = 500,
) -> list[None]:  # FIXME: GDSFactory expects a list of something...
    """Add a bundle route using the a-star algorithm.

    Args:
        component: The component to add the route into.
        ports1: the start ports
        ports2: the end ports
        spacing: the spacing between the waveguides in the bundle
        bend: the bend-spec to create bends with
        straight: the straight-spec to create straights with
        layers: the layers to avoid.
        grid_unit: the discretization unit for the a-star algorithm.

    """
    if len(ports1) != len(ports2):
        msg = "Number of start ports is different than number of end ports"
        raise ValueError(msg)
    num_ports = len(ports1)
    if num_ports == 0:
        msg = "No input/output ports given"
        raise ValueError(msg)
    xyo1 = [validate_position_with_orientation(p) for p in ports1]
    xyo2 = [validate_position_with_orientation(p) for p in ports2]
    os1 = [o for _, _, o in xyo1]
    os2 = [o for _, _, o in xyo2]
    if not all(o == os1[0] for o in os1):
        msg = f"Input port orientations are not all equal. Got: {os1}."
        raise ValueError(msg)
    if not all(o == os2[0] for o in os2):
        msg = f"Output port orientations are not all equal. Got: {os1}."
        raise ValueError(msg)

    o1 = validate_orientation(os1[0])
    o2 = validate_orientation(os2[0])
    if o1 == o2:
        # FIXME: this check seems necessary because the router doesn't
        # seem to find a solution anyway in this case :(
        msg = (
            f"The port orientation at the input needs to be different "
            f"from the port orientation at the output. Got: {o1!r}=={o2!r}."
        )
        raise ValueError(msg)

    if num_ports == 1:
        start = validate_position_with_orientation(ports1[0], invert_orientation=False)
        stop = validate_position_with_orientation(ports2[0], invert_orientation=True)
    else:
        inv_dbu = util.get_inv_dbu(component.kcl)
        spacing_dbu = round(spacing * inv_dbu)
        starts = add_fan_in(
            c=component,
            inputs=ports1,
            straight=straight,
            bend=bend,
            spacing_dbu=spacing_dbu,
        )
        stops = add_fan_in(
            c=component,
            inputs=ports2,
            straight=straight,
            bend=bend,
            spacing_dbu=spacing_dbu,
        )
        start = (*np.mean(starts, 0), o1)
        stop = (*np.mean(stops, 0), util.invert_orientation(o2))
        bend = partial(pcells.bends, bend, straight, num_ports, spacing)
        straight = partial(pcells.straights, straight, num_ports, spacing)

    add_route_astar(
        c=component,
        start=start,
        stop=stop,
        layers=layers,
        straight=straight,
        bend=bend,
        grid_unit=grid_unit,
    )
    return [None for _ in range(num_ports)]
