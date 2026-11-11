"""
Aperiodic rhomb tilings by de Bruijn's multigrid (dual grid) method.

A multigrid is N families of parallel lines x . e_i + gamma_i = n (n integer), e_i unit vectors.
Every crossing of a line of family j with a line of family k gives one tile: the rhomb with edges
e_j and e_k whose vertices are sum_i K_i e_i, where K_i = floor(x . e_i + gamma_i) is the index of the
strip of family i containing the crossing point x (and K_j, K_k take the two values around it).
Tiles meet edge to edge and cover the plane without gaps or overlaps.

- Penrose P3 (thick 72/108 and thin 36/144 rhombs): the pentagrid, e_i at 72-degree steps, with
  shifts gamma_i summing to 0 (de Bruijn 1981).
- Ammann-Beenker (45/135 rhombs and squares): the 4-grid, e_i at 45-degree steps (Beenker 1982).

Pure Python floats in a fixed order, so web/static/aperiodic.js reproduces the numbers.
"""

import math

# Generic shifts: no three grid lines meet in a point (that would make the tiling singular).
PENTAGRID_GAMMA = (0.13, 0.27, 0.09, -0.21, -0.28)  # sum 0: a true Penrose tiling
TETRAGRID_GAMMA = (0.11, 0.23, 0.37, 0.49)


def multigrid_tiles(directions, gammas, size, extent=1.0):
    """Rhombs of edge `size` covering the square [-extent, extent]^2.

    directions: angles of the unit vectors e_i (radians). Returns a list of (j, k, vertices) where
    vertices are 4 (x, y) corners in order around the rhomb and j < k are the families of its edges.
    """
    n = len(directions)
    e = [(math.cos(a), math.sin(a)) for a in directions]
    # sum_i K_i e_i is about (n / 2) x, so grid points within this radius cover the view (plus a margin)
    reach = (extent * math.sqrt(2) / size + 2) * 2 / n + 2
    tiles = []
    for j in range(n):
        for k in range(j + 1, n):
            (ajx, ajy), (akx, aky) = e[j], e[k]
            det = ajx * aky - ajy * akx
            for nj in range(math.floor(gammas[j] - reach), math.ceil(gammas[j] + reach) + 1):
                for nk in range(math.floor(gammas[k] - reach), math.ceil(gammas[k] + reach) + 1):
                    bj, bk = nj - gammas[j], nk - gammas[k]
                    px = (bj * aky - bk * ajy) / det
                    py = (ajx * bk - akx * bj) / det
                    if px * px + py * py > reach * reach:
                        continue
                    K = [math.floor(px * e[i][0] + py * e[i][1] + gammas[i]) for i in range(n)]
                    corners = []
                    for a, b in ((nj - 1, nk - 1), (nj, nk - 1), (nj, nk), (nj - 1, nk)):
                        K[j], K[k] = a, b
                        x = y = 0.0
                        for i in range(n):
                            x += K[i] * e[i][0]
                            y += K[i] * e[i][1]
                        corners.append((x * size, y * size))
                    cx = sum(c[0] for c in corners) / 4
                    cy = sum(c[1] for c in corners) / 4
                    if abs(cx) <= extent + size and abs(cy) <= extent + size:
                        tiles.append((j, k, corners))
    return tiles


def penrose_p3(size, extent=1.0):
    """Penrose P3 rhombs: (is_thick, vertices). Thick rhombs have edge families 1 or 4 steps apart (72 deg)."""
    dirs = [2 * math.pi * i / 5 for i in range(5)]
    return [((k - j) in (1, 4), v) for j, k, v in multigrid_tiles(dirs, PENTAGRID_GAMMA, size, extent)]


def ammann_beenker(size, extent=1.0):
    """Ammann-Beenker tiles: (is_square, vertices). Squares have edge families 2 steps apart (90 deg)."""
    dirs = [math.pi * i / 4 for i in range(4)]
    return [((k - j) == 2, v) for j, k, v in multigrid_tiles(dirs, TETRAGRID_GAMMA, size, extent)]
