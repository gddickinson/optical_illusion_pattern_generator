// Home page: hero with a live pattern (the Art Studio's rotation animation), counts from the API, entry cards.
import { route, api, app, esc, list } from './core.js';
import { loadCatalog, drawPattern, defaults, nice } from './ui.js';

const DOORS = [
  ['#/studio', 'Studio', 'The generator: nine pattern families, every parameter of the desktop apps, presets, animation, PNG export and the JSON config files.'],
  ['#/gallery', 'Gallery', 'All 49 patterns at their default settings, drawn live in your browser. Click one to open it in the studio.'],
  ['#/check', 'Cross-check', 'The browser drawing next to the Python/matplotlib render of the same settings, with the same random numbers.'],
  ['#/about', 'About', 'What the project is, the five desktop scripts, how to run the desktop and web apps, and how the port is tested.'],
];

route('home', async () => {
  const [info, cat] = await Promise.all([api('/info'), loadCatalog()]);
  app().innerHTML = `
  <section class="hero two heroart">
    <div>
      <p class="kicker">Spirals · moire · illusions · fractals · generative art</p>
      <h1 class="glow">Optical Illusion &amp; Pattern Generator</h1>
      <p class="lead">${esc(info.lead)} This site is the generator itself: the Python pattern code is ported to JavaScript,
      so every pattern is drawn in your browser.</p>
      <a class="btn" href="#/studio">Open the studio</a><a class="btn alt" href="#/gallery">Browse all patterns</a>
    </div>
    <figure class="fig"><canvas id="hero" width="560" height="420" role="img" aria-label="Animated logarithmic spiral with an angular colour gradient"></canvas>
      <figcaption class="small mute" id="herocap"></figcaption></figure>
  </section>
  <div class="tiles">
    <div class="tile"><b>${info.generators}</b><span>generators</span></div>
    <div class="tile"><b>${info.variants}</b><span>patterns (variants)</span></div>
    <div class="tile"><b>${info.parameters}</b><span>parameters</span></div>
    <div class="tile"><b>${info.palettes}</b><span>colour palettes</span></div>
    <div class="tile"><b>${info.web_presets}/${info.presets}</b><span>desktop presets on the web</span></div>
  </div>
  <div class="grid wide">${list(DOORS, ([href, t, d]) => `<a class="card door" href="${href}"><b>${t}</b><span>${d}</span></a>`)}</div>
  <h2>Generators</h2>
  ${list(cat.generators, g => `<p><a class="tag a" href="#/studio?g=${g.id}">${esc(g.name)}</a> ${list(g.variants, v =>
    `<a class="tag" href="#/studio?g=${g.id}&v=${encodeURIComponent(v)}">${esc(nice(v))}</a>`)}</p>`)}`;
  hero(cat);
});

// The Cosmic Spiral preset's spiral (logarithmic, three overlapping, angular gradient) turning 3 degrees a frame.
function hero(cat) {
  const canvas = document.getElementById('hero');
  const g = cat.generators.find(x => x.id === 'spiral');
  const params = defaults(g, { spiral_type: 'logarithmic', overlapping_spirals: 3, gradient_effect: 'angular' });
  const config = { ...cat.config, color_mode: 'color', color_palette: 'cosmic', width: 560, height: 420, resolution: 500,
    background_color: '#0a0716', line_width: 1.5 };
  document.getElementById('herocap').textContent = 'Spiral generator: logarithmic, 3 overlapping spirals, angular gradient (the Cosmic Spiral preset), rotating.';
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let rot = 0, last = 0, alive = true;
  const frame = t => {
    if (!alive || !canvas.isConnected) return;
    if (t - last > 60) { last = t; params.rotation = rot; drawPattern(canvas, 'spiral', params, config); rot = (rot + 3) % 360; }
    if (!still) requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
  window.addEventListener('hashchange', () => { alive = false; }, { once: true });
}
