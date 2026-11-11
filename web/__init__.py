"""Web interface for the Optical Illusion & Pattern Generator.

- app: FastAPI app (catalogue, Python cross-check renders) and STATIC_ENDPOINTS for the static site
- catalog: the nine generators offered on the web, their parameter specs, config defaults, palettes, presets
- render: Python (matplotlib Agg) rendering to PNG
- recorder: fake Axes / np.random log that records what the Python generators draw (for the JS engine tests)
- static/: the ES-module front end and the JS engine (engine.js and gen_*.js)
"""
