"""
Pattern generators for the Advanced Mathematical Art Studio.

Submodules:
- base: Abstract PatternGenerator base class
- islamic: Islamic geometric patterns
- voronoi: Voronoi diagram patterns
- cellular: Cellular automata patterns
- tessellation: Tessellation and tiling patterns
- spirals: Spiral and interference patterns
"""

from patterns.base import PatternGenerator
from patterns.islamic import IslamicGeometryGenerator
from patterns.voronoi import VoronoiGenerator
from patterns.cellular import CellularAutomataGenerator
from patterns.tessellation import TessellationGenerator
from patterns.spirals import SpiralGenerator, InterferenceGenerator

__all__ = [
    'PatternGenerator',
    'IslamicGeometryGenerator',
    'VoronoiGenerator',
    'CellularAutomataGenerator',
    'TessellationGenerator',
    'SpiralGenerator',
    'InterferenceGenerator',
]
