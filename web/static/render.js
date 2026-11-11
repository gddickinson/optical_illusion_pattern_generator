// Draw an engine scene on a canvas the way matplotlib lays out the generators' figures: a figure of
// figsize inches at 100 dpi (times `scale`), the axes filling it (tight_layout, axis off) with equal aspect,
// line widths and marker sizes in points, colormaps and Normalize for images and contour lines.
import { toRGBA, css, cmapFn } from './colors.js';

const PAD = 15;            // tight_layout padding (1.08 x 10 pt font at 100 dpi), in px at scale 1
const LW = 1.5;            // rcParams lines.linewidth (pt)
const PATCH_LW = 1.0;      // rcParams patch.linewidth (pt)

export function canvasSize(scene, scale = 1) {
  return [Math.round(scene.figsize[0] * 100 * scale), Math.round(scene.figsize[1] * 100 * scale)];
}

function dataBounds(scene) {
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity, img = false;
  const add = (x, y) => { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; };
  for (const p of scene.prims) {
    if (p.x && p.y && p.t !== 'contour') p.x.forEach((x, i) => add(x, p.y[i]));
    else if (p.t === 'image') { const e = p.extent || [-0.5, p.cols - 0.5, -0.5, p.rows - 0.5]; add(e[0], e[2]); add(e[1], e[3]); img = true; }
    else if (p.t === 'contour') { add(p.x[0], p.y[0]); add(p.x[p.x.length - 1], p.y[p.y.length - 1]); img = true; }
    else if (p.t === 'circle') { add(p.cx - p.r, p.cy - p.r); add(p.cx + p.r, p.cy + p.r); }
  }
  if (!isFinite(x0)) return [[0, 1], [0, 1]];
  if (img) return [[x0, x1], [y0, y1]];
  const mx = (x1 - x0 || 1) * 0.05, my = (y1 - y0 || 1) * 0.05; // axes.xmargin / ymargin
  return [[x0 - mx, x1 + mx], [y0 - my, y1 + my]];
}

export function drawScene(ctx, scene, scale = 1) {
  const [W, H] = canvasSize(scene, scale);
  if (ctx.canvas.width !== W || ctx.canvas.height !== H) { ctx.canvas.width = W; ctx.canvas.height = H; }
  const pt = scale * 100 / 72;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = css(scene.bg || [1, 1, 1, 1]);
  ctx.fillRect(0, 0, W, H);
  const auto = dataBounds(scene);
  const [x0, x1] = scene.view.xlim || auto[0], [y0, y1] = scene.view.ylim || auto[1];
  const pad = PAD * scale, aw = W - 2 * pad, ah = H - 2 * pad;
  let sx = aw / (x1 - x0), sy = ah / (y1 - y0);
  if (scene.view.aspect === 'equal' || scene.prims.some(p => p.t === 'image')) sx = sy = Math.min(sx, sy);
  const bw = (x1 - x0) * sx, bh = (y1 - y0) * sy, ox = pad + (aw - bw) / 2, oy = pad + (ah - bh) / 2;
  const T = { X: x => ox + (x - x0) * sx, Y: y => oy + (y1 - y) * sy, sx, sy, ox, oy, bw, bh, pt };
  ctx.beginPath(); ctx.rect(ox, oy, bw, bh); ctx.clip();
  ctx.lineJoin = 'round';
  for (const p of scene.prims) DRAW[p.t](ctx, p, T);
  ctx.restore();
}

const rgba = (c, alpha) => { const v = [...(c || [0, 0, 0, 1])]; if (alpha != null) v[3] = alpha; return v; };

function stroke(ctx, p, T, color, lwPt, ls = '-', cap = null) {
  ctx.strokeStyle = css(color);
  ctx.lineWidth = Math.max(0.3, lwPt * T.pt);
  const u = lwPt * T.pt;
  ctx.setLineDash(ls === '--' ? [3.7 * u, 1.6 * u] : ls === ':' ? [1 * u, 1.65 * u] : []);
  ctx.lineCap = cap === 'round' ? 'round' : ls === '-' ? 'square' : 'butt';
  ctx.stroke();
}

function path(ctx, xs, ys, T, close = false) {
  ctx.beginPath();
  for (let i = 0; i < xs.length; i++) (i ? ctx.lineTo : ctx.moveTo).call(ctx, T.X(xs[i]), T.Y(ys[i]));
  if (close) ctx.closePath();
}

