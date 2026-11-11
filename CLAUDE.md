# Optical Illusion & Pattern Generator

@INTERFACE.md

- Desktop: tkinter + matplotlib scripts at the root; reusable generators in `patterns/`.
- Web: `web/` (FastAPI + plain ES modules, JS port of the generators). Port 8127 (`python run_web.py`).
- Tests: `python -m pytest -q tests/` (includes the node test `web/static/engine.test.mjs`).
- After changing a Python generator, rerun `python scripts/make_scene_fixture.py` and port the change to its
  `web/static/gen_*.js`; `tests/test_web.py` fails while the fixture is stale.
- Keep new files under 500 lines; update INTERFACE.md and SESSION_LOG.md.
