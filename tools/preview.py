"""Render PNG previews of the built STEP file(s).

Tessellates each .step in the repo root and renders a 2x2 panel
(isometric + front + side + top) into preview/<name>.png using matplotlib.
No GPU / pyrender needed — handy for eyeballing a build at a glance.

Usage:
  py -3.12 -m src.build                 # build first
  py -3.12 tools/preview.py             # render every .step in repo root
  py -3.12 tools/preview.py adapter.step
"""

from __future__ import annotations

import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt              # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402
import numpy as np                           # noqa: E402
import cadquery as cq                        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "preview")

# (elev, azim, title) for each panel.
VIEWS = [
    (25, -60, "iso"),
    (0, -90, "front (XZ)"),
    (0, 0, "side (YZ)"),
    (90, -90, "top (XY)"),
]


def _triangles(path: str) -> np.ndarray:
    """Return an (N, 3, 3) array of triangle vertices for a STEP file."""
    shape = cq.importers.importStep(path).val()
    verts, tris = shape.tessellate(0.2)          # 0.2 mm deflection
    v = np.array([(p.x, p.y, p.z) for p in verts])
    f = np.array(tris)
    return v[f]


def _set_equal_aspect(ax, tris: np.ndarray) -> None:
    pts = tris.reshape(-1, 3)
    mins, maxs = pts.min(axis=0), pts.max(axis=0)
    centre = (mins + maxs) / 2
    span = (maxs - mins).max() / 2 or 1.0
    ax.set_xlim(centre[0] - span, centre[0] + span)
    ax.set_ylim(centre[1] - span, centre[1] + span)
    ax.set_zlim(centre[2] - span, centre[2] + span)


def render(path: str) -> str:
    tris = _triangles(path)
    fig = plt.figure(figsize=(10, 9))
    for i, (elev, azim, title) in enumerate(VIEWS, start=1):
        ax = fig.add_subplot(2, 2, i, projection="3d")
        coll = Poly3DCollection(tris, alpha=1.0, linewidths=0.1,
                                edgecolor=(0, 0, 0, 0.25))
        coll.set_facecolor((0.55, 0.65, 0.8))
        ax.add_collection3d(coll)
        _set_equal_aspect(ax, tris)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    name = os.path.splitext(os.path.basename(path))[0]
    fig.suptitle(name, fontsize=12)
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, f"{name}.png")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


def main() -> int:
    args = sys.argv[1:]
    if args:
        files = [a if os.path.isabs(a) else os.path.join(ROOT, a) for a in args]
    else:
        files = sorted(glob.glob(os.path.join(ROOT, "*.step")))
    if not files:
        sys.stderr.write("No .step files. Run `py -3.12 -m src.build` first.\n")
        return 2
    for f in files:
        print(f"Rendered {render(f)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
