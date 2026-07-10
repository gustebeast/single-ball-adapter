"""Top-level dimensions and fit clearances for the STADB05 adapter.

Coordinate system (matches the ASCII sketch in the README):

      Z (up)
      ^
      |   A = top of mounting leg (leg thickness)
      |  ___
      |  | |      C = inner vertical face (fit-critical)
      |  | |__D__ D = inner horizontal ledge (fit-critical)
      |  |______| E = foot outer face
      +----------> X (foot extends +X; back/outer face B at x = 0)
         F = bottom face (holds the 5 strings)

   Y = width (the 5 strings run side-by-side along Y; the part is
       extruded along Y and centred on y = 0).

Only C and D matter for the adapter to clip correctly onto the bass
bridge — they're the inside corner that grips the bridge edge. Everything
flagged "INFERRED" below is a best-guess placeholder to be confirmed.
"""

# ── L cross-section (the XZ profile that gets extruded along Y) ───────────────
WALL_T   =  4.3   # A — mounting-leg / back-wall thickness (given ≈4.3)
INNER_V  = 17.0   # C — inner vertical face height  [FIT-CRITICAL]
INNER_H  = 15.0   # D — inner horizontal ledge depth [FIT-CRITICAL]
FOOT_H   = 11.0   # E — foot outer-face height. Thickened from the ≈8 given so
                  #     the foot can stack, bottom-up: the M4 heat-set insert in
                  #     the floor (~5 mm) + the string tube (TUBE_D) + a 1 mm
                  #     solid roof the clamp screw presses the string against.
                  #     Sized to the short McMaster 94459A150 insert (4.7 mm).
                  #     Doesn't touch the fit (C and D keep their lengths).

# Derived outer envelope of the profile:
LEG_H    = FOOT_H + INNER_V        # B — full leg height  = 25.0
FOOT_LEN = WALL_T + INNER_H        # F — full bottom span = 19.3

# ── Width (Y) — spans the 5 strings (36 mm centre span) + wall margin ─────────
WIDTH = 44.0      # INFERRED total width along Y, centred on y = 0.
                  # 36 mm string span + Ø4 outer tubes → ±20 mm; 2 mm wall each
                  # side. Confirm against the real part's outer dimension.

# ── Curved back face (face B) ─────────────────────────────────────────────────
# On the original part the -X face (the one carrying the screw heads) isn't a
# rectangle — it's a domed D-shape: a flat bottom edge (z = 0, full width) with
# a curve rising over the top. Traced from the original (grid = 4.21 mm) and
# modelled here as a half-ellipse, intersected with the whole body. The flat
# edge stays flat; only the curved boundary is replicated.
# (First-pass ellipse fit — tweak DOME_A / DOME_B, or supply exact points.)
DOME_A = WIDTH / 2     # semi-axis along Y  = half the flat-edge length
DOME_B = LEG_H         # semi-axis along Z  = rise to the apex (at y = 0)

# ── Mounting screws — through the back wall (enter face C, head on face B) ─────
# Fully specified by the brief.
MOUNT_COUNT     =  2
MOUNT_SPACING   = 20.0   # centre-to-centre along Y
MOUNT_FROM_D    =  5.7   # centre distance above face D  →  z = FOOT_H + 5.7
MOUNT_BORE_D    =  3.4   # hole Ø at face C (shank clearance)
MOUNT_HEAD_D    =  6.3   # countersink Ø at face B (screw head)

# ── String tubes — through-bores along the foot, one per string ───────────────
# Each string runs in a fully-enclosed tube (axis along X) that goes ALL THE
# WAY THROUGH — open at both the back (face B) and the front (face E). The
# clamp screw (from face F below) locks each string in its tube.
STRING_COUNT    =  5
STRING_SPACING  =  9.0   # centre-to-centre along Y (36 mm string-1→string-5
                         #          span ÷ 4 gaps). Assumes even spacing.

# 3D-print hole shrink: a modelled Ø4.0 bore came out Ø3.8, so holes close up
# by ~0.2 mm on Ø. Compensate by enlarging every modelled bore so it shrinks
# to the intended final size.
HOLE_SHRINK_COMP = 0.2
# Desired FINAL (printed) tube Ø per string, ordered by ascending Y
# (string 1 at -Y → string 5 at +Y):
STRING_TUBE_FINAL_D = [2.2, 2.7, 3.1, 3.8, 4.0]
# Modelled (pre-print) diameters — each enlarged by the shrink compensation:
STRING_TUBE_D = [d + HOLE_SHRINK_COMP for d in STRING_TUBE_FINAL_D]

