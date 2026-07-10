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
from cadkit.step_export import export_step

from .helpers import heal
from . import adapter as _adapter_mod

adapter = heal(_adapter_mod.adapter)

# Map of part name → (workplane, output filename, optional note).
PARTS = {
    "adapter": (adapter, "adapter.step", "STADB05 5-string single-ball adapter body"),
}


def _export(name: str) -> None:
    obj, path, note = PARTS[name]
    export_step(obj, path)
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
