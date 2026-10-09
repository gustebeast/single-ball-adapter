"""STADB05 single-ball string adapter — main build script.

Run from the repo root:
  py -3.12 -m src.build              # build all parts
  py -3.12 -m src.build --part NAME  # build only one part (faster iteration)
  py -3.12 -m src.build --list       # list available part names

Produces a STEP file per part in the repo root.
"""

import argparse
import pathlib
import sys

import cadquery as cq

# Shared FreeCAD viewer helper (Archive/3D/freecad). show() makes the build's
# output viewable — opens or refreshes its tab in the FreeCAD hub. Never raises.
from cadkit.freecad import show
from cadkit.step_export import export_print
from cadkit.orientation import (PrintOrientation as PO,
                                require_declared, unconfirmed)

from .helpers import heal
from . import adapter as _adapter_mod

adapter = heal(_adapter_mod.adapter)

# Map of part name → (workplane, output filename, optional note).
PARTS = {
    "adapter": (adapter, "adapter.step", "STADB05 5-string single-ball adapter body"),
}

# ── PRINT ORIENTATION — the adapter's bed face, declared once, where cadkit's
# export reads it (cadkit/AGENTS.md).
#
# STANDS ON ITS +x FACE (user, 2026-10-08). That face is the bed and the part
# builds toward -x. Measured against all six axis-aligned candidates
# (cadkit.tools.suggest_orientation, 0.8 nozzle):
#
#   ((0, 1, 0), -90)  +x face down   148 mm2 unsupported   806 mm2 on the plate
#   None (as modelled)               381 mm2               726 mm2
#   ((0, 1, 0), 90)   -x face down   560 mm2               425 mm2
#   'flip'                           996 mm2                 7 mm2
#
# so it is 2.6x less unsupported face than printing it as modelled, on a wider
# base. It also decides the LAYER DIRECTION, which is the part that no overhang
# number can see: this adapter carries string tension, so the question was
# whether that load is pulled across layer boundaries or along beads. The user
# settled it.
#
# Before this the STEP exported as modelled, because nothing had ever declared
# a bed face and export could not tell that from a deliberate choice (#1070).
PRINT_ORIENTATION = {
    "adapter": PO.from_build_dir(
        (-1.0, 0.0, 0.0),
        "stands on its +x face and builds toward -x (user) — 148 mm2 of "
        "unsupported face against 381 as modelled, on an 806 mm2 base, and "
        "the string tension then runs the way the user wants it through the "
        "layers"),
}
require_declared(set(PARTS), PRINT_ORIENTATION)


def _export(name: str) -> None:
    obj, path, note = PARTS[name]
    export_print(obj, PRINT_ORIENTATION[name], path)
    suffix = f"  ({note})" if note else ""
    print(f"Wrote {path}{suffix}")


def main() -> None:
    p = argparse.ArgumentParser(
        prog="src.build", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--part", help="Build only this part.")
    p.add_argument("--list", action="store_true", help="List part names and exit.")
    args = p.parse_args()

    # 🚩 an UNCONFIRMED bed face is a guess nobody has checked — and the bed
    # face decides which faces are overhangs, so work done on top of a guess
    # can be silently wrong. Say so on every build (cadkit AGENTS.md).
    flagged = unconfirmed(PRINT_ORIENTATION)
    if flagged:
        print("UNCONFIRMED print orientation (confirm with the user BEFORE "
              "working on these parts): " + ", ".join(flagged), flush=True)

    if args.list:
        for name in PARTS:
            print(name)
        return

    if args.part:
        if args.part not in PARTS:
            print(f"unknown part: {args.part!r}. Use --list to see options.",
                  file=sys.stderr)
            sys.exit(2)
        _export(args.part)
        show("adapter.step")
        return

    for name in PARTS:
        _export(name)
    show("adapter.step")


main()
