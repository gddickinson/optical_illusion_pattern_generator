// Wallpaper-group symmetry for tiled motifs: a port of patterns/symmetry.py (same arithmetic order).
// p1/p2/p4/p6 -> rotation order 1/2/4/6; tiles on a rectangular (p1, p2), square (p4) or hexagonal (p6) lattice;
// a tile whose motif is not invariant under rotation by 360/n about its centre also gets its rotated copies.
export const ORDER = { p1: 1, p2: 2, p4: 4, p6: 6 };
const TOL = 1e-9;

export function tileCentres(rx, ry, sym) {
  const out = [];
  if (sym === 'p4') {
    const a = Math.min(2 / rx, 2 / ry), ox = -rx * a / 2, oy = -ry * a / 2;
    for (let i = 0; i < rx; i++) for (let j = 0; j < ry; j++) out.push([ox + (i + 0.5) * a, oy + (j + 0.5) * a, i, j]);
  } else if (sym === 'p6') {
    const h = Math.sqrt(3) / 2, a = Math.min(2 / (rx + 0.5), 2 / (ry * h)), ox = -(rx + 0.5) * a / 2, oy = -ry * a * h / 2;
    for (let i = 0; i < rx; i++) for (let j = 0; j < ry; j++) out.push([ox + (i + 0.5 + 0.5 * (j % 2)) * a, oy + (j + 0.5) * a * h, i, j]);
  } else {
    for (let i = 0; i < rx; i++) for (let j = 0; j < ry; j++) out.push([-1 + (i + 0.5) * 2 / rx, -1 + (j + 0.5) * 2 / ry, i, j]);
  }
  return out;
}

function rotate(xs, ys, cx, cy, k, n) {
  const c = Math.cos(2 * Math.PI * k / n), s = Math.sin(2 * Math.PI * k / n);
  return [xs.map((x, i) => cx + (x - cx) * c - (ys[i] - cy) * s), xs.map((x, i) => cy + (x - cx) * s + (ys[i] - cy) * c)];
}

const near = (p, q) => Math.abs(p[0] - q[0]) <= TOL && Math.abs(p[1] - q[1]) <= TOL;
function samePoints(ax, ay, bx, by) {
  const uniq = (xs, ys) => { const pts = []; xs.forEach((x, i) => { const p = [x, ys[i]]; if (!pts.some(q => near(p, q))) pts.push(p); }); return pts; };
  const a = uniq(ax, ay), b = uniq(bx, by);
  return a.length === b.length && a.every(p => b.some(q => near(p, q)));
}

// Collects one tile's fill / circle calls; flush() draws them n-fold symmetric on the real axes.
export class TileAxes {
  constructor(ax, cx, cy, n) { Object.assign(this, { ax, cx, cy, n, prims: [] }); }
  fill(x, y, o) { this.prims.push(['fill', Array.from(x, Number), Array.from(y, Number), o, JSON.stringify(o)]); }
  circle(cx, cy, r, o) { this.prims.push(['circle', [cx], [cy], { r, ...o }, JSON.stringify({ r, ...o })]); }
  invariant() {
    if (this.n === 1) return true;
    return this.prims.every(([kind, xs, ys, , key]) => {
      const [rx, ry] = rotate(xs, ys, this.cx, this.cy, 1, this.n);
      return this.prims.some(([k2, x2, y2, , key2]) => k2 === kind && key2 === key && samePoints(rx, ry, x2, y2));
    });
  }
  flush() {
    const copies = this.invariant() ? 1 : this.n;
    for (let k = 0; k < copies; k++) {
      for (const [kind, xs, ys, o] of this.prims) {
        const [x, y] = k === 0 ? [xs, ys] : rotate(xs, ys, this.cx, this.cy, k, this.n);
        if (kind === 'fill') this.ax.fill(x, y, o);
        else this.ax.circle(x[0], y[0], o.r, { color: o.color, alpha: o.alpha });
      }
    }
  }
}

// Calls fn(cx, cy, i, j, tileAxes) for every tile and draws each tile after its call.
export function eachTile(ax, rx, ry, sym, fn) {
  const n = ORDER[sym] || 1;
  for (const [cx, cy, i, j] of tileCentres(rx, ry, sym)) {
    const t = new TileAxes(ax, cx, cy, n);
    fn(cx, cy, i, j, t);
    t.flush();
  }
}
