"""
Voronoi diagram pattern generator.

Supports random, grid, Poisson disk, and Fibonacci point distributions
with Lloyd relaxation, multiple coloring modes, and clipping options.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
from typing import Dict, Any

from config import ColorManager
from patterns.base import PatternGenerator

logger = logging.getLogger(__name__)


class VoronoiGenerator(PatternGenerator):
    """Generates Voronoi diagram patterns."""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'num_points': {'type': 'int', 'range': (10, 500), 'default': 50},
            'distribution': {'type': 'choice', 'choices': ['random', 'grid', 'poisson', 'fibonacci'], 'default': 'random'},
            'style': {'type': 'choice', 'choices': ['filled', 'edges', 'both', 'stippled'], 'default': 'both'},
            'edge_thickness': {'type': 'float', 'range': (0.1, 5.0), 'default': 1.0},
            'color_by': {'type': 'choice', 'choices': ['random', 'distance', 'area', 'neighbors'], 'default': 'random'},
            'relaxation_steps': {'type': 'int', 'range': (0, 10), 'default': 0},
            'clip_bounds': {'type': 'choice', 'choices': ['square', 'circle', 'none'], 'default': 'square'}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate Voronoi diagram pattern."""
        fig = None
        try:
            num_points = kwargs.get('num_points', 50)
            distribution = kwargs.get('distribution', 'random')
            style = kwargs.get('style', 'both')
            edge_thickness = kwargs.get('edge_thickness', 1.0)
            color_by = kwargs.get('color_by', 'random')
            relaxation_steps = kwargs.get('relaxation_steps', 0)
            clip_bounds = kwargs.get('clip_bounds', 'square')

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            points = self._generate_points(num_points, distribution)
            for _ in range(relaxation_steps):
                points = self._lloyd_relaxation(points)

            vor = Voronoi(points)

            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            colors = ColorManager.get_palette(self.config.color_palette, num_points)
            cell_colors = self._assign_colors(vor, color_by, colors)
            self._draw_voronoi(ax, vor, style, edge_thickness, cell_colors, clip_bounds)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating Voronoi pattern: {e}")
            raise
        finally:
            if fig is not None:
                plt.close(fig)

    def _generate_points(self, num_points, distribution):
        if distribution == 'random':
            return np.random.uniform(-1, 1, (num_points, 2))
        elif distribution == 'grid':
            side = int(np.sqrt(num_points))
            x = np.linspace(-0.9, 0.9, side)
            y = np.linspace(-0.9, 0.9, side)
            xx, yy = np.meshgrid(x, y)
            points = np.column_stack([xx.ravel(), yy.ravel()])
            return points[:num_points]
        elif distribution == 'poisson':
            points = []
            attempts = 0
            min_distance = 0.1
            while len(points) < num_points and attempts < num_points * 10:
                candidate = np.random.uniform(-1, 1, 2)
                if not points or min(np.linalg.norm(candidate - np.array(p)) for p in points) > min_distance:
                    points.append(candidate)
                attempts += 1
            return np.array(points)
        elif distribution == 'fibonacci':
            points = []
            golden_ratio = (1 + np.sqrt(5)) / 2
            for i in range(num_points):
                r = np.sqrt(i / num_points) * 0.9
                theta = 2 * np.pi * i / golden_ratio
                points.append([r * np.cos(theta), r * np.sin(theta)])
            return np.array(points)
        else:
            return np.random.uniform(-1, 1, (num_points, 2))

    def _lloyd_relaxation(self, points):
        vor = Voronoi(points)
        centroids = []
        for point_idx in range(len(points)):
            region_idx = vor.point_region[point_idx]
            region = vor.regions[region_idx]
            if len(region) > 0 and -1 not in region:
                vertices = vor.vertices[region]
                centroids.append(np.mean(vertices, axis=0))
            else:
                centroids.append(points[point_idx])
        return np.array(centroids)

    def _assign_colors(self, vor, color_by, colors):
        if color_by == 'random':
            return [colors[i % len(colors)] for i in range(len(vor.points))]
        elif color_by == 'distance':
            distances = np.linalg.norm(vor.points, axis=1)
            normalized = (distances - distances.min()) / max(distances.max() - distances.min(), 1e-10)
            return [colors[int(d * (len(colors) - 1))] for d in normalized]
        elif color_by == 'area':
            areas = []
            for point_idx in range(len(vor.points)):
                region_idx = vor.point_region[point_idx]
                region = vor.regions[region_idx]
                if len(region) > 0 and -1 not in region:
                    vertices = vor.vertices[region]
                    area = 0.5 * abs(sum(
                        vertices[i][0] * (vertices[(i + 1) % len(vertices)][1] - vertices[i - 1][1])
                        for i in range(len(vertices))
                    ))
                    areas.append(area)
                else:
                    areas.append(0)
            if max(areas) > min(areas):
                normalized = [(a - min(areas)) / (max(areas) - min(areas)) for a in areas]
                return [colors[int(a * (len(colors) - 1))] for a in normalized]
            return [colors[0]] * len(vor.points)
        else:
            return [colors[i % len(colors)] for i in range(len(vor.points))]

    def _draw_voronoi(self, ax, vor, style, edge_thickness, cell_colors, clip_bounds):
        if style in ['filled', 'both']:
            for point_idx in range(len(vor.points)):
                region_idx = vor.point_region[point_idx]
                region = vor.regions[region_idx]
                if len(region) > 0 and -1 not in region:
                    vertices = vor.vertices[region]
                    if clip_bounds == 'square':
                        vertices = self._clip_to_square(vertices)
                    elif clip_bounds == 'circle':
                        vertices = self._clip_to_circle(vertices)
                    if len(vertices) > 2:
                        color = cell_colors[point_idx] if self.config.color_mode == 'color' else self.config.foreground_color
                        ax.fill(vertices[:, 0], vertices[:, 1], color=color, alpha=0.7)

        if style in ['edges', 'both']:
            for ridge in vor.ridge_vertices:
                if -1 not in ridge:
                    vertices = vor.vertices[ridge]
                    ax.plot(vertices[:, 0], vertices[:, 1], 'k-',
                            linewidth=self.config.line_width * edge_thickness, alpha=0.8)

        if style == 'stippled':
            for point_idx in range(len(vor.points)):
                region_idx = vor.point_region[point_idx]
                region = vor.regions[region_idx]
                if len(region) > 0 and -1 not in region:
                    vertices = vor.vertices[region]
                    if len(vertices) > 2:
                        centroid = np.mean(vertices, axis=0)
                        color = cell_colors[point_idx] if self.config.color_mode == 'color' else self.config.foreground_color
                        for _ in range(20):
                            test_point = centroid + np.random.normal(0, 0.1, 2)
                            if self._point_in_polygon(test_point, vertices):
                                ax.plot(test_point[0], test_point[1], 'o', color=color, markersize=2)

    def _clip_to_square(self, vertices):
        return np.clip(vertices, -1, 1)

    def _clip_to_circle(self, vertices):
        clipped = []
        for vertex in vertices:
            x, y = vertex
            dist = np.sqrt(x * x + y * y)
            if dist > 1:
                x, y = x / dist, y / dist
            clipped.append([x, y])
        return np.array(clipped)

    def _point_in_polygon(self, point, vertices):
        x, y = point
        n = len(vertices)
        inside = False
        p1x, p1y = vertices[0]
        for i in range(1, n + 1):
            p2x, p2y = vertices[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
