// CellularAutomataGenerator (patterns/cellular.py), ported line by line. Grids are flat row-major arrays indexed
// [x * size + y], with x the first NumPy index as in the Python.
import { subplots } from './scene.js';
import { getPalette } from './colors.js';
import { pmod, range } from './np.js';

export const CELLULAR_DEFAULTS = { automata_type: 'game_of_life', grid_size: 100, generations: 50, initial_density: 0.3,
  initial_pattern: 'random', visualization: 'final_state', neighborhood: 'moore' };

const PULSAR = [[-6, -4], [-6, -3], [-6, -2], [-6, 2], [-6, 3], [-6, 4], [-4, -6], [-4, -1], [-4, 1], [-4, 6], [-3, -6], [-3, -1],
  [-3, 1], [-3, 6], [-2, -6], [-2, -1], [-2, 1], [-2, 6], [2, -6], [2, -1], [2, 1], [2, 6], [3, -6], [3, -1], [3, 1], [3, 6],
  [4, -6], [4, -1], [4, 1], [4, 6], [6, -4], [6, -3], [6, -2], [6, 2], [6, 3], [6, 4]];
const GUN = ['000000000000000000000000100000000000', '000000000000000000000010100000000000', '000000000000110000001100000000000011',
  '000000000001000100001100000000000011', '110000000010000010001100000000000000', '110000000010001011000010100000000000',
  '000000000010000010000000100000000000', '000000000001000100000000000000000000', '000000000000110000000000000000000000'];

export function cellular(p, cfg, rnd) {
  const q = { ...CELLULAR_DEFAULTS, ...p }, n = q.grid_size;
  const grid = initGrid(n, q.initial_pattern, q.initial_density, rnd);
  // Each runner calls emit(grid, rows, cols) for every entry of the Python's `evolution` list and returns the final
  // grid; the views are accumulated as they come instead of keeping every generation.
  const type = q.automata_type, elem = ['rule_30', 'rule_90', 'rule_110'].includes(type);
  const L = elem ? q.generations : q.generations + 1, evoRows = [], view = q.visualization;
  let trail = null, cols0 = 0, rows0 = 0, gen = 0;
  const emit = (g, rows, cols) => {
    if (view === 'evolution') { const mid = Math.floor(rows / 2); for (let j = 0; j < cols; j++) evoRows.push(g[mid * cols + j]); }
    if (view === 'trail') {
      if (!trail) { trail = new Array(rows * cols).fill(0); rows0 = rows; cols0 = cols; }
      const i = gen++;
      for (let k = 0; k < trail.length; k++) trail[k] += g[k] * (i + 1) / L;
    }
    if (view === 'evolution') cols0 = cols;
  };
  const final = elem ? elementary(grid, n, q.generations, +type.split('_')[1], emit)
    : type === 'brian_brain' ? brianBrain(grid, n, q.generations, emit)
      : type === 'langton_ant' ? langton(grid, n, q.generations, emit) : life(grid, n, q.generations, q.neighborhood, emit);
  const ax = subplots(cfg);
  if (view === 'final_state') {
    const cmap = cfg.color_mode === 'color' ? { list: [cfg.background_color, ...getPalette(cfg.color_palette, 3).slice(0, 2)] } : 'gray';
    ax.imshow(Array.from(final.data), final.rows, final.cols, { cmap, origin: 'lower' });
  } else if (view === 'evolution' && L > 1) { // middle row of every generation, one image row per generation
    ax.imshow(evoRows, L, cols0, { cmap: 'hot', origin: 'lower' });
  } else if (view === 'trail' && L > 1) {
    const cmap = cfg.color_mode === 'color' ? { list: getPalette(cfg.color_palette, 5) } : 'viridis';
    ax.imshow(trail, rows0, cols0, { cmap, origin: 'lower' });
  }
  ax.setXlim(0, n); ax.setYlim(0, n); ax.setAspect('equal'); ax.axis('off');
  ax.setFacecolor(cfg.background_color);
  return ax.scene();
}

const G = (data, rows, cols) => ({ data, rows, cols });

