// About: what the project is, the desktop scripts, how to run the desktop and web apps, how the web port works.
import { route, app, esc, list } from './core.js';
import { loadCatalog } from './ui.js';

const SCRIPTS = [
  ['optical_illusion_generator_V2.py', 'Expanded version with more illusions, fractals and mathematical curves'],
  ['enhanced_pattern_generator_V2.py', 'Further expanded with more pattern types'],
  ['advanced_pattern_generator.py', '"Mathematical Art Studio": spirals, interference, Islamic geometry, Voronoi, cellular automata, tessellations'],
];

route('about', async () => {
  const cat = await loadCatalog();
  app().innerHTML = `<p class="kicker">About</p><h1 class="glow">Optical Illusion &amp; Pattern Generator</h1>
  <p class="lead">A desktop tool (tkinter + matplotlib) for generating mathematical patterns, fractals, classic optical
  illusions and generative art, by George Dickinson (MIT licence). This web interface puts its generators in the browser.</p>
  <h2>The desktop scripts</h2>
  <div class="scroll"><table><tr><th>File</th><th>Description</th></tr>
  ${list(SCRIPTS, ([f, d]) => `<tr><td><code>${f}</code></td><td>${esc(d)}</td></tr>`)}</table></div>
  <p>Each builds on the previous one; the first original and enhanced versions, superseded by these, are in
  <code>_archive/</code>. The web offers the generators of the two most complete: the illusions, fractals
  and curves of <code>optical_illusion_generator_V2.py</code> and the generative art of
  <code>advanced_pattern_generator.py</code> (both now kept in the <code>patterns/</code> package).</p>
  <h2>Generators on this site</h2>
  <div class="scroll"><table><tr><th>Generator</th><th>Python class</th><th>Patterns</th><th>Parameters</th></tr>
  ${list(cat.generators, g => `<tr><td><a href="#/studio?g=${g.id}">${esc(g.name)}</a></td><td><code>${esc(g.source)}</code></td>
    <td>${g.variants.length}</td><td>${Object.keys(g.params).length}</td></tr>`)}</table></div>
  <h3>Not on the web</h3>
  <ul class="small">
    <li>The V2 Spiral and Interference (the web uses the Art Studio versions, which add palettes) and with them the
      <i>Golden Spiral</i> and <i>Psychedelic</i> presets, which set V2-only options (line variation, custom colours).</li>
    <li>The genetic-algorithm "evolution" and aesthetic scoring of the enhanced scripts, and SVG export of the Art Studio.</li>
  </ul>
  <h2>How the web version works</h2>
  <p>Each generator's <code>generate()</code> draws with a handful of matplotlib calls (<code>plot</code>,
  <code>fill</code>, <code>axhline</code>, <code>contour</code>, <code>imshow</code>, <code>scatter</code>). The JS engine
  (<code>web/static/engine.js</code> and <code>gen_*.js</code>) is a line-by-line port that makes the same calls into a
  drawing list, and <code>render.js</code> draws it on a canvas with matplotlib's sizes and colour tables. Voronoi diagrams
  are computed in JS in place of SciPy's Qhull; the Penrose (P3) and Ammann-Beenker tilings come from de Bruijn's
  multigrid method in both languages. Random patterns use a seeded generator (the <i>Seed</i> setting).</p>
  <p>To check the port, <code>scripts/make_scene_fixture.py</code> runs the real Python generators against a recording
  axes and logs their NumPy random draws; the node test replays those draws through the engine and requires the same
  calls, coordinates and colours. The <a href="#/check">cross-check</a> page shows the two renders side by side.</p>
  <h2>Run it</h2>
  <pre>pip install numpy matplotlib pillow scipy
python advanced_pattern_generator.py        # desktop Art Studio
python optical_illusion_generator_V2.py     # desktop illusions / fractals / curves

pip install -r requirements-web.txt
python run_web.py                           # web app on http://127.0.0.1:8127</pre>
  <p class="small mute">The local web app adds <i>Render with Python</i> in the studio (any settings, rendered by the
  real generator). The static site (GitHub Pages) is built by <code>scripts/build_static.py</code>.</p>
  <h2>Credits</h2>
  <p>Code and design: George Dickinson (<a href="https://github.com/gddickinson/optical_illusion_pattern_generator">GitHub</a>).
  Colour tables: matplotlib's colormaps. Built with numpy, matplotlib and scipy on the desktop; plain JavaScript and canvas on the web.</p>`;
});