const DRAW = {
  line(ctx, p, T) {
    if (p.x.length < 2) return;
    path(ctx, p.x, p.y, T);
    stroke(ctx, p, T, rgba(p.color, p.alpha), p.lw ?? LW, p.ls || '-', p.cap);
  },
  marker(ctx, p, T) {
    const r = (p.ms ?? 6) / 2 * T.pt, face = rgba(p.color, p.alpha), edge = rgba(p.mec || p.color, p.alpha);
    for (let i = 0; i < p.x.length; i++) {
      ctx.beginPath(); ctx.arc(T.X(p.x[i]), T.Y(p.y[i]), Math.max(r, 0.4), 0, 2 * Math.PI);
      ctx.fillStyle = css(face); ctx.fill();
      ctx.setLineDash([]); ctx.lineWidth = (p.mew ?? 1) * T.pt; ctx.strokeStyle = css(edge); ctx.stroke();
    }
  },
  fill(ctx, p, T) {
    if (p.x.length < 2) return;
    path(ctx, p.x, p.y, T, true);
    ctx.fillStyle = css(rgba(p.color, p.alpha)); ctx.fill();
    const lw = p.lw ?? PATCH_LW;
    if (lw > 0) stroke(ctx, p, T, rgba(p.ec || p.color, p.alpha), lw, '-', 'butt');
  },
  hline(ctx, p, T) {
    ctx.beginPath();
    ctx.moveTo(T.ox + p.span[0] * T.bw, T.Y(p.v)); ctx.lineTo(T.ox + p.span[1] * T.bw, T.Y(p.v));
    stroke(ctx, p, T, rgba(p.color, p.alpha), p.lw ?? LW, '-', 'butt');
  },
  vline(ctx, p, T) {
    ctx.beginPath();
    ctx.moveTo(T.X(p.v), T.oy + T.bh * (1 - p.span[0])); ctx.lineTo(T.X(p.v), T.oy + T.bh * (1 - p.span[1]));
    stroke(ctx, p, T, rgba(p.color, p.alpha), p.lw ?? LW, '-', 'butt');
  },
  scatter(ctx, p, T) {
    const d = Math.max(1, (Math.sqrt(p.s) + 1) * T.pt); // marker of area s pt^2 plus its 1 pt edge
    ctx.fillStyle = css(rgba(p.color, p.alpha));
    for (let i = 0; i < p.x.length; i++) ctx.fillRect(T.X(p.x[i]) - d / 2, T.Y(p.y[i]) - d / 2, d, d);
  },
  circle(ctx, p, T) {
    ctx.beginPath();
    ctx.ellipse(T.X(p.cx), T.Y(p.cy), p.r * T.sx, p.r * T.sy, 0, 0, 2 * Math.PI);
    ctx.fillStyle = css(p.color); ctx.fill();
    ctx.setLineDash([]); ctx.lineWidth = PATCH_LW * T.pt; ctx.strokeStyle = css(p.color); ctx.stroke();
  },
  image(ctx, p, T) {
    let lo = Infinity, hi = -Infinity;
    for (const v of p.data) { if (v < lo) lo = v; if (v > hi) hi = v; }
    const f = cmapFn(p.cmap), img = new ImageData(p.cols, p.rows);
    for (let r = 0; r < p.rows; r++) {
      const dr = p.origin === 'lower' ? p.rows - 1 - r : r; // canvas row r shows data row dr
      for (let c = 0; c < p.cols; c++) {
        const v = p.data[dr * p.cols + c], col = f(hi > lo ? (v - lo) / (hi - lo) : 0), k = 4 * (r * p.cols + c);
        img.data[k] = Math.round(col[0] * 255); img.data[k + 1] = Math.round(col[1] * 255);
        img.data[k + 2] = Math.round(col[2] * 255); img.data[k + 3] = Math.round(col[3] * 255);
      }
    }
    const off = document.createElement('canvas');
    off.width = p.cols; off.height = p.rows;
    off.getContext('2d').putImageData(img, 0, 0);
    const e = p.extent || [-0.5, p.cols - 0.5, -0.5, p.rows - 0.5];
    ctx.imageSmoothingEnabled = p.cols * p.rows > 250000; // smooth big fractals, keep automaton cells crisp
    ctx.drawImage(off, T.X(e[0]), T.Y(e[3]), (e[1] - e[0]) * T.sx, (e[3] - e[2]) * T.sy);
  },
  contour(ctx, p, T) {
    const nl = p.levels.length, cm = p.cmap ? cmapFn(p.cmap) : null;
    const lo = p.levels[0], hi = p.levels[nl - 1];
    p.levels.forEach(level => {
      const color = p.color || cm(hi > lo ? (level - lo) / (hi - lo) : 0);
      ctx.beginPath();
      marchingSquares(p.x, p.y, p.z, level, (ax, ay, bx, by) => { ctx.moveTo(T.X(ax), T.Y(ay)); ctx.lineTo(T.X(bx), T.Y(by)); });
      stroke(ctx, p, T, color, p.lw ?? LW, '-', 'round');
    });
  },
};

// Contour segments of z (rows = y, cols = x) at one level; seg(ax, ay, bx, by) for each piece.
export function marchingSquares(xs, ys, z, level, seg) {
  const nx = xs.length, ny = ys.length;
  for (let i = 0; i < ny - 1; i++) {
    for (let j = 0; j < nx - 1; j++) {
      const a = z[i * nx + j], b = z[i * nx + j + 1], c = z[(i + 1) * nx + j + 1], d = z[(i + 1) * nx + j];
      const code = (a > level ? 1 : 0) | (b > level ? 2 : 0) | (c > level ? 4 : 0) | (d > level ? 8 : 0);
      if (code === 0 || code === 15) continue;
      const x0 = xs[j], x1 = xs[j + 1], y0 = ys[i], y1 = ys[i + 1];
      const e = [ // crossing points on the bottom, right, top and left edges
        () => [x0 + (level - a) / (b - a) * (x1 - x0), y0], () => [x1, y0 + (level - b) / (c - b) * (y1 - y0)],
        () => [x0 + (level - d) / (c - d) * (x1 - x0), y1], () => [x0, y0 + (level - a) / (d - a) * (y1 - y0)],
      ];
      const pairs = SEGMENTS[code];
      for (let k = 0; k < pairs.length; k += 2) { const p = e[pairs[k]](), q = e[pairs[k + 1]](); seg(p[0], p[1], q[0], q[1]); }
    }
  }
}
const SEGMENTS = [[], [3, 0], [0, 1], [3, 1], [1, 2], [3, 0, 1, 2], [0, 2], [3, 2], [2, 3], [0, 2], [0, 1, 2, 3], [1, 2],
  [1, 3], [0, 1], [3, 0], []];

export { toRGBA };
