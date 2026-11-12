# SESSION_LOG

## 2026-11-11: web interface and static GitHub Pages site (branch `web-interface`)

Refactor (no behaviour change)
- Moved OpticalIllusionGenerator, FractalGenerator, MathematicalCurvesGenerator from `optical_illusion_generator_V2.py`
  into `patterns/illusions.py`, `fractals.py`, `curves.py` (V2 imports them; rendered pixels identical, checked by hash).
- Quick presets of V2 and the Art Studio as data in `patterns/presets.py`; both GUIs apply them with `apply_preset()`
  (GUI state after each of the 10 presets checked identical to before, with a hidden Tk root).
- Added `.gitignore` (pycache, site/).

Bugs fixed (each its own "Fix ..." commit, regression test in `tests/test_generators.py` that failed first)
- `_fig_to_array` used `canvas.tostring_rgb()`, removed in matplotlib 3.10: every generate() in all five scripts and
  `patterns/` raised AttributeError on a current install. Now `buffer_rgba()`.
- `ui/__init__.py` imported the nonexistent `ui.app`: `import ui` failed. Now exports DialogsMixin.
- Kanizsa triangle: the bottom-left pac-man's mask was always empty (one shape missing) and the mouths did not face the
  triangle; now three pac-men (with apex) with 60-degree mouths towards the centre. Fixed in `patterns/illusions.py`
  and `optical_illusion_generator.py`.
- README listed features that do not exist (flow fields, reaction-diffusion, circle packing, L-systems, strange
  attractors, Fibonacci tiling); corrected to the implemented generators.

Web interface
- `web/`: FastAPI app (catalogue from the generators' own `get_parameters()`, Python PNG renders for the cross-check,
  POST /render) and a plain ES-module front end: Home, Studio, Gallery, Cross-check, About.
- JS engine: line-by-line ports of all nine generators (49 variants) to a drawing list rendered on canvas.
  Not ported: the V2 Spiral/Interference (Art Studio versions used), so the Golden Spiral and Psychedelic presets are
  desktop-only; genetic algorithm/aesthetic analyser of the enhanced scripts; SVG export.
- Agreement: `scripts/make_scene_fixture.py` records the Python drawing calls and np.random draws for 132 cases;
  `web/static/engine.test.mjs` replays the draws and matches all calls to 1e-9 (Mandelbrot/Julia escape counts:
  up to 0.1% boundary pixels allowed, none differ in the fixture).
- Tests: `python -m pytest -q tests/` 77 passed; node engine test ok (132 cases); screenshots.py static and
  `--base http://127.0.0.1:8127` all ok, no phone overflow.

## 2026-11-11 (later): fixes approved by George

- Fix: `advanced_pattern_generator.py` kept its own copies of PatternConfig, ColorManager, PatternGenerator and the
  six Art Studio generators (already drifting from `patterns/`); nothing imported them. It now imports `config.py`
  and `patterns/` (2,677 -> 1,131 lines); all 156 variant/colour renders pixel-identical, GUI presets identical.
- Fix: 'penrose' and 'ammann_beenker' tessellations were random overlapping scatters. Now real aperiodic tilings
  by de Bruijn's multigrid (`patterns/aperiodic.py`): Penrose P3 from the pentagrid, Ammann-Beenker from the 4-grid.
  Tests: edge length = tile_size, only P3 / A-B angles, interior edges shared by exactly 2 tiles, 360 degrees at
  every interior vertex, thick:thin near the golden ratio.
- Fix: Islamic `symmetry` now takes effect (`patterns/symmetry.py`): p1/p2 rectangular lattice, p4 square, p6
  hexagonal; every tile centre an n-fold rotation centre (rotated copies added when the motif lacks that order).
  p1 is pixel-identical to the old output; the default p4 now uses a square lattice.
- JS ports `web/static/aperiodic.js`, `symmetry.js`; fixture regenerated: 138 cases, 7,498 drawing calls match.
- Tests: `pytest tests/` 99 passed; node engine test ok; screenshots.py static (11 routes) and --base (6 routes)
  all ok, phone overflow 0px; README screenshots refreshed.

## 2026-11-11 (later): desktop scripts deduplicated

- Fix: `enhanced_pattern_generator_V2.py` imports PatternConfig, ColorManager, PatternGenerator, SpiralGenerator and
  InterferenceGenerator from `config.py`/`patterns/` (its copies were behaviourally identical); 2,410 -> 2,145 lines.
  All 92 variant/colour renders pixel-identical, GUI presets identical, GA builds. Its Islamic/Voronoi/Cellular/
  Tessellation generators are simplified versions with different parameters and output, so they stay (switching
  them to `patterns/` would change what the app draws: George's call).
- Fix: `optical_illusion_generator.py` and `enhanced_pattern_generator.py` moved to `_archive/` (README there): fully
  covered by their V2 versions (original's patterns pixel-identical in V2; enhanced v1's GA/animation code identical
  in V2, its demo spiral reproducible). Nothing imported them; docs, About/Home text and tests updated.
- Tests: `pytest tests/` 97 passed (the archived scripts' subprocess tests removed); node engine test 138 cases ok;
  screenshots.py static and --base (8127) all ok, phone overflow 0px.
- Still open: three maintained desktop apps (V2, enhanced V2, advanced) with overlapping GUIs (ROADMAP "consolidate");
  enhanced V2's simplified generative-art generators.
