"""Record what the Python generators draw, for the JS engine test (web/static/engine.test.mjs).

For every generator and every variant (spiral_type, illusion_type, ...), in black-and-white and colour mode, plus extra
cases for the other options, run the real generator against web/recorder.py's fake axes and save the drawing calls and
the np.random draws to tests/fixtures/scenes.json. The node test replays the random draws through the JS engine and
compares its scene with the Python's call by call. tests/test_web.py checks the fixture is still current.

Run: python scripts/make_scene_fixture.py [--check]
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.catalog import BY_ID, GENERATORS, generator_info, make_config  # noqa: E402
from web.recorder import record_scene  # noqa: E402

OUT = ROOT / "tests" / "fixtures" / "scenes.json"
BASE_CONFIG = {"width": 400, "height": 300, "resolution": 60, "line_width": 1.5, "color_palette": "sunset"}
# Smaller settings so the fixture stays small (the drawing code paths are the same).
SMALL = {
    "interference": {}, "illusion": {"spacing": 0.2}, "fractal": {"iterations": 10},
    "islamic": {"repetitions_x": 3, "repetitions_y": 2}, "voronoi": {"num_points": 25},
    "cellular": {"grid_size": 50, "generations": 6}, "tessellation": {"tile_size": 0.5},
}
CONFIG = {"interference": {"resolution": 25}, "fractal": {"resolution": 30}}
EXTRA = [
    ("spiral", {"gradient_effect": "radial", "arms": 2}), ("spiral", {"gradient_effect": "angular", "overlapping_spirals": 2}),
    ("spiral", {"spiral_type": "fermat", "overlapping_spirals": 3, "rotation": 30, "center_x": 0.2, "scale": 2.0}),
    ("interference", {"pattern_type": "grid", "phase": 90, "amplitude": 1.7}),
    ("illusion", {"illusion_type": "zollner", "tilt_angle": 30, "intensity": 1.5}),
    ("illusion", {"illusion_type": "rotating_snakes", "contrast": 0.3, "size": 0.9}),
    ("fractal", {"fractal_type": "mandelbrot", "zoom": 3.0, "center_x": -0.7, "color_scheme": "hot"}),
    ("fractal", {"fractal_type": "julia", "julia_c_real": 0.285, "julia_c_imag": 0.01, "color_scheme": "cool"}),
    ("fractal", {"fractal_type": "dragon_curve", "iterations": 80}),
    ("curves", {"line_style": "varied_width", "multiple_curves": 2}), ("curves", {"line_style": "dotted", "phase_shift": 45}),
    ("curves", {"curve_type": "rose", "a_parameter": 5, "b_parameter": 3, "multiple_curves": 3}),
    ("islamic", {"interlace": "complex", "ornament_detail": 1.5, "rotation": 15}),
    ("islamic", {"pattern_type": "girih_tiles", "symmetry": "p6"}), ("islamic", {"symmetry": "p1"}),
    ("islamic", {"pattern_type": "hexagon_flower", "symmetry": "p2", "rotation": 20}),
    ("islamic", {"pattern_type": "morocco_zellige", "symmetry": "p6", "ornament_detail": 1.3}),
    ("voronoi", {"style": "edges", "color_by": "distance"}), ("voronoi", {"style": "filled", "color_by": "area"}),
    ("voronoi", {"style": "stippled", "num_points": 12}), ("voronoi", {"relaxation_steps": 2, "clip_bounds": "circle"}),
    ("voronoi", {"distribution": "fibonacci", "relaxation_steps": 3, "style": "filled"}),
    ("cellular", {"visualization": "evolution"}), ("cellular", {"visualization": "trail"}),
    ("cellular", {"automata_type": "rule_110", "initial_pattern": "center_dot", "visualization": "evolution"}),
    ("cellular", {"initial_pattern": "glider", "neighborhood": "neumann"}),
    ("cellular", {"initial_pattern": "pulsar", "visualization": "trail"}),
    ("cellular", {"initial_pattern": "gosper_gun", "grid_size": 50, "generations": 4}),
    ("cellular", {"automata_type": "langton_ant", "generations": 40, "visualization": "trail"}),
    ("tessellation", {"base_shape": "square", "fill_pattern": "striped", "color_scheme": "random"}),
    ("tessellation", {"base_shape": "triangle", "fill_pattern": "dotted", "color_scheme": "gradient"}),
    ("tessellation", {"fill_pattern": "cross_hatch", "border_style": "decorative", "color_scheme": "symmetric"}),
    ("tessellation", {"tessellation_type": "hexagonal", "irregularity": 0.2, "border_style": "thick"}),
    ("tessellation", {"tessellation_type": "triangular", "irregularity": 0.3, "color_scheme": "random"}),
    ("tessellation", {"base_shape": "square", "irregularity": 0.25}),
    ("tessellation", {"tessellation_type": "penrose", "tile_size": 0.15, "border_style": "thick"}),
    ("tessellation", {"tessellation_type": "ammann_beenker", "tile_size": 0.15}),
]


def defaults(gid):
    return {k: v["default"] for k, v in generator_info(gid)["params"].items()}


def cases():
    out = []
    for gid, *_ in GENERATORS:
        info = generator_info(gid)
        for variant in info["variants"]:
            for mode in ("black_white", "color"):
                out.append((gid, {info["variant"]: variant}, {"color_mode": mode}))
    out += [(gid, p, {"color_mode": "color"}) for gid, p in EXTRA]
    out += [("illusion", {"illusion_type": t}, {"color_mode": "color", "foreground_color": "#1b4332", "background_color": "#f4a460"})
            for t in ("hermann_grid", "kanizsa", "cafe_wall")]
    return out


def fixture():
    rows = []
    for i, (gid, over, cfg_over) in enumerate(cases()):
        params = {**defaults(gid), **SMALL.get(gid, {}), **over}
        cfg = {**BASE_CONFIG, **CONFIG.get(gid, {}), **cfg_over}
        np.random.seed(i)
        scene, rand = record_scene(BY_ID[gid][2](make_config(cfg)), params)
        rows.append({"id": gid, "params": params, "config": cfg, "scene": scene, "random": rand})
    return {"cases": rows}


def close(a, b, rtol=1e-9, atol=1e-9, path="$"):
    """Deep comparison with a numeric tolerance (libm differs in the last digit between platforms)."""
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return f"{path}: keys {sorted(a)} != {sorted(b)}"
        return next((r for k in a for r in [close(a[k], b[k], rtol, atol, f"{path}.{k}")] if r), None)
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path}: length {len(a)} != {len(b)}"
        return next((r for i, (x, y) in enumerate(zip(a, b)) for r in [close(x, y, rtol, atol, f"{path}[{i}]")] if r), None)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return None if abs(a - b) <= atol + rtol * abs(b) else f"{path}: {a} != {b}"
    return None if a == b else f"{path}: {a!r} != {b!r}"


def write():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fixture(), separators=(",", ":")))


if __name__ == "__main__":
    if "--check" in sys.argv:
        diff = close(fixture(), json.loads(OUT.read_text()))
        print("current" if diff is None else f"STALE {diff}")
        sys.exit(diff is not None)
    write()
    n = len(json.loads(OUT.read_text())["cases"])
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB, {n} cases)")
