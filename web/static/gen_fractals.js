// FractalGenerator (patterns/fractals.py, from optical_illusion_generator_V2.py), ported line by line.
import { subplots } from './scene.js';
import { linspace } from './np.js';

export const FRACTAL_DEFAULTS = { fractal_type: 'mandelbrot', iterations: 100, zoom: 1.0, center_x: 0.0, center_y: 0.0,
  julia_c_real: -0.7, julia_c_imag: 0.27015, color_scheme: 'classic' };
const CMAP = { hot: 'hot', cool: 'cool', rainbow: 'rainbow' };

export function fractal(p, cfg, rnd) {
  const q = { ...FRACTAL_DEFAULTS, ...p };
  const ax = subplots(cfg), fg = cfg.foreground_color;
  const type = q.fractal_type;
  if (type === 'sierpinski') return sierpinski(ax, q.iterations, fg, rnd);
  if (type === 'barnsley_fern') return fern(ax, q.iterations, fg, rnd);
  if (type === 'dragon_curve') return dragon(ax, q.iterations, cfg);
  const julia = type === 'julia' ? [q.julia_c_real, q.julia_c_imag] : null;
  const data = escapeCounts(q.iterations, q.zoom, q.center_x, q.center_y, cfg.resolution, julia);
  const cmap = cfg.color_mode === 'black_white' ? 'gray' : (CMAP[q.color_scheme] || 'viridis');
  ax.imshow(data, cfg.resolution, cfg.resolution, { cmap, origin: 'lower', extent: [-2, 2, -2, 2] });
  ax.axis('off');
  ax.setFacecolor(cfg.background_color);
  return ax.scene();
}

// _generate_mandelbrot / _generate_julia: the iteration at which |z| first exceeds 2 (max_iter if never).
export function escapeCounts(maxIter, zoom, cx, cy, res, julia = null) {
  const xs = linspace(cx - 2 / zoom, cx + 2 / zoom, res), ys = linspace(cy - 2 / zoom, cy + 2 / zoom, res);
  const out = new Int32Array(res * res);
  for (let i = 0; i < res; i++) {
    for (let j = 0; j < res; j++) {
      let zr = julia ? xs[j] : 0, zi = julia ? ys[i] : 0;
      const cr = julia ? julia[0] : xs[j], ci = julia ? julia[1] : ys[i];
      let m = maxIter;
      for (let k = 0; k < maxIter; k++) {
        if (!(Math.hypot(zr, zi) <= 2)) { m = k; break; }
        const nr = zr * zr - zi * zi + cr;
        zi = zr * zi + zi * zr + ci; zr = nr;
      }
      out[i * res + j] = m;
    }
  }
  return out;
}

function sierpinski(ax, iterations, fg, rnd) {
  const v = [[0, 0], [1, 0], [0.5, Math.sqrt(3) / 2]];
  let px = 0.5, py = 0.25;
  const xs = [px], ys = [py];
  for (let k = 0; k < iterations * 100; k++) {
    const [vx, vy] = v[rnd.randint(0, 3)];
    px = (px + vx) / 2; py = (py + vy) / 2;
    xs.push(px); ys.push(py);
  }
  ax.scatter(xs, ys, { s: 0.1, c: fg, alpha: 0.8 });
  ax.setXlim(-0.1, 1.1); ax.setYlim(-0.1, 1.0); ax.setAspect('equal'); ax.axis('off');
  return ax.scene(); // the Python returns before setting the figure background
}

function fern(ax, iterations, fg, rnd) {
  let x = 0, y = 0;
  const xs = [], ys = [];
  for (let k = 0; k < iterations * 100; k++) {
    const r = rnd.random();
    if (r < 0.01) [x, y] = [0, 0.16 * y];
    else if (r < 0.86) [x, y] = [0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6];
    else if (r < 0.93) [x, y] = [0.2 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6];
    else [x, y] = [-0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44];
    xs.push(x); ys.push(y);
  }
  ax.scatter(xs, ys, { s: 0.1, c: fg, alpha: 0.7 });
  ax.setXlim(-3, 3); ax.setYlim(0, 10); ax.setAspect('equal'); ax.axis('off');
  return ax.scene();
}

// Dragon curve of order min(iterations // 10, 15): each step appends the curve rotated 90 degrees about its end.
export function dragonCoords(order) {
  let coords = [[0, 0], [1, 0]];
  for (let o = 1; o <= order; o++) {
    const [lx, ly] = coords[coords.length - 1], add = [];
    for (let i = coords.length - 2; i >= 0; i--) {
      const [x, y] = coords[i];
      add.push([lx - (y - ly), ly + (x - lx)]);
    }
    coords = coords.concat(add);
  }
  return coords;
}

function dragon(ax, iterations, cfg) {
  const c = dragonCoords(Math.min(Math.floor(iterations / 10), 15));
  ax.plot(c.map(v => v[0]), c.map(v => v[1]), { color: cfg.foreground_color, lw: cfg.line_width });
  ax.setAspect('equal'); ax.axis('off');
  return ax.scene();
}
