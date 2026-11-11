"""
Mathematical curve generator (Lissajous, rose, epicycloid, hypocycloid, cardioid, astroid, cycloid).

Moved verbatim from optical_illusion_generator_V2.py (which now imports it from here) so the
web interface can use it without tkinter. _fig_to_array comes from patterns.base.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any

from patterns.base import PatternGenerator

logger = logging.getLogger(__name__)


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
