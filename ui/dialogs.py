"""
Dialog methods for the Advanced Mathematical Art Studio.

Contains mixin class with show_shortcuts, show_pattern_guide, show_about,
and batch generation dialog functionality.
"""

import tkinter as tk
from tkinter import ttk


class DialogsMixin:
    """Mixin providing dialog windows for the Art Studio."""

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Keyboard Shortcuts")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        text_widget = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)

        shortcuts_text = """
KEYBOARD SHORTCUTS

File Operations:
  Ctrl+S       Save Image
  Ctrl+O       Import Configuration
  Ctrl+Q       Exit Application

Generation:
  F5           Generate Pattern
  F6           Animate Pattern
  F12          Surprise Me!
  R            Random Parameters
  Shift+R      Random Everything

View Controls:
  +            Zoom In
  -            Zoom Out
  0            Reset View
  F11          Toggle Fullscreen

Pattern Tips:
  Try different color palettes for dramatic effects
  Use animation to understand parameter effects
  Batch generate to explore parameter spaces
  Islamic Geometry works great with Earth palette
  Voronoi + Poisson distribution = organic patterns
  Cellular Automata + Neon palette = cyberpunk vibes

Pro Tips:
  Save configurations you like for later use
  High resolution (2000+) for print quality
  Experiment with overlapping spirals
  Try irregular tessellations for natural looks
        """

        text_widget.insert(tk.END, shortcuts_text)
        text_widget.config(state=tk.DISABLED)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def show_pattern_guide(self):
        """Show pattern guide dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Pattern Guide")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        text_widget = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)

        guide_text = """
PATTERN GENERATOR GUIDE

SPIRALS
  Archimedean: Uniform spacing, classic spiral
  Logarithmic: Exponential growth, nature-inspired
  Fermat: Square root spiral, sunflower patterns
  Fibonacci: Golden ratio, perfect proportions
  Try overlapping spirals with angular gradients!

ISLAMIC GEOMETRY
  Octagon Star: Classic 8-pointed star patterns
  Hexagon Flower: Nature-inspired 6-fold symmetry
  Girih Tiles: Complex interlocking patterns
  Morocco Zellige: Traditional tile patterns
  Use Earth or Ocean palettes for authenticity

VORONOI DIAGRAMS
  Random: Organic, cell-like structures
  Poisson: Evenly distributed, natural looking
  Fibonacci: Spiral-based point distribution
  Grid: Regular but with organic boundaries
  Color by distance creates beautiful gradients

CELLULAR AUTOMATA
  Game of Life: Conway's famous simulation
  Rule 30/90/110: Elementary automata patterns
  Brian's Brain: Three-state, colorful evolution
  Langton's Ant: Emergent complexity from simple rules
  Try "evolution" visualization for time patterns

TESSELLATIONS
  Penrose: Non-periodic, golden ratio tiles
  Truchet: Curved patterns in square tiles
  Hexagonal: Nature's favorite tessellation
  Add irregularity for organic, hand-drawn feel

INTERFERENCE
  Concentric: Ripple effects, water-like
  Wave: Linear interference patterns
  Grid: Complex standing wave patterns
  Try close frequencies for slow beat patterns

COLOR PALETTE GUIDE:
  Sunset: Warm, artistic, great for spirals
  Ocean: Cool blues, perfect for Voronoi
  Cosmic: Deep space, excellent for fractals
  Neon: Cyberpunk, amazing with automata
  Earth: Natural tones, ideal for Islamic patterns
        """

        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def show_about(self):
        """Show about dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("About Advanced Mathematical Art Studio")
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()

        text_widget = tk.Text(dialog, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)

        about_text = """
ADVANCED MATHEMATICAL ART STUDIO

A comprehensive application for creating stunning mathematical patterns and optical illusions.

FEATURES:
  6 Advanced Pattern Generators
  10 Beautiful Color Palettes
  Smart Animation System
  Batch Generation Tools
  Professional Export Options
  Infinite Creative Possibilities

GENERATORS:
  Enhanced Spirals with overlapping effects
  Islamic Geometric Patterns
  Voronoi Diagrams with multiple distributions
  Cellular Automata simulations
  Advanced Tessellations
  Interference Patterns

POWERED BY:
  Python & Tkinter
  Matplotlib for rendering
  NumPy for mathematics
  SciPy for advanced algorithms

Built with Python and passion for mathematical beauty
        """

        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
