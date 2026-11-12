# Optical Illusion & Pattern Generator — Roadmap

## Current State
(2026-11-11: the original and first enhanced scripts were moved to `_archive/`, superseded by their V2 versions; the generators are shared through `patterns/`.)
Five standalone generator scripts of increasing complexity: `optical_illusion_generator.py` (original), `optical_illusion_generator_V2.py`, `enhanced_pattern_generator.py`, `enhanced_pattern_generator_V2.py`, and `advanced_pattern_generator.py` (most feature-rich). Built with tkinter + matplotlib. Uses proper OOP with `PatternConfig` dataclass and `PatternGenerator` ABC. The advanced version includes Voronoi, flow fields, L-systems, and strange attractors. All files are very large (30K-116K characters) with no modularization.

## Short-term Improvements
- [ ] Consolidate into one canonical version — the five overlapping scripts are confusing for users
- [ ] Split `advanced_pattern_generator.py` into modules: `patterns/spirals.py`, `patterns/fractals.py`, `patterns/illusions.py`, `patterns/generative.py`, `ui/app.py`, `ui/controls.py`, `config.py`
- [ ] Add a `requirements.txt` (numpy, matplotlib, pillow, scipy)
- [ ] Add error handling for invalid parameter combinations that produce empty or broken patterns
- [ ] Add docstrings to each `PatternGenerator` subclass explaining the mathematical basis
- [ ] Move the `examples/` directory content to generated output — or populate it with actual examples

## Feature Enhancements
- [ ] Add SVG export for resolution-independent output (not just PNG/JPG)
- [ ] Add a pattern gallery/browser that shows thumbnails of all available patterns
- [ ] Add parameter randomization ("surprise me" button) with seed saving for reproducibility
- [ ] Add pattern layering/composition — overlay two patterns with blend modes
- [ ] Support custom color palette import (e.g., from coolors.co JSON)
- [ ] Add a batch export mode: render all patterns with current settings to a directory
- [ ] Add zoom and pan on the matplotlib canvas for detail exploration

## Long-term Vision
- [ ] Port to a web interface (Streamlit or p5.js) for wider accessibility
- [ ] Add shader-based rendering (ModernGL) for real-time high-resolution patterns
- [ ] Implement pattern tiling for seamless wallpaper/textile generation
- [ ] Add 3D pattern generation (Blender integration or three.js export)
- [ ] Create a pattern API: generate patterns programmatically without the GUI
- [ ] Publish as a pip package with CLI: `illusion generate --type mandelbrot --output out.png`

## Technical Debt
- [ ] The five script versions share massive amounts of duplicated code — extract shared patterns into a base library
- [ ] Each file exceeds 500 lines significantly — the advanced version is ~3000+ lines
- [ ] Add unit tests for mathematical pattern generation functions (verify output array shapes, value ranges)
- [ ] Replace hardcoded color values and figure sizes with configurable constants
- [ ] The animation engine likely has memory leaks with matplotlib — audit `FuncAnimation` usage
- [ ] Add proper `__main__.py` entry point that launches the most complete version
