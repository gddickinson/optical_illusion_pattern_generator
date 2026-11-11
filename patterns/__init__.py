"""
Pattern generators for the Advanced Mathematical Art Studio.

Submodules:
- base: Abstract PatternGenerator base class
- islamic: Islamic geometric patterns
- voronoi: Voronoi diagram patterns
- cellular: Cellular automata patterns
- tessellation: Tessellation and tiling patterns
- spirals: Spiral and interference patterns
- illusions: Classic optical illusions (from optical_illusion_generator_V2.py)
- fractals: Mandelbrot, Julia, Sierpinski, Barnsley fern, dragon curve (from V2)
- curves: Lissajous, rose, epi/hypocycloid and other curves (from V2)
- presets: Quick-preset data shared by the desktop GUIs and the web interface
"""

from patterns.base import PatternGenerator
from patterns.islamic import IslamicGeometryGenerator
from patterns.voronoi import VoronoiGenerator
from patterns.cellular import CellularAutomataGenerator
from patterns.tessellation import TessellationGenerator
from patterns.spirals import SpiralGenerator, InterferenceGenerator
from patterns.illusions import OpticalIllusionGenerator
from patterns.fractals import FractalGenerator
from patterns.curves import MathematicalCurvesGenerator

__all__ = [
    'PatternGenerator',
    'IslamicGeometryGenerator',
    'VoronoiGenerator',
    'CellularAutomataGenerator',
    'TessellationGenerator',
    'SpiralGenerator',
    'InterferenceGenerator',
    'OpticalIllusionGenerator',
    'FractalGenerator',
    'MathematicalCurvesGenerator',
]
