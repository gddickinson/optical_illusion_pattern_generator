// Voronoi diagram in the form scipy.spatial.Voronoi gives it to the Python generator: per input point its region
// (vertex indices, or bounded = false where SciPy's region contains -1) and the finite ridges (vertex index pairs).
// Each cell is found by clipping a large box with the bisector half-planes; every finite vertex is then recomputed as
// the circumcentre of its three generating points, and vertices that coincide (cocircular points, as on a grid,
// which Qhull merges) are shared.
const BOX = 1e6;

function circumcentre([ax, ay], [bx, by], [cx, cy]) {
  const d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by));
  const a2 = ax * ax + ay * ay, b2 = bx * bx + by * by, c2 = cx * cx + cy * cy;
  return [(a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d, (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d];
}

// Polygon as a list of { p: [x, y], src } where src is the neighbour whose bisector forms the edge from p to the next.
function clip(poly, pi, pj, j) {
  const nx = pj[0] - pi[0], ny = pj[1] - pi[1], mx = (pi[0] + pj[0]) / 2, my = (pi[1] + pj[1]) / 2;
  const side = p => (p[0] - mx) * nx + (p[1] - my) * ny; // <= 0: closer to pi
  const out = [];
  for (let k = 0; k < poly.length; k++) {
    const a = poly[k], b = poly[(k + 1) % poly.length], sa = side(a.p), sb = side(b.p);
    if (sa <= 0) out.push(a);
    if ((sa <= 0) !== (sb <= 0)) {
      const t = sa / (sa - sb), q = [a.p[0] + t * (b.p[0] - a.p[0]), a.p[1] + t * (b.p[1] - a.p[1])];
      if (sa <= 0) { out.push({ p: q, src: j }); } else { out.push({ p: q, src: a.src }); }
    }
  }
  return out;
}

export function voronoi(points) {
  const n = points.length, vertices = [], index = new Map(), regions = [], ridgeSet = new Map();
  const tol = 1e-9;
  const vid = (x, y) => { // index of the vertex within tol of (x, y), adding it if new
    const rx = Math.round(x / tol), ry = Math.round(y / tol);
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
      const k = `${rx + dx},${ry + dy}`;
      if (index.has(k)) return index.get(k);
    }
    vertices.push([x, y]); index.set(`${rx},${ry}`, vertices.length - 1);
    return vertices.length - 1;
  };
  for (let i = 0; i < n; i++) {
    const [px, py] = points[i];
    let poly = [[-BOX, -BOX], [BOX, -BOX], [BOX, BOX], [-BOX, BOX]].map(([x, y]) => ({ p: [px + x, py + y], src: -1 }));
    for (let j = 0; j < n; j++) if (j !== i) poly = clip(poly, points[i], points[j], j);
    // vertex k sits between edge k-1 (src of poly[k-1]) and edge k (src of poly[k])
    const m = poly.length, region = [], edges = [];
    let bounded = m > 0;
    for (let k = 0; k < m; k++) {
      const s0 = poly[(k - 1 + m) % m].src, s1 = poly[k].src;
      if (s0 < 0 || s1 < 0) { bounded = false; region.push(-1); continue; }
      const [x, y] = s0 === s1 ? poly[k].p : circumcentre(points[i], points[s0], points[s1]);
      region.push(vid(x, y));
    }
    for (let k = 0; k < m; k++) edges.push([poly[k].src, region[k], region[(k + 1) % m]]);
    const ids = [];
    region.forEach(v => { if (v >= 0 && ids[ids.length - 1] !== v) ids.push(v); });
    if (ids.length > 1 && ids[0] === ids[ids.length - 1]) ids.pop();
    regions.push({ bounded, vertices: bounded ? ids : [] });
    for (const [src, a, b] of edges) {
      if (src < 0 || src < i || a < 0 || b < 0 || a === b) continue;
      ridgeSet.set(`${i},${src}`, [a, b]);
    }
  }
  // a ridge is finite only if the neighbour's copy is finite as well
  return { vertices, regions, ridges: [...ridgeSet.values()] };
}

// Area of a region, with the generator's formula (0.5 |sum x_i (y_{i+1} - y_{i-1})|).
export function regionArea(vs) {
  let s = 0;
  for (let i = 0; i < vs.length; i++) s += vs[i][0] * (vs[(i + 1) % vs.length][1] - vs[(i - 1 + vs.length) % vs.length][1]);
  return 0.5 * Math.abs(s);
}
