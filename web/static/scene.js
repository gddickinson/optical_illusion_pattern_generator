// A drawing list with the matplotlib Axes calls the generators make (plot, fill, axhline, contour, imshow, ...).
// Each call becomes a primitive in the same schema web/recorder.py records from the real Python, so the node test can
// compare the two call by call, and render.js draws it on a canvas.
import { toRGBA } from './colors.js';

const FMT = { k: 'black', r: 'red', b: 'blue', g: 'green', w: 'white' };
const num = v => (v == null ? null : +v);

function parseFmt(fmt) {
  const color = FMT[fmt[0]] || null, rest = color ? fmt.slice(1) : fmt;
  if (rest === 'o') return { color, ls: null, marker: 'o' };
  return { color, ls: ['-', '--', ':'].includes(rest) ? rest : '-', marker: null };
}
const arr = v => (Array.isArray(v) || ArrayBuffer.isView(v) ? Array.from(v) : [v]);

export class Axes {
  constructor(figsize) {
    this.figsize = figsize;
    this.bg = null;
    this.prims = [];
    this.view = { xlim: null, ylim: null, aspect: null, axis_off: false };
  }
  plot(x, y, o = {}) {
    const f = o.fmt ? parseFmt(o.fmt) : { color: null, ls: '-', marker: null };
    const p = { x: arr(x), y: arr(y), color: toRGBA(o.color ?? f.color), alpha: num(o.alpha) };
    if (f.marker) Object.assign(p, { t: 'marker', ms: num(o.ms), mec: toRGBA(o.mec), mew: num(o.mew) });
    else Object.assign(p, { t: 'line', lw: num(o.lw), ls: f.ls, cap: o.cap || null });
    this.prims.push(p);
  }
  fill(x, y, o = {}) {
    this.prims.push({ t: 'fill', x: arr(x), y: arr(y), color: toRGBA(o.color), alpha: num(o.alpha), ec: toRGBA(o.ec), lw: num(o.lw) });
  }
  span(t, v, o) {
    this.prims.push({ t, v: +v, color: toRGBA(o.color), alpha: num(o.alpha), lw: num(o.lw), span: [o.xmin ?? 0, o.xmax ?? 1] });
  }
  axhline(y, o = {}) { this.span('hline', y, o); }
  axvline(x, o = {}) { this.span('vline', x, o); }
  scatter(x, y, o = {}) {
    this.prims.push({ t: 'scatter', x: arr(x), y: arr(y), s: +o.s, color: toRGBA(o.c), alpha: num(o.alpha) });
  }
  circle(cx, cy, r, o = {}) {
    const c = toRGBA(o.color);
    if (o.alpha != null) c[3] = o.alpha;
    this.prims.push({ t: 'circle', cx, cy, r, color: c });
  }
  // x: column coordinates, y: row coordinates, z: rows*cols values (row-major), levels from contourLevels().
  contour(x, y, z, o = {}) {
    this.prims.push({ t: 'contour', x, y, z, levels: contourLevels(z, o.levels ?? 7), color: o.colors ? toRGBA(o.colors) : null,
      cmap: o.colors ? null : (o.cmap || 'viridis'), lw: num(o.lw) });
  }
  imshow(data, rows, cols, o = {}) {
    this.prims.push({ t: 'image', rows, cols, data, cmap: o.cmap || 'viridis', origin: o.origin || 'upper', extent: o.extent || null });
  }
  setXlim(a, b) { this.view.xlim = [a, b]; }
  setYlim(a, b) { this.view.ylim = [a, b]; }
  setAspect(a) { this.view.aspect = a; }
  axis(a) { this.view.axis_off = a === 'off'; }
  setFacecolor(c) { this.bg = toRGBA(c); }
  scene() { return { figsize: this.figsize, bg: this.bg, view: this.view, prims: this.prims }; }
}

// plt.subplots(figsize=(width/100, height/100)) for a config.
export const subplots = config => new Axes([config.width / 100, config.height / 100]);

// --- contour levels: matplotlib's ContourSet._autolev with MaxNLocator(levels + 1, min_n_ticks=1) -------------------
const STEPS = [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10];
const EXT = [...STEPS.slice(0, -1).map(s => 0.1 * s), ...STEPS, 10 * STEPS[1]];

function scaleRange(vmin, vmax, n) {
  const dv = Math.abs(vmax - vmin), meanv = (vmax + vmin) / 2;
  const offset = Math.abs(meanv) / dv < 100 ? 0 : Math.sign(meanv) * 10 ** Math.floor(Math.log10(Math.abs(meanv)));
  return [10 ** Math.floor(Math.log10(dv / n)), offset];
}

function pyDivmod(x, y) { const d = Math.floor(x / y); return [d, x - d * y]; }

export function maxNTicks(vmin, vmax, nbins, minN = 1) {
  const [scale, offset] = scaleRange(vmin, vmax, nbins);
  const v0 = vmin - offset, v1 = vmax - offset, steps = EXT.map(s => s * scale);
  const raw = (v1 - v0) / nbins;
  let istep = steps.findIndex(s => s >= raw);
  if (istep < 0) istep = steps.length - 1;
  let ticks = [];
  for (let k = istep; k >= 0; k--) {
    const step = steps[k], best = Math.floor(v0 / step) * step;
    const tol = offset ? Math.min(0.4999, Math.max(1e-10, 10 ** (Math.log10(Math.abs(offset) / step) - 12))) : 1e-10;
    const close = (ms, e) => Math.abs(ms - e) < tol;
    let [d, m] = pyDivmod(v0 - best, step); const low = close(m / step, 1) ? d + 1 : d;
    [d, m] = pyDivmod(v1 - best, step); const high = close(m / step, 0) ? d : d + 1;
    ticks = [];
    for (let i = low; i <= high; i++) ticks.push(i * step + best);
    if (ticks.filter(t => t <= v1 && t >= v0).length >= minN) break;
  }
  return ticks.map(t => t + offset);
}

export function contourLevels(z, n) {
  let zmin = Infinity, zmax = -Infinity;
  for (const v of z) { if (v < zmin) zmin = v; if (v > zmax) zmax = v; }
  if (zmin === zmax) { zmin -= 1e-13 * Math.max(Math.abs(zmin), 1); zmax += 1e-13 * Math.max(Math.abs(zmax), 1); }
  const lev = maxNTicks(zmin, zmax, n + 1);
  let i0 = 0, i1 = lev.length;
  lev.forEach((v, i) => { if (v < zmin) i0 = i; });
  const over = lev.findIndex(v => v > zmax);
  if (over >= 0) i1 = over + 1;
  if (i1 - i0 < 3) { i0 = 0; i1 = lev.length; }
  return lev.slice(i0, i1);
}
