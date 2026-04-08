"""
Tessellation pattern generator.

Supports regular, Penrose, hexagonal, triangular, Ammann-Beenker, and Truchet
tilings with configurable irregularity, color schemes, borders, and fill patterns.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any

from config import ColorManager
from patterns.base import PatternGenerator

logger = logging.getLogger(__name__)


class TessellationGenerator(PatternGenerator):
    """Generates tessellation patterns."""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'tessellation_type': {'type': 'choice', 'choices': ['regular', 'penrose', 'hexagonal', 'triangular', 'ammann_beenker', 'truchet'], 'default': 'regular'},
            'base_shape': {'type': 'choice', 'choices': ['triangle', 'square', 'hexagon', 'rhombus'], 'default': 'hexagon'},
            'tile_size': {'type': 'float', 'range': (0.05, 0.5), 'default': 0.1},
            'irregularity': {'type': 'float', 'range': (0.0, 0.5), 'default': 0.0},
            'color_scheme': {'type': 'choice', 'choices': ['alternating', 'gradient', 'random', 'symmetric'], 'default': 'alternating'},
            'border_style': {'type': 'choice', 'choices': ['none', 'thin', 'thick', 'decorative'], 'default': 'thin'},
            'fill_pattern': {'type': 'choice', 'choices': ['solid', 'striped', 'dotted', 'cross_hatch'], 'default': 'solid'}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate tessellation pattern."""
        fig = None
        try:
            tess_type = kwargs.get('tessellation_type', 'regular')
            base_shape = kwargs.get('base_shape', 'hexagon')
            tile_size = kwargs.get('tile_size', 0.1)
            irregularity = kwargs.get('irregularity', 0.0)
            color_scheme = kwargs.get('color_scheme', 'alternating')
            border_style = kwargs.get('border_style', 'thin')
            fill_pattern = kwargs.get('fill_pattern', 'solid')

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            if tess_type == 'regular':
                self._generate_regular_tessellation(ax, base_shape, tile_size, irregularity, color_scheme, border_style, fill_pattern)
            elif tess_type == 'penrose':
                self._generate_penrose_tiling(ax, tile_size, color_scheme, border_style)
            elif tess_type == 'hexagonal':
                self._generate_hexagonal_tessellation(ax, tile_size, irregularity, color_scheme, border_style, fill_pattern)
            elif tess_type == 'triangular':
                self._generate_triangular_tessellation(ax, tile_size, irregularity, color_scheme, border_style, fill_pattern)
            elif tess_type == 'ammann_beenker':
                self._generate_ammann_beenker(ax, tile_size, color_scheme, border_style)
            elif tess_type == 'truchet':
                self._generate_truchet_tiles(ax, tile_size, color_scheme, border_style)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating tessellation: {e}")
            raise
        finally:
            if fig is not None:
                plt.close(fig)

    # --- Tessellation types ---

    def _generate_regular_tessellation(self, ax, shape, size, irregularity, color_scheme, border_style, fill_pattern):
        colors = ColorManager.get_palette(self.config.color_palette, 6)
        if shape == 'hexagon':
            hex_height = size * np.sqrt(3)
            hex_width = size * 2
            rows = int(2 / hex_height) + 2
            cols = int(2 / (hex_width * 0.75)) + 2
            for row in range(rows):
                for col in range(cols):
                    x_offset = col * hex_width * 0.75
                    y_offset = row * hex_height
                    if row % 2 == 1:
                        x_offset += hex_width * 0.375
                    x_center = -1 + x_offset
                    y_center = -1 + y_offset
                    if irregularity > 0:
                        x_center += np.random.uniform(-irregularity, irregularity) * size
                        y_center += np.random.uniform(-irregularity, irregularity) * size
                    hexagon = self._create_hexagon(x_center, y_center, size)
                    color = self._select_tile_color(colors, color_scheme, row, col)
                    self._apply_fill_pattern(ax, hexagon, color, fill_pattern)
                    self._apply_border(ax, hexagon, border_style)
        elif shape == 'square':
            rows = int(2 / size) + 1
            cols = int(2 / size) + 1
            for row in range(rows):
                for col in range(cols):
                    x_center = -1 + col * size + size / 2
                    y_center = -1 + row * size + size / 2
                    if irregularity > 0:
                        x_center += np.random.uniform(-irregularity, irregularity) * size
                        y_center += np.random.uniform(-irregularity, irregularity) * size
                    square = self._create_square(x_center, y_center, size)
                    color = self._select_tile_color(colors, color_scheme, row, col)
                    self._apply_fill_pattern(ax, square, color, fill_pattern)
                    self._apply_border(ax, square, border_style)
        elif shape == 'triangle':
            tri_height = size * np.sqrt(3) / 2
            rows = int(2 / tri_height) + 2
            cols = int(2 / size) + 2
            for row in range(rows):
                for col in range(cols):
                    x_center = -1 + col * size / 2
                    y_center = -1 + row * tri_height
                    pointing_up = (row + col) % 2 == 0
                    triangle = self._create_triangle(x_center, y_center, size, pointing_up)
                    color = self._select_tile_color(colors, color_scheme, row, col)
                    self._apply_fill_pattern(ax, triangle, color, fill_pattern)
                    self._apply_border(ax, triangle, border_style)

    def _generate_penrose_tiling(self, ax, size, color_scheme, border_style):
        colors = ColorManager.get_palette(self.config.color_palette, 2)
        phi = (1 + np.sqrt(5)) / 2
        num_tiles = int(100 / (size * size))
        for _ in range(num_tiles):
            x_center = np.random.uniform(-1, 1)
            y_center = np.random.uniform(-1, 1)
            orientation = np.random.uniform(0, 360)
            if np.random.random() < 0.5:
                rhombus = self._create_rhombus(x_center, y_center, size, size / phi, orientation, 72)
                color = colors[0]
            else:
                rhombus = self._create_rhombus(x_center, y_center, size, size * phi, orientation, 36)
                color = colors[1]
            if self.config.color_mode == 'color':
                ax.fill(rhombus[:, 0], rhombus[:, 1], color=color, alpha=0.8)
            else:
                ax.fill(rhombus[:, 0], rhombus[:, 1], color=self.config.foreground_color, alpha=0.8)
            self._apply_border(ax, rhombus, border_style)

    def _generate_hexagonal_tessellation(self, ax, size, irregularity, color_scheme, border_style, fill_pattern):
        colors = ColorManager.get_palette(self.config.color_palette, 8)
        hex_height = size * np.sqrt(3)
        hex_width = size * 2
        rows = int(2 / hex_height) + 2
        cols = int(2 / (hex_width * 0.75)) + 2
        for row in range(rows):
            for col in range(cols):
                x_offset = col * hex_width * 0.75
                y_offset = row * hex_height
                if row % 2 == 1:
                    x_offset += hex_width * 0.375
                x_center = -1 + x_offset
                y_center = -1 + y_offset
                if irregularity > 0:
                    x_center += np.random.uniform(-irregularity, irregularity) * size
                    y_center += np.random.uniform(-irregularity, irregularity) * size
                hexagon = self._create_hexagon(x_center, y_center, size * (1 + np.random.uniform(-irregularity, irregularity)))
                color = self._select_tile_color(colors, color_scheme, row, col)
                self._apply_fill_pattern(ax, hexagon, color, fill_pattern)
                self._apply_border(ax, hexagon, border_style)

    def _generate_triangular_tessellation(self, ax, size, irregularity, color_scheme, border_style, fill_pattern):
        colors = ColorManager.get_palette(self.config.color_palette, 4)
        tri_height = size * np.sqrt(3) / 2
        rows = int(2 / tri_height) + 2
        cols = int(2 / size) + 2
        for row in range(rows):
            for col in range(cols):
                x_center = -1 + col * size / 2
                y_center = -1 + row * tri_height
                if irregularity > 0:
                    x_center += np.random.uniform(-irregularity, irregularity) * size
                    y_center += np.random.uniform(-irregularity, irregularity) * size
                pointing_up = (row + col) % 2 == 0
                triangle = self._create_triangle(x_center, y_center, size, pointing_up)
                color = self._select_tile_color(colors, color_scheme, row, col)
                self._apply_fill_pattern(ax, triangle, color, fill_pattern)
                self._apply_border(ax, triangle, border_style)

    def _generate_ammann_beenker(self, ax, size, color_scheme, border_style):
        colors = ColorManager.get_palette(self.config.color_palette, 2)
        num_tiles = int(50 / (size * size))
        for _ in range(num_tiles):
            x_center = np.random.uniform(-1, 1)
            y_center = np.random.uniform(-1, 1)
            if np.random.random() < 0.6:
                octagon = self._create_regular_polygon(8, size, x_center, y_center, np.random.uniform(0, 45))
                color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
                ax.fill(octagon[:, 0], octagon[:, 1], color=color, alpha=0.8)
            else:
                square = self._create_square(x_center, y_center, size * 0.7)
                color = colors[1] if self.config.color_mode == 'color' else self.config.foreground_color
                ax.fill(square[:, 0], square[:, 1], color=color, alpha=0.8)

    def _generate_truchet_tiles(self, ax, size, color_scheme, border_style):
        colors = ColorManager.get_palette(self.config.color_palette, 4)
        rows = int(2 / size) + 1
        cols = int(2 / size) + 1
        for row in range(rows):
            for col in range(cols):
                x_center = -1 + col * size + size / 2
                y_center = -1 + row * size + size / 2
                square = self._create_square(x_center, y_center, size)
                color = colors[(row + col) % len(colors)] if self.config.color_mode == 'color' else self.config.background_color
                ax.fill(square[:, 0], square[:, 1], color=color, alpha=0.9)
                self._add_truchet_curve(ax, x_center, y_center, size, (row + col) % 4)

    # --- Shape creation helpers ---

    def _create_hexagon(self, x_center, y_center, size):
        angles = np.linspace(0, 2 * np.pi, 7)
        x = x_center + size * np.cos(angles)
        y = y_center + size * np.sin(angles)
        return np.column_stack([x, y])

    def _create_square(self, x_center, y_center, size):
        half = size / 2
        return np.array([
            [x_center - half, y_center - half], [x_center + half, y_center - half],
            [x_center + half, y_center + half], [x_center - half, y_center + half],
            [x_center - half, y_center - half]
        ])

    def _create_triangle(self, x_center, y_center, size, pointing_up=True):
        height = size * np.sqrt(3) / 2
        if pointing_up:
            return np.array([
                [x_center, y_center + height * 2 / 3],
                [x_center - size / 2, y_center - height * 1 / 3],
                [x_center + size / 2, y_center - height * 1 / 3],
                [x_center, y_center + height * 2 / 3]
            ])
        else:
            return np.array([
                [x_center, y_center - height * 2 / 3],
                [x_center - size / 2, y_center + height * 1 / 3],
                [x_center + size / 2, y_center + height * 1 / 3],
                [x_center, y_center - height * 2 / 3]
            ])

    def _create_rhombus(self, x_center, y_center, width, height, rotation, acute_angle):
        rot_rad = np.radians(rotation)
        half_w, half_h = width / 2, height / 2
        vertices = np.array([[-half_w, 0], [0, half_h], [half_w, 0], [0, -half_h], [-half_w, 0]])
        cos_r, sin_r = np.cos(rot_rad), np.sin(rot_rad)
        rotation_matrix = np.array([[cos_r, -sin_r], [sin_r, cos_r]])
        rotated = vertices @ rotation_matrix.T
        rotated[:, 0] += x_center
        rotated[:, 1] += y_center
        return rotated

    def _create_regular_polygon(self, n_sides, radius, x_center, y_center, rotation):
        angles = np.linspace(0, 2 * np.pi, n_sides + 1) + np.radians(rotation)
        x = x_center + radius * np.cos(angles)
        y = y_center + radius * np.sin(angles)
        return np.column_stack([x, y])

    # --- Style helpers ---

    def _select_tile_color(self, colors, scheme, row, col):
        if scheme == 'alternating':
            return colors[(row + col) % 2] if self.config.color_mode == 'color' else self.config.foreground_color
        elif scheme == 'gradient':
            return colors[(row + col) % len(colors)] if self.config.color_mode == 'color' else self.config.foreground_color
        elif scheme == 'random':
            return colors[np.random.randint(len(colors))] if self.config.color_mode == 'color' else self.config.foreground_color
        elif scheme == 'symmetric':
            return colors[min(row, col) % len(colors)] if self.config.color_mode == 'color' else self.config.foreground_color
        return colors[0] if self.config.color_mode == 'color' else self.config.foreground_color

    def _apply_fill_pattern(self, ax, vertices, color, pattern):
        ax.fill(vertices[:, 0], vertices[:, 1], color=color, alpha=0.8)
        if pattern == 'striped':
            center_x, center_y = np.mean(vertices[:-1], axis=0)
            for i in range(5):
                y_line = center_y + (i - 2) * 0.02
                ax.axhline(y=y_line, xmin=0, xmax=1, color='black', alpha=0.3, linewidth=0.5)
        elif pattern == 'dotted':
            center_x, center_y = np.mean(vertices[:-1], axis=0)
            for i in range(-2, 3):
                for j in range(-2, 3):
                    ax.plot(center_x + i * 0.02, center_y + j * 0.02, 'ko', markersize=1)
        elif pattern == 'cross_hatch':
            center_x, center_y = np.mean(vertices[:-1], axis=0)
            for i in range(5):
                offset = (i - 2) * 0.02
                ax.plot([center_x - 0.05, center_x + 0.05], [center_y + offset, center_y + offset], 'k-', alpha=0.3, linewidth=0.5)
                ax.plot([center_x + offset, center_x + offset], [center_y - 0.05, center_y + 0.05], 'k-', alpha=0.3, linewidth=0.5)

    def _apply_border(self, ax, vertices, style):
        if style == 'none':
            return
        elif style == 'thin':
            ax.plot(vertices[:, 0], vertices[:, 1], 'k-', linewidth=self.config.line_width * 0.5, alpha=0.8)
        elif style == 'thick':
            ax.plot(vertices[:, 0], vertices[:, 1], 'k-', linewidth=self.config.line_width * 2, alpha=0.8)
        elif style == 'decorative':
            ax.plot(vertices[:, 0], vertices[:, 1], 'k--', linewidth=self.config.line_width, alpha=0.6)

    def _add_truchet_curve(self, ax, x_center, y_center, size, variant):
        half = size / 2
        if variant == 0:
            theta = np.linspace(0, np.pi / 2, 20)
            x = x_center - half + half * (1 - np.cos(theta))
            y = y_center - half + half * np.sin(theta)
            ax.plot(x, y, 'k-', linewidth=self.config.line_width * 2)
        elif variant == 1:
            theta = np.linspace(np.pi / 2, np.pi, 20)
            x = x_center - half + half * (1 - np.cos(theta))
            y = y_center + half + half * np.sin(theta)
            ax.plot(x, y, 'k-', linewidth=self.config.line_width * 2)
        elif variant == 2:
            ax.plot([x_center - half, x_center + half], [y_center - half, y_center + half], 'k-', linewidth=self.config.line_width * 2)
        else:
            ax.plot([x_center - half, x_center + half], [y_center + half, y_center - half], 'k-', linewidth=self.config.line_width * 2)
