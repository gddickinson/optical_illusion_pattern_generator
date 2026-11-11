// Studio control panels: a generator's parameters (built from its Python get_parameters() spec) and the global
// settings of the desktop apps (colour mode, palette, resolution, line width, colours), plus seed and figure size.
import { esc, slider } from './core.js';
import { toRGBA, isColor } from './colors.js';
import { nice, selectEl, palSwatch } from './ui.js';

const hex = c => '#' + toRGBA(c).slice(0, 3).map(v => Math.round(v * 255).toString(16).padStart(2, '0')).join('');
const decimals = (lo, hi) => (hi - lo >= 50 ? 0 : hi - lo >= 5 ? 1 : 2);

// One control per parameter; onChange(name, value).
export function buildParams(host, g, params, onChange) {
  host.innerHTML = '';
  for (const [name, spec] of Object.entries(g.params)) {
    if (spec.type === 'choice') {
      selectEl(host, `p-${name}`, nice(name), spec.choices.map(c => [c, nice(c)]), params[name], v => onChange(name, v));
    } else {
      const [lo, hi] = spec.range, isInt = spec.type === 'int', d = decimals(lo, hi);
      const fmt = v => (isInt ? String(Math.round(v)) : (+v).toFixed(Math.max(d, String(spec.default).split('.')[1]?.length > d ? 5 : d)));
      slider(host, { id: `p-${name}`, label: nice(name), min: lo, max: hi, step: isInt ? 1 : 'any', value: params[name], fmt },
        v => onChange(name, isInt ? Math.round(v) : v));
    }
  }
}

// Global settings; onChange(key, value) with keys of PatternConfig plus 'seed'.
export function buildGlobals(host, cat, cfg, seed, onChange) {
  host.innerHTML = '';
  selectEl(host, 'g-mode', 'Colour mode', cat.color_modes.map(m => [m, nice(m)]), cfg.color_mode, v => onChange('color_mode', v));
  const pal = selectEl(host, 'g-pal', 'Colour palette', Object.keys(cat.palettes).map(p => [p, nice(p)]), cfg.color_palette,
    v => { onChange('color_palette', v); sw.innerHTML = palSwatch(cat.palettes[v]); });
  const sw = document.createElement('div');
  sw.className = 'small'; sw.innerHTML = palSwatch(cat.palettes[cfg.color_palette] || []);
  pal.parentNode.appendChild(sw);
  slider(host, { id: 'g-res', label: 'Resolution (sample points)', min: 100, max: 5000, step: 100, value: cfg.resolution }, v => onChange('resolution', v));
  slider(host, { id: 'g-lw', label: 'Line width', min: 0.1, max: 10, step: 0.1, value: cfg.line_width, fmt: v => (+v).toFixed(1) },
    v => onChange('line_width', v));
  const cols = document.createElement('div');
  cols.className = 'colors';
  cols.innerHTML = `<div><label for="g-bg">Background</label><input type="color" id="g-bg" value="${hex(cfg.background_color)}"></div>
    <div><label for="g-fg">Foreground</label><input type="color" id="g-fg" value="${hex(cfg.foreground_color)}"></div>`;
  host.appendChild(cols);
  cols.querySelector('#g-bg').addEventListener('input', e => onChange('background_color', e.target.value));
  cols.querySelector('#g-fg').addEventListener('input', e => onChange('foreground_color', e.target.value));
  const cc = document.createElement('div');
  cc.innerHTML = `<label for="g-cc">Custom colours (Mathematical Curves, colour mode)</label>
    <input id="g-cc" value="${esc(cfg.custom_colors.join(', '))}" spellcheck="false">`;
  host.appendChild(cc);
  cc.querySelector('input').addEventListener('change', e => {
    const list = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
    if (list.length && list.every(isColor)) { e.target.removeAttribute('aria-invalid'); onChange('custom_colors', list); } else e.target.setAttribute('aria-invalid', 'true');
  });
  const size = document.createElement('div');
  size.className = 'colors';
  size.innerHTML = `<div><label for="g-w">Width (px)</label><input type="number" id="g-w" min="200" max="2400" step="10" value="${cfg.width}"></div>
    <div><label for="g-h">Height (px)</label><input type="number" id="g-h" min="200" max="2400" step="10" value="${cfg.height}"></div>
    <div><label for="g-seed">Seed</label><input type="number" id="g-seed" min="1" step="1" value="${seed}"></div>`;
  host.appendChild(size);
  const num = (id, key, lo, hi) => size.querySelector(id).addEventListener('change', e => {
    const v = Math.round(+e.target.value);
    if (v >= lo && v <= hi) onChange(key, v);
  });
  num('#g-w', 'width', 200, 2400); num('#g-h', 'height', 200, 2400); num('#g-seed', 'seed', 1, 2 ** 31);
}
