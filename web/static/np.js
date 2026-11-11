// The small slice of NumPy the generators use, with NumPy's own arithmetic (so results match to the last bits where
// possible), and the np.random replacements: a seeded RNG for the browser and a replay RNG for exact comparisons.
import { rng as mulberry } from './core.js';

// np.linspace: start + i * step, last value set to stop exactly.
export function linspace(a, b, n) {
  if (n <= 0) return [];
  if (n === 1) return [a];
  const step = (b - a) / (n - 1), out = new Array(n);
  for (let i = 0; i < n; i++) out[i] = i * step + a;
  out[n - 1] = b;
  return out;
}

// np.arange for floats: NumPy fills start + i * (v1 - v0) where v1 = start + step.
export function arange(a, b, s = 1) {
  const n = Math.max(0, Math.ceil((b - a) / s));
  if (n === 0) return [];
  const out = [a];
  if (n > 1) {
    const v1 = a + s, d = v1 - a;
    out.push(v1);
    for (let i = 2; i < n; i++) out.push(a + i * d);
  }
  return out;
}

export const range = n => Array.from({ length: Math.max(0, n) }, (_, i) => i);
export const radians = d => d * (Math.PI / 180);
export const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
// Python's // and % for ints and floats (floor division, sign of the divisor).
export const fdiv = (a, b) => Math.floor(a / b);
export const pmod = (a, b) => ((a % b) + b) % b;

// --- np.random -------------------------------------------------------------------------------------------------
// Both RNGs answer the calls the generators make: random(), randint(lo[, hi]), uniform(lo, hi[, size]),
// normal(mu, sigma[, size]) and choice(values, size, p). A size returns a flat array.
const count = size => (size == null ? null : Array.isArray(size) ? size.reduce((a, b) => a * b, 1) : size);

export class SeededRandom {
  constructor(seed = 1) { this.r = mulberry(seed); this.spare = null; }
  random() { return this.r(); }
  randint(lo, hi) { if (hi == null) { hi = lo; lo = 0; } return lo + Math.floor(this.r() * (hi - lo)); }
  uniform(lo, hi, size) {
    const n = count(size), one = () => lo + (hi - lo) * this.r();
    return n == null ? one() : Array.from({ length: n }, one);
  }
  gauss() {
    if (this.spare != null) { const s = this.spare; this.spare = null; return s; }
    let u = 0; while (u === 0) u = this.r();
    const v = this.r(), m = Math.sqrt(-2 * Math.log(u));
    this.spare = m * Math.sin(2 * Math.PI * v);
    return m * Math.cos(2 * Math.PI * v);
  }
  normal(mu, sigma, size) {
    const n = count(size), one = () => mu + sigma * this.gauss();
    return n == null ? one() : Array.from({ length: n }, one);
  }
  choice(values, size, p) {
    const n = count(size), cdf = [];
    let acc = 0;
    for (const q of p) cdf.push(acc += q);
    const one = () => { const u = this.r() * acc; let i = 0; while (i < cdf.length - 1 && u >= cdf[i]) i++; return values[i]; };
    return n == null ? one() : Array.from({ length: n }, one);
  }
}

// Plays back a log of [name, value] pairs recorded from NumPy by web/recorder.py (RandomLog).
export class ReplayRandom {
  constructor(calls) { this.calls = calls; this.i = 0; }
  next(name) {
    const c = this.calls[this.i++];
    if (!c) throw new Error(`replay log exhausted at call ${this.i} (${name})`);
    if (c[0] !== name) throw new Error(`replay call ${this.i}: engine asked for ${name}, Python called ${c[0]}`);
    return c[1];
  }
  random() { return this.next('random'); }
  randint() { return this.next('randint'); }
  uniform() { return this.next('uniform'); }
  normal() { return this.next('normal'); }
  choice() { return this.next('choice'); }
  get done() { return this.i === this.calls.length; }
}
