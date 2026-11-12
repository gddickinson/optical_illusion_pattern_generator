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
SCRIPTS = ["optical_illusion_generator_V2", "enhanced_pattern_generator_V2", "advanced_pattern_generator"]  # (+ _archive/)


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
def test_advanced_script_uses_the_patterns_package():
    """advanced_pattern_generator.py kept its own copies of the patterns/ generators (already drifting apart);
    it must use the shared classes so the desktop app, the package and the web stay the same."""
    code = ("import sys; sys.path.insert(0, %r)\nimport advanced_pattern_generator as a, patterns, config\n"
            "names = ['IslamicGeometryGenerator', 'VoronoiGenerator', 'CellularAutomataGenerator', 'TessellationGenerator',"
            " 'SpiralGenerator', 'InterferenceGenerator', 'PatternGenerator']\n"
            "assert all(getattr(a, n) is getattr(patterns, n) for n in names), [n for n in names if getattr(a, n) is not getattr(patterns, n)]\n"
            "assert a.PatternConfig is config.PatternConfig and a.ColorManager is config.ColorManager\nprint('ok')\n") % str(ROOT)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT,
                       env=dict(os.environ, MPLBACKEND="Agg"), timeout=60)
    assert r.returncode == 0 and "ok" in r.stdout, r.stderr[-600:]


class _AxLog(_FillLog):
    def plot(self, *a, **k):
        pass


def _tiles(method, size):
    from patterns.tessellation import TessellationGenerator
    ax = _AxLog()
    getattr(TessellationGenerator(PatternConfig()), method)(ax, size, "alternating", "thin")
    return [np.column_stack([x, y])[:4] for x, y in ax.fills]


def _angles(q):
    out = []
    for i in range(4):
        a, b, c = q[i - 1], q[i], q[(i + 1) % 4]
        u, v = a - b, c - b
        out.append(round(float(np.degrees(np.arccos(np.dot(u, v) / np.hypot(*u) / np.hypot(*v)))), 6))
    return out


@pytest.mark.parametrize("method,allowed,size", [
    ("_generate_penrose_tiling", [[36, 144], [72, 108]], 0.12),
    ("_generate_ammann_beenker", [[45, 135], [90]], 0.12),
])
def test_aperiodic_tilings_are_real_tilings(method, allowed, size):
    """'penrose' and 'ammann_beenker' scattered random, overlapping rhombi/octagons. They must be edge-to-edge
    tilings: all edges of length tile_size, only the P3 (36/72/108/144) or Ammann-Beenker (45/90/135) angles, every
    interior edge shared by exactly two tiles and the tile angles at every interior vertex summing to 360."""
    quads = _tiles(method, size)
    assert len(quads) > 50
    edges, corner = {}, {}
    key = lambda p: (round(p[0] / size, 5), round(p[1] / size, 5))  # noqa: E731
    for q in quads:
        assert np.allclose([np.hypot(*(q[i] - q[i - 1])) for i in range(4)], size, rtol=1e-9)
        ang = _angles(q)
        assert sorted(set(round(a) for a in ang)) in allowed and abs(sum(ang) - 360) < 1e-6
        for i in range(4):
            e = tuple(sorted([key(q[i]), key(q[(i + 1) % 4])]))
            edges[e] = edges.get(e, 0) + 1
            corner[key(q[i])] = corner.get(key(q[i]), 0) + ang[i]
    assert max(edges.values()) <= 2
    inner = 0.6 / size
    for e, n in edges.items():
        if all(abs(c) < inner for p in e for c in p):
            assert n == 2, e
    for v, total in corner.items():
        if abs(v[0]) < inner and abs(v[1]) < inner:
            assert abs(total - 360) < 1e-4, (v, total)
    assert _tiles(method, size) and [q.tolist() for q in _tiles(method, size)] == [q.tolist() for q in quads]


def test_penrose_thick_to_thin_ratio_is_golden():
    from patterns.aperiodic import penrose_p3
    tiles = [t for t in penrose_p3(0.02) if all(abs(c) < 0.8 for xy in t[1] for c in xy)]
    thick = sum(t[0] for t in tiles)
    assert abs(thick / (len(tiles) - thick) - (1 + 5 ** 0.5) / 2) < 0.08


