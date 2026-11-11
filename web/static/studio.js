// Studio: the generator itself. Pick one of the nine generators and its variant, set its parameters and the global
// settings, load the desktop apps' presets, randomise, animate as the Art Studio does, export PNG, save/load the
// desktop apps' JSON configuration, and (local app) render the same settings with the Python generator.
import { route, app, api, esc, isStatic, needsServer, onLeave, download } from './core.js';
import { cost } from './engine.js';
import { ReplayRandom } from './np.js';
import { loadCatalog, defaults, drawPattern, nice, selectEl, buttonEl, nextFrame } from './ui.js';
import { buildParams, buildGlobals } from './studio_controls.js';

const AUTO_LIMIT = 3e8; // estimated steps above which a change waits for the Generate button

route('studio', async (args, q) => {
  const cat = await loadCatalog();
  const byId = Object.fromEntries(cat.generators.map(g => [g.id, g]));
  const st = { gid: byId[q.g] ? q.g : 'spiral', params: {}, config: { ...cat.config }, seed: 1, scale: 1, timer: 0, anim: 0 };
  st.params = defaults(byId[st.gid], q.v ? { [byId[st.gid].variant]: q.v } : {});

  app().innerHTML = `<p class="kicker">Studio</p><h1 class="glow">Pattern generator</h1>
  <p class="lead">Every pattern of the desktop apps, drawn in your browser by a JavaScript port of the Python generators.
  Changes redraw at once; heavy settings wait for <b>Generate</b>.</p>
  <div class="studio"><div class="controls">
    <div id="gen"></div>
    <div><button type="button" id="go">Generate</button><button type="button" id="rand" class="alt">Random parameters</button><button type="button" id="anim" class="alt">Animate</button></div>
    <h3>Parameters</h3><div id="params"></div>
    <h3>Global settings</h3><div id="globals"></div>
    <h3>Presets</h3><div class="presets" id="presets"></div>
    <h3>Files</h3><div id="files"></div>
  </div>
  <div class="view">
    <canvas id="art" width="800" height="600" role="img" aria-label="Generated pattern"></canvas>
    <div class="status" id="status" aria-live="polite"></div>
    <div class="panel"><h3 id="gname"></h3><p class="small mute" id="gsrc"></p><p class="doc small" id="gdoc"></p></div>
    <div id="py"></div>
  </div></div>`;
  const canvas = document.getElementById('art'), status = document.getElementById('status');
  const gen = document.getElementById('gen'), pHost = document.getElementById('params'), gHost = document.getElementById('globals');

  // --- controls ---------------------------------------------------------------------------------------------
  function buildGen() {
    gen.innerHTML = '';
    const g = byId[st.gid];
    selectEl(gen, 'gsel', 'Generator', cat.generators.map(x => [x.id, `${x.name} (${x.variants.length})`]), st.gid, v => setGenerator(v));
    document.getElementById('gname').textContent = g.name;
    document.getElementById('gsrc').innerHTML = `${esc(g.class)} in <code>${esc(g.source)}</code> · desktop app <code>${esc(g.app)}</code>`;
    document.getElementById('gdoc').textContent = g.doc;
  }
  const rebuild = () => {
    buildGen();
    buildParams(pHost, byId[st.gid], st.params, (k, v) => { st.params[k] = v; schedule(); });
    buildGlobals(gHost, cat, st.config, st.seed, (k, v) => { if (k === 'seed') st.seed = v; else st.config[k] = v; schedule(); });
  };
  function setGenerator(id, over = {}) {
    stopAnim();
    st.gid = id; st.params = defaults(byId[id], over);
    rebuild(); schedule(0);
  }

  const presetHost = document.getElementById('presets');
  for (const p of cat.presets) {
    const b = buttonEl(presetHost, p.name, () => applyPreset(p));
    b.title = p.web ? `${p.app}: ${p.pattern}` : `Desktop only: ${p.note}`;
    b.disabled = !p.web;
  }
  presetHost.insertAdjacentHTML('beforeend', '<p class="small mute">The quick presets of both desktop apps (patterns/presets.py). Greyed: they set options of the V2 Spiral, which the web replaces with the Art Studio Spiral.</p>');
  function applyPreset(p) {
    const g = p.globals;
    for (const k of ['color_mode', 'resolution', 'background_color', 'foreground_color', 'custom_colors']) if (g[k] != null) st.config[k] = g[k];
    if (g.color_palette) st.config.color_palette = g.color_palette;
    setGenerator(p.generator, Object.fromEntries(Object.entries(p.params).filter(([k]) => k in byId[p.generator].params)));
    say(`Preset <b>${esc(p.name)}</b> (${esc(p.app)})`);
  }

  // --- rendering --------------------------------------------------------------------------------------------
  let msg = '';
  const say = m => { msg = m; };
  function schedule(delay = 120, force = false) {
    clearTimeout(st.timer);
    st.timer = setTimeout(() => render(force), delay);
  }
  async function render(force = false, rnd = null) {
    const est = cost(st.gid, st.params, st.config);
    if (!force && !rnd && est > AUTO_LIMIT) {
      status.innerHTML = `Heavy settings (about ${(est / 1e9).toFixed(1)} billion steps): press <b>Generate</b> to draw.`;
      return;
    }
    if (est > 5e7) { status.textContent = 'Rendering...'; await nextFrame(); }
    try {
      const scene = drawPattern(canvas, st.gid, st.params, st.config, { seed: st.seed, rnd });
      const g = byId[st.gid];
      canvas.setAttribute('aria-label', `${g.name}: ${nice(st.params[g.variant])} pattern`);
      status.innerHTML = `${msg ? msg + ' · ' : ''}<b>${nice(st.params[g.variant])}</b> · ${scene.prims.length.toLocaleString('en')} drawing calls · ${scene.ms.toFixed(0)} ms${rnd ? ' · Python random draws replayed' : ''}`;
      msg = '';
    } catch (e) {
      status.innerHTML = `<span class="err">${esc(e.message)}</span>`;
    }
  }

  document.getElementById('go').addEventListener('click', () => render(true));
  document.getElementById('rand').addEventListener('click', () => {
    for (const [k, s] of Object.entries(byId[st.gid].params)) { // randomize_parameters() of the Art Studio
      if (s.type === 'choice') st.params[k] = s.choices[Math.floor(Math.random() * s.choices.length)];
      else if (s.type === 'int') st.params[k] = s.range[0] + Math.floor(Math.random() * (s.range[1] - s.range[0] + 1));
      else st.params[k] = s.range[0] + Math.random() * (s.range[1] - s.range[0]);
    }
    rebuild(); say('Parameters randomised'); schedule(0);
  });

  // Animate as the Art Studio does: 'rotation' steps 15 degrees a frame, otherwise the first numeric parameter
  // swings sinusoidally across its range; a frame every 100 ms.
  const animBtn = document.getElementById('anim');
  function stopAnim() {
    if (!st.anim) return;
    clearTimeout(st.anim.timer); st.params[st.anim.name] = st.anim.orig; st.anim = 0;
    animBtn.textContent = 'Animate'; rebuild(); schedule(0);
  }
  animBtn.addEventListener('click', () => {
    if (st.anim) return stopAnim();
    const spec = byId[st.gid].params, nums = Object.keys(spec).filter(k => spec[k].type !== 'choice' && spec[k].range);
    if (!nums.length) { status.textContent = 'No animatable parameters for this pattern.'; return; }
    const name = nums.includes('rotation') ? 'rotation' : nums[0], [lo, hi] = spec[name].range;
    st.anim = { name, orig: st.params[name], frame: 0, timer: 0 };
    animBtn.textContent = 'Stop animation';
    const step = () => {
      if (!st.anim) return;
      const f = st.anim.frame++;
      let v = name === 'rotation' ? (f * 15) % 360 : lo + (Math.sin(f * 0.2) + 1) / 2 * (hi - lo);
      if (spec[name].type === 'int') v = Math.round(v);
      st.params[name] = v;
      render(true);
      status.innerHTML += ` · animating <b>${esc(name)}</b> = ${(+v).toFixed(2)}`;
      st.anim.timer = setTimeout(step, 100);
    };
    step();
  });
  onLeave(() => { if (st.anim) clearTimeout(st.anim.timer); st.anim = 0; });

  // --- files ------------------------------------------------------------------------------------------------
  const files = document.getElementById('files');
  selectEl(files, 'scale', 'PNG size', [[1, '1x (as on screen)'], [2, '2x'], [4, '4x']], 1, v => { st.scale = +v; });
  buttonEl(files, 'Export PNG', async () => {
    const off = document.createElement('canvas');
    drawPattern(off, st.gid, st.params, st.config, { seed: st.seed, scale: st.scale });
    off.toBlob(b => download(`${st.gid}_${st.params[byId[st.gid].variant]}.png`, b), 'image/png');
  });
  buttonEl(files, 'Save config', () => download(`${st.gid}_config.json`, JSON.stringify({
    pattern_type: byId[st.gid].name, parameters: st.params,
    global_settings: { resolution: st.config.resolution, line_width: st.config.line_width, color_mode: st.config.color_mode,
      color_palette: st.config.color_palette, background_color: st.config.background_color, foreground_color: st.config.foreground_color },
  }, null, 2), 'application/json'), true);
  const loadIn = document.createElement('input');
  loadIn.type = 'file'; loadIn.accept = '.json,application/json'; loadIn.hidden = true;
  files.appendChild(loadIn);
  buttonEl(files, 'Load config', () => loadIn.click(), true);
  loadIn.addEventListener('change', async () => {
    try {
      const d = JSON.parse(await loadIn.files[0].text()), g = cat.generators.find(x => x.name === d.pattern_type);
      if (!g) throw new Error(`unknown pattern_type ${d.pattern_type}`);
      Object.assign(st.config, Object.fromEntries(Object.entries(d.global_settings || {}).filter(([k]) => k in st.config)));
      setGenerator(g.id, Object.fromEntries(Object.entries(d.parameters || {}).filter(([k]) => k in g.params)));
      say(`Loaded ${esc(loadIn.files[0].name)}`);
    } catch (e) { status.innerHTML = `<span class="err">Could not load: ${esc(e.message)}</span>`; }
    loadIn.value = '';
  });
  files.insertAdjacentHTML('beforeend', '<p class="small mute">Config files use the desktop apps\' JSON format (Export/Import Config).</p>');
  const py = document.getElementById('py');
  if (isStatic()) py.innerHTML = needsServer('Rendering these settings with the Python generator');
  else {
    buttonEl(py, 'Render with Python', async () => {
      py.querySelector('.out')?.remove();
      py.insertAdjacentHTML('beforeend', '<div class="out"><p class="mute">Rendering with matplotlib...</p></div>');
      const out = py.querySelector('.out');
      try {
        const r = await api('/render', { body: { generator: st.gid, params: st.params, config: st.config, seed: st.seed } });
        out.innerHTML = `<h3>Python (matplotlib)</h3><img class="pyimg" src="data:image/png;base64,${r.png}" alt="The same pattern rendered by the Python generator">`;
        if (r.random && r.random.length) { say('Python render'); render(true, new ReplayRandom(r.random)); }
      } catch (e) { out.innerHTML = `<p class="err">${esc(e.message)}</p>`; }
    }, true);
  }

  rebuild();
  schedule(0);
});
