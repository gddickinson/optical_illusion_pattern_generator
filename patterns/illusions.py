"""
Classic optical illusion generator (Hermann grid, Fraser spiral, Mueller-Lyer, Kanizsa,
cafe wall, Zollner, rotating snakes, scintillating grid, impossible triangle).

Moved verbatim from optical_illusion_generator_V2.py (which now imports it from here) so the
web interface can use it without tkinter. _fig_to_array comes from patterns.base.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any

from patterns.base import PatternGenerator

logger = logging.getLogger(__name__)


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

        for (cx, cy) in centers:
            # Pac-man: a disc with a 60-degree wedge cut out, the mouth facing the centre of the
            # triangle, so the wedge edges line up with the illusory triangle's sides.
            mouth = np.arctan2(-cy, -cx)
            theta = np.linspace(mouth + np.pi/6, mouth + 2*np.pi - np.pi/6, 100)
            x = np.concatenate([[cx], cx + circle_radius * np.cos(theta)])
            y = np.concatenate([[cy], cy + circle_radius * np.sin(theta)])
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
