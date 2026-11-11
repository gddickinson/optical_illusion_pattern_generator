// Gallery: every variant of every generator at its default parameters (with the cross-check's lighter settings for
// the heavy ones), drawn progressively in the browser. Click one to open it in the studio.
import { route, app, esc, list } from './core.js';
import { loadCatalog, drawPattern, thumbSettings, nice, nextFrame } from './ui.js';

route('gallery', async () => {
  const cat = await loadCatalog();
  const total = cat.generators.reduce((n, g) => n + g.variants.length, 0);
  app().innerHTML = `<p class="kicker">Gallery</p><h1 class="glow">All ${total} patterns</h1>
  <p class="lead">Each generator's variants at their default parameters, in colour mode with the default palette, at
  resolution ${cat.check.config.resolution}. Drawn live by the JS engine; click one to open it in the studio.</p>
  ${list(cat.generators, g => `<h2>${esc(g.name)}</h2><p class="small mute">${esc(g.class)} · <code>${esc(g.source)}</code></p>
    <div class="gal">${list(g.variants, v => `<a href="#/studio?g=${g.id}&v=${encodeURIComponent(v)}">
      <canvas width="320" height="240" data-g="${g.id}" data-v="${esc(v)}" role="img" aria-label="${esc(g.name)}: ${esc(nice(v))}"></canvas>
      <span>${esc(nice(v))}</span><small>${esc(g.variant)} = ${esc(v)}</small></a>`)}</div>`)}`;
  const byId = Object.fromEntries(cat.generators.map(g => [g.id, g]));
  for (const c of app().querySelectorAll('canvas[data-g]')) {
    if (!c.isConnected) return; // page left
    const g = byId[c.dataset.g], { params, config } = thumbSettings(cat, g, c.dataset.v);
    drawPattern(c, g.id, params, config, { seed: 7 });
    await nextFrame();
  }
});
