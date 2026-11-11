// Cross-check: the JS engine's drawing next to the real Python generator's matplotlib render of the same settings.
// The Python renders come from /api/check (made at build time on the static site) with the np.random draws they used,
// which the JS engine replays, so even the random patterns should look the same.
import { route, app, api, esc, list } from './core.js';
import { ReplayRandom } from './np.js';
import { loadCatalog, drawPattern, nice } from './ui.js';

route('check', async (args, q) => {
  const cat = await loadCatalog();
  const byId = Object.fromEntries(cat.generators.map(g => [g.id, g]));
  let gid = byId[q.g] ? q.g : 'illusion', variant = q.v || byId[gid].variants[0];
  app().innerHTML = `<p class="kicker">Cross-check</p><h1 class="glow">Browser vs Python</h1>
  <p class="lead">Left: the JavaScript engine in your browser. Right: the repo's Python generator rendering the same
  parameters with matplotlib. Where the pattern is random, the browser replays the random numbers NumPy drew, so the two
  should match; small differences in line rendering are matplotlib's antialiasing and layout.</p>
  <div id="pick"></div>
  <div class="two" style="margin-top:12px">
    <figure class="fig"><canvas id="js" width="480" height="360" role="img" aria-label="Pattern drawn by the JS engine"></canvas><figcaption class="small mute" id="jscap">JavaScript (canvas)</figcaption></figure>
    <figure class="fig"><img id="pyimg" class="pyimg" alt="The same pattern rendered by the Python generator"><figcaption class="small mute" id="pycap">Python (matplotlib)</figcaption></figure>
  </div>
  <div class="panel small" id="params"></div>
  <div class="callout a small">The same comparison runs as an automated test: <code>web/static/engine.test.mjs</code> replays
  132 cases recorded from the Python generators (every variant in black-and-white and colour, plus extra options) and
  checks that the engine makes the same drawing calls with the same coordinates and colours, to 1e-9.</div>`;
  const pick = document.getElementById('pick');
  pick.innerHTML = list(cat.generators, g => `<div class="pick"><b>${esc(g.name)}</b>${list(g.variants, v =>
    `<button type="button" data-g="${g.id}" data-v="${esc(v)}">${esc(nice(v))}</button>`)}</div>`);
  pick.addEventListener('click', e => { const b = e.target.closest('button'); if (b) { gid = b.dataset.g; variant = b.dataset.v; show(); } });

  async function show() {
    pick.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.g === gid && b.dataset.v === variant));
    const r = await api(`/check/${gid}/${encodeURIComponent(variant)}`);
    document.getElementById('pyimg').src = `data:image/png;base64,${r.png}`;
    const rnd = r.random ? new ReplayRandom(r.random) : null;
    const scene = drawPattern(document.getElementById('js'), gid, r.params, { ...cat.config, ...r.config }, { rnd, seed: 1 });
    document.getElementById('jscap').textContent = `JavaScript (canvas): ${scene.prims.length.toLocaleString('en')} drawing calls in ${scene.ms.toFixed(0)} ms` +
      (r.random && r.random.length ? `, ${r.random.length.toLocaleString('en')} NumPy random draws replayed` : '');
    document.getElementById('pycap').textContent = `Python (matplotlib): ${byId[gid].class}.generate(), ${r.width} x ${r.height} px`;
    document.getElementById('params').innerHTML = `<b>${esc(byId[gid].name)} · ${esc(nice(variant))}</b><br>
      parameters: <code>${esc(JSON.stringify(r.params))}</code><br>config: <code>${esc(JSON.stringify(r.config))}</code>, np.random.seed(${cat.check.seed})`;
  }
  show();
});
