This Python project is a GUI-based tool for generating complex mathematical patterns, fractals, and classic optical illusions. It leverages `numpy` and `matplotlib` to render high-resolution visuals through a user-friendly `tkinter` interface.

---

# Optical Illusion & Pattern Generator

An interactive desktop application that blends art with mathematics. Whether you're interested in the geometry of the **Golden Spiral**, the complexity of **Mandelbrot sets**, or the brain-bending nature of **Op Art**, this tool provides a playground for exploration.

## 🚀 Features

### 1. Pattern Generators

* **Spirals:** Supports Archimedean, Logarithmic, Fermat, and Fibonacci (Golden) spirals with adjustable arms, density, and line variations.
* **Interference:** Create Moiré effects using concentric circles, waves, or grids.
* **Optical Illusions:** A gallery of classic illusions including:
* Hermann Grid & Scintillating Grid
* Fraser Spiral & Café Wall
* Müller-Lyer lines & Kanizsa Triangle
* Rotating Snakes & Impossible (Penrose) Triangle.


* **Fractals:** Generate Mandelbrot and Julia sets, Sierpinski triangles, Barnsley Ferns, and Dragon Curves.
* **Mathematical Curves:** Render Lissajous figures, Rose curves, Epicycloids, and Hypocycloids.

### 2. Customization & Tools

* **Global Settings:** Real-time control over resolution, line width, and color modes (Black & White, Color, Gradient).
* **Animation Engine:** Dynamically animate patterns by cycling through parameters (like rotation).
* **Export/Import:** Save your favorite configurations as JSON files to reload them later.
* **High-Res Export:** Save generated patterns as PNG or JPG for use in digital art or publications.

---

## 🛠️ Installation

### Prerequisites

* Python 3.7 or higher
* Tkinter (usually included with Python)

### Dependencies

Install the required libraries via pip:

```bash
pip install numpy matplotlib pillow

```

---

## 🖥️ Usage

1. **Run the application:**
```bash
python optical_illusion_generator_V2.py

```


2. **Select a Pattern:** Use the dropdown menu on the left to choose a category.
3. **Adjust Parameters:** Tweak the sliders and inputs in the "Parameters" frame.
4. **Click Generate:** View your creation in the main display area.
5. **Try Presets:** Use the "Quick Presets" buttons to instantly load famous patterns like the "Golden Spiral" or "Psychedelic" layouts.

---

## 🏗️ Architecture

The project follows a clean, object-oriented design:

* **`PatternConfig`**: A dataclass holding global visual settings.
* **`PatternGenerator` (ABC)**: An abstract base class ensuring all generators implement a standardized `generate` and `get_parameters` interface.
* **`OpticalIllusionApp`**: The main GUI controller that manages the `tkinter` event loop and integrates `matplotlib` canvases.