def _islamic(pattern, symmetry):
    from patterns.islamic import IslamicGeometryGenerator
    from web.recorder import record_scene
    params = dict(pattern_type=pattern, symmetry=symmetry, tile_size=0.15, repetitions_x=5, repetitions_y=4,
                  rotation=10, interlace="simple", ornament_detail=1.3)
    scene, _ = record_scene(IslamicGeometryGenerator(PatternConfig()), params)
    return scene["prims"]


@pytest.mark.parametrize("pattern", ["octagon_star", "hexagon_flower", "square_kufic", "girih_tiles", "morocco_zellige"])
@pytest.mark.parametrize("symmetry,n", [("p2", 2), ("p4", 4), ("p6", 6)])
def test_islamic_symmetry_takes_effect(pattern, symmetry, n):
    """The 'symmetry' parameter was never read. Now p2/p4/p6 make every tile centre an n-fold rotation centre
    (n = 2, 4, 6): rotating any drawn shape by 360/n about its tile centre gives another drawn shape."""
    from patterns.symmetry import tile_centres
    prims = _islamic(pattern, symmetry)
    def centroid(p):  # mean of the distinct vertices (polygons repeat their first point at the end)
        if p["t"] == "circle":
            return [p["cx"], p["cy"]]
        v = np.column_stack([p["x"], p["y"]])
        return (v[:-1] if np.allclose(v[0], v[-1]) else v).mean(axis=0)
    cents = np.array([centroid(p) for p in prims])
    th = 2 * np.pi / n
    rot = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    centres = np.array([c[:2] for c in tile_centres(5, 4, symmetry)])
    for c in centres:
        near = cents[np.hypot(*(cents - c).T) < 0.12]
        assert len(near)
        for m in near:
            r = (m - c) @ rot.T + c
            assert np.min(np.hypot(*(cents - r).T)) < 1e-7, (pattern, symmetry, c, m)


@pytest.mark.parametrize("symmetry,n", [("p4", 4), ("p6", 6)])
def test_islamic_symmetry_lattice(symmetry, n):
    """p4 needs a square lattice and p6 a hexagonal one: nearest neighbours of an interior tile centre are n
    (4 or 6) at one distance, 360/n degrees apart."""
    from patterns.symmetry import tile_centres
    c = np.array([t[:2] for t in tile_centres(6, 6, symmetry)])
    mid = c[np.argmin(np.hypot(*c.T))]
    d = np.hypot(*(c - mid).T)
    d1 = np.min(d[d > 1e-12])
    nn = c[(d > 1e-12) & (d < d1 * (1 + 1e-9))] - mid
    assert len(nn) == n
    ang = np.sort(np.degrees(np.arctan2(nn[:, 1], nn[:, 0])) % 360)
    assert np.allclose(np.diff(ang), 360 / n)


def test_islamic_p1_is_the_old_rectangular_layout():
    prims = _islamic("girih_tiles", "p1")
    assert abs(np.mean(prims[0]["x"][:-1]) - (-1 + 0.5 * 2 / 5)) < 1e-12
    assert abs(np.mean(prims[0]["y"][:-1]) - (-1 + 0.5 * 2 / 4)) < 1e-12
    assert len(prims) == 20 * 6


@pytest.mark.skipif(NO_TK, reason="tkinter or a display not available")
def test_enhanced_v2_uses_the_shared_classes():
    """enhanced_pattern_generator_V2.py carried copies of PatternConfig, ColorManager, PatternGenerator and the Spiral and
    Interference generators identical in behaviour to config.py / patterns/; it must import them."""
    code = ("import sys; sys.path.insert(0, %r)\nimport enhanced_pattern_generator_V2 as e, patterns, config\n"
            "names = ['PatternGenerator', 'SpiralGenerator', 'InterferenceGenerator']\n"
            "assert all(getattr(e, n) is getattr(patterns, n) for n in names)\n"
            "assert e.PatternConfig is config.PatternConfig and e.ColorManager is config.ColorManager\nprint('ok')\n") % str(ROOT)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT,
                       env=dict(os.environ, MPLBACKEND="Agg"), timeout=60)
    assert r.returncode == 0 and "ok" in r.stdout, r.stderr[-600:]
