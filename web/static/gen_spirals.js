// SpiralGenerator and InterferenceGenerator (patterns/spirals.py), ported line by line.
import { subplots } from './scene.js';
import { getPalette, cmapFn } from './colors.js';
import { linspace, radians, range } from './np.js';

export const SPIRAL_DEFAULTS = { spiral_type: 'archimedean', arms: 3, density: 1.0, rotation: 0, scale: 1.0, center_x: 0.0,
  center_y: 0.0, overlapping_spirals: 1, gradient_effect: 'none' };

export function spiral(p, cfg) {
  const { spiral_type: type, arms, density, rotation, scale, center_x: cx, center_y: cy,
    overlapping_spirals: overlapping, gradient_effect: gradient } = { ...SPIRAL_DEFAULTS, ...p };
  const ax = subplots(cfg);
  ax.setXlim(-1, 1); ax.setYlim(-1, 1); ax.setAspect('equal'); ax.axis('off');
  const t = linspace(0, 20 * Math.PI * density, cfg.resolution);
  const colors = getPalette(cfg.color_palette, Math.max(arms * overlapping, 8));
  const hsv = cmapFn('hsv'), phi = (1 + Math.sqrt(5)) / 2, half = Math.floor(overlapping / 2);
  for (const s of range(overlapping)) {
    const ox = cx + (s - half) * 0.2, oy = cy + (s - half) * 0.15;
    for (const arm of range(arms)) {
      const rr = radians(rotation + (arm * 360 / arms) + (s * 45));
      const r = t.map(v => type === 'archimedean' ? 0.05 * v * scale : type === 'logarithmic' ? 0.1 * Math.exp(0.1 * v) * scale
        : type === 'fermat' ? 0.3 * Math.sqrt(v) * scale : 0.1 * phi ** (v / Math.PI) * scale);
      let x = r.map((v, i) => v * Math.cos(t[i] + rr) + ox), y = r.map((v, i) => v * Math.sin(t[i] + rr) + oy);
      const keep = x.map((v, i) => (v - ox) * (v - ox) + (y[i] - oy) * (y[i] - oy) <= 1);
      x = x.filter((_, i) => keep[i]); y = y.filter((_, i) => keep[i]);
      if (!x.length) continue;
      const base = cfg.color_mode === 'color' ? colors[(arm + s) % colors.length] : cfg.foreground_color;
      if (gradient === 'radial') {
        const alphas = linspace(1.0, 0.3, x.length);
        for (let i = 0; i < x.length - 1; i++) ax.plot(x.slice(i, i + 2), y.slice(i, i + 2), { color: base, lw: cfg.line_width, alpha: alphas[i] });
      } else if (gradient === 'angular') {
        for (let i = 0; i < x.length - 1; i++) {
          const a = Math.atan2(y[i] - oy, x[i] - ox);
          ax.plot(x.slice(i, i + 2), y.slice(i, i + 2), { color: hsv((a + Math.PI) / (2 * Math.PI)), lw: cfg.line_width });
        }
      } else {
        ax.plot(x, y, { color: base, lw: cfg.line_width, alpha: 0.8 });
      }
    }
  }
  ax.setFacecolor(cfg.background_color);
  return ax.scene();
}

export const INTERFERENCE_DEFAULTS = { pattern_type: 'concentric', frequency1: 10, frequency2: 12, phase: 0, amplitude: 1.0 };

// The interference field on the resolution x resolution grid (row-major, rows = y).
export function interferenceField(type, f1, f2, phaseDeg, amplitude, res) {
  const x = linspace(-1, 1, res), y = x, phase = radians(phaseDeg), z = new Float64Array(res * res);
  const w1 = 2 * Math.PI * f1, w2 = 2 * Math.PI * f2;
  for (let i = 0; i < res; i++) {
    for (let j = 0; j < res; j++) {
      const X = x[j], Y = y[i];
      let p1, p2;
      if (type === 'concentric') {
        const R = Math.sqrt(X * X + Y * Y);
        p1 = Math.sin(w1 * R + phase); p2 = Math.sin(w2 * R);
      } else if (type === 'wave') {
        p1 = Math.sin(w1 * X + phase); p2 = Math.sin(w2 * Y);
      } else {
        p1 = Math.sin(w1 * X + phase) + Math.sin(w1 * Y + phase); p2 = Math.sin(w2 * X) + Math.sin(w2 * Y);
      }
      z[i * res + j] = amplitude * (p1 + p2);
    }
  }
  return { x, y, z };
}

export function interference(p, cfg) {
  const q = { ...INTERFERENCE_DEFAULTS, ...p };
  const { x, y, z } = interferenceField(q.pattern_type, q.frequency1, q.frequency2, q.phase, q.amplitude, cfg.resolution);
  const ax = subplots(cfg);
  if (cfg.color_mode === 'color') ax.contour(x, y, z, { levels: 20, cmap: { list: getPalette(cfg.color_palette, 5) }, lw: cfg.line_width });
  else ax.contour(x, y, z, { levels: 20, colors: cfg.foreground_color, lw: cfg.line_width });
  ax.setXlim(-1, 1); ax.setYlim(-1, 1); ax.setAspect('equal'); ax.axis('off');
  ax.setFacecolor(cfg.background_color);
  return ax.scene();
}
