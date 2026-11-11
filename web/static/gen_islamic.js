// IslamicGeometryGenerator (patterns/islamic.py), ported line by line. ('symmetry' is a parameter of the Python
// generator that its drawing code never reads; it is kept for parity and has no effect, as on the desktop.)
import { subplots } from './scene.js';
import { getPalette } from './colors.js';
import { linspace, radians, range } from './np.js';

export const ISLAMIC_DEFAULTS = { pattern_type: 'octagon_star', tile_size: 0.2, repetitions_x: 8, repetitions_y: 6, rotation: 0,
  interlace: 'simple', ornament_detail: 1.0 };

export function islamic(p, cfg) {
  const q = { ...ISLAMIC_DEFAULTS, ...p };
  const ax = subplots(cfg);
  ax.setXlim(-1, 1); ax.setYlim(-1, 1); ax.setAspect('equal'); ax.axis('off');
  const fn = DRAW[q.pattern_type];
  if (fn) fn(ax, cfg, q.tile_size, q.repetitions_x, q.repetitions_y, q.rotation, q.ornament_detail, q.interlace);
  ax.setFacecolor(cfg.background_color);
  return ax.scene();
}

const pick = (cfg, colors, i) => (cfg.color_mode === 'color' ? colors[i] : cfg.foreground_color);
const xs = pts => pts.map(v => v[0]), ys = pts => pts.map(v => v[1]);
function fillPts(ax, pts, o) { ax.fill(xs(pts), ys(pts), o); }
function cells(rx, ry, fn) {
  for (const i of range(rx)) for (const j of range(ry)) fn(-1 + (i + 0.5) * 2 / rx, -1 + (j + 0.5) * 2 / ry, i, j);
}

const DRAW = {
  octagon_star(ax, cfg, size, rx, ry, rot, detail, interlace) {
    const colors = getPalette(cfg.color_palette, 4), lw = cfg.line_width;
    cells(rx, ry, (cx, cy) => {
      fillPts(ax, polygon(8, size, cx, cy, rot), { color: pick(cfg, colors, 0), alpha: 0.8, ec: 'black', lw });
      fillPts(ax, star(8, size * 0.6, size * 0.3, cx, cy, rot + 22.5), { color: pick(cfg, colors, 1), alpha: 0.9, ec: 'black', lw });
      if (interlace !== 'none') interlacePattern(ax, cfg, cx, cy, size, detail, colors.slice(2));
    });
  },
  hexagon_flower(ax, cfg, size, rx, ry, rot) {
    const colors = getPalette(cfg.color_palette, 6), lw = cfg.line_width;
    cells(rx, ry, (cx, cy) => {
      fillPts(ax, polygon(6, size, cx, cy, rot), { color: pick(cfg, colors, 0), alpha: 0.8, ec: 'black', lw });
      for (const k of range(6)) {
        const angle = k * 60 + rot;
        const petal = petalPts(size * 0.4, cx + size * 0.8 * Math.cos(radians(angle)), cy + size * 0.8 * Math.sin(radians(angle)), angle);
        fillPts(ax, petal, { color: pick(cfg, colors, (k + 1) % colors.length), alpha: 0.7, ec: 'black', lw: lw * 0.5 });
      }
    });
  },
  square_kufic(ax, cfg, size, rx, ry) {
    const colors = getPalette(cfg.color_palette, 3), lw = cfg.line_width;
    cells(rx, ry, (cx, cy) => {
      [[[-0.5, -0.3], [0.5, -0.3], [0.5, 0.3], [-0.5, 0.3]], [[-0.3, -0.5], [0.3, -0.5], [0.3, 0.5], [-0.3, 0.5]]].forEach((el, i) => {
        const pts = el.map(([x, y]) => [x * size + cx, y * size + cy]);
        fillPts(ax, pts, { color: pick(cfg, colors, i % colors.length), alpha: 0.8, ec: 'black', lw });
      });
    });
  },
  girih_tiles(ax, cfg, size, rx, ry, rot) {
    const colors = getPalette(cfg.color_palette, 5), lw = cfg.line_width;
    cells(rx, ry, (cx, cy) => {
      fillPts(ax, polygon(10, size, cx, cy, rot), { color: pick(cfg, colors, 0), alpha: 0.7, ec: 'black', lw });
      for (const k of range(5)) {
        const angle = k * 72 + rot;
        const bow = bowtie(size * 0.3, cx + size * 0.7 * Math.cos(radians(angle)), cy + size * 0.7 * Math.sin(radians(angle)), angle);
        fillPts(ax, bow, { color: pick(cfg, colors, (k + 1) % colors.length), alpha: 0.8, ec: 'black', lw: lw * 0.5 });
      }
    });
  },
  morocco_zellige(ax, cfg, size, rx, ry, rot) {
    const colors = getPalette('ocean', 8), lw = cfg.line_width;
    cells(rx, ry, (cx, cy, i, j) => {
      if ((i + j) % 2 === 0) fillPts(ax, star(8, size, size * 0.5, cx, cy, rot), { color: pick(cfg, colors, 0), alpha: 0.8, ec: 'white', lw });
      else fillPts(ax, cross(size, cx, cy, rot), { color: pick(cfg, colors, 1), alpha: 0.8, ec: 'white', lw });
    });
  },
};

// --- shape helpers (same names as the Python) ---
export function polygon(n, radius, cx, cy, rot) {
  return linspace(0, 2 * Math.PI, n + 1).map(a => a + radians(rot)).map(a => [cx + radius * Math.cos(a), cy + radius * Math.sin(a)]);
}

export function star(n, outer, inner, cx, cy, rot) {
  const angles = [];
  for (const i of range(n)) { angles.push(2 * Math.PI * i / n + radians(rot)); angles.push(2 * Math.PI * (i + 0.5) / n + radians(rot)); }
  const pts = angles.map((a, i) => { const r = i % 2 === 0 ? outer : inner; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; });
  pts.push(pts[0]);
  return pts;
}

function petalPts(size, cx, cy, angle) {
  return linspace(0, Math.PI, 20).map(t => { const r = size * Math.sin(t); return [cx + r * Math.cos(t + radians(angle)), cy + r * Math.sin(t + radians(angle))]; });
}

// points @ R.T with R = [[cos, -sin], [sin, cos]], then translated.
function rotate(points, angle, cx, cy) {
  const c = Math.cos(radians(angle)), s = Math.sin(radians(angle));
  return points.map(([x, y]) => [x * c + y * -s + cx, x * s + y * c + cy]);
}

function bowtie(s, cx, cy, angle) {
  return rotate([[-s, 0], [-s * 0.3, -s * 0.3], [0, 0], [-s * 0.3, s * 0.3], [-s, 0], [s, 0], [s * 0.3, s * 0.3], [0, 0],
    [s * 0.3, -s * 0.3], [s, 0]], angle, cx, cy);
}

function cross(size, cx, cy, rot) {
  const t = size * 0.3;
  return rotate([[-t, -size], [t, -size], [t, -t], [size, -t], [size, t], [t, t], [t, size], [-t, size], [-t, t], [-size, t],
    [-size, -t], [-t, -t]], rot, cx, cy);
}

function interlacePattern(ax, cfg, cx, cy, size, detail, colors) {
  for (const i of range(Math.trunc(4 * detail))) {
    const angle = i * 90 / detail;
    const color = colors.length && cfg.color_mode === 'color' ? colors[i % colors.length] : cfg.foreground_color;
    ax.circle(cx + size * 0.2 * Math.cos(radians(angle)), cy + size * 0.2 * Math.sin(radians(angle)), size * 0.1, { color, alpha: 0.6 });
  }
}
