#!/usr/bin/env python3
"""
Optical Illusion and Pattern Generator
A comprehensive GUI application for creating mathematical patterns and optical illusions.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Explicitly use TkAgg backend for Tkinter integration
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PatternConfig:
    """Configuration class for pattern parameters"""
    width: int = 800
    height: int = 600
    resolution: int = 1000
    color_mode: str = "black_white"  # "black_white", "color", "gradient"
    line_width: float = 1.0
    background_color: str = "white"
    foreground_color: str = "black"
    custom_colors: list = None

    def __post_init__(self):
        if self.custom_colors is None:
            self.custom_colors = ["red", "blue", "green", "purple", "orange"]

class PatternGenerator(ABC):
    """Abstract base class for all pattern generators"""

    def __init__(self, config: PatternConfig):
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    def generate(self, **kwargs) -> np.ndarray:
        """Generate the pattern and return as numpy array"""
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Return dictionary of adjustable parameters for this pattern"""
        pass

    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters"""
        try:
            params = self.get_parameters()
            for key, value in kwargs.items():
                if key in params:
                    param_info = params[key]
                    if 'range' in param_info:
                        min_val, max_val = param_info['range']
                        if not (min_val <= value <= max_val):
                            raise ValueError(f"{key} must be between {min_val} and {max_val}")
            return True
        except Exception as e:
            logger.error(f"Parameter validation failed: {e}")
            return False

class SpiralGenerator(PatternGenerator):
    """Generates various types of spiral patterns with advanced options"""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'spiral_type': {'type': 'choice', 'choices': ['archimedean', 'logarithmic', 'fermat', 'fibonacci'], 'default': 'archimedean'},
            'arms': {'type': 'int', 'range': (1, 20), 'default': 3},
            'density': {'type': 'float', 'range': (0.1, 10.0), 'default': 1.0},
            'rotation': {'type': 'float', 'range': (0, 360), 'default': 0},
            'scale': {'type': 'float', 'range': (0.1, 5.0), 'default': 1.0},
            'center_x': {'type': 'float', 'range': (-0.8, 0.8), 'default': 0.0},
            'center_y': {'type': 'float', 'range': (-0.8, 0.8), 'default': 0.0},
            'overlapping_spirals': {'type': 'int', 'range': (1, 5), 'default': 1},
            'gradient_effect': {'type': 'choice', 'choices': ['none', 'radial', 'angular'], 'default': 'none'},
            'line_variation': {'type': 'choice', 'choices': ['constant', 'increasing', 'oscillating'], 'default': 'constant'}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate enhanced spiral pattern"""
        try:
            spiral_type = kwargs.get('spiral_type', 'archimedean')
            arms = kwargs.get('arms', 3)
            density = kwargs.get('density', 1.0)
            rotation = kwargs.get('rotation', 0)
            scale = kwargs.get('scale', 1.0)
            center_x = kwargs.get('center_x', 0.0)
            center_y = kwargs.get('center_y', 0.0)
            overlapping = kwargs.get('overlapping_spirals', 1)
            gradient_effect = kwargs.get('gradient_effect', 'none')
            line_variation = kwargs.get('line_variation', 'constant')

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            t = np.linspace(0, 20 * np.pi * density, self.config.resolution)

            # Generate multiple overlapping spirals
            for spiral_idx in range(overlapping):
                spiral_offset_x = center_x + (spiral_idx - overlapping//2) * 0.2
                spiral_offset_y = center_y + (spiral_idx - overlapping//2) * 0.15

                for arm in range(arms):
                    arm_rotation = rotation + (arm * 360 / arms) + (spiral_idx * 45)
                    arm_rotation_rad = np.radians(arm_rotation)

                    # Different spiral equations
                    if spiral_type == 'archimedean':
                        r = 0.05 * t * scale
                    elif spiral_type == 'logarithmic':
                        r = 0.1 * np.exp(0.1 * t) * scale
                    elif spiral_type == 'fermat':
                        r = 0.3 * np.sqrt(t) * scale
                    elif spiral_type == 'fibonacci':
                        # Golden spiral approximation
                        phi = (1 + np.sqrt(5)) / 2
                        r = 0.1 * phi ** (t / np.pi) * scale

                    x = r * np.cos(t + arm_rotation_rad) + spiral_offset_x
                    y = r * np.sin(t + arm_rotation_rad) + spiral_offset_y

                    # Filter points within bounds
                    mask = ((x - spiral_offset_x)**2 + (y - spiral_offset_y)**2) <= 1
                    x, y = x[mask], y[mask]

                    if len(x) == 0:
                        continue

                    # Line width variation
                    if line_variation == 'increasing':
                        linewidths = np.linspace(self.config.line_width * 0.5,
                                               self.config.line_width * 2, len(x))
                    elif line_variation == 'oscillating':
                        linewidths = self.config.line_width * (1 + 0.5 * np.sin(np.linspace(0, 10*np.pi, len(x))))
                    else:
                        linewidths = self.config.line_width

                    # Color and gradient effects
                    if self.config.color_mode == "color" and self.config.custom_colors:
                        base_color = self.config.custom_colors[(arm + spiral_idx) % len(self.config.custom_colors)]

                        if gradient_effect == 'radial':
                            # Create color gradient based on radius
                            alphas = np.linspace(1.0, 0.3, len(x))
                            for i in range(len(x)-1):
                                ax.plot(x[i:i+2], y[i:i+2], color=base_color,
                                       linewidth=linewidths[i] if hasattr(linewidths, '__len__') else linewidths,
                                       alpha=alphas[i])
                        elif gradient_effect == 'angular':
                            # Create color gradient based on angle
                            angles = np.arctan2(y - spiral_offset_y, x - spiral_offset_x)
                            colors = plt.cm.hsv((angles + np.pi) / (2 * np.pi))
                            for i in range(len(x)-1):
                                ax.plot(x[i:i+2], y[i:i+2], color=colors[i],
                                       linewidth=linewidths[i] if hasattr(linewidths, '__len__') else linewidths)
                        else:
                            ax.plot(x, y, color=base_color, linewidth=self.config.line_width, alpha=0.8)
                    else:
                        color = self.config.foreground_color
                        if isinstance(linewidths, np.ndarray):
                            # Plot with varying line width
                            for i in range(len(x)-1):
                                ax.plot(x[i:i+2], y[i:i+2], color=color, linewidth=linewidths[i])
                        else:
                            ax.plot(x, y, color=color, linewidth=linewidths, alpha=0.8)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating spiral: {e}")
            raise
        finally:
            plt.close(fig)

    def _fig_to_array(self, fig) -> np.ndarray:
        """Convert matplotlib figure to numpy array"""
        try:
            fig.canvas.draw()
            buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            return buf
        except Exception as e:
            logger.error(f"Error converting figure to array: {e}")
            raise

class InterferenceGenerator(PatternGenerator):
    """Generates interference patterns and moiré effects"""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'pattern_type': {'type': 'choice', 'choices': ['concentric', 'wave', 'grid'], 'default': 'concentric'},
            'frequency1': {'type': 'float', 'range': (1, 50), 'default': 10},
            'frequency2': {'type': 'float', 'range': (1, 50), 'default': 12},
            'phase': {'type': 'float', 'range': (0, 360), 'default': 0},
            'amplitude': {'type': 'float', 'range': (0.1, 2.0), 'default': 1.0}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate interference pattern"""
        try:
            pattern_type = kwargs.get('pattern_type', 'concentric')
            freq1 = kwargs.get('frequency1', 10)
            freq2 = kwargs.get('frequency2', 12)
            phase = np.radians(kwargs.get('phase', 0))
            amplitude = kwargs.get('amplitude', 1.0)

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            x = np.linspace(-1, 1, self.config.resolution)
            y = np.linspace(-1, 1, self.config.resolution)
            X, Y = np.meshgrid(x, y)

            if pattern_type == 'concentric':
                R = np.sqrt(X**2 + Y**2)
                pattern1 = np.sin(2 * np.pi * freq1 * R + phase)
                pattern2 = np.sin(2 * np.pi * freq2 * R)
            elif pattern_type == 'wave':
                pattern1 = np.sin(2 * np.pi * freq1 * X + phase)
                pattern2 = np.sin(2 * np.pi * freq2 * Y)
            elif pattern_type == 'grid':
                pattern1 = np.sin(2 * np.pi * freq1 * X + phase) + np.sin(2 * np.pi * freq1 * Y + phase)
                pattern2 = np.sin(2 * np.pi * freq2 * X) + np.sin(2 * np.pi * freq2 * Y)

            interference = amplitude * (pattern1 + pattern2)

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))

            if self.config.color_mode == "black_white":
                ax.contour(X, Y, interference, levels=20, colors=self.config.foreground_color, linewidths=self.config.line_width)
            else:
                ax.contour(X, Y, interference, levels=20, linewidths=self.config.line_width)

            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')
            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating interference pattern: {e}")
            raise
        finally:
            plt.close(fig)

    def _fig_to_array(self, fig) -> np.ndarray:
        """Convert matplotlib figure to numpy array"""
        try:
            fig.canvas.draw()
            buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            return buf
        except Exception as e:
            logger.error(f"Error converting figure to array: {e}")
            raise

# The illusion, fractal and curve generators live in the Tk-free patterns package (shared with the web interface).
from patterns.illusions import OpticalIllusionGenerator  # noqa: E402
from patterns.fractals import FractalGenerator  # noqa: E402
from patterns.curves import MathematicalCurvesGenerator  # noqa: E402
from patterns.presets import apply_preset  # noqa: E402


class OpticalIllusionApp:
    """Main GUI application for optical illusion generator"""

    def __init__(self, root):
        self.root = root
        self.root.title("Optical Illusion & Pattern Generator")
        self.root.geometry("1200x800")

        # Initialize configuration
        self.config = PatternConfig()

        # Initialize generators
        self.generators = {
            'Spiral': SpiralGenerator(self.config),
            'Interference': InterferenceGenerator(self.config),
            'Optical Illusion': OpticalIllusionGenerator(self.config),
            'Fractal': FractalGenerator(self.config),
            'Mathematical Curves': MathematicalCurvesGenerator(self.config)
        }

        self.current_generator = None
        self.current_image = None
        self.parameter_widgets = {}
        self.animation_running = False

        self.setup_ui()
        self.setup_logging_display()

        logger.info("Application initialized successfully")

    def setup_ui(self):
        """Setup the user interface"""
        # Create main frames
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel for controls
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Right panel for display
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.setup_controls()
        self.setup_display()

    def setup_controls(self):
        """Setup control panel"""
        # Pattern selection
        ttk.Label(self.control_frame, text="Pattern Type:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.pattern_var = tk.StringVar(value="Spiral")
        pattern_combo = ttk.Combobox(self.control_frame, textvariable=self.pattern_var,
                                   values=list(self.generators.keys()), state="readonly", width=20)
        pattern_combo.pack(anchor=tk.W, pady=(0, 10))
        pattern_combo.bind('<<ComboboxSelected>>', self.on_pattern_change)

        # Parameters frame
        self.params_frame = ttk.LabelFrame(self.control_frame, text="Parameters", padding=10)
        self.params_frame.pack(fill=tk.X, pady=(0, 10))

        # Global settings frame
        self.global_frame = ttk.LabelFrame(self.control_frame, text="Global Settings", padding=10)
        self.global_frame.pack(fill=tk.X, pady=(0, 10))

        self.setup_global_controls()

        # Action buttons
        self.button_frame = ttk.Frame(self.control_frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))

        self.generate_btn = ttk.Button(self.button_frame, text="Generate Pattern",
                                     command=self.generate_pattern, style="Accent.TButton")
        self.generate_btn.pack(fill=tk.X, pady=2)

        self.save_btn = ttk.Button(self.button_frame, text="Save Image",
                                 command=self.save_image)
        self.save_btn.pack(fill=tk.X, pady=2)

        self.export_btn = ttk.Button(self.button_frame, text="Export Config",
                                   command=self.export_config)
        self.export_btn.pack(fill=tk.X, pady=2)

        self.import_btn = ttk.Button(self.button_frame, text="Import Config",
                                   command=self.import_config)
        self.import_btn.pack(fill=tk.X, pady=2)

        self.animate_btn = ttk.Button(self.button_frame, text="Animate Pattern",
                                    command=self.animate_pattern)
        self.animate_btn.pack(fill=tk.X, pady=2)

        # Quick presets
        self.presets_frame = ttk.LabelFrame(self.control_frame, text="Quick Presets", padding=10)
        self.presets_frame.pack(fill=tk.X, pady=(0, 10))

        presets = [
            ("Golden Spiral", self.load_golden_spiral_preset),
            ("Fractal Art", self.load_fractal_preset),
            ("Op Art", self.load_op_art_preset),
            ("Psychedelic", self.load_psychedelic_preset)
        ]

        for i, (name, command) in enumerate(presets):
            row, col = i // 2, i % 2
            ttk.Button(self.presets_frame, text=name, command=command).grid(
                row=row, column=col, sticky=tk.EW, padx=2, pady=2)

        self.presets_frame.columnconfigure(0, weight=1)
        self.presets_frame.columnconfigure(1, weight=1)

        # Initialize with first pattern
        self.on_pattern_change()

    def setup_global_controls(self):
        """Setup global configuration controls"""
        # Color mode
        ttk.Label(self.global_frame, text="Color Mode:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.color_mode_var = tk.StringVar(value="black_white")
        color_combo = ttk.Combobox(self.global_frame, textvariable=self.color_mode_var,
                                 values=["black_white", "color", "gradient"], state="readonly", width=15)
        color_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        color_combo.bind('<<ComboboxSelected>>', self.on_color_mode_change)

        # Resolution
        ttk.Label(self.global_frame, text="Resolution:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.resolution_var = tk.IntVar(value=1000)
        resolution_spin = ttk.Spinbox(self.global_frame, from_=100, to=5000, increment=100,
                                    textvariable=self.resolution_var, width=15)
        resolution_spin.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)

        # Line width
        ttk.Label(self.global_frame, text="Line Width:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.line_width_var = tk.DoubleVar(value=1.0)
        line_width_spin = ttk.Spinbox(self.global_frame, from_=0.1, to=10.0, increment=0.1,
                                    textvariable=self.line_width_var, width=15)
        line_width_spin.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)

        # Color buttons
        self.bg_color_btn = ttk.Button(self.global_frame, text="Background Color",
                                     command=lambda: self.choose_color('background'))
        self.bg_color_btn.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=2)

        self.fg_color_btn = ttk.Button(self.global_frame, text="Foreground Color",
                                     command=lambda: self.choose_color('foreground'))
        self.fg_color_btn.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=2)

    def setup_display(self):
        """Setup display area"""
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.text(0.5, 0.5, 'Select a pattern and click Generate',
                    ha='center', va='center', transform=self.ax.transAxes, fontsize=14)
        self.ax.axis('off')

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.display_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add toolbar
        toolbar_frame = ttk.Frame(self.display_frame)
        toolbar_frame.pack(fill=tk.X)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(toolbar_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=5, pady=2)

    def setup_logging_display(self):
        """Setup logging display in status bar"""
        class StatusBarHandler(logging.Handler):
            def __init__(self, status_var):
                super().__init__()
                self.status_var = status_var

            def emit(self, record):
                msg = self.format(record)
                self.status_var.set(msg)

        handler = StatusBarHandler(self.status_var)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)

    def on_pattern_change(self, event=None):
        """Handle pattern selection change"""
        pattern_name = self.pattern_var.get()
        self.current_generator = self.generators[pattern_name]
        self.update_parameter_controls()
        logger.info(f"Selected pattern: {pattern_name}")

    def on_color_mode_change(self, event=None):
        """Handle color mode change"""
        self.config.color_mode = self.color_mode_var.get()
        logger.info(f"Color mode changed to: {self.config.color_mode}")

    def update_parameter_controls(self):
        """Update parameter controls based on selected pattern"""
        # Clear existing parameter widgets
        for widget_info in self.parameter_widgets.values():
            widget_info['widget'].destroy()
        self.parameter_widgets.clear()

        if not self.current_generator:
            return

        parameters = self.current_generator.get_parameters()
        row = 0

        for param_name, param_info in parameters.items():
            ttk.Label(self.params_frame, text=f"{param_name.replace('_', ' ').title()}:").grid(
                row=row, column=0, sticky=tk.W, pady=2)

            if param_info['type'] == 'choice':
                var = tk.StringVar(value=param_info['default'])
                widget = ttk.Combobox(self.params_frame, textvariable=var,
                                    values=param_info['choices'], state="readonly", width=15)
            elif param_info['type'] == 'int':
                var = tk.IntVar(value=param_info['default'])
                min_val, max_val = param_info['range']
                widget = ttk.Spinbox(self.params_frame, from_=min_val, to=max_val,
                                   textvariable=var, width=15)
            elif param_info['type'] == 'float':
                var = tk.DoubleVar(value=param_info['default'])
                min_val, max_val = param_info['range']
                widget = ttk.Spinbox(self.params_frame, from_=min_val, to=max_val,
                                   increment=0.1, textvariable=var, width=15)

            widget.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=2)
            self.parameter_widgets[param_name] = {'widget': widget, 'var': var}
            row += 1

    def choose_color(self, color_type):
        """Open color chooser dialog"""
        if color_type == 'background':
            current_color = self.config.background_color
        else:
            current_color = self.config.foreground_color

        color = colorchooser.askcolor(initialcolor=current_color)[1]
        if color:
            if color_type == 'background':
                self.config.background_color = color
                logger.info(f"Background color changed to: {color}")
            else:
                self.config.foreground_color = color
                logger.info(f"Foreground color changed to: {color}")

    def get_current_parameters(self) -> Dict[str, Any]:
        """Get current parameter values"""
        params = {}
        for param_name, widget_info in self.parameter_widgets.items():
            params[param_name] = widget_info['var'].get()
        return params

    def update_config(self):
        """Update configuration with current GUI values"""
        self.config.resolution = self.resolution_var.get()
        self.config.line_width = self.line_width_var.get()
        self.config.color_mode = self.color_mode_var.get()

    def generate_pattern(self):
        """Generate pattern using current settings"""
        try:
            if not self.current_generator:
                raise ValueError("No pattern selected")

            self.update_config()
            self.status_var.set("Generating pattern...")
            self.generate_btn.config(state='disabled')
            self.root.update()

            # Get parameters
            params = self.get_current_parameters()

            # Generate pattern synchronously to avoid threading issues
            try:
                image_array = self.current_generator.generate(**params)
                self.display_pattern(image_array)

            except Exception as e:
                error_msg = f"Error generating pattern: {str(e)}"
                logger.error(error_msg)
                messagebox.showerror("Generation Error", error_msg)
                self.status_var.set("Generation failed")
            finally:
                self.generate_btn.config(state='normal')

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Ready")
            self.generate_btn.config(state='normal')

    def display_pattern(self, image_array):
        """Display generated pattern"""
        try:
            self.current_image = image_array

            # Clear the current axes and display new image
            self.ax.clear()
            self.ax.imshow(image_array, aspect='equal')
            self.ax.axis('off')

            # Force the canvas to redraw
            self.canvas.draw_idle()
            self.root.update_idletasks()

            self.status_var.set("Pattern generated successfully")
            logger.info("Pattern displayed successfully")

        except Exception as e:
            error_msg = f"Error displaying pattern: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Display Error", error_msg)
            self.status_var.set("Display failed")

    def save_image(self):
        """Save current image to file"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image to save. Generate a pattern first.")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )

            if filename:
                from PIL import Image
                img = Image.fromarray(self.current_image)
                img.save(filename)
                logger.info(f"Image saved to: {filename}")
                messagebox.showinfo("Success", f"Image saved to: {filename}")

        except Exception as e:
            error_msg = f"Error saving image: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Save Error", error_msg)

    def export_config(self):
        """Export current configuration"""
        try:
            import json
            config_data = {
                'pattern_type': self.pattern_var.get(),
                'parameters': self.get_current_parameters(),
                'global_settings': {
                    'resolution': self.resolution_var.get(),
                    'line_width': self.line_width_var.get(),
                    'color_mode': self.color_mode_var.get(),
                    'background_color': self.config.background_color,
                    'foreground_color': self.config.foreground_color
                }
            }

            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if filename:
                with open(filename, 'w') as f:
                    json.dump(config_data, f, indent=2)
                logger.info(f"Configuration exported to: {filename}")
                messagebox.showinfo("Success", f"Configuration exported to: {filename}")

        except Exception as e:
            error_msg = f"Error exporting configuration: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Export Error", error_msg)

    def import_config(self):
        """Import configuration from file"""
        try:
            import json
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if filename:
                with open(filename, 'r') as f:
                    config_data = json.load(f)

                # Apply configuration
                self.pattern_var.set(config_data.get('pattern_type', 'Spiral'))
                self.on_pattern_change()

                # Set global settings
                global_settings = config_data.get('global_settings', {})
                self.resolution_var.set(global_settings.get('resolution', 1000))
                self.line_width_var.set(global_settings.get('line_width', 1.0))
                self.color_mode_var.set(global_settings.get('color_mode', 'black_white'))
                self.config.background_color = global_settings.get('background_color', 'white')
                self.config.foreground_color = global_settings.get('foreground_color', 'black')

                # Set pattern parameters
                parameters = config_data.get('parameters', {})
                for param_name, value in parameters.items():
                    if param_name in self.parameter_widgets:
                        self.parameter_widgets[param_name]['var'].set(value)

                logger.info(f"Configuration imported from: {filename}")
                messagebox.showinfo("Success", f"Configuration imported from: {filename}")

        except Exception as e:
            error_msg = f"Error importing configuration: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Import Error", error_msg)

    def load_golden_spiral_preset(self):
        """Load golden spiral preset"""
        apply_preset(self, 'golden_spiral')

    def load_fractal_preset(self):
        """Load fractal art preset"""
        apply_preset(self, 'fractal_art')

    def load_op_art_preset(self):
        """Load Op Art preset"""
        apply_preset(self, 'op_art')

    def load_psychedelic_preset(self):
        """Load psychedelic preset"""
        apply_preset(self, 'psychedelic')

    def animate_pattern(self):
        """Create animated pattern by varying parameters"""
        try:
            if not self.current_generator:
                messagebox.showwarning("Warning", "No pattern selected for animation.")
                return

            # Simple animation by cycling through rotation values
            original_rotation = None
            if 'rotation' in self.parameter_widgets:
                original_rotation = self.parameter_widgets['rotation']['var'].get()

            self.animate_btn.config(text="Stop Animation", command=self.stop_animation)
            self.animation_running = True

            def animate_step(frame):
                if not hasattr(self, 'animation_running') or not self.animation_running:
                    return

                try:
                    # Vary rotation parameter
                    if 'rotation' in self.parameter_widgets:
                        rotation = (frame * 10) % 360
                        self.parameter_widgets['rotation']['var'].set(rotation)

                    # Generate and display new frame
                    self.update_config()
                    params = self.get_current_parameters()
                    image_array = self.current_generator.generate(**params)
                    self.display_pattern(image_array)

                    # Schedule next frame
                    if self.animation_running:
                        self.root.after(200, lambda: animate_step(frame + 1))
                    else:
                        # Restore original values
                        if original_rotation is not None and 'rotation' in self.parameter_widgets:
                            self.parameter_widgets['rotation']['var'].set(original_rotation)
                        self.animate_btn.config(text="Animate Pattern", command=self.animate_pattern)

                except Exception as e:
                    logger.error(f"Animation error: {e}")
                    self.stop_animation()

            animate_step(0)

        except Exception as e:
            error_msg = f"Error starting animation: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Animation Error", error_msg)

    def stop_animation(self):
        """Stop the current animation"""
        self.animation_running = False
        self.animate_btn.config(text="Animate Pattern", command=self.animate_pattern)
        logger.info("Animation stopped")

    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop any running animation
            if hasattr(self, 'animation_running'):
                self.animation_running = False

            if hasattr(self, 'fig'):
                plt.close(self.fig)
            logger.info("Application resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def main():
    """Main application entry point"""
    try:
        # Set matplotlib to non-interactive mode to prevent conflicts
        plt.ioff()

        root = tk.Tk()

        # Set up styling
        style = ttk.Style()
        style.theme_use('clam')

        app = OpticalIllusionApp(root)

        # Handle window closing
        def on_closing():
            logger.info("Application closing")
            app.cleanup()
            root.quit()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Start the application
        logger.info("Starting Optical Illusion Generator")
        root.mainloop()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if 'root' in locals():
            messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")
    finally:
        # Ensure matplotlib cleanup
        plt.close('all')

if __name__ == "__main__":
    main()