TUBE_ROOF       =  1.0   # solid roof above each tube — gap from the tube top
                         #          up to the +Z face (face D)
TUBE_TOP_Z      = FOOT_H - TUBE_ROOF                 # every tube's top sits here
TUBE_FLOOR_MIN  = TUBE_TOP_Z - max(STRING_TUBE_D)    # thinnest floor (widest tube)

# ── Truss-rod access hole — through the back wall, between the mount holes ─────
# Lets a truss-rod tool pass through the adapter to the rod behind it. Centred
# between the two mounting screws (y = 0) and at the same height; axis along X.
# Modelled oversize by the same print-shrink compensation as the other bores.
TRUSS_FINAL_D = 9.0                          # desired final Ø
TRUSS_D       = TRUSS_FINAL_D + HOLE_SHRINK_COMP    # = 9.2 modelled
TRUSS_Z       = FOOT_H + MOUNT_FROM_D         # same height as the mount holes

# ── Clamp set-screw hardware — M4 socket set screw + M4 heat-set insert ───────
# Upsized from M2 so it drives with the bass's 2 mm hex key (M4 set screws take
# a 2 mm hex) and the larger tip makes solid contact with the string. Insert is
# a tapered brass heat-set type for plastic (McMaster 94459-series M4, same
# style as the M2 ones that worked well). The insert presses into face F; the
# set screw threads up through it and its tip presses the string against the
# roof — tighten it and the screw recesses (it never protrudes past face F).
#
# VALUES ARE TYPICAL M4 — confirm against the datasheet of the insert you buy.
CLAMP_SCREW_CLR_D    = 4.5   # M4 set-screw shaft clearance (Ø4 + ~0.25/side).
                             # Screw: McMaster 91390A114 (M4×0.7 cup-tip, 10 mm).
CLAMP_INSERT_PILOT_D = 5.6   # 94459A150 spec: 7/32" (5.56 mm) drill, 5.6 mm max
                             # hole. NOT shrink-compensated on purpose — it'll
                             # print ~0.2 mm under, staying within the max and
                             # giving the heat-set insert a slightly tighter
                             # grip. (Bump to 5.8 if you'd rather print at 5.6.)
CLAMP_INSERT_DEPTH   = 5.0   # McMaster 94459A150 is 4.7 mm long + 0.3 relief
CLAMP_INSERT_MIN_MAT = 5.5   # 94459A150 "For Minimum Material Thickness"

# ── Clamp position — one per string, vertical, entering from face F (-Z) ──────
# Each clamp sits over its own string tube; X is an explicit coordinate (Y
# comes from the string spacing).
CLAMP_X = 2.0 + CLAMP_INSERT_PILOT_D / 2    # = 4.8. Insert hole sits 2 mm in
                         #          from the -X end of face F (the face-B edge):
                         #          2 mm wall + the Ø5.6 pilot radius.

# ── Fits & boolean hygiene ────────────────────────────────────────────────────
FIT_CLR        = 0.15    # standard slip-fit clearance, per side
BOOL_OVERSHOOT = 0.5     # extend cutters past faces for clean booleans

# ── Sanity asserts (cheap guards against typo'd edits) ────────────────────────
assert MOUNT_HEAD_D > MOUNT_BORE_D, "countersink must be wider than the bore"
assert MOUNT_SPACING < WIDTH, "mount screws must fit within the width"
assert (STRING_COUNT - 1) * STRING_SPACING < WIDTH, "strings overrun the width"
assert MOUNT_FROM_D < INNER_V, "mount holes must land on face C"
assert len(STRING_TUBE_D) == STRING_COUNT, "need one tube Ø per string"
assert STRING_SPACING > max(STRING_TUBE_D), "string tubes overlap"
assert TUBE_ROOF > 0, "no solid roof left above the tube"
assert CLAMP_INSERT_DEPTH < TUBE_FLOOR_MIN, "clamp insert breaks into the widest tube"
assert TUBE_FLOOR_MIN >= CLAMP_INSERT_MIN_MAT, \
    "floor under widest tube below insert's min material thickness (5.5 mm)"
assert CLAMP_INSERT_PILOT_D / 2 <= CLAMP_X <= FOOT_LEN - CLAMP_INSERT_PILOT_D / 2, \
    "clamp insert hole runs off the foot ends"
assert STRING_SPACING > CLAMP_INSERT_PILOT_D, "clamp inserts overlap between strings"
assert TRUSS_D / 2 + MOUNT_HEAD_D / 2 < MOUNT_SPACING / 2, "truss hole overlaps a mount hole"