export function initGrid(n, pattern, density, rnd) {
  const g = new Array(n * n).fill(0);
  if (pattern === 'random') return rnd.choice([0, 1], [n, n], [1 - density, density]).slice();
  if (pattern === 'center_dot') g[Math.floor(n / 2) * n + Math.floor(n / 2)] = 1;
  else if (pattern === 'glider') {
    const s = Math.floor(n / 4);
    [[0, 1, 0], [0, 0, 1], [1, 1, 1]].forEach((row, i) => row.forEach((v, j) => { g[(s + i) * n + s + j] = v; }));
  } else if (pattern === 'pulsar') {
    const c = Math.floor(n / 2);
    for (const [dx, dy] of PULSAR) { const x = c + dx, y = c + dy; if (x >= 0 && x < n && y >= 0 && y < n) g[x * n + y] = 1; }
  } else if (pattern === 'gosper_gun') {
    const ex = Math.min(10 + GUN.length, n), ey = Math.min(10 + GUN[0].length, n);
    for (let x = 10; x < ex; x++) for (let y = 10; y < ey; y++) g[x * n + y] = +GUN[x - 10][y - 10];
  }
  return g;
}

function neighbours(g, n, x, y, moore, onlyState = null) {
  let c = 0;
  const offs = moore ? [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]] : [[-1, 0], [1, 0], [0, -1], [0, 1]];
  for (const [dx, dy] of offs) {
    const v = g[pmod(x + dx, n) * n + pmod(y + dy, n)];
    c += onlyState == null ? v : (v === onlyState ? 1 : 0);
  }
  return c;
}

function life(start, n, gens, hood, emit) {
  let g = Uint8Array.from(start);
  emit(g, n, n);
  for (let k = 0; k < gens; k++) {
    const ng = new Uint8Array(n * n);
    for (let x = 0; x < n; x++) for (let y = 0; y < n; y++) {
      const nb = neighbours(g, n, x, y, hood === 'moore');
      if (g[x * n + y] === 1) { if (nb >= 2 && nb <= 3) ng[x * n + y] = 1; } else if (nb === 3) ng[x * n + y] = 1;
    }
    g = ng; emit(g, n, n);
  }
  return G(g, n, n);
}

function elementary(start, n, gens, rule, emit) {
  const w = n, rows = range(gens).map(() => new Uint8Array(w));
  const mid = Math.floor(n / 2);
  for (let j = 0; j < w; j++) rows[0][j] = start[mid * n + j];
  for (let k = 1; k < gens; k++) {
    for (let i = 0; i < w; i++) {
      const idx = (rows[k - 1][pmod(i - 1, w)] << 2) | (rows[k - 1][i] << 1) | rows[k - 1][(i + 1) % w];
      rows[k][i] = (rule >> idx) & 1;
    }
  }
  // each generation tiled to an n x w image (np.tile(row, (n // gens + 1, 1))[:n])
  for (const r of rows) { const d = new Uint8Array(n * w); for (let x = 0; x < n; x++) d.set(r, x * w); emit(d, n, w); }
  return G(rows[gens - 1], 1, w);
}

function brianBrain(start, n, gens, emit) {
  let g = Uint8Array.from(start);
  emit(g, n, n);
  for (let k = 0; k < gens; k++) {
    const ng = new Uint8Array(n * n);
    for (let x = 0; x < n; x++) for (let y = 0; y < n; y++) {
      const v = g[x * n + y];
      if (v === 0) { if (neighbours(g, n, x, y, true, 1) === 2) ng[x * n + y] = 1; } else if (v === 1) ng[x * n + y] = 2;
    }
    g = ng; emit(g, n, n);
  }
  return G(g, n, n);
}

function langton(start, n, gens, emit) {
  const g = Uint8Array.from(start), dirs = [[-1, 0], [0, 1], [1, 0], [0, -1]];
  let ax = Math.floor(n / 2), ay = Math.floor(n / 2), dir = 0;
  emit(g, n, n);
  for (let k = 0; k < gens; k++) {
    if (ax >= 0 && ax < n && ay >= 0 && ay < n) {
      if (g[ax * n + ay] === 0) { dir = (dir + 1) % 4; g[ax * n + ay] = 1; } else { dir = pmod(dir - 1, 4); g[ax * n + ay] = 0; }
      ax += dirs[dir][0]; ay += dirs[dir][1];
    }
    emit(g, n, n);
  }
  return G(g, n, n);
}
