// VoronoiGenerator (patterns/voronoi.py), ported line by line; the diagram itself comes from voronoi.js in place of
// scipy.spatial.Voronoi.
import { subplots } from './scene.js';
import { getPalette } from './colors.js';
import { linspace, mean, range } from './np.js';
import { voronoi, regionArea } from './voronoi.js';

export const VORONOI_DEFAULTS = { num_points: 50, distribution: 'random', style: 'both', edge_thickness: 1.0, color_by: 'random',
  relaxation_steps: 0, clip_bounds: 'square' };

export function voronoiPattern(p, cfg, rnd) {
  const q = { ...VORONOI_DEFAULTS, ...p };
  let points = generatePoints(q.num_points, q.distribution, rnd);
  for (let k = 0; k < q.relaxation_steps; k++) points = lloyd(points);
  const vor = voronoi(points);
  const ax = subplots(cfg);
  ax.setXlim(-1, 1); ax.setYlim(-1, 1); ax.setAspect('equal'); ax.axis('off');
  const colors = getPalette(cfg.color_palette, q.num_points);
  const cellColors = assignColors(points, vor, q.color_by, colors);
  draw(ax, cfg, points, vor, q.style, q.edge_thickness, cellColors, q.clip_bounds, rnd);
  ax.setFacecolor(cfg.background_color);
  return ax.scene();
}

export function generatePoints(n, dist, rnd) {
  const pairs = flat => range(flat.length / 2).map(i => [flat[2 * i], flat[2 * i + 1]]);
  if (dist === 'grid') {
    const side = Math.trunc(Math.sqrt(n)), g = linspace(-0.9, 0.9, side), pts = [];
    for (const y of g) for (const x of g) pts.push([x, y]);
    return pts.slice(0, n);
  }
  if (dist === 'poisson') {
    const pts = [];
    let attempts = 0;
    while (pts.length < n && attempts < n * 10) {
      const [cx, cy] = rnd.uniform(-1, 1, 2);
      if (!pts.length || Math.min(...pts.map(([x, y]) => Math.sqrt((cx - x) ** 2 + (cy - y) ** 2))) > 0.1) pts.push([cx, cy]);
      attempts++;
    }
    return pts;
  }
  if (dist === 'fibonacci') {
    const golden = (1 + Math.sqrt(5)) / 2;
    return range(n).map(i => { const r = Math.sqrt(i / n) * 0.9, th = 2 * Math.PI * i / golden; return [r * Math.cos(th), r * Math.sin(th)]; });
  }
  return pairs(rnd.uniform(-1, 1, [n, 2])); // 'random' and anything else
}

function regionPts(vor, i) { return vor.regions[i].vertices.map(v => vor.vertices[v]); }

function lloyd(points) {
  const vor = voronoi(points);
  return points.map((p, i) => {
    const r = vor.regions[i];
    if (r.bounded && r.vertices.length) { const vs = regionPts(vor, i); return [mean(vs.map(v => v[0])), mean(vs.map(v => v[1]))]; }
    return p;
  });
}

function assignColors(points, vor, by, colors) {
  const n = points.length;
  if (by === 'distance') {
    const d = points.map(([x, y]) => Math.sqrt(x * x + y * y)), lo = Math.min(...d), hi = Math.max(...d);
    return d.map(v => colors[Math.trunc((v - lo) / Math.max(hi - lo, 1e-10) * (colors.length - 1))]);
  }
  if (by === 'area') {
    const areas = range(n).map(i => (vor.regions[i].bounded && vor.regions[i].vertices.length ? regionArea(regionPts(vor, i)) : 0));
    const lo = Math.min(...areas), hi = Math.max(...areas);
    if (hi > lo) return areas.map(a => colors[Math.trunc((a - lo) / (hi - lo) * (colors.length - 1))]);
    return range(n).map(() => colors[0]);
  }
  return range(n).map(i => colors[i % colors.length]); // 'random', 'neighbors' and anything else
}

function draw(ax, cfg, points, vor, style, thick, cellColors, clipBounds, rnd) {
  const bounded = i => vor.regions[i].bounded && vor.regions[i].vertices.length > 0;
  const colorOf = i => (cfg.color_mode === 'color' ? cellColors[i] : cfg.foreground_color);
  if (style === 'filled' || style === 'both') {
    for (const i of range(points.length)) {
      if (!bounded(i)) continue;
      let vs = regionPts(vor, i);
      if (clipBounds === 'square') vs = vs.map(([x, y]) => [Math.min(1, Math.max(-1, x)), Math.min(1, Math.max(-1, y))]);
      else if (clipBounds === 'circle') vs = vs.map(([x, y]) => { const d = Math.sqrt(x * x + y * y); return d > 1 ? [x / d, y / d] : [x, y]; });
      if (vs.length > 2) ax.fill(vs.map(v => v[0]), vs.map(v => v[1]), { color: colorOf(i), alpha: 0.7 });
    }
  }
  if (style === 'edges' || style === 'both') {
    for (const [a, b] of vor.ridges) {
      ax.plot([vor.vertices[a][0], vor.vertices[b][0]], [vor.vertices[a][1], vor.vertices[b][1]], { fmt: 'k-', lw: cfg.line_width * thick, alpha: 0.8 });
    }
  }
  if (style === 'stippled') {
    for (const i of range(points.length)) {
      if (!bounded(i)) continue;
      const vs = regionPts(vor, i);
      if (vs.length <= 2) continue;
      const c = [mean(vs.map(v => v[0])), mean(vs.map(v => v[1]))];
      for (let k = 0; k < 20; k++) {
        const [dx, dy] = rnd.normal(0, 0.1, 2), tp = [c[0] + dx, c[1] + dy];
        if (pointInPolygon(tp, vs)) ax.plot(tp[0], tp[1], { fmt: 'o', color: colorOf(i), ms: 2 });
      }
    }
  }
}

// _point_in_polygon, including its use of xinters from an earlier edge when an edge is horizontal.
function pointInPolygon([x, y], vs) {
  const n = vs.length;
  let inside = false, [p1x, p1y] = vs[0], xinters;
  for (let i = 1; i <= n; i++) {
    const [p2x, p2y] = vs[i % n];
    if (y > Math.min(p1y, p2y) && y <= Math.max(p1y, p2y) && x <= Math.max(p1x, p2x)) {
      if (p1y !== p2y) xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x;
      if (p1x === p2x || x <= xinters) inside = !inside;
    }
    [p1x, p1y] = [p2x, p2y];
  }
  return inside;
}
