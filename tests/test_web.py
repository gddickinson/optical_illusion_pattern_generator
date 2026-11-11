"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific -------------------------------------------------------------------------------------------
import json  # noqa: E402

import numpy as np  # noqa: E402

from web.catalog import GENERATORS  # noqa: E402


def test_catalog_lists_every_generator_and_variant():
    cat = client.get("/api/catalog").json()
    assert [g["id"] for g in cat["generators"]] == [g[0] for g in GENERATORS]
    assert sum(len(g["variants"]) for g in cat["generators"]) == 49
    assert len(cat["palettes"]) == 10 and len(cat["presets"]) == 10
    for p in cat["presets"]:
        if p["web"]:
            g = next(x for x in cat["generators"] if x["id"] == p["generator"])
            assert set(p["params"]) <= set(g["params"]), p["key"]


def test_check_renders_png_and_random_log():
    r = client.get("/api/check/fractal/barnsley_fern").json()
    assert r["png"].startswith("iVBOR") and r["random"] and r["random"][0][0] == "random"
    assert client.get("/api/check/fractal/nope").status_code == 404


def test_render_post_and_limits():
    r = client.post("/api/render", json={"generator": "curves", "params": {"curve_type": "rose"},
                                         "config": {"width": 300, "height": 200, "resolution": 200}})
    assert r.status_code == 200 and r.json()["png"].startswith("iVBOR")
    heavy = client.post("/api/render", json={"generator": "cellular", "params": {"grid_size": 500, "generations": 200}})
    assert heavy.status_code == 422
    bad = client.post("/api/render", json={"generator": "spiral", "params": {"arms": 99}})
    assert bad.status_code == 422  # the generator's own validate_parameters


def test_scene_fixture_is_current():
    """tests/fixtures/scenes.json (used by engine.test.mjs) still matches what the Python generators draw."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_scene_fixture
    diff = make_scene_fixture.close(make_scene_fixture.fixture(), json.loads(make_scene_fixture.OUT.read_text()))
    assert diff is None, diff


def test_mpl_data_is_current():
    """web/static/mpl_data.js holds matplotlib's colormap tables and named colours, and config.py's palettes."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_mpl_data
    text = make_mpl_data.OUT.read_text()
    for name, vals in make_mpl_data.tables().items():
        line = next(ln for ln in text.splitlines() if ln.strip().startswith(name + ":"))
        assert np.allclose(json.loads(line.split(":", 1)[1].rstrip(",")), vals, atol=2e-6), name
    from config import ColorManager
    assert json.dumps(ColorManager.PALETTES, separators=(",", ":")) in text
