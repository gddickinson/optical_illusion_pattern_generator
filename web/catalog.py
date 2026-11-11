"""The generators the web interface offers: the repo's own PatternGenerator classes, their parameter specs and presets.

Nine generators: Spiral, Interference, Islamic Geometry, Voronoi Diagrams, Cellular Automata and Tessellations from the
patterns package (the Art Studio, advanced_pattern_generator.py) and Optical Illusion, Fractal and Mathematical Curves
(optical_illusion_generator_V2.py, now in patterns/illusions.py, fractals.py, curves.py). Each one's "variant" parameter
(spiral_type, illusion_type, ...) gives the individual patterns.
"""
import inspect

from config import ColorManager, PatternConfig
from patterns import (
    CellularAutomataGenerator, FractalGenerator, InterferenceGenerator, IslamicGeometryGenerator,
    MathematicalCurvesGenerator, OpticalIllusionGenerator, SpiralGenerator, TessellationGenerator, VoronoiGenerator,
)
from patterns.presets import PRESETS

# id, GUI name (pattern_type in saved JSON), class, source file, desktop app, variant parameter, family
GENERATORS = [
    ("spiral", "Spiral", SpiralGenerator, "patterns/spirals.py", "advanced", "spiral_type", "Spirals"),
    ("interference", "Interference", InterferenceGenerator, "patterns/spirals.py", "advanced", "pattern_type", "Spirals"),
    ("illusion", "Optical Illusion", OpticalIllusionGenerator, "patterns/illusions.py", "v2", "illusion_type", "Illusions"),
    ("fractal", "Fractal", FractalGenerator, "patterns/fractals.py", "v2", "fractal_type", "Fractals"),
    ("curves", "Mathematical Curves", MathematicalCurvesGenerator, "patterns/curves.py", "v2", "curve_type", "Curves"),
    ("islamic", "Islamic Geometry", IslamicGeometryGenerator, "patterns/islamic.py", "advanced", "pattern_type",
     "Generative art"),
    ("voronoi", "Voronoi Diagrams", VoronoiGenerator, "patterns/voronoi.py", "advanced", "distribution", "Generative art"),
    ("cellular", "Cellular Automata", CellularAutomataGenerator, "patterns/cellular.py", "advanced", "automata_type",
     "Generative art"),
    ("tessellation", "Tessellations", TessellationGenerator, "patterns/tessellation.py", "advanced", "tessellation_type",
     "Generative art"),
]
BY_ID = {g[0]: g for g in GENERATORS}
BY_NAME = {g[1]: g[0] for g in GENERATORS}
APPS = {"v2": "optical_illusion_generator_V2.py", "advanced": "advanced_pattern_generator.py"}
# Presets whose generator in the web (the Art Studio Spiral) lacks what they set: V2's line_variation / custom colours.
WEB_SKIP = {"golden_spiral": "sets line_variation and custom colours of the V2 Spiral; the web uses the Art Studio Spiral",
            "psychedelic": "sets custom colours of the V2 Spiral; the web uses the Art Studio Spiral (palette colours)"}


def _spec(params):
    out = {}
    for name, info in params.items():
        d = {k: (list(v) if isinstance(v, tuple) else v) for k, v in info.items()}
        out[name] = d
    return out


def generator_info(gid):
    gid_, name, cls, src, app, variant, family = BY_ID[gid]
    params = cls(PatternConfig()).get_parameters()
    return {"id": gid_, "name": name, "class": cls.__name__, "source": src, "app": APPS[app], "variant": variant,
            "family": family, "doc": inspect.cleandoc(cls.__doc__ or ""), "params": _spec(params),
            "variants": list(params[variant]["choices"])}


def config_defaults():
    c = PatternConfig()
    return {"width": c.width, "height": c.height, "resolution": c.resolution, "color_mode": c.color_mode,
            "line_width": c.line_width, "background_color": c.background_color,
            "foreground_color": c.foreground_color, "custom_colors": list(c.custom_colors),
            "color_palette": c.color_palette}


def presets():
    out = []
    for key, p in PRESETS.items():
        out.append({"key": key, "name": p["name"], "app": APPS[p["app"]], "generator": BY_NAME.get(p["pattern"]),
                    "pattern": p["pattern"], "params": p["params"], "globals": p["globals"],
                    "web": key not in WEB_SKIP, "note": WEB_SKIP.get(key, "")})
    return out


def palettes():
    return dict(ColorManager.PALETTES)


def make_config(cfg):
    """PatternConfig from a JSON dict (unknown keys ignored)."""
    c = PatternConfig()
    for k in config_defaults():
        if k in cfg and cfg[k] is not None:
            setattr(c, k, list(cfg[k]) if k == "custom_colors" else cfg[k])
    return c
