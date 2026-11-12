# INTERFACE.md: navigation map

## Desktop scripts (tkinter + matplotlib, run directly)
| File | Contents |
|------|----------|
| `optical_illusion_generator_V2.py` | V2 app: own Spiral/Interference; imports OpticalIllusion, Fractal, MathematicalCurves generators and presets from `patterns/` |
| `enhanced_pattern_generator_V2.py` | Enhanced app: genetic algorithm, aesthetic analyser, multi-parameter animation; shared config/Spiral/Interference from `config.py`/`patterns/`, its own simplified Islamic/Voronoi/Cellular/Tessellation generators |
| `_archive/` | Superseded scripts (`optical_illusion_generator.py`, `enhanced_pattern_generator.py`), see `_archive/README.md` |
| `advanced_pattern_generator.py` | "Mathematical Art Studio" (AdvancedArtStudio, the tkinter app); generators from `patterns/`, config from `config.py`, presets from `patterns/presets.py` |
| `config.py` | PatternConfig dataclass, ColorManager (palettes, HSV palette, interpolation) |

## `patterns/` (Tk-free generators; each class has `get_parameters()` and `generate(**params) -> RGB array`)
| Module | Contents |
|--------|----------|
| `base.py` | PatternGenerator ABC (validate_parameters, _fig_to_array) |
| `spirals.py` | SpiralGenerator, InterferenceGenerator (Art Studio versions) |
| `illusions.py` | OpticalIllusionGenerator (from V2) |
| `fractals.py` | FractalGenerator (from V2) |
| `curves.py` | MathematicalCurvesGenerator (from V2) |
| `islamic.py`, `voronoi.py`, `cellular.py`, `tessellation.py` | Art Studio generators |
| `symmetry.py` | Wallpaper symmetry p1/p2/p4/p6 for tiled motifs: tile_centres (lattices), TileAxes (n-fold copies), tiles() |
| `aperiodic.py` | de Bruijn multigrid: penrose_p3 (pentagrid), ammann_beenker (4-grid) |
| `presets.py` | PRESETS (the ten quick presets of V2 and the Art Studio) and apply_preset(app, key) used by both GUIs |

`ui/`: DialogsMixin (`dialogs.py`); the app class is still in `advanced_pattern_generator.py`.

## `web/` (web interface)
| File | Contents |
|------|----------|
| `app.py` | FastAPI app: `/api/info`, `/api/catalog`, `/api/check/{gen}/{variant}` (Python PNG + random log), `POST /api/render`; STATIC_ENDPOINTS |
| `catalog.py` | GENERATORS (the nine web generators: id, GUI name, class, source, variant parameter), presets/palettes/config defaults |
| `render.py` | Python rendering to PNG with a lock and cost limits |
| `recorder.py` | FakeAxes/record_scene (record the generators' matplotlib calls) and RandomLog (log np.random calls) |
| `static/index.html`, `main.js`, `core.js`, `style.css`, `style_app.css`, `static_api.js`, `icon.svg` | Shell, router, theme, static-site API |
| `static/home.js`, `studio.js` (+ `studio_controls.js`), `gallery.js`, `check.js`, `about.js` | Pages |
| `static/ui.js` | Shared page helpers (catalog, drawPattern, selects, thumbnails) |
| `static/engine.js` | Generator registry `generate(id, params, config, rnd)` -> scene, CONFIG_DEFAULTS, cost estimate |
| `static/gen_spirals.js`, `gen_illusions.js`, `gen_fractals.js`, `gen_curves.js`, `gen_islamic.js`, `gen_voronoi.js`, `gen_cellular.js`, `gen_tessellation.js` | Line-by-line ports of the Python generators |
| `static/scene.js` | Axes-like drawing list (same schema as recorder.py), matplotlib contour levels (MaxNLocator) |
| `static/render.js` | Draws a scene on a canvas (matplotlib layout, points, colormaps, marching squares) |
| `static/colors.js`, `mpl_data.js` | Colour parsing, colormaps, ColorManager palettes; generated matplotlib tables |
| `static/np.js` | linspace/arange as NumPy computes them; SeededRandom and ReplayRandom (np.random stand-ins) |
| `static/voronoi.js` | Voronoi regions/ridges in scipy's form (half-plane clipping + circumcentres) |
| `static/symmetry.js`, `static/aperiodic.js` | Ports of `patterns/symmetry.py` and `patterns/aperiodic.py` |
| `static/engine.test.mjs` | Node test: engine vs `tests/fixtures/scenes.json` |

## Scripts and tests
| File | Contents |
|------|----------|
| `run_web.py` | Starts the web app on 127.0.0.1:8127 |
| `scripts/build_static.py` | Exports the static site to `site/` |
| `scripts/screenshots.py` | Playwright smoke test and README screenshots (`docs/img/`) |
| `scripts/make_scene_fixture.py` | Records the Python generators' drawing calls into `tests/fixtures/scenes.json` |
| `scripts/make_mpl_data.py` | Writes `web/static/mpl_data.js` |
| `tests/test_generators.py` | Regression tests for the Python generators and the desktop scripts |
| `tests/test_web.py` | API, static build, fixture/data currency, node engine test |

Data flow: Python class -> `get_parameters()` -> `/api/catalog` -> studio controls -> `engine.generate()` -> scene ->
`render.drawScene()` -> canvas. Agreement: `recorder.record_scene()` -> fixture -> `engine.test.mjs`.
