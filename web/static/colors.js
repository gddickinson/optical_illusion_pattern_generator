// Colour handling as matplotlib does it: named/hex colours to RGBA, colormaps (lookup tables and
// LinearSegmentedColormap.from_list), Normalize, and ColorManager from config.py (palettes).
import { CMAPS, CSS4, PALETTES } from './mpl_data.js';

export { PALETTES };
const SHORT = { k: 'black', r: 'red', b: 'blue', g: 'green', w: 'white', c: 'cyan', m: 'magenta', y: 'yellow' };
const N = 256;

function hex(h) {
  const s = h.slice(1);
  const full = s.length <= 4 ? [...s].map(c => c + c).join('') : s;
  const v = [0, 2, 4, 6].map(i => (i < full.length ? parseInt(full.slice(i, i + 2), 16) / 255 : 1));
  if (v.slice(0, 3).some(Number.isNaN)) throw new Error(`bad colour ${h}`);
  return v;
}

// matplotlib.colors.to_rgba for the forms the generators and the UI use.
export function toRGBA(c) {
  if (c == null) return null;
  if (Array.isArray(c)) return c.length === 3 ? [...c, 1] : [...c];
  const s = String(c).trim().toLowerCase();
  if (s.startsWith('#')) return hex(s);
  const name = SHORT[s] || s;
  if (CSS4[name]) return hex(CSS4[name]);
  if (/^(0|1|0?\.\d+)$/.test(s)) { const g = +s; return [g, g, g, 1]; } // grey level string
  throw new Error(`unknown colour ${c}`);
}

export function isColor(c) { try { toRGBA(c); return true; } catch { return false; } }

export function css(rgba, alpha = null) {
  const [r, g, b, a] = rgba;
  const al = alpha == null ? a : a * alpha;
  return `rgba(${Math.round(r * 255)},${Math.round(g * 255)},${Math.round(b * 255)},${+al.toFixed(4)})`;
}

// A colormap spec is a name ('viridis', 'hot', ...) or { list: [colours] } (LinearSegmentedColormap.from_list).
export function cmapLUT(spec) {
  if (typeof spec === 'string') {
    const t = CMAPS[spec];
    if (!t) throw new Error(`unknown colormap ${spec}`);
    return Array.from({ length: N }, (_, i) => [t[3 * i], t[3 * i + 1], t[3 * i + 2], 1]);
  }
  const cols = spec.list.map(toRGBA), k = cols.length - 1;
  return Array.from({ length: N }, (_, i) => {
    const x = i / (N - 1) * k, j = Math.min(Math.floor(x), k - 1), f = x - j;
    return [0, 1, 2, 3].map(c => cols[j][c] + (cols[j + 1][c] - cols[j][c]) * f);
  });
}

// Colormap.__call__ for floats in [0, 1].
export function cmapFn(spec) {
  const lut = cmapLUT(spec);
  return v => {
    let x = v * N;
    if (x === N) x = N - 1;
    const i = Math.max(0, Math.min(N - 1, Math.trunc(x)));
    return lut[i];
  };
}

// The 9-point signature the Python recorder stores for a colormap (cmap(linspace(0, 1, 9))).
export const cmapSignature = spec => { const f = cmapFn(spec); return Array.from({ length: 9 }, (_, i) => f(i / 8)); };

// ColorManager.get_palette / generate_hsv_palette (config.py).
export function getPalette(name, n = 8) {
  if (PALETTES[name]) {
    const c = PALETTES[name], reps = Math.floor(n / c.length) + 1;
    return Array.from({ length: c.length * reps }, (_, i) => c[i % c.length]).slice(0, n);
  }
  return hsvPalette(n);
}

export function hsvPalette(n, s = 0.8, v = 0.9) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const [r, g, b] = hsvToRgb(i / n, s, v);
    out.push('#' + [r, g, b].map(x => Math.trunc(x * 255).toString(16).padStart(2, '0')).join(''));
  }
  return out;
}

// colorsys.hsv_to_rgb
export function hsvToRgb(h, s, v) {
  if (s === 0) return [v, v, v];
  const i = Math.trunc(h * 6), f = h * 6 - i, p = v * (1 - s), q = v * (1 - s * f), t = v * (1 - s * (1 - f));
  return [[v, t, p], [q, v, p], [p, v, t], [p, q, v], [t, p, v], [v, p, q]][((i % 6) + 6) % 6];
}
