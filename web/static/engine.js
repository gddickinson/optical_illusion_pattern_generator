// The pattern engine: the nine Python generators ported to JS. generate(id, params, config, rnd) returns a scene
// (figure size, background, view limits and the list of drawing primitives) that render.js draws on a canvas.
// rnd answers the np.random calls: SeededRandom in the browser, ReplayRandom (a log from Python) in the tests.
import { spiral, interference } from './gen_spirals.js';
import { illusion } from './gen_illusions.js';
import { fractal } from './gen_fractals.js';
import { curves } from './gen_curves.js';
import { islamic } from './gen_islamic.js';
import { voronoiPattern } from './gen_voronoi.js';
import { cellular } from './gen_cellular.js';
import { tessellation } from './gen_tessellation.js';
import { SeededRandom } from './np.js';

export const GENERATORS = { spiral, interference, illusion, fractal, curves, islamic, voronoi: voronoiPattern, cellular, tessellation };

// PatternConfig defaults (config.py); the web page loads the same values from /api/catalog.
export const CONFIG_DEFAULTS = { width: 800, height: 600, resolution: 1000, color_mode: 'black_white', line_width: 1.0,
  background_color: 'white', foreground_color: 'black', custom_colors: ['red', 'blue', 'green', 'purple', 'orange'],
  color_palette: 'default' };

export function generate(id, params = {}, config = {}, rnd = new SeededRandom(1)) {
  const fn = GENERATORS[id];
  if (!fn) throw new Error(`unknown generator ${id}`);
  return fn(params, { ...CONFIG_DEFAULTS, ...config }, rnd);
}

// Rough cost of a render in elementary steps, so the page can warn before a slow one.
export function cost(id, p, cfg) {
  const r = cfg.resolution || 1000;
  if (id === 'fractal' && ['mandelbrot', 'julia'].includes(p.fractal_type)) return r * r * (p.iterations || 100) / 4;
  if (id === 'interference') return r * r * 20;
  if (id === 'cellular') return (p.grid_size || 100) ** 2 * (p.generations || 50) * 9;
  if (id === 'tessellation' && p.tessellation_type === 'penrose') return 100 / (p.tile_size || 0.1) ** 2 * 50;
  if (id === 'voronoi') return (p.num_points || 50) ** 2 * 40 * (1 + (p.relaxation_steps || 0));
  return r * 10;
}
