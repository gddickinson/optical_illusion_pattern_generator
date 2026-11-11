// TessellationGenerator (patterns/tessellation.py), ported line by line, including its random draws (irregularity,
// 'random' colours, and the scattered rhombi/octagons of the 'penrose' and 'ammann_beenker' types).
import { subplots } from './scene.js';
import { getPalette } from './colors.js';
import { linspace, mean, radians, range } from './np.js';
import { polygon } from './gen_islamic.js';

export const TESSELLATION_DEFAULTS = { tessellation_type: 'regular', base_shape: 'hexagon', tile_size: 0.1, irregularity: 0.0,
  color_scheme: 'alternating', border_style: 'thin', fill_pattern: 'solid' };

export function tessellation(p, cfg, rnd) {
  const q = { ...TESSELLATION_DEFAULTS, ...p };
  const ax = subplots(cfg);
  ax.setXlim(-1, 1); ax.setYlim(-1, 1); ax.setAspect('equal'); ax.axis('off');
  const T = new Tiler(ax, cfg, rnd, q);
  const fn = { regular: 'regular', penrose: 'penrose', hexagonal: 'hexagonal', triangular: 'triangular',
    ammann_beenker: 'ammann', truchet: 'truchet' }[q.tessellation_type];
  if (fn) T[fn]();
  ax.setFacecolor(cfg.background_color);
  return ax.scene();
}

const hexagon = (cx, cy, s) => linspace(0, 2 * Math.PI, 7).map(a => [cx + s * Math.cos(a), cy + s * Math.sin(a)]);
const square = (cx, cy, s) => { const h = s / 2; return [[cx - h, cy - h], [cx + h, cy - h], [cx + h, cy + h], [cx - h, cy + h], [cx - h, cy - h]]; };
function triangle(cx, cy, s, up) {
  const h = s * Math.sqrt(3) / 2, k = up ? 1 : -1;
  return [[cx, cy + k * (h * 2 / 3)], [cx - s / 2, cy - k * (h * 1 / 3)], [cx + s / 2, cy - k * (h * 1 / 3)], [cx, cy + k * (h * 2 / 3)]];
}
function rhombus(cx, cy, w, h, rot) {
  const r = radians(rot), c = Math.cos(r), s = Math.sin(r), hw = w / 2, hh = h / 2;
  return [[-hw, 0], [0, hh], [hw, 0], [0, -hh], [-hw, 0]].map(([x, y]) => [x * c + y * -s + cx, x * s + y * c + cy]);
}
const X = pts => pts.map(v => v[0]), Y = pts => pts.map(v => v[1]);

