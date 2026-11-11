// Node test: the JS engine draws what the Python generators draw. tests/fixtures/scenes.json (made by
// scripts/make_scene_fixture.py) holds, per case, the parameters, the drawing calls recorded from the real Python
// generator and its np.random draws; the engine replays the draws and must produce the same calls.
// Run: node web/static/engine.test.mjs
import { readFileSync } from 'node:fs';
import { generate } from './engine.js';
import { ReplayRandom } from './np.js';
import { cmapSignature } from './colors.js';
import { contourLevels } from './scene.js';

const fx = JSON.parse(readFileSync(new URL('../../tests/fixtures/scenes.json', import.meta.url)));
const RTOL = 1e-9, ATOL = 1e-9;

function close(a, b, path, tol = ATOL) {
  if (a == null || b == null) { if (a != b) throw new Error(`${path}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`); return; }
  if (Array.isArray(b) || ArrayBuffer.isView(b)) {
    if (a.length !== b.length) throw new Error(`${path}: length ${a.length} != ${b.length}`);
    for (let i = 0; i < b.length; i++) close(a[i], b[i], `${path}[${i}]`, tol);
    return;
  }
  if (typeof b === 'object') { for (const k of Object.keys(b)) close(a[k], b[k], `${path}.${k}`, tol); return; }
  if (typeof b === 'number') { if (!(Math.abs(a - b) <= tol + RTOL * Math.abs(b))) throw new Error(`${path}: ${a} != ${b}`); return; }
  if (a !== b) throw new Error(`${path}: ${a} != ${b}`);
}

// Polygon up to starting vertex and direction (scipy and voronoi.js list a region's vertices differently).
function canonPoly(xs, ys) {
  let pts = xs.map((x, i) => [x, ys[i]]);
  let area = 0;
  for (let i = 0; i < pts.length; i++) { const [a, b] = pts[i], [c, d] = pts[(i + 1) % pts.length]; area += a * d - b * c; }
  if (area < 0) pts = pts.reverse();
  let k = 0;
  pts.forEach((p, i) => { if (p[0] < pts[k][0] - 1e-12 || (Math.abs(p[0] - pts[k][0]) <= 1e-12 && p[1] < pts[k][1])) k = i; });
  return pts.slice(k).concat(pts.slice(0, k));
}
const r6 = v => Math.round(v * 1e6);
const segKey = p => [[p.x[0], p.y[0]], [p.x[1], p.y[1]]].sort((u, v) => r6(u[0]) - r6(v[0]) || r6(u[1]) - r6(v[1])).flat();

function comparePrim(js, py, path, id) {
  if (js.t !== py.t) throw new Error(`${path}: type ${js.t} != ${py.t}`);
  const skip = new Set(['cmap', 'levels', 'data']);
  for (const k of Object.keys(py)) if (!skip.has(k)) {
    if (id === 'voronoi' && js.t === 'fill' && (k === 'x' || k === 'y')) continue;
    close(js[k], py[k], `${path}.${k}`, ['color', 'ec', 'mec'].includes(k) ? 2e-6 : ATOL); // cmap colours: 6-digit tables
  }
  if (id === 'voronoi' && js.t === 'fill') close(canonPoly(js.x, js.y), canonPoly(py.x, py.y), `${path}.polygon`);
  if (py.cmap) close(cmapSignature(js.cmap), py.cmap, `${path}.cmap`, 2e-6);
  if (py.levels) close(js.levels, py.levels, `${path}.levels`);
  if (py.data) {
    if (id === 'fractal') { // escape counts: allow a few boundary pixels (|z| = 2 ties) to differ
      const bad = py.data.filter((v, i) => v !== js.data[i]).length;
      if (bad > py.data.length * 1e-3) throw new Error(`${path}.data: ${bad} of ${py.data.length} pixels differ`);
    } else close(Array.from(js.data), py.data, `${path}.data`);
  }
}

let n = 0, prims = 0;
const failures = [];
fx.cases.forEach((c, ci) => {
  const label = `case ${ci} ${c.id} ${JSON.stringify(c.params).slice(0, 90)} ${c.config.color_mode}`;
  try {
    const rnd = new ReplayRandom(c.random);
    const js = generate(c.id, c.params, c.config, rnd), py = c.scene;
    if (!rnd.done) throw new Error(`only ${rnd.i} of ${c.random.length} random draws used`);
    close(js.figsize, py.figsize, 'figsize'); close(js.bg, py.bg, 'bg'); close(js.view, py.view, 'view');
    let jp = js.prims, pp = py.prims;
    if (c.id === 'voronoi') { // ridge order is Qhull's: compare the edges as a set
      const lines = a => a.filter(p => p.t === 'line').map(segKey).sort((u, v) => u.map((x, k) => r6(x) - r6(v[k])).find(d => d) || 0);
      close(lines(jp), lines(pp), 'ridges');
      jp = jp.filter(p => p.t !== 'line'); pp = pp.filter(p => p.t !== 'line');
    }
    if (jp.length !== pp.length) throw new Error(`${jp.length} primitives, Python drew ${pp.length}`);
    jp.forEach((p, i) => comparePrim(p, pp[i], `prims[${i}]`, c.id));
    n++; prims += pp.length;
  } catch (e) { failures.push(`${label}: ${e.message}`); }
});

// contour levels on their own: matplotlib's MaxNLocator choices for a few ranges
for (const [lo, hi, want] of [[-2, 2, 21], [-4, 4, 21], [0, 1, 21]]) {
  const lv = contourLevels([lo, hi], 20);
  if (lv[0] > lo || lv[lv.length - 1] < hi || lv.length > want + 2) failures.push(`levels for [${lo}, ${hi}]: ${lv}`);
}

if (failures.length) {
  console.error(failures.slice(0, 25).join('\n'));
  console.error(`FAILED ${failures.length} of ${fx.cases.length} cases`);
  process.exit(1);
}
console.log(`ok: ${n} cases, ${prims} drawing calls match the Python generators`);
