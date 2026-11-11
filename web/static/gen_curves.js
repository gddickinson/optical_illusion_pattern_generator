// MathematicalCurvesGenerator (patterns/curves.py, from optical_illusion_generator_V2.py), ported line by line.
import { subplots } from './scene.js';
import { linspace, radians, range } from './np.js';

export const CURVE_DEFAULTS = { curve_type: 'lissajous', a_parameter: 3, b_parameter: 2, phase_shift: 0, scale: 0.8,
  multiple_curves: 1, line_style: 'solid' };

function curveXY(type, a, b, ph, sc, t, res) {
  const cos = Math.cos, sin = Math.sin;
  switch (type) {
    case 'lissajous': return [t.map(v => sc * sin(a * v + ph)), t.map(v => sc * sin(b * v))];
    case 'rose': {
      const th = linspace(0, b * Math.PI, res), r = th.map(v => sc * cos(a * v / b));
      return [th.map((v, i) => r[i] * cos(v + ph)), th.map((v, i) => r[i] * sin(v + ph))];
    }
    case 'epicycloid': return [t.map(v => sc * ((a + b) * cos(v) - b * cos((a + b) * v / b + ph))),
      t.map(v => sc * ((a + b) * sin(v) - b * sin((a + b) * v / b + ph)))];
    case 'hypocycloid': return [t.map(v => sc * ((a - b) * cos(v) + b * cos((a - b) * v / b + ph))),
      t.map(v => sc * ((a - b) * sin(v) - b * sin((a - b) * v / b + ph)))];
    case 'cardioid': return [t.map(v => sc * (2 * cos(v) - cos(2 * v + ph))), t.map(v => sc * (2 * sin(v) - sin(2 * v + ph)))];
    case 'astroid': return [t.map(v => sc * cos(v + ph) ** 3), t.map(v => sc * sin(v + ph) ** 3)];
    case 'cycloid': return [t.map(v => sc * (a * v - b * sin(v + ph))), t.map(v => sc * (a - b * cos(v + ph)))];
    default: return [[], []];
  }
}

export function curves(p, cfg) {
  const q = { ...CURVE_DEFAULTS, ...p };
  const a = q.a_parameter, b = q.b_parameter, phase = radians(q.phase_shift);
  const ax = subplots(cfg);
  ax.setXlim(-1, 1); ax.setYlim(-1, 1); ax.setAspect('equal'); ax.axis('off');
  const t = linspace(0, 4 * Math.PI, cfg.resolution);
  for (const i of range(q.multiple_curves)) {
    let [x, y] = curveXY(q.curve_type, a, b, phase + i * Math.PI / 4, q.scale * (1 - i * 0.1), t, cfg.resolution);
    if (x.length && y.length) {
      const m = Math.max(Math.max(...x.map(Math.abs)), Math.max(...y.map(Math.abs)));
      if (m > 0) { x = x.map(v => v / m * 0.9); y = y.map(v => v / m * 0.9); }
    }
    const custom = cfg.custom_colors || [];
    const color = cfg.color_mode === 'color' && custom.length ? custom[i % custom.length] : cfg.foreground_color;
    if (q.line_style === 'dotted') ax.plot(x, y, { fmt: ':', color, lw: cfg.line_width * 2, alpha: 0.8 });
    else if (q.line_style === 'varied_width') {
      for (let j = 0; j < x.length - 1; j++) {
        ax.plot(x.slice(j, j + 2), y.slice(j, j + 2), { color, lw: cfg.line_width * (1 + Math.sin(j * 0.1)), alpha: 0.8 });
      }
    } else ax.plot(x, y, { color, lw: cfg.line_width, alpha: 0.8 });
  }
  ax.setFacecolor(cfg.background_color);
  return ax.scene();
}
