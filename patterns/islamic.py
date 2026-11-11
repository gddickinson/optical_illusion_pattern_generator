"""
Islamic geometric pattern generator.

Generates octagon-star, hexagon-flower, square Kufic, Girih tiles,
and Moroccan Zellige patterns with interlacing and symmetry options
(symmetry p1/p2/p4/p6: lattice and n-fold tile symmetry from patterns/symmetry.py).
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any

from config import ColorManager
from patterns.base import PatternGenerator
from patterns.symmetry import tiles

logger = logging.getLogger(__name__)


class IslamicGeometryGenerator(PatternGenerator):
    """Generates Islamic geometric patterns."""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'pattern_type': {'type': 'choice', 'choices': ['octagon_star', 'hexagon_flower', 'square_kufic', 'girih_tiles', 'morocco_zellige'], 'default': 'octagon_star'},
            'tile_size': {'type': 'float', 'range': (0.1, 1.0), 'default': 0.2},
            'repetitions_x': {'type': 'int', 'range': (2, 20), 'default': 8},
            'repetitions_y': {'type': 'int', 'range': (2, 20), 'default': 6},
            'rotation': {'type': 'float', 'range': (0, 360), 'default': 0},
            'interlace': {'type': 'choice', 'choices': ['none', 'simple', 'complex'], 'default': 'simple'},
            'symmetry': {'type': 'choice', 'choices': ['p1', 'p2', 'p4', 'p6'], 'default': 'p4'},
            'ornament_detail': {'type': 'float', 'range': (0.1, 2.0), 'default': 1.0}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate Islamic geometric pattern."""
        fig = None
        try:
            pattern_type = kwargs.get('pattern_type', 'octagon_star')
            tile_size = kwargs.get('tile_size', 0.2)
            rep_x = kwargs.get('repetitions_x', 8)
            rep_y = kwargs.get('repetitions_y', 6)
            rotation = kwargs.get('rotation', 0)
            interlace = kwargs.get('interlace', 'simple')
            detail = kwargs.get('ornament_detail', 1.0)
            self._symmetry = kwargs.get('symmetry', 'p4')

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            if pattern_type == 'octagon_star':
                self._generate_octagon_star(ax, tile_size, rep_x, rep_y, rotation, interlace, detail)
            elif pattern_type == 'hexagon_flower':
                self._generate_hexagon_flower(ax, tile_size, rep_x, rep_y, rotation, detail)
            elif pattern_type == 'square_kufic':
                self._generate_square_kufic(ax, tile_size, rep_x, rep_y, rotation, detail)
            elif pattern_type == 'girih_tiles':
                self._generate_girih_tiles(ax, tile_size, rep_x, rep_y, rotation, detail)
            elif pattern_type == 'morocco_zellige':
                self._generate_morocco_zellige(ax, tile_size, rep_x, rep_y, rotation, detail)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating Islamic pattern: {e}")
            raise
        finally:
            if fig is not None:
                plt.close(fig)

    def _generate_octagon_star(self, ax, size, rep_x, rep_y, rotation, interlace, detail):
        colors = ColorManager.get_palette(self.config.color_palette, 4)
        for x_center, y_center, i, j, tile in tiles(ax, rep_x, rep_y, self._symmetry):
            octagon = self._create_regular_polygon(8, size, x_center, y_center, rotation)
            color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
            tile.fill(octagon[:, 0], octagon[:, 1], color=color, alpha=0.8, edgecolor='black', linewidth=self.config.line_width)
            star = self._create_star(8, size * 0.6, size * 0.3, x_center, y_center, rotation + 22.5)
            color = colors[1] if self.config.color_mode == 'color' else self.config.foreground_color
            tile.fill(star[:, 0], star[:, 1], color=color, alpha=0.9, edgecolor='black', linewidth=self.config.line_width)
            if interlace != 'none':
                self._add_interlace_pattern(tile, x_center, y_center, size, detail, colors[2:])

    def _generate_hexagon_flower(self, ax, size, rep_x, rep_y, rotation, detail):
        colors = ColorManager.get_palette(self.config.color_palette, 6)
        for x_center, y_center, i, j, tile in tiles(ax, rep_x, rep_y, self._symmetry):
            hexagon = self._create_regular_polygon(6, size, x_center, y_center, rotation)
            color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
            tile.fill(hexagon[:, 0], hexagon[:, 1], color=color, alpha=0.8, edgecolor='black', linewidth=self.config.line_width)
            for k in range(6):
                angle = k * 60 + rotation
                petal_x = x_center + size * 0.8 * np.cos(np.radians(angle))
                petal_y = y_center + size * 0.8 * np.sin(np.radians(angle))
                petal = self._create_petal(size * 0.4, petal_x, petal_y, angle)
                color = colors[(k + 1) % len(colors)] if self.config.color_mode == 'color' else self.config.foreground_color
                tile.fill(petal[:, 0], petal[:, 1], color=color, alpha=0.7, edgecolor='black', linewidth=self.config.line_width * 0.5)

    def _generate_square_kufic(self, ax, size, rep_x, rep_y, rotation, detail):
        colors = ColorManager.get_palette(self.config.color_palette, 3)
        for x_center, y_center, i, j, tile in tiles(ax, rep_x, rep_y, self._symmetry):
            self._create_kufic_element(tile, x_center, y_center, size, rotation, detail, colors)

    def _generate_girih_tiles(self, ax, size, rep_x, rep_y, rotation, detail):
        colors = ColorManager.get_palette(self.config.color_palette, 5)
        for x_center, y_center, i, j, tile in tiles(ax, rep_x, rep_y, self._symmetry):
            decagon = self._create_regular_polygon(10, size, x_center, y_center, rotation)
            color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
            tile.fill(decagon[:, 0], decagon[:, 1], color=color, alpha=0.7, edgecolor='black', linewidth=self.config.line_width)
            for k in range(5):
                angle = k * 72 + rotation
                bowtie_x = x_center + size * 0.7 * np.cos(np.radians(angle))
                bowtie_y = y_center + size * 0.7 * np.sin(np.radians(angle))
                bowtie = self._create_bowtie(size * 0.3, bowtie_x, bowtie_y, angle)
                color = colors[(k + 1) % len(colors)] if self.config.color_mode == 'color' else self.config.foreground_color
                tile.fill(bowtie[:, 0], bowtie[:, 1], color=color, alpha=0.8, edgecolor='black', linewidth=self.config.line_width * 0.5)

    def _generate_morocco_zellige(self, ax, size, rep_x, rep_y, rotation, detail):
        colors = ColorManager.get_palette('ocean', 8)
        for x_center, y_center, i, j, tile in tiles(ax, rep_x, rep_y, self._symmetry):
            if (i + j) % 2 == 0:
                star = self._create_star(8, size, size * 0.5, x_center, y_center, rotation)
                color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
                tile.fill(star[:, 0], star[:, 1], color=color, alpha=0.8, edgecolor='white', linewidth=self.config.line_width)
            else:
                cross = self._create_cross(size, x_center, y_center, rotation)
                color = colors[1] if self.config.color_mode == 'color' else self.config.foreground_color
                tile.fill(cross[:, 0], cross[:, 1], color=color, alpha=0.8, edgecolor='white', linewidth=self.config.line_width)

    # --- Shape helpers ---

    def _create_regular_polygon(self, n_sides, radius, x_center, y_center, rotation):
        angles = np.linspace(0, 2 * np.pi, n_sides + 1) + np.radians(rotation)
        x = x_center + radius * np.cos(angles)
        y = y_center + radius * np.sin(angles)
        return np.column_stack([x, y])

    def _create_star(self, n_points, outer_radius, inner_radius, x_center, y_center, rotation):
        angles = []
        for i in range(n_points):
            angles.append(2 * np.pi * i / n_points + np.radians(rotation))
            angles.append(2 * np.pi * (i + 0.5) / n_points + np.radians(rotation))
        x, y = [], []
        for i, angle in enumerate(angles):
            radius = outer_radius if i % 2 == 0 else inner_radius
            x.append(x_center + radius * np.cos(angle))
            y.append(y_center + radius * np.sin(angle))
        x.append(x[0])
        y.append(y[0])
        return np.column_stack([x, y])

    def _create_petal(self, size, x_center, y_center, angle):
        t = np.linspace(0, np.pi, 20)
        r = size * np.sin(t)
        x = x_center + r * np.cos(t + np.radians(angle))
        y = y_center + r * np.sin(t + np.radians(angle))
        return np.column_stack([x, y])

    def _create_kufic_element(self, ax, x_center, y_center, size, rotation, detail, colors):
        elements = [
            np.array([[-0.5, -0.3], [0.5, -0.3], [0.5, 0.3], [-0.5, 0.3]]) * size,
            np.array([[-0.3, -0.5], [0.3, -0.5], [0.3, 0.5], [-0.3, 0.5]]) * size
        ]
        for i, element in enumerate(elements):
            element[:, 0] += x_center
            element[:, 1] += y_center
            color = colors[i % len(colors)] if self.config.color_mode == 'color' else self.config.foreground_color
            ax.fill(element[:, 0], element[:, 1], color=color, alpha=0.8, edgecolor='black', linewidth=self.config.line_width)

    def _create_bowtie(self, size, x_center, y_center, angle):
        points = np.array([
            [-size, 0], [-size * 0.3, -size * 0.3], [0, 0], [-size * 0.3, size * 0.3],
            [-size, 0], [size, 0], [size * 0.3, size * 0.3], [0, 0], [size * 0.3, -size * 0.3], [size, 0]
        ])
        cos_a, sin_a = np.cos(np.radians(angle)), np.sin(np.radians(angle))
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        rotated_points = points @ rotation_matrix.T
        rotated_points[:, 0] += x_center
        rotated_points[:, 1] += y_center
        return rotated_points

    def _create_cross(self, size, x_center, y_center, rotation):
        thickness = size * 0.3
        points = np.array([
            [-thickness, -size], [thickness, -size], [thickness, -thickness],
            [size, -thickness], [size, thickness], [thickness, thickness],
            [thickness, size], [-thickness, size], [-thickness, thickness],
            [-size, thickness], [-size, -thickness], [-thickness, -thickness]
        ])
        cos_a, sin_a = np.cos(np.radians(rotation)), np.sin(np.radians(rotation))
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        rotated_points = points @ rotation_matrix.T
        rotated_points[:, 0] += x_center
        rotated_points[:, 1] += y_center
        return rotated_points

    def _add_interlace_pattern(self, ax, x_center, y_center, size, detail, colors):
        for i in range(int(4 * detail)):
            angle = i * 90 / detail
            x = x_center + size * 0.2 * np.cos(np.radians(angle))
            y = y_center + size * 0.2 * np.sin(np.radians(angle))
            circle = plt.Circle(
                (x, y), size * 0.1,
                color=colors[i % len(colors)] if colors and self.config.color_mode == 'color' else self.config.foreground_color,
                alpha=0.6
            )
            ax.add_patch(circle)
