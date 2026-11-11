"""
Wallpaper-group symmetry for tiled motifs (used by the Islamic geometry generator).

The groups p1, p2, p4 and p6 have rotation centres of order n = 1, 2, 4, 6. ``tile_centres`` puts the
tiles on the lattice the group needs (rectangular for p1/p2, square for p4, hexagonal for p6), and
``tiles`` hands out one ``TileAxes`` per tile: it collects the motif's fill/patch calls and, if the motif
is not already invariant under a rotation by 360/n degrees about the tile centre, also draws its
rotated copies, so every tile centre is an n-fold rotation centre.
"""

import math

import matplotlib.pyplot as plt
import numpy as np

ORDER = {'p1': 1, 'p2': 2, 'p4': 4, 'p6': 6}
TOL = 1e-9


def tile_centres(rep_x, rep_y, symmetry):
    """(x, y, i, j) of each tile, column by column, centred in [-1, 1]^2."""
    out = []
    if symmetry == 'p4':
        a = min(2 / rep_x, 2 / rep_y)
        ox, oy = -rep_x * a / 2, -rep_y * a / 2
        for i in range(rep_x):
            for j in range(rep_y):
                out.append((ox + (i + 0.5) * a, oy + (j + 0.5) * a, i, j))
    elif symmetry == 'p6':
        h = math.sqrt(3) / 2
        a = min(2 / (rep_x + 0.5), 2 / (rep_y * h))
        ox, oy = -(rep_x + 0.5) * a / 2, -rep_y * a * h / 2
        for i in range(rep_x):
            for j in range(rep_y):
                out.append((ox + (i + 0.5 + 0.5 * (j % 2)) * a, oy + (j + 0.5) * a * h, i, j))
    else:  # p1, p2: the original rectangular layout
        for i in range(rep_x):
            for j in range(rep_y):
                out.append((-1 + (i + 0.5) * 2 / rep_x, -1 + (j + 0.5) * 2 / rep_y, i, j))
    return out


def _rotate(xs, ys, cx, cy, k, n):
    c, s = math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n)
    return ([cx + (x - cx) * c - (y - cy) * s for x, y in zip(xs, ys)],
            [cy + (x - cx) * s + (y - cy) * c for x, y in zip(xs, ys)])


def _same_points(ax_, ay_, bx, by):
    """Same set of points (order and repeats ignored), to TOL."""
    def uniq(xs, ys):
        pts = []
        for p in zip(xs, ys):
            if not any(abs(p[0] - q[0]) <= TOL and abs(p[1] - q[1]) <= TOL for q in pts):
                pts.append(p)
        return pts
    a, b = uniq(ax_, ay_), uniq(bx, by)
    return len(a) == len(b) and all(any(abs(p[0] - q[0]) <= TOL and abs(p[1] - q[1]) <= TOL for q in b) for p in a)


class TileAxes:
    """Collects one tile's ax.fill / ax.add_patch(Circle) calls; flush() draws them n-fold symmetric."""

    def __init__(self, ax, cx, cy, n):
        self.ax, self.cx, self.cy, self.n, self.prims = ax, cx, cy, n, []

    def fill(self, x, y, **kw):
        self.prims.append(('fill', [float(v) for v in x], [float(v) for v in y], kw))

    def add_patch(self, circle):
        self.prims.append(('circle', [float(circle.center[0])], [float(circle.center[1])], circle))

    def invariant(self):
        if self.n == 1:
            return True
        for kind, xs, ys, kw in self.prims:
            rx, ry = _rotate(xs, ys, self.cx, self.cy, 1, self.n)
            if not any(k2 == kind and (kw2 is kw or kw2 == kw or (kind == 'circle' and _same_circle(kw, kw2)))
                       and _same_points(rx, ry, x2, y2) for k2, x2, y2, kw2 in self.prims):
                return False
        return True

    def flush(self):
        copies = 1 if self.invariant() else self.n
        for k in range(copies):
            for kind, xs, ys, kw in self.prims:
                x, y = (xs, ys) if k == 0 else _rotate(xs, ys, self.cx, self.cy, k, self.n)
                if kind == 'fill':
                    self.ax.fill(np.array(x), np.array(y), **kw)
                elif k == 0:
                    self.ax.add_patch(kw)
                else:
                    self.ax.add_patch(plt.Circle((x[0], y[0]), kw.radius, color=tuple(kw.get_facecolor())))


def _same_circle(a, b):
    return abs(a.radius - b.radius) <= TOL and tuple(a.get_facecolor()) == tuple(b.get_facecolor())


def tiles(ax, rep_x, rep_y, symmetry):
    """Yield (x_center, y_center, i, j, tile_ax) per tile; each tile is drawn when the next one is requested."""
    n = ORDER.get(symmetry, 1)
    for cx, cy, i, j in tile_centres(rep_x, rep_y, symmetry):
        tile = TileAxes(ax, cx, cy, n)
        yield cx, cy, i, j, tile
        tile.flush()
