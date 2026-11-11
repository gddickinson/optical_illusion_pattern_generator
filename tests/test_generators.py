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


@pytest.mark.skipif(importlib.util.find_spec("tkinter") is None, reason="tkinter not installed")
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
