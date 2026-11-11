// Shared page helpers: the catalogue, drawing a pattern into a canvas, labels and small form controls.
import { api, esc } from './core.js';
import { generate } from './engine.js';
import { drawScene } from './render.js';
import { SeededRandom } from './np.js';

export const loadCatalog = () => api('/catalog');

export const nice = s => String(s).replace(/_/g, ' ').replace(/^./, c => c.toUpperCase());

// Defaults of a generator from its get_parameters() spec, with overrides.
export const defaults = (g, over = {}) => ({ ...Object.fromEntries(Object.entries(g.params).map(([k, v]) => [k, v.default])), ...over });

// Generate and draw; returns the scene (with .ms, the time it took).
export function drawPattern(canvas, id, params, config, { rnd = null, seed = 1, scale = 1 } = {}) {
  const t0 = performance.now();
  const scene = generate(id, params, config, rnd || new SeededRandom(seed));
  drawScene(canvas.getContext('2d'), scene, scale);
  scene.ms = performance.now() - t0;
  return scene;
}

// Lighter settings for thumbnails (the cross-check settings from the API, at thumbnail size).
export function thumbSettings(cat, g, variant) {
  const params = defaults(g, { ...(cat.check.params[g.id] || {}), [g.variant]: variant });
  const config = { ...cat.config, ...cat.check.config, width: 320, height: 240 };
  return { params, config };
}

export function selectEl(host, id, label, options, value, onChange) {
  const wrap = document.createElement('div');
  wrap.innerHTML = `<label for="${id}">${esc(label)}</label><select id="${id}">${options.map(([v, t]) =>
    `<option value="${esc(v)}"${String(v) === String(value) ? ' selected' : ''}>${esc(t)}</option>`).join('')}</select>`;
  host.appendChild(wrap);
  const sel = wrap.querySelector('select');
  sel.addEventListener('change', () => onChange(sel.value));
  return sel;
}

export function buttonEl(host, text, onClick, alt = false) {
  const b = document.createElement('button');
  b.type = 'button'; b.textContent = text;
  if (alt) b.className = 'alt';
  b.addEventListener('click', onClick);
  host.appendChild(b);
  return b;
}

export const palSwatch = colors => `<span class="swatch" aria-hidden="true">${colors.slice(0, 8).map(c => `<i style="background:${esc(c)}"></i>`).join('')}</span>`;

// Yield to the browser so a status message paints before a long synchronous render.
export const nextFrame = () => new Promise(r => requestAnimationFrame(() => setTimeout(r, 0)));
