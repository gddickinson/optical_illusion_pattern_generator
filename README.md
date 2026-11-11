# Optical Illusion & Pattern Generator

![Optical Illusion Patterns](examples/optical_illusion_example.png)

An interactive desktop application for generating mathematical patterns, fractals, optical illusions, and generative art. Built with tkinter and matplotlib, it provides real-time parameter adjustment, animation, and high-resolution export.

## Features

### Pattern Categories

- **Spirals**: Archimedean, Logarithmic, Fermat, and Fibonacci (Golden) spirals with adjustable arms, density, overlapping spirals and radial/angular gradients
- **Interference**: Moire effects using concentric circles, waves, or grids
- **Optical Illusions** (V2): Hermann Grid, Scintillating Grid, Fraser Spiral, Cafe Wall, Zollner, Muller-Lyer, Kanizsa Triangle, Rotating Snakes, Impossible (Penrose) Triangle
- **Fractals** (V2): Mandelbrot and Julia sets, Sierpinski triangles, Barnsley Ferns, Dragon Curves
- **Mathematical Curves** (V2): Lissajous figures, Rose curves, Epicycloids, Hypocycloids, Cardioids, Astroids, Cycloids
- **Generative Art** (Advanced version): Islamic geometric patterns, Voronoi diagrams (with Lloyd relaxation), cellular automata (Game of Life, elementary rules 30/90/110, Brian's Brain, Langton's ant) and tessellations (regular, hexagonal, triangular, Truchet, and random Penrose-style rhombi / Ammann-Beenker-style octagons)

### Tools and Controls

- **Global Settings**: Resolution, line width, color mode (Black & White, Color, Gradient)
- **Animation Engine**: Animate patterns by cycling through rotation, phase, or other parameters
- **Quick Presets**: Instantly load configurations for Golden Spiral, Psychedelic, and other popular patterns
- **Export/Import**: Save and load pattern configurations as JSON
- **High-Resolution Export**: Save patterns as PNG or JPG (and SVG in the advanced version)

## Application Versions

| File | Description |
|------|-------------|
| `optical_illusion_generator.py` | Original version with core illusion patterns (~30k) |
| `optical_illusion_generator_V2.py` | Expanded version with more illusions and improved UI (~63k) |
| `enhanced_pattern_generator.py` | Extended generator with additional mathematical curves (~44k) |
| `enhanced_pattern_generator_V2.py` | Further expanded with more pattern types (~102k) |
| `advanced_pattern_generator.py` | Full-featured "Mathematical Art Studio" with spirals, interference, Islamic geometry, Voronoi diagrams, cellular automata and tessellations (~116k) |

Each version builds on the previous, adding more pattern types and UI refinements. The `advanced_pattern_generator.py` is the most feature-rich for generative art; the optical illusions, fractals and mathematical curves are in `optical_illusion_generator_V2.py`.

## Architecture

The project uses an object-oriented design with clean separation between pattern generation and UI:

- **`PatternConfig`** (dataclass): Holds global visual settings (resolution, colors, line width)
- **`PatternGenerator`** (ABC): Abstract base class requiring `generate()` and `get_parameters()` methods. Each pattern type is a concrete subclass.
- **`OpticalIllusionApp`**: Main tkinter application managing the GUI event loop, parameter widgets, matplotlib canvas integration, animation, and file I/O

## Prerequisites

- Python 3.7+
- tkinter (included with most Python installations)

## Installation

```bash
pip install numpy matplotlib pillow scipy
```

`scipy` is only required for the advanced pattern generator (Voronoi tessellations).

## Usage

Run any version directly:

```bash
# Recommended: most feature-rich version
python advanced_pattern_generator.py

# Or the optical illusion focused version
python optical_illusion_generator_V2.py
```

1. **Select a Pattern**: Use the dropdown menu on the left to choose a category
2. **Adjust Parameters**: Tweak sliders and inputs in the Parameters frame
3. **Click Generate**: View the result in the main display area
4. **Try Presets**: Use Quick Presets buttons to load preconfigured patterns
5. **Animate**: Click the Animate button to cycle through parameter values
6. **Export**: Save the current pattern as an image or save the configuration as JSON

## Example Patterns

The generator can produce patterns including:
- Golden Spiral (Fibonacci spiral)
- Mandelbrot and Julia set fractals with custom color maps
- Moire interference patterns from overlapping grids
- Classic optical illusions (Hermann Grid, Cafe Wall, etc.)
- Lissajous curves and Rose curves
- Voronoi diagrams and Islamic geometric patterns
- Cellular automata and Truchet / hexagonal tessellations

## GUI Framework

Built with **tkinter** for the application shell and **matplotlib** (TkAgg backend) for pattern rendering via `FigureCanvasTkAgg`.