class Tiler {
  constructor(ax, cfg, rnd, q) { Object.assign(this, { ax, cfg, rnd, q }); }
  col(colors, row, col) {
    const s = this.q.color_scheme, c = this.cfg;
    if (c.color_mode !== 'color') return c.foreground_color;
    if (s === 'alternating') return colors[(row + col) % 2];
    if (s === 'gradient') return colors[(row + col) % colors.length];
    if (s === 'random') return colors[this.rnd.randint(colors.length)];
    if (s === 'symmetric') return colors[Math.min(row, col) % colors.length];
    return colors[0];
  }
  jitter(x, y, size) {
    const irr = this.q.irregularity;
    if (irr > 0) { x += this.rnd.uniform(-irr, irr) * size; y += this.rnd.uniform(-irr, irr) * size; }
    return [x, y];
  }
  tile(pts, color) { this.fillPattern(pts, color); this.border(pts); }
  fillPattern(v, color) {
    const ax = this.ax, pat = this.q.fill_pattern;
    ax.fill(X(v), Y(v), { color, alpha: 0.8 });
    if (pat === 'solid') return;
    const cx = mean(X(v).slice(0, -1)), cy = mean(Y(v).slice(0, -1));
    if (pat === 'striped') {
      for (const i of range(5)) ax.axhline(cy + (i - 2) * 0.02, { xmin: 0, xmax: 1, color: 'black', alpha: 0.3, lw: 0.5 });
    } else if (pat === 'dotted') {
      for (let i = -2; i < 3; i++) for (let j = -2; j < 3; j++) ax.plot(cx + i * 0.02, cy + j * 0.02, { fmt: 'ko', ms: 1 });
    } else if (pat === 'cross_hatch') {
      for (const i of range(5)) {
        const o = (i - 2) * 0.02;
        ax.plot([cx - 0.05, cx + 0.05], [cy + o, cy + o], { fmt: 'k-', alpha: 0.3, lw: 0.5 });
        ax.plot([cx + o, cx + o], [cy - 0.05, cy + 0.05], { fmt: 'k-', alpha: 0.3, lw: 0.5 });
      }
    }
  }
  border(v) {
    const s = this.q.border_style, lw = this.cfg.line_width;
    if (s === 'thin') this.ax.plot(X(v), Y(v), { fmt: 'k-', lw: lw * 0.5, alpha: 0.8 });
    else if (s === 'thick') this.ax.plot(X(v), Y(v), { fmt: 'k-', lw: lw * 2, alpha: 0.8 });
    else if (s === 'decorative') this.ax.plot(X(v), Y(v), { fmt: 'k--', lw, alpha: 0.6 });
  }
  hexGrid(colors, sizeJitter) {
    const size = this.q.tile_size, hh = size * Math.sqrt(3), hw = size * 2;
    const rows = Math.trunc(2 / hh) + 2, cols = Math.trunc(2 / (hw * 0.75)) + 2;
    for (const row of range(rows)) for (const col of range(cols)) {
      let xo = col * hw * 0.75;
      const yo = row * hh;
      if (row % 2 === 1) xo += hw * 0.375;
      const [cx, cy] = this.jitter(-1 + xo, -1 + yo, size);
      const s = sizeJitter ? size * (1 + this.rnd.uniform(-this.q.irregularity, this.q.irregularity)) : size;
      const hex = hexagon(cx, cy, s);
      this.tile(hex, this.col(colors, row, col));
    }
  }
  triGrid(colors, jitter) {
    const size = this.q.tile_size, th = size * Math.sqrt(3) / 2, rows = Math.trunc(2 / th) + 2, cols = Math.trunc(2 / size) + 2;
    for (const row of range(rows)) for (const col of range(cols)) {
      let [cx, cy] = [-1 + col * size / 2, -1 + row * th];
      if (jitter) [cx, cy] = this.jitter(cx, cy, size);
      const tri = triangle(cx, cy, size, (row + col) % 2 === 0);
      this.tile(tri, this.col(colors, row, col));
    }
  }
  regular() {
    const colors = getPalette(this.cfg.color_palette, 6), shape = this.q.base_shape, size = this.q.tile_size;
    if (shape === 'hexagon') this.hexGrid(colors, false);
    else if (shape === 'square') {
      const n = Math.trunc(2 / size) + 1;
      for (const row of range(n)) for (const col of range(n)) {
        const [cx, cy] = this.jitter(-1 + col * size + size / 2, -1 + row * size + size / 2, size);
        const sq = square(cx, cy, size);
        this.tile(sq, this.col(colors, row, col));
      }
    } else if (shape === 'triangle') this.triGrid(colors, false);
  }
  hexagonal() { this.hexGrid(getPalette(this.cfg.color_palette, 8), true); }
  triangular() { this.triGrid(getPalette(this.cfg.color_palette, 4), true); }
  penrose() {
    const colors = getPalette(this.cfg.color_palette, 2), phi = (1 + Math.sqrt(5)) / 2, size = this.q.tile_size, r = this.rnd;
    for (let k = 0; k < Math.trunc(100 / (size * size)); k++) {
      const cx = r.uniform(-1, 1), cy = r.uniform(-1, 1), rot = r.uniform(0, 360);
      const thin = r.random() < 0.5;
      const rh = thin ? rhombus(cx, cy, size, size / phi, rot) : rhombus(cx, cy, size, size * phi, rot);
      const color = this.cfg.color_mode === 'color' ? colors[thin ? 0 : 1] : this.cfg.foreground_color;
      this.ax.fill(X(rh), Y(rh), { color, alpha: 0.8 });
      this.border(rh);
    }
  }
  ammann() {
    const colors = getPalette(this.cfg.color_palette, 2), size = this.q.tile_size, r = this.rnd, c = this.cfg;
    for (let k = 0; k < Math.trunc(50 / (size * size)); k++) {
      const cx = r.uniform(-1, 1), cy = r.uniform(-1, 1);
      if (r.random() < 0.6) {
        const oct = polygon(8, size, cx, cy, r.uniform(0, 45));
        this.ax.fill(X(oct), Y(oct), { color: c.color_mode === 'color' ? colors[0] : c.foreground_color, alpha: 0.8 });
      } else {
        const sq = square(cx, cy, size * 0.7);
        this.ax.fill(X(sq), Y(sq), { color: c.color_mode === 'color' ? colors[1] : c.foreground_color, alpha: 0.8 });
      }
    }
  }
  truchet() {
    const colors = getPalette(this.cfg.color_palette, 4), size = this.q.tile_size, n = Math.trunc(2 / size) + 1, c = this.cfg;
    for (const row of range(n)) for (const col of range(n)) {
      const cx = -1 + col * size + size / 2, cy = -1 + row * size + size / 2, sq = square(cx, cy, size);
      this.ax.fill(X(sq), Y(sq), { color: c.color_mode === 'color' ? colors[(row + col) % colors.length] : c.background_color, alpha: 0.9 });
      this.truchetCurve(cx, cy, size, (row + col) % 4);
    }
  }
  truchetCurve(cx, cy, size, variant) {
    const h = size / 2, o = { fmt: 'k-', lw: this.cfg.line_width * 2 };
    if (variant === 0) {
      const th = linspace(0, Math.PI / 2, 20);
      this.ax.plot(th.map(t => cx - h + h * (1 - Math.cos(t))), th.map(t => cy - h + h * Math.sin(t)), o);
    } else if (variant === 1) {
      const th = linspace(Math.PI / 2, Math.PI, 20);
      this.ax.plot(th.map(t => cx - h + h * (1 - Math.cos(t))), th.map(t => cy + h + h * Math.sin(t)), o);
    } else if (variant === 2) this.ax.plot([cx - h, cx + h], [cy - h, cy + h], o);
    else this.ax.plot([cx - h, cx + h], [cy + h, cy - h], o);
  }
}
