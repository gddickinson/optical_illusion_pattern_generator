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

Left for George
- IslamicGeometryGenerator's `symmetry` parameter is never used by its drawing code (no effect).
- The 'penrose' and 'ammann_beenker' tessellations are random scatters of rhombi/octagons, not aperiodic tilings
  (the README now says so); turning them into real tilings is a feature decision.
- Five overlapping desktop scripts (ROADMAP "consolidate"); `advanced_pattern_generator.py` is 2,677 lines.

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
