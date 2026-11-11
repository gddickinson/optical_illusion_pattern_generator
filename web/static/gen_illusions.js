// OpticalIllusionGenerator (patterns/illusions.py, from optical_illusion_generator_V2.py), ported line by line.
import { subplots } from './scene.js';
import { linspace, arange, radians, range } from './np.js';

export const ILLUSION_DEFAULTS = { illusion_type: 'mueller_lyer', intensity: 1.0, size: 0.5, spacing: 0.1, tilt_angle: 15, contrast: 0.8 };

export function illusion(p, cfg) {
  const q = { ...ILLUSION_DEFAULTS, ...p };
  const ax = subplots(cfg);
  ax.setXlim(-1, 1); ax.setYlim(-1, 1); ax.setAspect('equal'); ax.axis('off');
  const fn = DRAW[q.illusion_type];
  if (fn) fn(ax, q, cfg);
  ax.setFacecolor(cfg.background_color);
  return ax.scene();
}

const DRAW = {
  hermann_grid(ax, { spacing, intensity }, c) {
    for (const i of arange(-1, 1, spacing)) {
      ax.axhline(i, { color: c.foreground_color, lw: c.line_width * intensity * 10 });
      ax.axvline(i, { color: c.foreground_color, lw: c.line_width * intensity * 10 });
    }
  },
  fraser_spiral(ax, { size, intensity }, c) {
    const t = linspace(0, 20 * Math.PI, c.resolution);
    for (const phase of arange(0, 2 * Math.PI, Math.PI / 4)) {
      const x = [], y = [];
      t.forEach(v => { const r = size * v / (20 * Math.PI); x.push(r * Math.cos(v + phase)); y.push(r * Math.sin(v + phase)); });
      for (let i = 0; i < x.length - 10; i += 20) {
        const color = Math.floor(i / 20) % 2 === 0 ? c.foreground_color : 'gray';
        ax.plot(x.slice(i, i + 10), y.slice(i, i + 10), { color, lw: c.line_width * intensity });
      }
    }
  },
  mueller_lyer(ax, { size, intensity }, c) {
    const fg = c.foreground_color, lw3 = c.line_width * intensity * 3, lw2 = c.line_width * intensity * 2, a = size * 0.2;
    ax.plot([-size, size], [0.3, 0.3], { color: fg, lw: lw3 });
    ax.plot([-size, size], [-0.3, -0.3], { color: fg, lw: lw3 });
    ax.plot([-size, -size + a], [0.3, 0.3 + a], { color: fg, lw: lw2 });
    ax.plot([-size, -size + a], [0.3, 0.3 - a], { color: fg, lw: lw2 });
    ax.plot([size, size - a], [0.3, 0.3 + a], { color: fg, lw: lw2 });
    ax.plot([size, size - a], [0.3, 0.3 - a], { color: fg, lw: lw2 });
    ax.plot([-size, -size - a], [-0.3, -0.3 + a], { color: fg, lw: lw2 });
    ax.plot([-size, -size - a], [-0.3, -0.3 - a], { color: fg, lw: lw2 });
    ax.plot([size, size + a], [-0.3, -0.3 + a], { color: fg, lw: lw2 });
    ax.plot([size, size + a], [-0.3, -0.3 - a], { color: fg, lw: lw2 });
  },
  kanizsa(ax, { size, intensity }, c) {
    const rad = size * 0.3, centers = [[0, size], [-size * 0.866, -size * 0.5], [size * 0.866, -size * 0.5]];
    for (const [cx, cy] of centers) { // disc minus a 60-degree wedge, mouth towards the triangle's centre
      const mouth = Math.atan2(-cy, -cx), th = linspace(mouth + Math.PI / 6, mouth + 2 * Math.PI - Math.PI / 6, 100);
      ax.fill([cx, ...th.map(t => cx + rad * Math.cos(t))], [cy, ...th.map(t => cy + rad * Math.sin(t))],
        { color: c.foreground_color, alpha: intensity });
    }
  },
  cafe_wall(ax, { spacing, intensity }, c) {
    const rows = Math.trunc(2 / spacing), cols = Math.trunc(2 / spacing), w = spacing * 0.8, h = spacing * 0.4;
    for (const row of range(rows)) {
      const y = -1 + row * spacing, offset = row % 2 === 1 ? w / 2 : 0;
      for (const col of range(cols + 1)) {
        const x = -1 + col * spacing + offset, even = (row + col) % 2 === 0;
        ax.fill([x, x + w, x + w, x, x], [y, y, y + h, y + h, y],
          { color: even ? c.foreground_color : 'gray', alpha: even ? intensity : intensity * 0.5 });
      }
      ax.axhline(y + h, { color: c.foreground_color, lw: c.line_width * intensity, alpha: 0.8 });
    }
  },
  zollner(ax, { spacing, intensity, tilt_angle }, c) {
    const lines = Math.trunc(2 / spacing), tilt = radians(tilt_angle);
    for (const i of range(lines)) {
      const x = -1 + i * spacing;
      ax.axvline(x, { color: c.foreground_color, lw: c.line_width * intensity * 2 });
      for (const y of arange(-1, 1, spacing / 3)) {
        const x1 = x - spacing / 4, x2 = x + spacing / 4, d = spacing / 4 * Math.tan(tilt);
        const [y1, y2] = i % 2 === 0 ? [y - d, y + d] : [y + d, y - d];
        ax.plot([x1, x2], [y1, y2], { color: c.foreground_color, lw: c.line_width * intensity });
      }
    }
  },
  rotating_snakes(ax, { size, intensity, contrast }, c) {
    const angles = linspace(0, 2 * Math.PI, 7).slice(0, 6); // np.linspace(0, 2pi, 6, endpoint=False)
    for (const angle of angles) {
      const cx = size * 0.6 * Math.cos(angle), cy = size * 0.6 * Math.sin(angle);
      const theta = linspace(0, 2 * Math.PI, 20), radius = size * 0.2;
      for (let j = 0; j < theta.length - 1; j++) {
        const arc = linspace(theta[j], theta[j + 1], 10);
        const [color, alpha] = [['black', intensity], ['white', intensity * contrast], ['gray', intensity * 0.7], ['darkgray', intensity * 0.9]][j % 4];
        ax.plot(arc.map(t => cx + radius * Math.cos(t)), arc.map(t => cy + radius * Math.sin(t)),
          { color, lw: c.line_width * 4, alpha, cap: 'round' });
      }
    }
  },
  scintillating_grid(ax, { spacing, intensity }, c) {
    const pts = arange(-1, 1.1, spacing);
    for (const i of pts) {
      ax.axhline(i, { color: c.foreground_color, lw: c.line_width * intensity * 3 });
      ax.axvline(i, { color: c.foreground_color, lw: c.line_width * intensity * 3 });
    }
    for (const x of pts) for (const y of pts) {
      ax.plot(x, y, { fmt: 'o', color: 'white', ms: c.line_width * intensity * 2, mec: c.foreground_color, mew: 0.5 });
    }
  },
  impossible_triangle(ax, { size, intensity }, c) {
    const b = size * 0.1;
    const x1 = [-size, size, size - b, -size + b, -size];
    const y1 = [-size * 0.5, -size * 0.5, -size * 0.5 + b, -size * 0.5 + b, -size * 0.5];
    const x2 = [size - b / 2, size / 2, size / 2 - b * 0.866, size - b / 2 - b * 0.866, size - b / 2];
    const y2 = [-size * 0.5 + b, size * 0.5, size * 0.5 - b * 0.5, -size * 0.5 + b - b * 0.5, -size * 0.5 + b];
    const x3 = [-size + b / 2, -size / 2, -size / 2 + b * 0.866, -size + b / 2 + b * 0.866, -size + b / 2];
    const y3 = y2;
    ax.fill(x1, y1, { color: c.foreground_color, alpha: intensity });
    ax.fill(x2, y2, { color: 'gray', alpha: intensity * 0.7 });
    ax.fill(x3, y3, { color: 'darkgray', alpha: intensity * 0.9 });
  },
};
