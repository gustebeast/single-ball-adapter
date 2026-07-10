"""The STADB05 single-ball string adapter body.

Built as an L-shaped cross-section in the XZ plane, extruded along Y
(the string-spread direction), then drilled:

  - 2 countersunk mounting holes through the back wall (head on face B,
    shank exits face C) — clamps the adapter to the bridge.
  - 5 string grooves along the bottom face F.
  - 5 vertical clamp-screw holes (insert counterbore from face D down
    into each string groove) — a screw drives into each string's ball
    end to lock it.

All geometry is parametric — see src/dimensions.py.
"""

import cadquery as cq

from .helpers import cyl, countersink_cutter_x
from .dimensions import (
    WALL_T, INNER_V, INNER_H, FOOT_H, LEG_H, FOOT_LEN, WIDTH,
    DOME_A, DOME_B,
    MOUNT_SPACING, MOUNT_FROM_D, MOUNT_BORE_D, MOUNT_HEAD_D,
    TRUSS_D, TRUSS_Z,
    STRING_COUNT, STRING_SPACING, STRING_TUBE_D, TUBE_TOP_Z,
    CLAMP_SCREW_CLR_D, CLAMP_INSERT_PILOT_D, CLAMP_INSERT_DEPTH, CLAMP_X,
    BOOL_OVERSHOOT,
)

OV = BOOL_OVERSHOOT


def _centred_positions(count: int, spacing: float) -> list[float]:
    """`count` positions, `spacing` apart, centred on 0."""
    return [(i - (count - 1) / 2.0) * spacing for i in range(count)]


def _l_profile() -> cq.Workplane:
    """The L cross-section, extruded along Y and centred on y = 0.

    Profile points in the XZ plane (face B at x=0, foot extends +X,
    foot bottom face F at z=0):
        (0, 0)          bottom-left  (B ∩ F)
        (0, LEG_H)      top-left     (top of face B)
        (WALL_T, LEG_H) top-right    (face A)
        (WALL_T, FOOT_H)inner corner (foot of face C)
        (FOOT_LEN, FOOT_H)           (end of ledge D)
        (FOOT_LEN, 0)                (foot of face E)
    """
    pts = [
        (0.0, 0.0),
        (0.0, LEG_H),
        (WALL_T, LEG_H),
        (WALL_T, FOOT_H),
        (FOOT_LEN, FOOT_H),
        (FOOT_LEN, 0.0),
    ]
    return (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .extrude(WIDTH / 2.0, both=True)
    )


def _dome(body: cq.Workplane) -> cq.Workplane:
    """Trim the part's -X silhouette (face B) to a half-ellipse: a flat bottom
    edge at z=0 (full width) with an elliptical curve rising to the apex.
    Intersecting the whole body with an X-axis elliptical prism domes both the
    leg and the foot. Face B stays planar at x=0 — only its outline changes."""
    prism = (
        cq.Workplane("YZ").workplane(offset=-OV)
        .ellipse(DOME_A, DOME_B)               # semi-axes: Y=DOME_A, Z=DOME_B
        .extrude(FOOT_LEN + 2 * OV)            # along +X through the whole part
    )
    return body.intersect(prism)


def _mount_holes(body: cq.Workplane) -> cq.Workplane:
    """2 countersunk holes through the back wall, axis along X."""
    z = FOOT_H + MOUNT_FROM_D
    for y in _centred_positions(2, MOUNT_SPACING):
        body = body.cut(
            countersink_cutter_x(
                bore_d=MOUNT_BORE_D,
                head_d=MOUNT_HEAD_D,
                x_face_c=WALL_T,
                x_face_b=0.0,
                y=y,
                z=z,
                overshoot=OV,
            )
        )
    return body


def _truss_hole(body: cq.Workplane) -> cq.Workplane:
    """Truss-rod access bore through the back wall (axis along X), centred
    between the two mount holes (y=0) at their height. Plain through-hole."""
    bore = (
        cq.Workplane("YZ").workplane(offset=-OV)
        .center(0.0, TRUSS_Z).circle(TRUSS_D / 2)
        .extrude(WALL_T + 2 * OV)
    )
    return body.cut(bore)


def _string_tubes(body: cq.Workplane) -> cq.Workplane:
    """5 through-tubes along the foot (axis along X), one per string. Each goes
    all the way through — open at both the back (face B) and front (face E).
    Diameters differ per string (STRING_TUBE_D, ascending Y); all tube tops
    sit at the same height (TUBE_TOP_Z), so only the diameters vary."""
    ys = _centred_positions(STRING_COUNT, STRING_SPACING)
    for y, d in zip(ys, STRING_TUBE_D):
        center_z = TUBE_TOP_Z - d / 2               # top aligned, centre varies
        tube = (
            cq.Workplane("YZ")
            .workplane(offset=-OV)                  # open through face B (x=0)
            .center(y, center_z)                    # (Y, Z) of the tube axis
            .circle(d / 2)
            .extrude(FOOT_LEN + 2 * OV)            # open through face E (+X)
        )
        body = body.cut(tube)
    return body


def _clamp_holes(body: cq.Workplane) -> cq.Workplane:
    """5 clamp screws entering from the bottom face F (-Z), pointing up (+Z),
    perpendicular to the string tubes: a Ø3.3 heat-set insert pocket (McMaster
    94459A110) at the face-F mouth, with an M2 shaft-clearance bore continuing
    up to the string tube's AXIS — one tube radius in (halfway through). It
    stops there so it opens into the tube without piercing the far wall / the
    solid roof above. Per-string, since tube centres differ with diameter."""
    ys = _centred_positions(STRING_COUNT, STRING_SPACING)
    for y, d in zip(ys, STRING_TUBE_D):
        tube_center_z = TUBE_TOP_Z - d / 2          # tops aligned, centre varies
        # M4 insert pocket — opens on face F (z = 0), up by CLAMP_INSERT_DEPTH.
        pocket = cyl(CLAMP_INSERT_PILOT_D, CLAMP_INSERT_DEPTH + OV,
                     z=-OV).translate((CLAMP_X, y, 0))
        # M4 set-screw clearance — from inside the insert up to the tube axis.
        shaft_z0 = CLAMP_INSERT_DEPTH - OV          # overlap into the pocket
        shaft_h = tube_center_z - shaft_z0          # top lands on the tube axis
        shaft = cyl(CLAMP_SCREW_CLR_D, shaft_h,
                    z=shaft_z0).translate((CLAMP_X, y, 0))
        body = body.cut(pocket).cut(shaft)
    return body


def _build_adapter() -> cq.Workplane:
    body = _l_profile()
    body = _dome(body)
    body = _mount_holes(body)
    body = _truss_hole(body)
    body = _string_tubes(body)
    body = _clamp_holes(body)
    return body


adapter = _build_adapter()
