"""Test pcells.

NOTE: this submodule needs gdsfactory.
"""

from typing import Any

import numpy as np
from kfactory.instance import DInstance
from kfactory.kcell import DKCell
from kfactory.layout import KCLayout
from kfactory.typings import KCellSpec

from . import util
from .types import Int, OrientationChar, OrientationTransition, Um

try:
    from gdsfactory import kcl  # type: ignore[reportMissingImports]
except ImportError:
    kcl = KCLayout(name="test_pcells")

__all__ = []


@kcl.cell
def straights(
    straight: KCellSpec,
    num: Int,
    spacing: Um,
    **straight_kwargs: Any,
) -> DKCell:
    c = DKCell()
    cstraight = kcl.get_component(straight, **straight_kwargs)
    o1, o2 = [p.name for p in cstraight.ports]

    refs = [c.create_inst(cstraight) for _ in range(num)]
    util.orient_east_at_origin(refs[0].to_itype())
    c.add_port(name=o1, port=refs[0].ports[o1])
    c.add_port(name=o2, port=refs[0].ports[o2])

    for i in range(num):
        util.orient_east_at_origin(refs[i].to_itype())
        refs[i].dmove((0.0, float((num - 1) * spacing / 2 - i * spacing)))

    return c


@kcl.cell
def bends(
    bend: KCellSpec,
    straight: KCellSpec,
    num: Int,
    spacing: Um,
    **kwargs: Any,
) -> DKCell:
    c = DKCell()
    cbend = kcl.get_component(bend, output_type=DKCell, **kwargs)
    straight_kwargs = {
        k: kwargs.get(k) for k in ["cross_section", "width"] if k in kwargs
    }
    cstraights = [
        kcl.get_component(
            straight,
            output_type=DKCell,
            length=spacing * i,
            **straight_kwargs,
        )
        for i in range(1, num)
    ]
    o1 = str(next(p.name for p in cstraights[0].ports))
    b1, b2 = [p.name for p in cbend.ports]

    bend_refs = [c.create_inst(cbend) for _ in range(num)]
    for i in range(num):
        util.orient_east_to_north_at_origin(bend_refs[i].to_itype())

    straight_refs = [(c.create_inst(s), c.create_inst(s)) for s in cstraights]
    for i in range(num - 1):
        util.orient_east_at_origin(straight_refs[i][0].to_itype())
        util.orient_east_at_origin(straight_refs[i][1].to_itype())

    for i in range(num):
        bend_refs[i].dmove(
            (
                float(-i * spacing + (num - 1) * spacing),
                float(i * spacing - (num - 1) * spacing / 2),
            )
        )

    for i in range(num - 1):
        straight_refs[i][0].connect(o1, bend_refs[num - 2 - i].ports[b1])
        straight_refs[i][1].connect(o1, bend_refs[num - 2 - i].ports[b2])

    inv_dbu = util.get_inv_dbu(kcl)
    radius = util.extract_bend_radius(kcl, cbend) / inv_dbu
    c.add_port(name=b1, port=cbend.ports[b1])
    c.ports[b1].dcenter = (
        0.0,
        0.0,
    )
    c.add_port(name=b2, port=cbend.ports[b2])
    c.ports[b2].dcenter = (
        float(radius + (num - 1) * spacing / 2),
        float(radius + (num - 1) * spacing / 2),
    )
    return c


@kcl.cell
def frame(
    width: Um = 100,
    height: Um = 50,
    frame_width: Um = 1.0,
    straight: KCellSpec = "straight",
) -> DKCell:
    c = DKCell()
    h = kcl.get_component(
        straight,
        output_type=DKCell,
        length=width,
        width=frame_width,
    )
    v = kcl.get_component(
        straight,
        output_type=DKCell,
        length=height + 2 * frame_width,
        width=frame_width,
    )
    top = c.create_inst(h)
    util.orient_east_at_origin(top.to_itype())
    top.dmove((float(frame_width / 2), float(height + frame_width / 2)))
    btm = c.create_inst(h)
    util.orient_east_at_origin(btm.to_itype())
    btm.dmove((float(frame_width / 2), -float(frame_width / 2)))
    lft = c.create_inst(v)
    util.orient_east_at_origin(lft.to_itype())
    lft.drotate(90)
    lft.dmove((0.0, -float(frame_width)))
    rgt = c.create_inst(v)
    util.orient_east_at_origin(rgt.to_itype())
    rgt.drotate(90)
    rgt.dmove((float(width + frame_width), -float(frame_width)))
    return c


@kcl.cell
def field0(width: Um = 20, height: Um = 20, straight: KCellSpec = "straight") -> DKCell:
    c = DKCell()
    c.create_inst(frame(width, height))
    straight_in = kcl.get_component(straight, output_type=DKCell, length=1, width=1)
    ref = _named_inst(c, ref=straight_in, name="in")
    util.orient_east_at_origin(ref.to_itype())
    ref.dmove((1.5, 2.5))
    straight_out = kcl.get_component(straight, output_type=DKCell, length=1, width=1)
    ref = _named_inst(c, ref=straight_out, name="out")
    util.orient_east_at_origin(ref.to_itype())
    ref.dmove((float(width - 2.5), float(height - 2.5)))
    return c


