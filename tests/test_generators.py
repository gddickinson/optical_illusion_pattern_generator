"""Regression tests for the Python pattern generators (patterns package and the standalone desktop scripts).

Run: python -m pytest -q tests/test_generators.py
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np  # noqa: E402
import pytest  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import PatternConfig  # noqa: E402
import patterns  # noqa: E402

GENERATORS = [getattr(patterns, n) for n in patterns.__all__ if n != "PatternGenerator"]


@pytest.mark.parametrize("cls", GENERATORS, ids=lambda c: c.__name__)
def test_generate_returns_rgb_image(cls):
    """_fig_to_array used canvas.tostring_rgb(), removed in matplotlib 3.10: every generate() raised."""
    cfg = PatternConfig(width=200, height=150, resolution=80)
    small = {"iterations": 20, "grid_size": 50, "generations": 5, "num_points": 20, "tile_size": 0.4}
    params = {k: v for k, v in small.items() if k in cls(cfg).get_parameters()}
    np.random.seed(0)
    img = cls(cfg).generate(**params)
    assert img.dtype == np.uint8 and img.ndim == 3 and img.shape[2] == 3 and img.shape[0] > 0


SCRIPT = """
import sys, numpy as np
sys.path.insert(0, {root!r})
import importlib
m = importlib.import_module({mod!r})
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
cfg = m.PatternConfig(width=200, height=150, resolution=60)
img = m.SpiralGenerator(cfg).generate()
assert img.ndim == 3 and img.shape[2] == 3, img.shape
print('ok')
"""
SCRIPTS = ["optical_illusion_generator", "optical_illusion_generator_V2", "enhanced_pattern_generator",
           "enhanced_pattern_generator_V2", "advanced_pattern_generator"]


# The desktop scripts call matplotlib.use('TkAgg'), which cannot load without a display (e.g. Linux CI).
NO_TK = importlib.util.find_spec("tkinter") is None or (sys.platform.startswith("linux") and not os.environ.get("DISPLAY"))


@pytest.mark.skipif(NO_TK, reason="tkinter or a display not available")
@pytest.mark.parametrize("mod", SCRIPTS)
def test_desktop_script_generators_render(mod):
    """The same tostring_rgb failure in each standalone desktop script (run in a subprocess: they select TkAgg)."""
    env = dict(os.environ, MPLBACKEND="Agg")
    r = subprocess.run([sys.executable, "-c", SCRIPT.format(root=str(ROOT), mod=mod)], capture_output=True, text=True,
                       env=env, cwd=ROOT, timeout=120)
    assert r.returncode == 0 and "ok" in r.stdout, r.stderr[-800:]


@pytest.mark.skipif(importlib.util.find_spec("tkinter") is None, reason="tkinter not installed")
def test_ui_package_imports():
    """ui/__init__.py imported ui.app, which does not exist, so `import ui` raised ModuleNotFoundError."""
    import ui
    assert hasattr(ui.DialogsMixin, "show_about")


class _FillLog:
    def __init__(self):
        self.fills = []

    def fill(self, x, y, **kw):
        self.fills.append((np.asarray(x, float), np.asarray(y, float)))


def test_kanizsa_draws_three_pacmen_facing_the_centre():
    """The bottom-left mask (theta > 7pi/6) & (theta < pi/2) was always empty, so only two shapes were drawn, and the
    others' mouths did not face the illusory triangle. Each pac-man must be drawn, with its mouth towards (0, 0)."""
    from matplotlib.path import Path as MPath
    from patterns.illusions import OpticalIllusionGenerator
    size, ax = 0.5, _FillLog()
    OpticalIllusionGenerator(PatternConfig())._generate_kanizsa_triangle(ax, size, 1.0)
    centers = [(0, size), (-size * 0.866, -size * 0.5), (size * 0.866, -size * 0.5)]
    assert len(ax.fills) == 3
    r = size * 0.3
    for (x, y), (cx, cy) in zip(ax.fills, centers):
        assert len(x) > 10
        path = MPath(np.column_stack([x, y]))
        to_centre = -np.array([cx, cy]) / np.hypot(cx, cy)
        assert not path.contains_point((cx + 0.6 * r * to_centre[0], cy + 0.6 * r * to_centre[1]))  # the mouth
        assert path.contains_point((cx - 0.6 * r * to_centre[0], cy - 0.6 * r * to_centre[1]))  # the body


@pytest.mark.skipif(NO_TK, reason="tkinter or a display not available")
def test_kanizsa_original_script_same_fix():
    """optical_illusion_generator.py carries its own copy of the Kanizsa code; it must match the patterns version."""
    code = ("import sys; sys.path.insert(0, %r)\nimport numpy as np, optical_illusion_generator as o\n"
            "from patterns.illusions import OpticalIllusionGenerator as G\nfrom config import PatternConfig\n"
            "class L:\n  def __init__(s): s.f=[]\n  def fill(s, x, y, **k): s.f.append((list(x), list(y)))\n"
            "a, b = L(), L()\no.OpticalIllusionGenerator(o.PatternConfig())._generate_kanizsa_triangle(a, 0.5, 1)\n"
            "G(PatternConfig())._generate_kanizsa_triangle(b, 0.5, 1)\nassert a.f == b.f and len(a.f) == 3 and all(len(x) > 10 for x, y in a.f)\nprint('ok')\n") % str(ROOT)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT,
                       env=dict(os.environ, MPLBACKEND="Agg"), timeout=60)
    assert r.returncode == 0 and "ok" in r.stdout, r.stderr[-600:]
