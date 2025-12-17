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

class OpticalIllusionGenerator(PatternGenerator):
    """Generates classic optical illusions"""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'illusion_type': {'type': 'choice', 'choices': ['mueller_lyer', 'kanizsa', 'hermann_grid', 'fraser_spiral', 'cafe_wall', 'zollner', 'rotating_snakes', 'scintillating_grid', 'impossible_triangle'], 'default': 'mueller_lyer'},
            'intensity': {'type': 'float', 'range': (0.1, 2.0), 'default': 1.0},
            'size': {'type': 'float', 'range': (0.1, 1.0), 'default': 0.5},
            'spacing': {'type': 'float', 'range': (0.05, 0.5), 'default': 0.1},
            'tilt_angle': {'type': 'float', 'range': (0, 45), 'default': 15},
            'contrast': {'type': 'float', 'range': (0.1, 1.0), 'default': 0.8}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate optical illusion"""
        try:
            illusion_type = kwargs.get('illusion_type', 'mueller_lyer')
            intensity = kwargs.get('intensity', 1.0)
            size = kwargs.get('size', 0.5)
            spacing = kwargs.get('spacing', 0.1)
            tilt_angle = kwargs.get('tilt_angle', 15)
            contrast = kwargs.get('contrast', 0.8)

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            if illusion_type == 'hermann_grid':
                self._generate_hermann_grid(ax, spacing, intensity)
            elif illusion_type == 'fraser_spiral':
                self._generate_fraser_spiral(ax, size, intensity)
            elif illusion_type == 'mueller_lyer':
                self._generate_mueller_lyer(ax, size, intensity)
            elif illusion_type == 'kanizsa':
                self._generate_kanizsa_triangle(ax, size, intensity)
            elif illusion_type == 'cafe_wall':
                self._generate_cafe_wall(ax, spacing, intensity, tilt_angle)
            elif illusion_type == 'zollner':
                self._generate_zollner(ax, spacing, intensity, tilt_angle)
            elif illusion_type == 'rotating_snakes':
                self._generate_rotating_snakes(ax, size, intensity, contrast)
            elif illusion_type == 'scintillating_grid':
                self._generate_scintillating_grid(ax, spacing, intensity)
            elif illusion_type == 'impossible_triangle':
                self._generate_impossible_triangle(ax, size, intensity)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating optical illusion: {e}")
            raise
        finally:
            plt.close(fig)

    def _generate_hermann_grid(self, ax, spacing, intensity):
        """Generate Hermann grid illusion"""
        for i in np.arange(-1, 1, spacing):
            ax.axhline(y=i, color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 10)
            ax.axvline(x=i, color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 10)

    def _generate_fraser_spiral(self, ax, size, intensity):
        """Generate Fraser spiral illusion"""
        t = np.linspace(0, 20 * np.pi, self.config.resolution)
        for phase in np.arange(0, 2*np.pi, np.pi/4):
            r = size * t / (20 * np.pi)
            x = r * np.cos(t + phase)
            y = r * np.sin(t + phase)

            # Create alternating segments
            for i in range(0, len(x)-10, 20):
                segment_x = x[i:i+10]
                segment_y = y[i:i+10]
                color = self.config.foreground_color if (i//20) % 2 == 0 else 'gray'
                ax.plot(segment_x, segment_y, color=color, linewidth=self.config.line_width * intensity)

    def _generate_mueller_lyer(self, ax, size, intensity):
        """Generate Müller-Lyer illusion"""
        # Main lines
        ax.plot([-size, size], [0.3, 0.3], color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 3)
        ax.plot([-size, size], [-0.3, -0.3], color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 3)

        # Arrow heads (inward for top line)
        arrow_size = size * 0.2
        ax.plot([-size, -size + arrow_size], [0.3, 0.3 + arrow_size], color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 2)
        ax.plot([-size, -size + arrow_size], [0.3, 0.3 - arrow_size], color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 2)
        ax.plot([size, size - arrow_size], [0.3, 0.3 + arrow_size], color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 2)
        ax.plot([size, size - arrow_size], [0.3, 0.3 - arrow_size], color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 2)

        # Arrow heads (outward for bottom line)
        ax.plot([-size, -size - arrow_size], [-0.3, -0.3 + arrow_size], color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 2)
        ax.plot([-size, -size - arrow_size], [-0.3, -0.3 - arrow_size], color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 2)
        ax.plot([size, size + arrow_size], [-0.3, -0.3 + arrow_size], color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 2)
        ax.plot([size, size + arrow_size], [-0.3, -0.3 - arrow_size], color=self.config.foreground_color, linewidth=self.config.line_width * intensity * 2)

    def _generate_kanizsa_triangle(self, ax, size, intensity):
        """Generate Kanizsa triangle illusion"""
        # Three pac-man shapes that create an illusory triangle
        circle_radius = size * 0.3
        centers = [(0, size), (-size*0.866, -size*0.5), (size*0.866, -size*0.5)]

        for i, (cx, cy) in enumerate(centers):
            theta = np.linspace(0, 2*np.pi, 100)
            # Create pac-man by removing a wedge
            if i == 0:  # Top circle, mouth facing down
                mask = (theta > np.pi/6) & (theta < 11*np.pi/6)
            elif i == 1:  # Bottom left, mouth facing up-right
                mask = (theta > 7*np.pi/6) & (theta < np.pi/2)
            else:  # Bottom right, mouth facing up-left
                mask = (theta > np.pi/2) & (theta < 11*np.pi/6)

            theta_filtered = theta[mask]
            x = cx + circle_radius * np.cos(theta_filtered)
            y = cy + circle_radius * np.sin(theta_filtered)
            ax.fill(x, y, color=self.config.foreground_color, alpha=intensity)

    def _generate_cafe_wall(self, ax, spacing, intensity, tilt_angle):
        """Generate Café Wall illusion"""
        rows = int(2 / spacing)
        cols = int(2 / spacing)
        rect_width = spacing * 0.8
        rect_height = spacing * 0.4

        for row in range(rows):
            y = -1 + row * spacing
            offset = (rect_width / 2) if row % 2 == 1 else 0

            for col in range(cols + 1):
                x = -1 + col * spacing + offset

                # Alternate colors
                color = self.config.foreground_color if (row + col) % 2 == 0 else 'gray'
                alpha = intensity if (row + col) % 2 == 0 else intensity * 0.5

                # Create tilted rectangles
                rect_x = [x, x + rect_width, x + rect_width, x, x]
                rect_y = [y, y, y + rect_height, y + rect_height, y]

                ax.fill(rect_x, rect_y, color=color, alpha=alpha)

            # Add horizontal line with slight offset to enhance illusion
            line_y = y + rect_height
            ax.axhline(y=line_y, color=self.config.foreground_color,
                      linewidth=self.config.line_width * intensity, alpha=0.8)

    def _generate_zollner(self, ax, spacing, intensity, tilt_angle):
        """Generate Zöllner illusion"""
        lines = int(2 / spacing)
        tilt_rad = np.radians(tilt_angle)

        for i in range(lines):
            x = -1 + i * spacing
            # Main vertical line
            ax.axvline(x=x, color=self.config.foreground_color,
                      linewidth=self.config.line_width * intensity * 2)

            # Tilted cross-hatches
            for y in np.arange(-1, 1, spacing/3):
                if i % 2 == 0:
                    # Tilt one way
                    x1, x2 = x - spacing/4, x + spacing/4
                    y1 = y - spacing/4 * np.tan(tilt_rad)
                    y2 = y + spacing/4 * np.tan(tilt_rad)
                else:
                    # Tilt the other way
                    x1, x2 = x - spacing/4, x + spacing/4
                    y1 = y + spacing/4 * np.tan(tilt_rad)
                    y2 = y - spacing/4 * np.tan(tilt_rad)

                ax.plot([x1, x2], [y1, y2], color=self.config.foreground_color,
                       linewidth=self.config.line_width * intensity)

    def _generate_rotating_snakes(self, ax, size, intensity, contrast):
        """Generate Rotating Snakes illusion"""
        # Create circular elements that appear to rotate
        num_circles = 6
        angles = np.linspace(0, 2*np.pi, num_circles, endpoint=False)

        for i, angle in enumerate(angles):
            center_x = size * 0.6 * np.cos(angle)
            center_y = size * 0.6 * np.sin(angle)

            # Create segmented circle
            theta = np.linspace(0, 2*np.pi, 20)
            radius = size * 0.2

            for j in range(len(theta)-1):
                t1, t2 = theta[j], theta[j+1]
                arc_theta = np.linspace(t1, t2, 10)

                x = center_x + radius * np.cos(arc_theta)
                y = center_y + radius * np.sin(arc_theta)

                # Alternate colors to create motion illusion
                if j % 4 == 0:
                    color = 'black'
                    alpha = intensity
                elif j % 4 == 1:
                    color = 'white'
                    alpha = intensity * contrast
                elif j % 4 == 2:
                    color = 'gray'
                    alpha = intensity * 0.7
                else:
                    color = 'darkgray'
                    alpha = intensity * 0.9

                ax.plot(x, y, color=color, linewidth=self.config.line_width * 4,
                       alpha=alpha, solid_capstyle='round')

    def _generate_scintillating_grid(self, ax, spacing, intensity):
        """Generate Scintillating Grid illusion"""
        # Grid lines
        for i in np.arange(-1, 1.1, spacing):
            ax.axhline(y=i, color=self.config.foreground_color,
                      linewidth=self.config.line_width * intensity * 3)
            ax.axvline(x=i, color=self.config.foreground_color,
                      linewidth=self.config.line_width * intensity * 3)

        # White dots at intersections (create scintillation effect)
        for x in np.arange(-1, 1.1, spacing):
            for y in np.arange(-1, 1.1, spacing):
                ax.plot(x, y, 'o', color='white', markersize=self.config.line_width * intensity * 2,
                       markeredgecolor=self.config.foreground_color, markeredgewidth=0.5)

    def _generate_impossible_triangle(self, ax, size, intensity):
        """Generate Penrose (impossible) triangle"""
        # Define the three main beams of the triangle
        beam_width = size * 0.1

        # Beam 1 (bottom horizontal)
        x1 = np.array([-size, size, size-beam_width, -size+beam_width, -size])
        y1 = np.array([-size*0.5, -size*0.5, -size*0.5+beam_width, -size*0.5+beam_width, -size*0.5])

        # Beam 2 (top right diagonal)
        x2 = np.array([size-beam_width/2, size/2, size/2-beam_width*0.866, size-beam_width/2-beam_width*0.866, size-beam_width/2])
        y2 = np.array([-size*0.5+beam_width, size*0.5, size*0.5-beam_width*0.5, -size*0.5+beam_width-beam_width*0.5, -size*0.5+beam_width])

        # Beam 3 (top left diagonal)
        x3 = np.array([-size+beam_width/2, -size/2, -size/2+beam_width*0.866, -size+beam_width/2+beam_width*0.866, -size+beam_width/2])
        y3 = np.array([-size*0.5+beam_width, size*0.5, size*0.5-beam_width*0.5, -size*0.5+beam_width-beam_width*0.5, -size*0.5+beam_width])

        # Different shades for 3D effect
        ax.fill(x1, y1, color=self.config.foreground_color, alpha=intensity)
        ax.fill(x2, y2, color='gray', alpha=intensity * 0.7)
        ax.fill(x3, y3, color='darkgray', alpha=intensity * 0.9)

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

class FractalGenerator(PatternGenerator):
    """Generates fractal patterns"""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'fractal_type': {'type': 'choice', 'choices': ['mandelbrot', 'julia', 'sierpinski', 'barnsley_fern', 'dragon_curve'], 'default': 'mandelbrot'},
            'iterations': {'type': 'int', 'range': (10, 500), 'default': 100},
            'zoom': {'type': 'float', 'range': (0.1, 10.0), 'default': 1.0},
            'center_x': {'type': 'float', 'range': (-2.0, 2.0), 'default': 0.0},
            'center_y': {'type': 'float', 'range': (-2.0, 2.0), 'default': 0.0},
            'julia_c_real': {'type': 'float', 'range': (-2.0, 2.0), 'default': -0.7},
            'julia_c_imag': {'type': 'float', 'range': (-2.0, 2.0), 'default': 0.27015},
            'color_scheme': {'type': 'choice', 'choices': ['classic', 'hot', 'cool', 'rainbow'], 'default': 'classic'}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate fractal pattern"""
        try:
            fractal_type = kwargs.get('fractal_type', 'mandelbrot')
            iterations = kwargs.get('iterations', 100)
            zoom = kwargs.get('zoom', 1.0)
            center_x = kwargs.get('center_x', 0.0)
            center_y = kwargs.get('center_y', 0.0)
            julia_c = complex(kwargs.get('julia_c_real', -0.7), kwargs.get('julia_c_imag', 0.27015))
            color_scheme = kwargs.get('color_scheme', 'classic')

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))

            if fractal_type == 'mandelbrot':
                data = self._generate_mandelbrot(iterations, zoom, center_x, center_y)
            elif fractal_type == 'julia':
                data = self._generate_julia(iterations, julia_c, zoom, center_x, center_y)
            elif fractal_type == 'sierpinski':
                return self._generate_sierpinski(ax, iterations)
            elif fractal_type == 'barnsley_fern':
                return self._generate_barnsley_fern(ax, iterations)
            elif fractal_type == 'dragon_curve':
                return self._generate_dragon_curve(ax, iterations)

            # Apply color scheme
            if self.config.color_mode == "black_white":
                ax.imshow(data, extent=[-2, 2, -2, 2], cmap='gray', origin='lower')
            else:
                if color_scheme == 'hot':
                    cmap = plt.cm.hot
                elif color_scheme == 'cool':
                    cmap = plt.cm.cool
                elif color_scheme == 'rainbow':
                    cmap = plt.cm.rainbow
                else:
                    cmap = plt.cm.viridis
                ax.imshow(data, extent=[-2, 2, -2, 2], cmap=cmap, origin='lower')

            ax.axis('off')
            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating fractal: {e}")
            raise
        finally:
            plt.close(fig)

    def _generate_mandelbrot(self, max_iter, zoom, center_x, center_y):
        """Generate Mandelbrot set"""
        width, height = self.config.resolution, self.config.resolution
        xmin, xmax = center_x - 2/zoom, center_x + 2/zoom
        ymin, ymax = center_y - 2/zoom, center_y + 2/zoom

        x = np.linspace(xmin, xmax, width)
        y = np.linspace(ymin, ymax, height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j*Y

        Z = np.zeros_like(C)
        M = np.full(C.shape, max_iter, dtype=int)

        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + C[mask]
            M[~mask & (M == max_iter)] = i

        return M

    def _generate_julia(self, max_iter, c, zoom, center_x, center_y):
        """Generate Julia set"""
        width, height = self.config.resolution, self.config.resolution
        xmin, xmax = center_x - 2/zoom, center_x + 2/zoom
        ymin, ymax = center_y - 2/zoom, center_y + 2/zoom

        x = np.linspace(xmin, xmax, width)
        y = np.linspace(ymin, ymax, height)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j*Y

        M = np.full(Z.shape, max_iter, dtype=int)

        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + c
            M[~mask & (M == max_iter)] = i

        return M

    def _generate_sierpinski(self, ax, iterations):
        """Generate Sierpinski triangle"""
        # Starting triangle vertices
        vertices = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]])

        # Start with random point
        point = np.array([0.5, 0.25])
        points = [point.copy()]

        for _ in range(iterations * 100):
            # Choose random vertex
            vertex = vertices[np.random.randint(0, 3)]
            # Move halfway to chosen vertex
            point = (point + vertex) / 2
            points.append(point.copy())

        points = np.array(points)
        ax.scatter(points[:, 0], points[:, 1], s=0.1, c=self.config.foreground_color, alpha=0.8)
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.0)
        ax.set_aspect('equal')
        ax.axis('off')

        plt.tight_layout()
        return self._fig_to_array(plt.gcf())

    def _generate_barnsley_fern(self, ax, iterations):
        """Generate Barnsley fern"""
        x, y = 0, 0
        xs, ys = [], []

        for _ in range(iterations * 100):
            r = np.random.random()
            if r < 0.01:
                x, y = 0, 0.16 * y
            elif r < 0.86:
                x, y = 0.85*x + 0.04*y, -0.04*x + 0.85*y + 1.6
            elif r < 0.93:
                x, y = 0.2*x - 0.26*y, 0.23*x + 0.22*y + 1.6
            else:
                x, y = -0.15*x + 0.28*y, 0.26*x + 0.24*y + 0.44

            xs.append(x)
            ys.append(y)

        ax.scatter(xs, ys, s=0.1, c=self.config.foreground_color, alpha=0.7)
        ax.set_xlim(-3, 3)
        ax.set_ylim(0, 10)
        ax.set_aspect('equal')
        ax.axis('off')

        plt.tight_layout()
        return self._fig_to_array(plt.gcf())

    def _generate_dragon_curve(self, ax, iterations):
        """Generate Dragon curve"""
        def dragon_curve_coords(order):
            if order == 0:
                return [(0, 0), (1, 0)]

            coords = dragon_curve_coords(order - 1)
            # Rotate and reflect the curve
            last_point = coords[-1]
            new_coords = []

            for i in range(len(coords) - 2, -1, -1):
                x, y = coords[i]
                # Rotate 90 degrees around last point
                new_x = last_point[0] - (y - last_point[1])
                new_y = last_point[1] + (x - last_point[0])
                new_coords.append((new_x, new_y))

            return coords + new_coords

        coords = dragon_curve_coords(min(iterations // 10, 15))
        xs, ys = zip(*coords)

        ax.plot(xs, ys, color=self.config.foreground_color, linewidth=self.config.line_width)
        ax.set_aspect('equal')
        ax.axis('off')

        plt.tight_layout()
        return self._fig_to_array(plt.gcf())

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

class MathematicalCurvesGenerator(PatternGenerator):
    """Generates mathematical curves and parametric patterns"""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'curve_type': {'type': 'choice', 'choices': ['lissajous', 'rose', 'epicycloid', 'hypocycloid', 'cardioid', 'astroid', 'cycloid'], 'default': 'lissajous'},
            'a_parameter': {'type': 'float', 'range': (1, 20), 'default': 3},
            'b_parameter': {'type': 'float', 'range': (1, 20), 'default': 2},
            'phase_shift': {'type': 'float', 'range': (0, 360), 'default': 0},
            'scale': {'type': 'float', 'range': (0.1, 2.0), 'default': 0.8},
            'multiple_curves': {'type': 'int', 'range': (1, 10), 'default': 1},
            'line_style': {'type': 'choice', 'choices': ['solid', 'dotted', 'varied_width'], 'default': 'solid'}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate mathematical curve patterns"""
        try:
            curve_type = kwargs.get('curve_type', 'lissajous')
            a = kwargs.get('a_parameter', 3)
            b = kwargs.get('b_parameter', 2)
            phase = np.radians(kwargs.get('phase_shift', 0))
            scale = kwargs.get('scale', 0.8)
            multiple = kwargs.get('multiple_curves', 1)
            line_style = kwargs.get('line_style', 'solid')

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            t = np.linspace(0, 4*np.pi, self.config.resolution)

            for i in range(multiple):
                curve_phase = phase + i * np.pi / 4
                curve_scale = scale * (1 - i * 0.1)

                if curve_type == 'lissajous':
                    x = curve_scale * np.sin(a * t + curve_phase)
                    y = curve_scale * np.sin(b * t)
                elif curve_type == 'rose':
                    # Rose curve: r = cos(a/b * theta)
                    theta = np.linspace(0, b * np.pi, self.config.resolution)
                    r = curve_scale * np.cos(a * theta / b)
                    x = r * np.cos(theta + curve_phase)
                    y = r * np.sin(theta + curve_phase)
                elif curve_type == 'epicycloid':
                    # Epicycloid: circle rolling outside another circle
                    x = curve_scale * ((a + b) * np.cos(t) - b * np.cos((a + b) * t / b + curve_phase))
                    y = curve_scale * ((a + b) * np.sin(t) - b * np.sin((a + b) * t / b + curve_phase))
                elif curve_type == 'hypocycloid':
                    # Hypocycloid: circle rolling inside another circle
                    x = curve_scale * ((a - b) * np.cos(t) + b * np.cos((a - b) * t / b + curve_phase))
                    y = curve_scale * ((a - b) * np.sin(t) - b * np.sin((a - b) * t / b + curve_phase))
                elif curve_type == 'cardioid':
                    # Heart-shaped curve
                    x = curve_scale * (2 * np.cos(t) - np.cos(2 * t + curve_phase))
                    y = curve_scale * (2 * np.sin(t) - np.sin(2 * t + curve_phase))
                elif curve_type == 'astroid':
                    # Four-pointed star curve
                    x = curve_scale * (np.cos(t + curve_phase))**3
                    y = curve_scale * (np.sin(t + curve_phase))**3
                elif curve_type == 'cycloid':
                    # Curve traced by a point on a rolling circle
                    x = curve_scale * (a * t - b * np.sin(t + curve_phase))
                    y = curve_scale * (a - b * np.cos(t + curve_phase))

                # Normalize to fit in bounds
                if len(x) > 0 and len(y) > 0:
                    max_coord = max(np.max(np.abs(x)), np.max(np.abs(y)))
                    if max_coord > 0:
                        x = x / max_coord * 0.9
                        y = y / max_coord * 0.9

                # Apply line style
                if self.config.color_mode == "color" and self.config.custom_colors:
                    color = self.config.custom_colors[i % len(self.config.custom_colors)]
                else:
                    color = self.config.foreground_color

                if line_style == 'dotted':
                    ax.plot(x, y, ':', color=color, linewidth=self.config.line_width * 2, alpha=0.8)
                elif line_style == 'varied_width':
                    # Variable line width
                    for j in range(len(x)-1):
                        width = self.config.line_width * (1 + np.sin(j * 0.1))
                        ax.plot(x[j:j+2], y[j:j+2], color=color, linewidth=width, alpha=0.8)
                else:
                    ax.plot(x, y, color=color, linewidth=self.config.line_width, alpha=0.8)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating mathematical curve: {e}")
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
        self.pattern_var.set("Spiral")
        self.on_pattern_change()

        if 'spiral_type' in self.parameter_widgets:
            self.parameter_widgets['spiral_type']['var'].set('fibonacci')
        if 'arms' in self.parameter_widgets:
            self.parameter_widgets['arms']['var'].set(1)
        if 'gradient_effect' in self.parameter_widgets:
            self.parameter_widgets['gradient_effect']['var'].set('radial')
        if 'line_variation' in self.parameter_widgets:
            self.parameter_widgets['line_variation']['var'].set('increasing')

        self.color_mode_var.set('color')
        self.config.custom_colors = ['gold', 'orange', 'darkorange']
        logger.info("Loaded Golden Spiral preset")

    def load_fractal_preset(self):
        """Load fractal art preset"""
        self.pattern_var.set("Fractal")
        self.on_pattern_change()

        if 'fractal_type' in self.parameter_widgets:
            self.parameter_widgets['fractal_type']['var'].set('mandelbrot')
        if 'iterations' in self.parameter_widgets:
            self.parameter_widgets['iterations']['var'].set(200)
        if 'color_scheme' in self.parameter_widgets:
            self.parameter_widgets['color_scheme']['var'].set('rainbow')

        self.color_mode_var.set('color')
        self.resolution_var.set(2000)
        logger.info("Loaded Fractal Art preset")

    def load_op_art_preset(self):
        """Load Op Art preset"""
        self.pattern_var.set("Optical Illusion")
        self.on_pattern_change()

        if 'illusion_type' in self.parameter_widgets:
            self.parameter_widgets['illusion_type']['var'].set('rotating_snakes')
        if 'intensity' in self.parameter_widgets:
            self.parameter_widgets['intensity']['var'].set(1.5)
        if 'contrast' in self.parameter_widgets:
            self.parameter_widgets['contrast']['var'].set(0.9)

        self.color_mode_var.set('black_white')
        self.config.background_color = 'white'
        self.config.foreground_color = 'black'
        logger.info("Loaded Op Art preset")

    def load_psychedelic_preset(self):
        """Load psychedelic preset"""
        self.pattern_var.set("Spiral")
        self.on_pattern_change()

        if 'overlapping_spirals' in self.parameter_widgets:
            self.parameter_widgets['overlapping_spirals']['var'].set(4)
        if 'gradient_effect' in self.parameter_widgets:
            self.parameter_widgets['gradient_effect']['var'].set('angular')
        if 'arms' in self.parameter_widgets:
            self.parameter_widgets['arms']['var'].set(8)

        self.color_mode_var.set('color')
        self.config.custom_colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta']
        logger.info("Loaded Psychedelic preset")

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
