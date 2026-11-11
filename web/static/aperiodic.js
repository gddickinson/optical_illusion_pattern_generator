// Aperiodic rhomb tilings by de Bruijn's multigrid method: a port of patterns/aperiodic.py (same arithmetic order).
// Penrose P3 from the pentagrid (shifts summing to 0), Ammann-Beenker from the 4-grid at 45-degree steps.
export const PENTAGRID_GAMMA = [0.13, 0.27, 0.09, -0.21, -0.28];
export const TETRAGRID_GAMMA = [0.11, 0.23, 0.37, 0.49];

// Rhombs of edge `size` covering [-extent, extent]^2: [j, k, corners] with corners [[x, y] x 4].
export function multigridTiles(directions, gammas, size, extent = 1.0) {
  const n = directions.length, e = directions.map(a => [Math.cos(a), Math.sin(a)]);
  const reach = (extent * Math.sqrt(2) / size + 2) * 2 / n + 2, tiles = [];
  for (let j = 0; j < n; j++) {
    for (let k = j + 1; k < n; k++) {
      const [ajx, ajy] = e[j], [akx, aky] = e[k], det = ajx * aky - ajy * akx;
      for (let nj = Math.floor(gammas[j] - reach); nj <= Math.ceil(gammas[j] + reach); nj++) {
        for (let nk = Math.floor(gammas[k] - reach); nk <= Math.ceil(gammas[k] + reach); nk++) {
          const bj = nj - gammas[j], bk = nk - gammas[k];
          const px = (bj * aky - bk * ajy) / det, py = (ajx * bk - akx * bj) / det;
          if (px * px + py * py > reach * reach) continue;
          const K = e.map(([ex, ey], i) => Math.floor(px * ex + py * ey + gammas[i]));
          const corners = [[nj - 1, nk - 1], [nj, nk - 1], [nj, nk], [nj - 1, nk]].map(([a, b]) => {
            K[j] = a; K[k] = b;
            let x = 0, y = 0;
            for (let i = 0; i < n; i++) { x += K[i] * e[i][0]; y += K[i] * e[i][1]; }
            return [x * size, y * size];
          });
          const cx = corners.reduce((s, c) => s + c[0], 0) / 4, cy = corners.reduce((s, c) => s + c[1], 0) / 4;
          if (Math.abs(cx) <= extent + size && Math.abs(cy) <= extent + size) tiles.push([j, k, corners]);
        }
      }
    }
  }
  return tiles;
}

export const penroseP3 = (size, extent = 1.0) => multigridTiles([0, 1, 2, 3, 4].map(i => 2 * Math.PI * i / 5), PENTAGRID_GAMMA, size, extent)
  .map(([j, k, v]) => [k - j === 1 || k - j === 4, v]);
export const ammannBeenker = (size, extent = 1.0) => multigridTiles([0, 1, 2, 3].map(i => Math.PI * i / 4), TETRAGRID_GAMMA, size, extent)
  .map(([j, k, v]) => [k - j === 2, v]);
