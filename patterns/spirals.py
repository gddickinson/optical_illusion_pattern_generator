"""
Spiral and interference pattern generators.

SpiralGenerator: Archimedean, logarithmic, Fermat, and Fibonacci spirals.
InterferenceGenerator: Concentric, wave, and grid interference patterns.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from typing import Dict, Any

from config import ColorManager
from patterns.base import PatternGenerator

logger = logging.getLogger(__name__)


class SpiralGenerator(PatternGenerator):
    """Enhanced spiral generator with multiple spiral types and effects."""

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
        """Generate enhanced spiral pattern."""
        fig = None
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

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            t = np.linspace(0, 20 * np.pi * density, self.config.resolution)
            colors = ColorManager.get_palette(self.config.color_palette, max(arms * overlapping, 8))

            for spiral_idx in range(overlapping):
                spiral_offset_x = center_x + (spiral_idx - overlapping // 2) * 0.2
                spiral_offset_y = center_y + (spiral_idx - overlapping // 2) * 0.15

                for arm in range(arms):
                    arm_rotation = rotation + (arm * 360 / arms) + (spiral_idx * 45)
                    arm_rotation_rad = np.radians(arm_rotation)

                    if spiral_type == 'archimedean':
                        r = 0.05 * t * scale
                    elif spiral_type == 'logarithmic':
                        r = 0.1 * np.exp(0.1 * t) * scale
                    elif spiral_type == 'fermat':
                        r = 0.3 * np.sqrt(t) * scale
                    elif spiral_type == 'fibonacci':
                        phi = (1 + np.sqrt(5)) / 2
                        r = 0.1 * phi ** (t / np.pi) * scale

                    x = r * np.cos(t + arm_rotation_rad) + spiral_offset_x
                    y = r * np.sin(t + arm_rotation_rad) + spiral_offset_y

                    mask = ((x - spiral_offset_x) ** 2 + (y - spiral_offset_y) ** 2) <= 1
                    x, y = x[mask], y[mask]

                    if len(x) == 0:
                        continue

                    color_idx = (arm + spiral_idx) % len(colors)
                    base_color = colors[color_idx] if self.config.color_mode == 'color' else self.config.foreground_color

                    if gradient_effect == 'radial':
                        alphas = np.linspace(1.0, 0.3, len(x))
                        for i in range(len(x) - 1):
                            ax.plot(x[i:i + 2], y[i:i + 2], color=base_color,
                                    linewidth=self.config.line_width, alpha=alphas[i])
                    elif gradient_effect == 'angular':
                        angles = np.arctan2(y - spiral_offset_y, x - spiral_offset_x)
                        colors_gradient = plt.cm.hsv((angles + np.pi) / (2 * np.pi))
                        for i in range(len(x) - 1):
                            ax.plot(x[i:i + 2], y[i:i + 2], color=colors_gradient[i],
                                    linewidth=self.config.line_width)
                    else:
                        ax.plot(x, y, color=base_color, linewidth=self.config.line_width, alpha=0.8)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating spiral: {e}")
            raise
        finally:
            if fig is not None:
                plt.close(fig)


class InterferenceGenerator(PatternGenerator):
    """Interference patterns generator (concentric, wave, grid)."""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'pattern_type': {'type': 'choice', 'choices': ['concentric', 'wave', 'grid'], 'default': 'concentric'},
            'frequency1': {'type': 'float', 'range': (1, 50), 'default': 10},
            'frequency2': {'type': 'float', 'range': (1, 50), 'default': 12},
            'phase': {'type': 'float', 'range': (0, 360), 'default': 0},
            'amplitude': {'type': 'float', 'range': (0.1, 2.0), 'default': 1.0}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate interference pattern."""
        fig = None
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
                R = np.sqrt(X ** 2 + Y ** 2)
                pattern1 = np.sin(2 * np.pi * freq1 * R + phase)
                pattern2 = np.sin(2 * np.pi * freq2 * R)
            elif pattern_type == 'wave':
                pattern1 = np.sin(2 * np.pi * freq1 * X + phase)
                pattern2 = np.sin(2 * np.pi * freq2 * Y)
            elif pattern_type == 'grid':
                pattern1 = np.sin(2 * np.pi * freq1 * X + phase) + np.sin(2 * np.pi * freq1 * Y + phase)
                pattern2 = np.sin(2 * np.pi * freq2 * X) + np.sin(2 * np.pi * freq2 * Y)

            interference = amplitude * (pattern1 + pattern2)

            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))

            if self.config.color_mode == "color":
                colors = ColorManager.get_palette(self.config.color_palette, 5)
                cmap = LinearSegmentedColormap.from_list('interference', colors)
                ax.contour(X, Y, interference, levels=20, cmap=cmap, linewidths=self.config.line_width)
            else:
                ax.contour(X, Y, interference, levels=20, colors=self.config.foreground_color, linewidths=self.config.line_width)

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
            if fig is not None:
                plt.close(fig)
