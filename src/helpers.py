"""Geometric helper functions used by adapter.py.

Pure functions — no module-level state. Dimensions are passed in as
arguments OR pulled from src.dimensions.
"""

from __future__ import annotations

import cadquery as cq


def cyl(d: float, h: float, z: float = 0.0) -> cq.Workplane:
    """Solid cylinder, diameter d, height h, base at z (axis = +Z)."""
    return cq.Workplane("XY").workplane(offset=z).circle(d / 2).extrude(h)


def countersink_cutter_x(
    bore_d: float,
    head_d: float,
    x_face_c: float,
    x_face_b: float,
    y: float,
    z: float,
    overshoot: float,
) -> cq.Workplane:
    """Cutter for a back-wall mounting hole whose axis runs along X.

    The shank bore (bore_d) passes through the whole wall; a 90° countersink
    cone widens it from bore_d (at face C, x=x_face_c) out to head_d (at
    face B, x=x_face_b) so a flat screw head sits flush on the back face B.

    Both x_face_b < x_face_c are absolute X coordinates of the two faces.
    The cylinder/cone are oversized by `overshoot` past each face for a
    clean boolean cut.
    """
    wall_t = x_face_c - x_face_b
    # Shank bore — full wall plus overshoot at both ends.
    shank = (
        cq.Workplane("YZ")
        .workplane(offset=x_face_b - overshoot)
        .center(y, z)
        .circle(bore_d / 2)
        .extrude(wall_t + 2 * overshoot)
    )
    # Countersink cone: head_d at face B → bore_d at the cone's inner end.
    # 90° countersink → axial depth = (head_d - bore_d) / 2.
    cone_depth = (head_d - bore_d) / 2.0
    cone = (
        cq.Workplane("YZ")
        .workplane(offset=x_face_b - overshoot)
        .center(y, z)
        .circle(head_d / 2)                       # mouth at face B (+overshoot)
        .workplane(offset=overshoot + cone_depth)
        .circle(bore_d / 2)                        # throat where it meets the bore
        .loft()
    )
    return shank.union(cone)


def heal(wp: cq.Workplane) -> cq.Workplane:
    """Run OCCT's ShapeFix + ShapeUpgrade on a Workplane's underlying shape
    to clean up minor face/edge tolerance issues and merge same-domain
    adjacent faces before STEP export. Long cadquery boolean pipelines can
    accumulate tiny invalidities that pass cadquery's shallow validator but
    get flagged by strict STEP importers."""
    from OCP.ShapeFix import ShapeFix_Shape  # type: ignore[import]
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain  # type: ignore[import]
    from OCP.TopAbs import TopAbs_COMPOUND

    shape = wp.val().wrapped
    fixer = ShapeFix_Shape(shape)
    fixer.SetPrecision(1e-4)
    fixer.SetMaxTolerance(1e-3)
    fixer.Perform()
    fixed = fixer.Shape()
    try:
        unifier = ShapeUpgrade_UnifySameDomain(fixed, True, True, True)
        unifier.Build()
        unified = unifier.Shape()
    except Exception:
        unified = fixed
    if unified.ShapeType() == TopAbs_COMPOUND:
        wrapped = cq.Compound(unified)
    else:
        wrapped = cq.Solid(unified)
    return cq.Workplane("XY").add(wrapped)
