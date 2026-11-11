"""FastAPI web app for the Optical Illusion & Pattern Generator: serves the front end in static/ and the JSON API.

Run with `python run_web.py` (http://127.0.0.1:8127, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below.

The patterns themselves are drawn in the browser by a JS port of the generators (static/engine.js). The server gives
the catalogue (the generators' own get_parameters() specs, palettes, presets) and renders with the real Python
generators (matplotlib) for the side-by-side cross-check.
"""
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from web.render import cost_error, render_png  # noqa: E402  (sets the Agg backend before pyplot loads)
from web.catalog import (  # noqa: E402
    BY_ID, GENERATORS, config_defaults, generator_info, make_config, palettes, presets,
)

STATIC = Path(__file__).resolve().parent / "static"
TITLE = "Optical Illusion & Pattern Generator"
# Cross-check renders: small figure, colour mode, and lighter settings for the pure-Python loops.
CHECK_CONFIG = {"width": 480, "height": 360, "resolution": 300, "color_mode": "color"}
CHECK_PARAMS = {"cellular": {"grid_size": 60, "generations": 30}, "tessellation": {"tile_size": 0.2}}
CHECK_SEED = 0
MAX_RANDOM_LOG = 60_000

app = FastAPI(title=TITLE)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


def _lead():
    text = (ROOT / "README.md").read_text(encoding="utf-8").split("\n## ")[0]
    return " ".join(line for line in text.splitlines()[1:] if line and not line.startswith(("!", "#")))


@app.get("/api/info")
def info():
    """Project summary and counts for the home page."""
    gens = [generator_info(g[0]) for g in GENERATORS]
    pr = presets()
    return {"title": TITLE, "lead": _lead(), "generators": len(gens), "variants": sum(len(g["variants"]) for g in gens),
            "palettes": len(palettes()), "presets": len(pr), "web_presets": sum(p["web"] for p in pr),
            "parameters": sum(len(g["params"]) for g in gens)}


@app.get("/api/catalog")
def catalog():
    """Everything the studio needs: generators with their parameter specs, config defaults, palettes, presets."""
    return {"generators": [generator_info(g[0]) for g in GENERATORS], "config": config_defaults(),
            "color_modes": ["black_white", "color", "gradient"], "palettes": palettes(), "presets": presets(),
            "check": {"config": CHECK_CONFIG, "params": CHECK_PARAMS, "seed": CHECK_SEED}}


def _check_params(gid, variant):
    g = generator_info(gid)
    if variant not in g["variants"]:
        raise HTTPException(404, f"unknown variant {variant!r} for {gid}")
    params = {k: v["default"] for k, v in g["params"].items()}
    params.update(CHECK_PARAMS.get(gid, {}))
    params[g["variant"]] = variant
    return params


def _trim(out):
    if sum(len(c[1]) if isinstance(c[1], list) else 1 for c in out["random"]) > MAX_RANDOM_LOG:
        out["random"] = None  # too long to ship; the page then says the random draws differ
    return out


@app.get("/api/check/{gid}/{variant}")
def check(gid: str, variant: str):
    """The real Python generator at its defaults (with CHECK_* settings), as PNG, with the random draws it made."""
    if gid not in BY_ID:
        raise HTTPException(404, f"unknown generator {gid!r}")
    params = _check_params(gid, variant)
    out = render_png(gid, params, CHECK_CONFIG, seed=CHECK_SEED)
    return _trim({"generator": gid, "variant": variant, "params": params, "config": CHECK_CONFIG, **out})


class RenderRequest(BaseModel):
    generator: str
    params: dict = Field(default_factory=dict)
    config: dict = Field(default_factory=dict)
    seed: int | None = None


@app.post("/api/render")
def render(req: RenderRequest):
    """Render any parameters with the Python generator (local app only; the static site has no Python)."""
    if req.generator not in BY_ID:
        raise HTTPException(404, f"unknown generator {req.generator!r}")
    spec = generator_info(req.generator)["params"]
    params = {k: v for k, v in req.params.items() if k in spec}
    why = cost_error(req.generator, params, make_config(req.config))
    if why:
        raise HTTPException(422, f"too heavy for the Python renderer: {why}")
    try:
        out = render_png(req.generator, params, req.config, seed=req.seed)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return _trim({"generator": req.generator, "params": params, **out})


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/catalog"] + [f"/check/{g[0]}/{v}" for g in GENERATORS
                                             for v in generator_info(g[0])["variants"]]
