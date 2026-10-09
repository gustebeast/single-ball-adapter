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

# ── PRINT ORIENTATION — cadkit requires every printed part to declare its bed
# face, and export refuses one that has not (cadkit/AGENTS.md).
#
# 🚩 UNCONFIRMED. This records what the STEP has ALWAYS exported as — the part
# as modelled — so nothing about how it prints changes. It is NOT a studied
# decision, and this part is the kind where that matters most: it carries
# STRING TENSION, so the print direction decides whether that load is pulled
# across layer boundaries or along beads, and no overhang measurement can see
# a load path.
#
# What the measurement says, for whoever settles this
# (cadkit.tools.suggest_orientation, 0.8 nozzle):
#   ((0, 1, 0), -90)  on its +x face  148 mm2 unsupported, 806 mm2 on the
#                                     plate, aspect 0.7   <- best measured
#   None (as modelled)                381 mm2 unsupported, 726 mm2, aspect 1.5
#   'flip'                            996 mm2 unsupported, 7 mm2 on the plate
# so there is a real case for re-posing it onto its +x face — 2.6x less
# unsupported area and a wider base. CONFIRM THE LOAD DIRECTION FIRST.
PRINT_ORIENTATION = {
    "adapter": PO(None,
                  "as modelled — what this part's STEP has always exported "
                  "as, kept so the migration changes no print. UNSTUDIED: "
                  "see the note above; the +x face measures 2.6x less "
                  "unsupported area, but this part carries string tension "
                  "and the layer direction is the question, not the overhangs",
                  confirmed=False),
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
