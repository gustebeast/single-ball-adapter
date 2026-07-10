# Single-Ball String Adapter (Steinberger STADB05 replica)

A 3D-printable replica of the **Steinberger STADB05** — the single-ball
string adapter for 5-string headless basses. It clips onto the end of the
bridge and carries five clamp screws that lock each standard single-ball
string at the chosen length, so you're not limited to double-ball strings.

The part is an L-shaped cross-section extruded along the string-spread
direction:

```
      Z (up)
      ^      A = top of mounting leg (leg thickness ≈ 4.3)
      |  ___
      |  | |        C = inner vertical face   (17 mm, FIT-CRITICAL)
      |  | |__ D __ D = inner horizontal ledge (15 mm, FIT-CRITICAL)
      |  |________| E = foot outer face (≈ 8, may thicken for screws)
      +-------------> X   (foot extends +X; back/outer face B at x = 0)
          F = bottom face (the 5 strings sit here)

   Y = width — the 5 strings run side-by-side along Y; the profile is
       extruded along Y and centred on y = 0.
```

**Only C (17 mm) and D (15 mm)** must be exact — they're the inside corner
that grips the bridge edge. The mounting-screw spec is also fixed. Other
dimensions (overall width, string spacing/groove, clamp-hole geometry) are
parametric placeholders flagged `INFERRED` in `src/dimensions.py`, to be
confirmed against the real part.

## Building

```bash
py -3.12 -m pip install cadquery
py -3.12 -m src.build                  # build the part → adapter.step
py -3.12 -m src.build --part adapter   # build a single part (faster iteration)
py -3.12 -m src.build --list           # list available part names
```

(or run the convenience wrapper: `./build.sh`)

Render a PNG preview (iso + front + side + top) into `preview/`:

```bash
py -3.12 tools/preview.py              # render every .step in repo root
```

### Viewing

Every `py -3.12 -m src.build` also opens (or refreshes) `adapter.step` in the
shared FreeCAD viewer hub — best-effort via `Archive/3D/freecad`; it never
breaks the build. See `Archive/3D/freecad/README.md`.

Geometry-regression check:

```bash
py -3.12 tools/check_geometry.py              # diff against committed baseline
py -3.12 tools/check_geometry.py --update-baseline   # bless current as new baseline
```

## Source layout

| File                   | Contents                                                        |
|------------------------|-----------------------------------------------------------------|
| `src/dimensions.py`    | Top-level dimensional / fit constants + sanity asserts          |
| `src/helpers.py`       | Geometric helpers (`cyl`, `countersink_cutter_x`, `heal`)       |
| `src/adapter.py`       | The adapter body — L-profile, mount holes, string grooves, clamp holes |
| `src/build.py`         | Orchestrator: heals, exports STEP, opens the FreeCAD viewer. CLI: `--part NAME` / `--list` |
| `tools/check_geometry.py` | bbox/volume/centroid regression check vs `baseline.tsv`      |
| `tools/preview.py`     | Headless matplotlib PNG renderer of the built STEP(s)           |

## Outputs

- `adapter.step` — the STADB05 adapter body
- `preview/adapter.png` — rendered preview panel

## Features modelled

- **L profile** with the fit-critical 17 mm (C) inner vertical face and
  15 mm (D) inner ledge.
- **Domed back face (face B)** — the -X face is a D-shape (flat bottom edge,
  elliptical curve over the top), traced from the original part. Modelled as
  a half-ellipse (`DOME_A` × `DOME_B`) intersected with the whole body.
- **2 countersunk mounting holes** through the back wall — Ø3.4 mm shank,
  coning to Ø6.3 mm for the head on face B, 20 mm apart, centred 5.7 mm
  above face D.
- **Truss-rod access hole** — Ø9 (final) bore through the back wall, centred
  between the two mount holes (y = 0) at their height, for a truss-rod tool.
  Modelled Ø9.2 with the print-shrink compensation.
- **5 string through-tubes** along the foot, on 9 mm centres (36 mm
  string-1→string-5 span), open at both ends (face B and face E). Each has
  its own diameter — final targets `[2.2, 2.7, 3.1, 3.8, 4.0]` mm from
  string 1 (−Y) to string 5 (+Y). Bores are modelled 0.2 mm oversize
  (`HOLE_SHRINK_COMP`) to compensate for print shrink. All tube tops sit
  1 mm below the +Z face, so only the diameters vary.
- **5 clamp set screws** entering from the **bottom face F (-Z), pointing up** —
  perpendicular to the strings. An **M4 heat-set insert** seats in a pocket in
  the floor; an **M4 cup-tip set screw (2 mm hex)** runs up to each tube's axis
  and presses the string against the solid tube roof. Sited at `CLAMP_X`.
  - Insert: **McMaster 94459A150** (M4 × 0.7, 4.7 mm long). *Confirm its
    "Installed Hole Diameter" — `CLAMP_INSERT_PILOT_D` is a 5.6 mm placeholder.*
  - Set screw: **McMaster 91390A114** (M4 × 0.7 cup-tip, 10 mm). Strings sit
    5.8–7.6 mm above face F, so a 10 mm screw protrudes ~2–4 mm below face F
    when clamped; drop to ~6–8 mm if you want it flush.

## Tuning

All constants live in `src/dimensions.py`. Anything marked `INFERRED`
is a placeholder — measure the real STADB05 and update it. The sanity
asserts at the bottom of that file catch obviously-inconsistent edits
(e.g. screws wider than the part).