@kcl.cell
def field1(width: Um = 50, height: Um = 50, straight: KCellSpec = "straight") -> DKCell:
    c = DKCell()
    c.create_inst(frame(width, height))
    ref = c.create_inst(
        kcl.get_component(
            straight, output_type=DKCell, length=4 / 5 * width, width=0.1 * height
        )
    )
    util.orient_east_at_origin(ref.to_itype())
    ref.dmove((0.5, float(29 / 50 * height)))
    ref = c.create_inst(
        kcl.get_component(
            straight, output_type=DKCell, length=0.1 * width, width=0.1 * height
        )
    )
    util.orient_east_at_origin(ref.to_itype())
    ref.dmove((float(0.9 * width + 0.5), float(3 / 5 * height)))
    ref = c.create_inst(
        kcl.get_component(straight, output_type=DKCell, length=4 / 5 * width, width=1)
    )
    util.orient_east_at_origin(ref.to_itype())
    ref.dmove((float(width - 4 / 5 * width + 0.5), 40.0))
    ref = _named_inst(
        c,
        ref=kcl.get_component(straight, output_type=DKCell, length=1, width=1),
        name="in",
    )
    util.orient_east_at_origin(ref.to_itype())
    ref.dmove((1.5, 2.5))
    ref = _named_inst(
        c,
        ref=kcl.get_component(straight, output_type=DKCell, length=1, width=1),
        name="out",
    )
    util.orient_east_at_origin(ref.to_itype())
    ref.dmove((float(width - 2.5), float(height - 2.5)))
    return c


@kcl.cell
def fanout_frame(
    width: Um = 100,
    num_inputs: Int = 5,
    input_spacing: Um = 40,
    straight: KCellSpec = "straight",
    orientation: OrientationChar = "e",
    *,
    add_frame: bool = True,
) -> DKCell:
    add_width = float(orientation in "ws")
    idx = 1 if orientation in "we" else 0
    c = DKCell()
    height = num_inputs * input_spacing
    cstraight = kcl.get_component(straight, output_type=DKCell, length=1)
    refs_in = [_named_inst(c, ref=cstraight, name=f"in{i}") for i in range(num_inputs)]
    for i in range(num_inputs):
        util.orient_at_origin(refs_in[i].to_itype(), orientation)
    for i in range(num_inputs):
        move = np.array([add_width, add_width]) * width
        move[idx] = float(height / 2 - (i + 1) // 2 * input_spacing * (2 * (i % 2) - 1))
        refs_in[i].dmove((move[0], move[1]))

    if add_frame:
        if idx == 1:
            c.create_inst(frame(width=width, height=height))
        else:
            c.create_inst(frame(width=height, height=width))

    for i in range(num_inputs):
        c.add_port(name=f"in{i}", port=refs_in[i].ports["o2"])
    return c


@kcl.cell
def fanout_frame2(
    width: Um = 100,
    num_inputs: Int = 5,
    input_spacing: Um = 40,
    output_spacing: Um = 30,
    straight: KCellSpec = "straight",
    transition: OrientationTransition = ("e", "w"),
    *,
    add_frame: bool = True,
) -> DKCell:
    c = DKCell()
    r1 = c << fanout_frame(
        width, num_inputs, input_spacing, straight, transition[0], add_frame=add_frame
    )
    r2 = c << fanout_frame(
        width, num_inputs, output_spacing, straight, transition[1], add_frame=False
    )
    for i, p in enumerate(r1.ports):
        c.add_port(name=f"in{i}", port=p)
    for i, p in enumerate(r2.ports):
        c.add_port(name=f"out{i}", port=p)
    return c


@kcl.cell
def fanout_frame3(
    width: Um = 100,
    num_inputs: Int = 5,
    input_spacing: Um = 40,
    output_spacing: Um = 30,
    straight: KCellSpec = "straight",
    transition: OrientationTransition = ("e", "w"),
) -> DKCell:
    c = DKCell()
    r1 = c << fanout_frame(
        width, num_inputs, input_spacing, straight, transition[0], add_frame=False
    )
    height = num_inputs * input_spacing
    r2 = c << fanout_frame(
        width, num_inputs, output_spacing, straight, transition[1], add_frame=False
    )
    r2.drotate(90.0).dmove((height, height / 2))
    for i, p in enumerate(r1.ports):
        c.add_port(name=f"in{i}", port=p)
    for i, p in enumerate(r2.ports):
        c.add_port(name=f"out{i}", port=p)
    return c


@kcl.cell
def routing_frame(
    num_links: int = 5,
    input_spacing: int = 60,
    output_spacing: int = 40,
    straight: KCellSpec = "straight",
    bend_radius: int = 5,
) -> DKCell:
    c = DKCell()
    height = num_links * input_spacing
    cstraight = kcl.get_component(straight, output_type=DKCell, length=1)
    refs_in = [_named_inst(c, ref=cstraight, name=f"in{i}") for i in range(num_links)]
    for i in range(num_links):
        refs_in[i].dmove(
            (0, height / 2 - (i + 1) // 2 * input_spacing * (2 * (i % 2) - 1))
        )
    refs_out = [_named_inst(c, ref=cstraight, name=f"out{i}") for i in range(num_links)]
    for i in range(num_links):
        refs_out[i].dmove(
            (
                0,
                6 * bend_radius
                + height / 2
                - (i + 1) // 2 * output_spacing * (2 * (i % 2) - 1),
            )
        )

    # starts = np.array(sorted([r.ports["o2"].center for r in refs_in]))
    # stops = np.array(sorted([r.ports["o1"].center for r in refs_out]))
    # above = ((starts[:, 1] - stops[:, 1]) > 0).sum()
    # below = num_links - above

    # width = int(2 * bend_radius + max(above, below) * output_spacing)
    width = 200
    c.create_inst(frame(width=width, height=height))
    for i in range(num_links):
        refs_out[i].dmove((width, 0))

    for i in range(num_links):
        c.add_port(name=f"in{i}", port=refs_in[i].ports["o2"])
        c.add_port(name=f"out{i}", port=refs_out[i].ports["o1"])
    return c


def _named_inst(c: DKCell, /, *, ref: DKCell, name: str) -> DInstance:
    inst = c << ref
    inst.name = name
    return inst
