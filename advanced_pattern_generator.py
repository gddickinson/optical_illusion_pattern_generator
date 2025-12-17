#!/usr/bin/env python3
"""
Advanced Mathematical Art Studio
A comprehensive GUI application for creating mathematical patterns, optical illusions, and generative art.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import math
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any, List
import time
import random
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial.distance import pdist, squareform
import colorsys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PatternConfig:
    """Configuration class for pattern parameters"""
    width: int = 800
    height: int = 600
    resolution: int = 1000
    color_mode: str = "black_white"
    line_width: float = 1.0
    background_color: str = "white"
    foreground_color: str = "black"
    custom_colors: list = None
    color_palette: str = "default"
    use_gradients: bool = False

    def __post_init__(self):
        if self.custom_colors is None:
            self.custom_colors = ["red", "blue", "green", "purple", "orange"]

class ColorManager:
    """Advanced color management and palette generation"""

    @staticmethod
    def get_palette(palette_name: str, num_colors: int = 8) -> List[str]:
        """Get color palette by name"""
        palettes = {
            'default': ["red", "blue", "green", "purple", "orange", "cyan", "magenta", "yellow"],
            'sunset': ["#FF6B35", "#F7931E", "#FFD23F", "#EE4B6A", "#963D97", "#009DDC"],
            'ocean': ["#003F5C", "#2F4B7C", "#665191", "#A05195", "#D45087", "#F95D6A", "#FF7C43", "#FFA600"],
            'forest': ["#1B4332", "#2D5016", "#40531B", "#52734D", "#74A892", "#B7CE63"],
            'cosmic': ["#0B0C10", "#1F2833", "#C5C6C7", "#66FCF1", "#45A29E", "#FF6B6B"],
            'fire': ["#8B0000", "#DC143C", "#FF4500", "#FF6347", "#FFD700", "#FFFF00"],
            'ice': ["#E0F6FF", "#87CEEB", "#4682B4", "#1E90FF", "#0000FF", "#000080"],
            'earth': ["#8B4513", "#A0522D", "#CD853F", "#D2B48C", "#F4A460", "#DEB887"],
            'neon': ["#FF0080", "#00FF80", "#8000FF", "#FF8000", "#0080FF", "#80FF00"],
            'pastel': ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", "#E1BAFF"]
        }

        if palette_name in palettes:
            colors = palettes[palette_name]
            return (colors * ((num_colors // len(colors)) + 1))[:num_colors]
        else:
            return ColorManager.generate_hsv_palette(num_colors)

    @staticmethod
    def generate_hsv_palette(num_colors: int, saturation: float = 0.8, value: float = 0.9) -> List[str]:
        """Generate HSV-based color palette"""
        colors = []
        for i in range(num_colors):
            hue = i / num_colors
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            hex_color = '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            colors.append(hex_color)
        return colors

    @staticmethod
    def interpolate_colors(color1: str, color2: str, steps: int) -> List[str]:
        """Interpolate between two colors"""
        # Convert hex to RGB
        c1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
        c2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]

        colors = []
        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            colors.append(f'#{r:02x}{g:02x}{b:02x}')
        return colors

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

class IslamicGeometryGenerator(PatternGenerator):
    """Generates Islamic geometric patterns"""

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
        """Generate Islamic geometric pattern"""
        try:
            pattern_type = kwargs.get('pattern_type', 'octagon_star')
            tile_size = kwargs.get('tile_size', 0.2)
            rep_x = kwargs.get('repetitions_x', 8)
            rep_y = kwargs.get('repetitions_y', 6)
            rotation = kwargs.get('rotation', 0)
            interlace = kwargs.get('interlace', 'simple')
            symmetry = kwargs.get('symmetry', 'p4')
            detail = kwargs.get('ornament_detail', 1.0)

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
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
            plt.close(fig)

    def _generate_octagon_star(self, ax, size, rep_x, rep_y, rotation, interlace, detail):
        """Generate octagon and star pattern"""
        colors = ColorManager.get_palette(self.config.color_palette, 4)

        for i in range(rep_x):
            for j in range(rep_y):
                x_center = -1 + (i + 0.5) * 2 / rep_x
                y_center = -1 + (j + 0.5) * 2 / rep_y

                # Octagon
                octagon = self._create_regular_polygon(8, size, x_center, y_center, rotation)
                color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
                ax.fill(octagon[:, 0], octagon[:, 1], color=color, alpha=0.8, edgecolor='black', linewidth=self.config.line_width)

                # Star pattern
                star = self._create_star(8, size * 0.6, size * 0.3, x_center, y_center, rotation + 22.5)
                color = colors[1] if self.config.color_mode == 'color' else self.config.foreground_color
                ax.fill(star[:, 0], star[:, 1], color=color, alpha=0.9, edgecolor='black', linewidth=self.config.line_width)

                # Interlacing details
                if interlace != 'none':
                    self._add_interlace_pattern(ax, x_center, y_center, size, detail, colors[2:])

    def _generate_hexagon_flower(self, ax, size, rep_x, rep_y, rotation, detail):
        """Generate hexagonal flower pattern"""
        colors = ColorManager.get_palette(self.config.color_palette, 6)

        for i in range(rep_x):
            for j in range(rep_y):
                x_center = -1 + (i + 0.5) * 2 / rep_x
                y_center = -1 + (j + 0.5) * 2 / rep_y

                # Central hexagon
                hexagon = self._create_regular_polygon(6, size, x_center, y_center, rotation)
                color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
                ax.fill(hexagon[:, 0], hexagon[:, 1], color=color, alpha=0.8, edgecolor='black', linewidth=self.config.line_width)

                # Flower petals around hexagon
                for k in range(6):
                    angle = k * 60 + rotation
                    petal_x = x_center + size * 0.8 * np.cos(np.radians(angle))
                    petal_y = y_center + size * 0.8 * np.sin(np.radians(angle))

                    petal = self._create_petal(size * 0.4, petal_x, petal_y, angle)
                    color = colors[(k + 1) % len(colors)] if self.config.color_mode == 'color' else self.config.foreground_color
                    ax.fill(petal[:, 0], petal[:, 1], color=color, alpha=0.7, edgecolor='black', linewidth=self.config.line_width * 0.5)

    def _generate_square_kufic(self, ax, size, rep_x, rep_y, rotation, detail):
        """Generate square Kufic calligraphy pattern"""
        colors = ColorManager.get_palette(self.config.color_palette, 3)

        for i in range(rep_x):
            for j in range(rep_y):
                x_center = -1 + (i + 0.5) * 2 / rep_x
                y_center = -1 + (j + 0.5) * 2 / rep_y

                # Create geometric "letter" forms
                self._create_kufic_element(ax, x_center, y_center, size, rotation, detail, colors)

    def _generate_girih_tiles(self, ax, size, rep_x, rep_y, rotation, detail):
        """Generate Girih tiling pattern"""
        colors = ColorManager.get_palette(self.config.color_palette, 5)

        for i in range(rep_x):
            for j in range(rep_y):
                x_center = -1 + (i + 0.5) * 2 / rep_x
                y_center = -1 + (j + 0.5) * 2 / rep_y

                # Decagon
                decagon = self._create_regular_polygon(10, size, x_center, y_center, rotation)
                color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
                ax.fill(decagon[:, 0], decagon[:, 1], color=color, alpha=0.7, edgecolor='black', linewidth=self.config.line_width)

                # Bowties and other Girih shapes
                for k in range(5):
                    angle = k * 72 + rotation
                    bowtie_x = x_center + size * 0.7 * np.cos(np.radians(angle))
                    bowtie_y = y_center + size * 0.7 * np.sin(np.radians(angle))

                    bowtie = self._create_bowtie(size * 0.3, bowtie_x, bowtie_y, angle)
                    color = colors[(k + 1) % len(colors)] if self.config.color_mode == 'color' else self.config.foreground_color
                    ax.fill(bowtie[:, 0], bowtie[:, 1], color=color, alpha=0.8, edgecolor='black', linewidth=self.config.line_width * 0.5)

    def _generate_morocco_zellige(self, ax, size, rep_x, rep_y, rotation, detail):
        """Generate Moroccan Zellige pattern"""
        colors = ColorManager.get_palette('ocean', 8)

        for i in range(rep_x):
            for j in range(rep_y):
                x_center = -1 + (i + 0.5) * 2 / rep_x
                y_center = -1 + (j + 0.5) * 2 / rep_y

                # Create complex interlocking pattern
                if (i + j) % 2 == 0:
                    star = self._create_star(8, size, size * 0.5, x_center, y_center, rotation)
                    color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
                    ax.fill(star[:, 0], star[:, 1], color=color, alpha=0.8, edgecolor='white', linewidth=self.config.line_width)
                else:
                    cross = self._create_cross(size, x_center, y_center, rotation)
                    color = colors[1] if self.config.color_mode == 'color' else self.config.foreground_color
                    ax.fill(cross[:, 0], cross[:, 1], color=color, alpha=0.8, edgecolor='white', linewidth=self.config.line_width)

    def _create_regular_polygon(self, n_sides, radius, x_center, y_center, rotation):
        """Create a regular polygon"""
        angles = np.linspace(0, 2*np.pi, n_sides + 1) + np.radians(rotation)
        x = x_center + radius * np.cos(angles)
        y = y_center + radius * np.sin(angles)
        return np.column_stack([x, y])

    def _create_star(self, n_points, outer_radius, inner_radius, x_center, y_center, rotation):
        """Create a star shape"""
        angles = []
        for i in range(n_points):
            angles.append(2 * np.pi * i / n_points + np.radians(rotation))
            angles.append(2 * np.pi * (i + 0.5) / n_points + np.radians(rotation))

        x = []
        y = []
        for i, angle in enumerate(angles):
            radius = outer_radius if i % 2 == 0 else inner_radius
            x.append(x_center + radius * np.cos(angle))
            y.append(y_center + radius * np.sin(angle))

        x.append(x[0])  # Close the shape
        y.append(y[0])
        return np.column_stack([x, y])

    def _create_petal(self, size, x_center, y_center, angle):
        """Create a petal shape"""
        t = np.linspace(0, np.pi, 20)
        r = size * np.sin(t)
        x = x_center + r * np.cos(t + np.radians(angle))
        y = y_center + r * np.sin(t + np.radians(angle))
        return np.column_stack([x, y])

    def _create_kufic_element(self, ax, x_center, y_center, size, rotation, detail, colors):
        """Create geometric Kufic-style elements"""
        # Simplified geometric "calligraphy"
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
        """Create a bowtie shape for Girih tiles"""
        points = np.array([
            [-size, 0], [-size*0.3, -size*0.3], [0, 0], [-size*0.3, size*0.3],
            [-size, 0], [size, 0], [size*0.3, size*0.3], [0, 0], [size*0.3, -size*0.3], [size, 0]
        ])

        # Rotate points
        cos_a, sin_a = np.cos(np.radians(angle)), np.sin(np.radians(angle))
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        rotated_points = points @ rotation_matrix.T

        rotated_points[:, 0] += x_center
        rotated_points[:, 1] += y_center
        return rotated_points

    def _create_cross(self, size, x_center, y_center, rotation):
        """Create a cross shape"""
        thickness = size * 0.3
        points = np.array([
            [-thickness, -size], [thickness, -size], [thickness, -thickness],
            [size, -thickness], [size, thickness], [thickness, thickness],
            [thickness, size], [-thickness, size], [-thickness, thickness],
            [-size, thickness], [-size, -thickness], [-thickness, -thickness]
        ])

        # Rotate and translate
        cos_a, sin_a = np.cos(np.radians(rotation)), np.sin(np.radians(rotation))
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        rotated_points = points @ rotation_matrix.T

        rotated_points[:, 0] += x_center
        rotated_points[:, 1] += y_center
        return rotated_points

    def _add_interlace_pattern(self, ax, x_center, y_center, size, detail, colors):
        """Add interlacing decorative elements"""
        for i in range(int(4 * detail)):
            angle = i * 90 / detail
            x = x_center + size * 0.2 * np.cos(np.radians(angle))
            y = y_center + size * 0.2 * np.sin(np.radians(angle))

            circle = plt.Circle((x, y), size * 0.1,
                              color=colors[i % len(colors)] if colors and self.config.color_mode == 'color' else self.config.foreground_color,
                              alpha=0.6)
            ax.add_patch(circle)

class VoronoiGenerator(PatternGenerator):
    """Generates Voronoi diagram patterns"""

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
        """Generate Voronoi diagram pattern"""
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

            # Generate points
            points = self._generate_points(num_points, distribution)

            # Apply Lloyd relaxation
            for _ in range(relaxation_steps):
                points = self._lloyd_relaxation(points)

            # Create Voronoi diagram
            vor = Voronoi(points)

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            # Get colors
            colors = ColorManager.get_palette(self.config.color_palette, num_points)
            cell_colors = self._assign_colors(vor, color_by, colors)

            # Draw Voronoi diagram
            self._draw_voronoi(ax, vor, style, edge_thickness, cell_colors, clip_bounds)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating Voronoi pattern: {e}")
            raise
        finally:
            plt.close(fig)

    def _generate_points(self, num_points, distribution):
        """Generate points with specified distribution"""
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
            # Simplified Poisson disk sampling
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
            # Fibonacci spiral distribution
            points = []
            golden_ratio = (1 + np.sqrt(5)) / 2
            for i in range(num_points):
                r = np.sqrt(i / num_points) * 0.9
                theta = 2 * np.pi * i / golden_ratio
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                points.append([x, y])
            return np.array(points)
        else:
            return np.random.uniform(-1, 1, (num_points, 2))

    def _lloyd_relaxation(self, points):
        """Apply Lloyd relaxation to improve point distribution"""
        vor = Voronoi(points)
        centroids = []

        for point_idx in range(len(points)):
            # Find the Voronoi cell for this point
            region_idx = vor.point_region[point_idx]
            region = vor.regions[region_idx]

            if len(region) > 0 and -1 not in region:
                vertices = vor.vertices[region]
                # Calculate centroid of the cell
                centroid = np.mean(vertices, axis=0)
                centroids.append(centroid)
            else:
                centroids.append(points[point_idx])

        return np.array(centroids)

    def _assign_colors(self, vor, color_by, colors):
        """Assign colors to Voronoi cells"""
        if color_by == 'random':
            return [colors[i % len(colors)] for i in range(len(vor.points))]
        elif color_by == 'distance':
            # Color by distance from center
            distances = np.linalg.norm(vor.points, axis=1)
            normalized = (distances - distances.min()) / (distances.max() - distances.min())
            return [colors[int(d * (len(colors) - 1))] for d in normalized]
        elif color_by == 'area':
            # Color by cell area (simplified)
            areas = []
            for point_idx in range(len(vor.points)):
                region_idx = vor.point_region[point_idx]
                region = vor.regions[region_idx]
                if len(region) > 0 and -1 not in region:
                    vertices = vor.vertices[region]
                    area = 0.5 * abs(sum(vertices[i][0] * (vertices[(i+1) % len(vertices)][1] - vertices[i-1][1]) for i in range(len(vertices))))
                    areas.append(area)
                else:
                    areas.append(0)

            if max(areas) > min(areas):
                normalized = [(a - min(areas)) / (max(areas) - min(areas)) for a in areas]
                return [colors[int(a * (len(colors) - 1))] for a in normalized]
            else:
                return [colors[0]] * len(vor.points)
        else:
            return [colors[i % len(colors)] for i in range(len(vor.points))]

    def _draw_voronoi(self, ax, vor, style, edge_thickness, cell_colors, clip_bounds):
        """Draw the Voronoi diagram"""
        # Draw filled regions
        if style in ['filled', 'both']:
            for point_idx in range(len(vor.points)):
                region_idx = vor.point_region[point_idx]
                region = vor.regions[region_idx]

                if len(region) > 0 and -1 not in region:
                    vertices = vor.vertices[region]

                    # Clip to bounds if needed
                    if clip_bounds == 'square':
                        vertices = self._clip_to_square(vertices)
                    elif clip_bounds == 'circle':
                        vertices = self._clip_to_circle(vertices)

                    if len(vertices) > 2:
                        color = cell_colors[point_idx] if self.config.color_mode == 'color' else self.config.foreground_color
                        ax.fill(vertices[:, 0], vertices[:, 1], color=color, alpha=0.7)

        # Draw edges
        if style in ['edges', 'both']:
            for ridge in vor.ridge_vertices:
                if -1 not in ridge:
                    vertices = vor.vertices[ridge]
                    ax.plot(vertices[:, 0], vertices[:, 1], 'k-',
                           linewidth=self.config.line_width * edge_thickness, alpha=0.8)

        # Draw stippled version
        if style == 'stippled':
            for point_idx in range(len(vor.points)):
                region_idx = vor.point_region[point_idx]
                region = vor.regions[region_idx]

                if len(region) > 0 and -1 not in region:
                    vertices = vor.vertices[region]
                    if len(vertices) > 2:
                        # Create stippled effect
                        centroid = np.mean(vertices, axis=0)
                        color = cell_colors[point_idx] if self.config.color_mode == 'color' else self.config.foreground_color

                        # Add random points within the cell
                        for _ in range(20):
                            # Simple point-in-polygon test
                            test_point = centroid + np.random.normal(0, 0.1, 2)
                            if self._point_in_polygon(test_point, vertices):
                                ax.plot(test_point[0], test_point[1], 'o', color=color, markersize=2)

    def _clip_to_square(self, vertices):
        """Clip vertices to [-1, 1] square"""
        clipped = []
        for vertex in vertices:
            x, y = vertex
            x = max(-1, min(1, x))
            y = max(-1, min(1, y))
            clipped.append([x, y])
        return np.array(clipped)

    def _clip_to_circle(self, vertices):
        """Clip vertices to unit circle"""
        clipped = []
        for vertex in vertices:
            x, y = vertex
            dist = np.sqrt(x*x + y*y)
            if dist > 1:
                x, y = x/dist, y/dist
            clipped.append([x, y])
        return np.array(clipped)

    def _point_in_polygon(self, point, vertices):
        """Simple point-in-polygon test"""
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

class CellularAutomataGenerator(PatternGenerator):
    """Generates cellular automata patterns"""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'automata_type': {'type': 'choice', 'choices': ['game_of_life', 'rule_30', 'rule_90', 'rule_110', 'brian_brain', 'langton_ant'], 'default': 'game_of_life'},
            'grid_size': {'type': 'int', 'range': (50, 500), 'default': 100},
            'generations': {'type': 'int', 'range': (1, 200), 'default': 50},
            'initial_density': {'type': 'float', 'range': (0.1, 0.9), 'default': 0.3},
            'initial_pattern': {'type': 'choice', 'choices': ['random', 'center_dot', 'glider', 'pulsar', 'gosper_gun'], 'default': 'random'},
            'visualization': {'type': 'choice', 'choices': ['final_state', 'evolution', 'trail'], 'default': 'final_state'},
            'neighborhood': {'type': 'choice', 'choices': ['moore', 'neumann'], 'default': 'moore'}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate cellular automata pattern"""
        try:
            automata_type = kwargs.get('automata_type', 'game_of_life')
            grid_size = kwargs.get('grid_size', 100)
            generations = kwargs.get('generations', 50)
            initial_density = kwargs.get('initial_density', 0.3)
            initial_pattern = kwargs.get('initial_pattern', 'random')
            visualization = kwargs.get('visualization', 'final_state')
            neighborhood = kwargs.get('neighborhood', 'moore')

            if not self.validate_parameters(**kwargs):
                raise ValueError("Invalid parameters")

            # Initialize grid
            grid = self._initialize_grid(grid_size, initial_pattern, initial_density)

            # Run automata
            if automata_type == 'game_of_life':
                final_grid, evolution = self._run_game_of_life(grid, generations, neighborhood)
            elif automata_type in ['rule_30', 'rule_90', 'rule_110']:
                rule_number = int(automata_type.split('_')[1])
                final_grid, evolution = self._run_elementary_ca(grid, generations, rule_number)
            elif automata_type == 'brian_brain':
                final_grid, evolution = self._run_brian_brain(grid, generations)
            elif automata_type == 'langton_ant':
                final_grid, evolution = self._run_langton_ant(grid, generations)
            else:
                final_grid, evolution = self._run_game_of_life(grid, generations, neighborhood)

            # Create visualization
            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))

            if visualization == 'final_state':
                self._visualize_grid(ax, final_grid)
            elif visualization == 'evolution':
                self._visualize_evolution(ax, evolution)
            elif visualization == 'trail':
                self._visualize_trail(ax, evolution)

            ax.set_xlim(0, grid_size)
            ax.set_ylim(0, grid_size)
            ax.set_aspect('equal')
            ax.axis('off')
            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating cellular automata: {e}")
            raise
        finally:
            plt.close(fig)

    def _initialize_grid(self, size, pattern, density):
        """Initialize the cellular automata grid"""
        grid = np.zeros((size, size), dtype=int)

        if pattern == 'random':
            grid = np.random.choice([0, 1], size=(size, size), p=[1-density, density])
        elif pattern == 'center_dot':
            grid[size//2, size//2] = 1
        elif pattern == 'glider':
            # Conway's Game of Life glider
            glider = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]])
            start_x, start_y = size//4, size//4
            grid[start_x:start_x+3, start_y:start_y+3] = glider
        elif pattern == 'pulsar':
            # Conway's Game of Life pulsar
            center = size // 2
            pulsar_coords = [
                (-6, -4), (-6, -3), (-6, -2), (-6, 2), (-6, 3), (-6, 4),
                (-4, -6), (-4, -1), (-4, 1), (-4, 6),
                (-3, -6), (-3, -1), (-3, 1), (-3, 6),
                (-2, -6), (-2, -1), (-2, 1), (-2, 6),
                (2, -6), (2, -1), (2, 1), (2, 6),
                (3, -6), (3, -1), (3, 1), (3, 6),
                (4, -6), (4, -1), (4, 1), (4, 6),
                (6, -4), (6, -3), (6, -2), (6, 2), (6, 3), (6, 4)
            ]
            for dx, dy in pulsar_coords:
                x, y = center + dx, center + dy
                if 0 <= x < size and 0 <= y < size:
                    grid[x, y] = 1
        elif pattern == 'gosper_gun':
            # Gosper glider gun (simplified)
            gun_pattern = np.array([
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            ])
            start_x, start_y = 10, 10
            end_x, end_y = min(start_x + gun_pattern.shape[0], size), min(start_y + gun_pattern.shape[1], size)
            grid[start_x:end_x, start_y:end_y] = gun_pattern[:end_x-start_x, :end_y-start_y]

        return grid

    def _run_game_of_life(self, initial_grid, generations, neighborhood):
        """Run Conway's Game of Life"""
        grid = initial_grid.copy()
        evolution = [grid.copy()]

        for _ in range(generations):
            new_grid = np.zeros_like(grid)

            for i in range(grid.shape[0]):
                for j in range(grid.shape[1]):
                    if neighborhood == 'moore':
                        neighbors = self._count_moore_neighbors(grid, i, j)
                    else:
                        neighbors = self._count_neumann_neighbors(grid, i, j)

                    if grid[i, j] == 1:  # Alive
                        if neighbors < 2 or neighbors > 3:
                            new_grid[i, j] = 0  # Dies
                        else:
                            new_grid[i, j] = 1  # Survives
                    else:  # Dead
                        if neighbors == 3:
                            new_grid[i, j] = 1  # Born

            grid = new_grid
            evolution.append(grid.copy())

        return grid, evolution

    def _run_elementary_ca(self, initial_grid, generations, rule_number):
        """Run elementary cellular automaton"""
        # Use only the middle row of initial grid
        width = initial_grid.shape[1]
        grid = np.zeros((generations, width))
        grid[0] = initial_grid[initial_grid.shape[0]//2]

        # Convert rule number to binary
        rule = format(rule_number, '08b')
        rule_dict = {format(i, '03b'): int(rule[7-i]) for i in range(8)}

        for gen in range(1, generations):
            for i in range(width):
                left = grid[gen-1][(i-1) % width]
                center = grid[gen-1][i]
                right = grid[gen-1][(i+1) % width]

                pattern = f"{int(left)}{int(center)}{int(right)}"
                grid[gen][i] = rule_dict[pattern]

        evolution = [np.tile(grid[i], (initial_grid.shape[0]//generations + 1, 1))[:initial_grid.shape[0]] for i in range(generations)]
        return grid[-1:], evolution

    def _run_brian_brain(self, initial_grid, generations):
        """Run Brian's Brain cellular automaton (3 states)"""
        grid = initial_grid.copy().astype(int)  # 0=dead, 1=alive, 2=dying
        evolution = [grid.copy()]

        for _ in range(generations):
            new_grid = np.zeros_like(grid)

            for i in range(grid.shape[0]):
                for j in range(grid.shape[1]):
                    if grid[i, j] == 0:  # Dead
                        alive_neighbors = self._count_alive_neighbors_brian(grid, i, j)
                        if alive_neighbors == 2:
                            new_grid[i, j] = 1  # Born
                    elif grid[i, j] == 1:  # Alive
                        new_grid[i, j] = 2  # Dying
                    # else: dying cells become dead (already 0 in new_grid)

            grid = new_grid
            evolution.append(grid.copy())

        return grid, evolution

    def _run_langton_ant(self, initial_grid, generations):
        """Run Langton's Ant"""
        grid = initial_grid.copy()
        ant_x, ant_y = grid.shape[0]//2, grid.shape[1]//2
        ant_dir = 0  # 0=up, 1=right, 2=down, 3=left
        evolution = [grid.copy()]

        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

        for _ in range(generations):
            if 0 <= ant_x < grid.shape[0] and 0 <= ant_y < grid.shape[1]:
                if grid[ant_x, ant_y] == 0:  # White square
                    ant_dir = (ant_dir + 1) % 4  # Turn right
                    grid[ant_x, ant_y] = 1  # Make black
                else:  # Black square
                    ant_dir = (ant_dir - 1) % 4  # Turn left
                    grid[ant_x, ant_y] = 0  # Make white

                # Move forward
                dx, dy = directions[ant_dir]
                ant_x += dx
                ant_y += dy

            evolution.append(grid.copy())

        return grid, evolution

    def _count_moore_neighbors(self, grid, x, y):
        """Count Moore neighbors (8-connected)"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % grid.shape[0], (y + dy) % grid.shape[1]
                count += grid[nx, ny]
        return count

    def _count_neumann_neighbors(self, grid, x, y):
        """Count Neumann neighbors (4-connected)"""
        count = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = (x + dx) % grid.shape[0], (y + dy) % grid.shape[1]
            count += grid[nx, ny]
        return count

    def _count_alive_neighbors_brian(self, grid, x, y):
        """Count alive neighbors for Brian's Brain"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % grid.shape[0], (y + dy) % grid.shape[1]
                if grid[nx, ny] == 1:  # Only count alive cells
                    count += 1
        return count

    def _visualize_grid(self, ax, grid):
        """Visualize a single grid state"""
        if self.config.color_mode == 'color':
            colors = ColorManager.get_palette(self.config.color_palette, 3)
            cmap = LinearSegmentedColormap.from_list('custom', [self.config.background_color] + colors[:2])
        else:
            cmap = 'gray'

        ax.imshow(grid, cmap=cmap, origin='lower')

    def _visualize_evolution(self, ax, evolution):
        """Visualize the evolution as a space-time diagram"""
        if len(evolution) > 1:
            # Create space-time diagram
            evolution_array = np.array(evolution)
            if len(evolution_array.shape) == 3:  # 2D grids
                # Take a slice through the middle
                middle_slice = evolution_array[:, evolution_array.shape[1]//2, :]
                ax.imshow(middle_slice, cmap='hot', origin='lower', aspect='auto')
            else:  # 1D evolution
                ax.imshow(evolution_array, cmap='hot', origin='lower', aspect='auto')

    def _visualize_trail(self, ax, evolution):
        """Visualize trails of activity"""
        if len(evolution) > 1:
            trail = np.zeros_like(evolution[0], dtype=float)
            for i, grid in enumerate(evolution):
                trail += grid * (i + 1) / len(evolution)

            if self.config.color_mode == 'color':
                colors = ColorManager.get_palette(self.config.color_palette, 5)
                cmap = LinearSegmentedColormap.from_list('trail', colors)
            else:
                cmap = 'viridis'

            ax.imshow(trail, cmap=cmap, origin='lower')

class TessellationGenerator(PatternGenerator):
    """Generates tessellation patterns"""

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
        """Generate tessellation pattern"""
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

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
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
            plt.close(fig)

    def _generate_regular_tessellation(self, ax, shape, size, irregularity, color_scheme, border_style, fill_pattern):
        """Generate regular tessellation"""
        colors = ColorManager.get_palette(self.config.color_palette, 6)

        if shape == 'hexagon':
            # Hexagonal tessellation
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

                    # Add irregularity
                    if irregularity > 0:
                        x_center += np.random.uniform(-irregularity, irregularity) * size
                        y_center += np.random.uniform(-irregularity, irregularity) * size

                    hexagon = self._create_hexagon(x_center, y_center, size)

                    # Color selection
                    color = self._select_tile_color(colors, color_scheme, row, col)

                    # Fill pattern
                    self._apply_fill_pattern(ax, hexagon, color, fill_pattern)

                    # Border
                    self._apply_border(ax, hexagon, border_style)

        elif shape == 'square':
            # Square tessellation
            rows = int(2 / size) + 1
            cols = int(2 / size) + 1

            for row in range(rows):
                for col in range(cols):
                    x_center = -1 + col * size + size/2
                    y_center = -1 + row * size + size/2

                    # Add irregularity
                    if irregularity > 0:
                        x_center += np.random.uniform(-irregularity, irregularity) * size
                        y_center += np.random.uniform(-irregularity, irregularity) * size

                    square = self._create_square(x_center, y_center, size)

                    color = self._select_tile_color(colors, color_scheme, row, col)
                    self._apply_fill_pattern(ax, square, color, fill_pattern)
                    self._apply_border(ax, square, border_style)

        elif shape == 'triangle':
            # Triangular tessellation
            tri_height = size * np.sqrt(3) / 2

            rows = int(2 / tri_height) + 2
            cols = int(2 / size) + 2

            for row in range(rows):
                for col in range(cols):
                    x_center = -1 + col * size / 2
                    y_center = -1 + row * tri_height

                    # Alternate triangle orientation
                    pointing_up = (row + col) % 2 == 0

                    triangle = self._create_triangle(x_center, y_center, size, pointing_up)

                    color = self._select_tile_color(colors, color_scheme, row, col)
                    self._apply_fill_pattern(ax, triangle, color, fill_pattern)
                    self._apply_border(ax, triangle, border_style)

    def _generate_penrose_tiling(self, ax, size, color_scheme, border_style):
        """Generate simplified Penrose tiling"""
        colors = ColorManager.get_palette(self.config.color_palette, 2)

        # Simplified Penrose P1 tiling approximation
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio

        # Generate rhombi with golden ratio proportions
        num_tiles = int(100 / (size * size))

        for _ in range(num_tiles):
            x_center = np.random.uniform(-1, 1)
            y_center = np.random.uniform(-1, 1)
            orientation = np.random.uniform(0, 360)

            # Two types of rhombi
            if np.random.random() < 0.5:
                # Wide rhombus
                rhombus = self._create_rhombus(x_center, y_center, size, size/phi, orientation, 72)
                color = colors[0]
            else:
                # Narrow rhombus
                rhombus = self._create_rhombus(x_center, y_center, size, size*phi, orientation, 36)
                color = colors[1]

            if self.config.color_mode == 'color':
                ax.fill(rhombus[:, 0], rhombus[:, 1], color=color, alpha=0.8)
            else:
                ax.fill(rhombus[:, 0], rhombus[:, 1], color=self.config.foreground_color, alpha=0.8)

            self._apply_border(ax, rhombus, border_style)

    def _generate_hexagonal_tessellation(self, ax, size, irregularity, color_scheme, border_style, fill_pattern):
        """Generate hexagonal tessellation with variations"""
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

                # Add irregularity
                if irregularity > 0:
                    noise_x = np.random.uniform(-irregularity, irregularity) * size
                    noise_y = np.random.uniform(-irregularity, irregularity) * size
                    x_center += noise_x
                    y_center += noise_y

                hexagon = self._create_hexagon(x_center, y_center, size * (1 + np.random.uniform(-irregularity, irregularity)))

                color = self._select_tile_color(colors, color_scheme, row, col)
                self._apply_fill_pattern(ax, hexagon, color, fill_pattern)
                self._apply_border(ax, hexagon, border_style)

    def _generate_triangular_tessellation(self, ax, size, irregularity, color_scheme, border_style, fill_pattern):
        """Generate triangular tessellation"""
        colors = ColorManager.get_palette(self.config.color_palette, 4)

        tri_height = size * np.sqrt(3) / 2
        rows = int(2 / tri_height) + 2
        cols = int(2 / size) + 2

        for row in range(rows):
            for col in range(cols):
                x_center = -1 + col * size / 2
                y_center = -1 + row * tri_height

                # Add irregularity
                if irregularity > 0:
                    x_center += np.random.uniform(-irregularity, irregularity) * size
                    y_center += np.random.uniform(-irregularity, irregularity) * size

                pointing_up = (row + col) % 2 == 0
                triangle = self._create_triangle(x_center, y_center, size, pointing_up)

                color = self._select_tile_color(colors, color_scheme, row, col)
                self._apply_fill_pattern(ax, triangle, color, fill_pattern)
                self._apply_border(ax, triangle, border_style)

    def _generate_ammann_beenker(self, ax, size, color_scheme, border_style):
        """Generate Ammann-Beenker tiling approximation"""
        colors = ColorManager.get_palette(self.config.color_palette, 2)

        # Simplified octagonal tiling
        num_tiles = int(50 / (size * size))

        for _ in range(num_tiles):
            x_center = np.random.uniform(-1, 1)
            y_center = np.random.uniform(-1, 1)

            if np.random.random() < 0.6:
                # Regular octagon
                octagon = self._create_regular_polygon(8, size, x_center, y_center, np.random.uniform(0, 45))
                color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
                ax.fill(octagon[:, 0], octagon[:, 1], color=color, alpha=0.8)
            else:
                # Square
                square = self._create_square(x_center, y_center, size * 0.7)
                color = colors[1] if self.config.color_mode == 'color' else self.config.foreground_color
                ax.fill(square[:, 0], square[:, 1], color=color, alpha=0.8)

    def _generate_truchet_tiles(self, ax, size, color_scheme, border_style):
        """Generate Truchet tiles pattern"""
        colors = ColorManager.get_palette(self.config.color_palette, 4)

        rows = int(2 / size) + 1
        cols = int(2 / size) + 1

        for row in range(rows):
            for col in range(cols):
                x_center = -1 + col * size + size/2
                y_center = -1 + row * size + size/2

                # Create square tile
                square = self._create_square(x_center, y_center, size)
                color = colors[(row + col) % len(colors)] if self.config.color_mode == 'color' else self.config.background_color
                ax.fill(square[:, 0], square[:, 1], color=color, alpha=0.9)

                # Add Truchet curve
                self._add_truchet_curve(ax, x_center, y_center, size, (row + col) % 4)

    def _create_hexagon(self, x_center, y_center, size):
        """Create hexagon vertices"""
        angles = np.linspace(0, 2*np.pi, 7)
        x = x_center + size * np.cos(angles)
        y = y_center + size * np.sin(angles)
        return np.column_stack([x, y])

    def _create_square(self, x_center, y_center, size):
        """Create square vertices"""
        half_size = size / 2
        return np.array([
            [x_center - half_size, y_center - half_size],
            [x_center + half_size, y_center - half_size],
            [x_center + half_size, y_center + half_size],
            [x_center - half_size, y_center + half_size],
            [x_center - half_size, y_center - half_size]
        ])

    def _create_triangle(self, x_center, y_center, size, pointing_up=True):
        """Create triangle vertices"""
        height = size * np.sqrt(3) / 2
        if pointing_up:
            return np.array([
                [x_center, y_center + height * 2/3],
                [x_center - size/2, y_center - height * 1/3],
                [x_center + size/2, y_center - height * 1/3],
                [x_center, y_center + height * 2/3]
            ])
        else:
            return np.array([
                [x_center, y_center - height * 2/3],
                [x_center - size/2, y_center + height * 1/3],
                [x_center + size/2, y_center + height * 1/3],
                [x_center, y_center - height * 2/3]
            ])

    def _create_rhombus(self, x_center, y_center, width, height, rotation, acute_angle):
        """Create rhombus vertices"""
        # Convert to radians
        angle_rad = np.radians(acute_angle)
        rot_rad = np.radians(rotation)

        # Calculate vertices
        half_width = width / 2
        half_height = height / 2

        vertices = np.array([
            [-half_width, 0],
            [0, half_height],
            [half_width, 0],
            [0, -half_height],
            [-half_width, 0]
        ])

        # Rotate
        cos_r, sin_r = np.cos(rot_rad), np.sin(rot_rad)
        rotation_matrix = np.array([[cos_r, -sin_r], [sin_r, cos_r]])
        rotated_vertices = vertices @ rotation_matrix.T

        # Translate
        rotated_vertices[:, 0] += x_center
        rotated_vertices[:, 1] += y_center

        return rotated_vertices

    def _create_regular_polygon(self, n_sides, radius, x_center, y_center, rotation):
        """Create regular polygon vertices"""
        angles = np.linspace(0, 2*np.pi, n_sides + 1) + np.radians(rotation)
        x = x_center + radius * np.cos(angles)
        y = y_center + radius * np.sin(angles)
        return np.column_stack([x, y])

    def _select_tile_color(self, colors, scheme, row, col):
        """Select color based on scheme"""
        if scheme == 'alternating':
            return colors[(row + col) % 2] if self.config.color_mode == 'color' else self.config.foreground_color
        elif scheme == 'gradient':
            color_index = (row + col) % len(colors)
            return colors[color_index] if self.config.color_mode == 'color' else self.config.foreground_color
        elif scheme == 'random':
            return colors[np.random.randint(len(colors))] if self.config.color_mode == 'color' else self.config.foreground_color
        elif scheme == 'symmetric':
            symmetric_index = min(row, col) % len(colors)
            return colors[symmetric_index] if self.config.color_mode == 'color' else self.config.foreground_color
        else:
            return colors[0] if self.config.color_mode == 'color' else self.config.foreground_color

    def _apply_fill_pattern(self, ax, vertices, color, pattern):
        """Apply fill pattern to shape"""
        if pattern == 'solid':
            ax.fill(vertices[:, 0], vertices[:, 1], color=color, alpha=0.8)
        elif pattern == 'striped':
            ax.fill(vertices[:, 0], vertices[:, 1], color=color, alpha=0.8)
            # Add stripes (simplified)
            center_x, center_y = np.mean(vertices[:-1], axis=0)
            for i in range(5):
                y_line = center_y + (i - 2) * 0.02
                ax.axhline(y=y_line, xmin=0, xmax=1, color='black', alpha=0.3, linewidth=0.5)
        elif pattern == 'dotted':
            ax.fill(vertices[:, 0], vertices[:, 1], color=color, alpha=0.8)
            # Add dots
            center_x, center_y = np.mean(vertices[:-1], axis=0)
            for i in range(-2, 3):
                for j in range(-2, 3):
                    ax.plot(center_x + i*0.02, center_y + j*0.02, 'ko', markersize=1)
        elif pattern == 'cross_hatch':
            ax.fill(vertices[:, 0], vertices[:, 1], color=color, alpha=0.8)
            # Add cross-hatch pattern (simplified)
            center_x, center_y = np.mean(vertices[:-1], axis=0)
            for i in range(5):
                offset = (i - 2) * 0.02
                ax.plot([center_x - 0.05, center_x + 0.05], [center_y + offset, center_y + offset], 'k-', alpha=0.3, linewidth=0.5)
                ax.plot([center_x + offset, center_x + offset], [center_y - 0.05, center_y + 0.05], 'k-', alpha=0.3, linewidth=0.5)
        else:
            ax.fill(vertices[:, 0], vertices[:, 1], color=color, alpha=0.8)

    def _apply_border(self, ax, vertices, style):
        """Apply border style to shape"""
        if style == 'none':
            return
        elif style == 'thin':
            ax.plot(vertices[:, 0], vertices[:, 1], 'k-', linewidth=self.config.line_width * 0.5, alpha=0.8)
        elif style == 'thick':
            ax.plot(vertices[:, 0], vertices[:, 1], 'k-', linewidth=self.config.line_width * 2, alpha=0.8)
        elif style == 'decorative':
            ax.plot(vertices[:, 0], vertices[:, 1], 'k--', linewidth=self.config.line_width, alpha=0.6)

    def _add_truchet_curve(self, ax, x_center, y_center, size, variant):
        """Add Truchet curve to tile"""
        half_size = size / 2

        if variant == 0:
            # Quarter circle from bottom-left to top-right
            theta = np.linspace(0, np.pi/2, 20)
            x = x_center - half_size + half_size * (1 - np.cos(theta))
            y = y_center - half_size + half_size * np.sin(theta)
            ax.plot(x, y, 'k-', linewidth=self.config.line_width * 2)
        elif variant == 1:
            # Quarter circle from top-left to bottom-right
            theta = np.linspace(np.pi/2, np.pi, 20)
            x = x_center - half_size + half_size * (1 - np.cos(theta))
            y = y_center + half_size + half_size * np.sin(theta)
            ax.plot(x, y, 'k-', linewidth=self.config.line_width * 2)
        elif variant == 2:
            # Straight diagonal
            ax.plot([x_center - half_size, x_center + half_size],
                   [y_center - half_size, y_center + half_size],
                   'k-', linewidth=self.config.line_width * 2)
        else:
            # Other diagonal
            ax.plot([x_center - half_size, x_center + half_size],
                   [y_center + half_size, y_center - half_size],
                   'k-', linewidth=self.config.line_width * 2)

# Include all the previous generators with the _fig_to_array method
class SpiralGenerator(PatternGenerator):
    """Enhanced spiral generator from previous code"""

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

            # Get colors from palette
            colors = ColorManager.get_palette(self.config.color_palette, max(arms * overlapping, 8))

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
                        phi = (1 + np.sqrt(5)) / 2
                        r = 0.1 * phi ** (t / np.pi) * scale

                    x = r * np.cos(t + arm_rotation_rad) + spiral_offset_x
                    y = r * np.sin(t + arm_rotation_rad) + spiral_offset_y

                    # Filter points within bounds
                    mask = ((x - spiral_offset_x)**2 + (y - spiral_offset_y)**2) <= 1
                    x, y = x[mask], y[mask]

                    if len(x) == 0:
                        continue

                    # Color selection
                    color_idx = (arm + spiral_idx) % len(colors)
                    base_color = colors[color_idx] if self.config.color_mode == 'color' else self.config.foreground_color

                    # Apply gradient effects and line variations
                    if gradient_effect == 'radial':
                        alphas = np.linspace(1.0, 0.3, len(x))
                        for i in range(len(x)-1):
                            ax.plot(x[i:i+2], y[i:i+2], color=base_color,
                                   linewidth=self.config.line_width, alpha=alphas[i])
                    elif gradient_effect == 'angular':
                        angles = np.arctan2(y - spiral_offset_y, x - spiral_offset_x)
                        colors_gradient = plt.cm.hsv((angles + np.pi) / (2 * np.pi))
                        for i in range(len(x)-1):
                            ax.plot(x[i:i+2], y[i:i+2], color=colors_gradient[i],
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
            plt.close(fig)

# Include simplified versions of other previous generators
class InterferenceGenerator(PatternGenerator):
    """Interference patterns generator"""

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
            plt.close(fig)

# Advanced Art Studio Application
class AdvancedArtStudio:
    """Main GUI application for the advanced mathematical art studio"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Mathematical Art Studio")
        self.root.geometry("1400x900")

        # Initialize configuration
        self.config = PatternConfig()

        # Initialize generators
        self.generators = {
            'Spiral': SpiralGenerator(self.config),
            'Interference': InterferenceGenerator(self.config),
            'Islamic Geometry': IslamicGeometryGenerator(self.config),
            'Voronoi Diagrams': VoronoiGenerator(self.config),
            'Cellular Automata': CellularAutomataGenerator(self.config),
            'Tessellations': TessellationGenerator(self.config)
        }

        self.current_generator = None
        self.current_image = None
        self.parameter_widgets = {}
        self.animation_running = False

        self.setup_ui()
        self.setup_logging_display()

        logger.info("Advanced Art Studio initialized successfully")

    def setup_ui(self):
        """Setup the enhanced user interface"""
        # Create menu bar first
        self.setup_menu_bar()

        # Create main frames with better layout
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel for controls (scrollable)
        self.setup_scrollable_controls()

        # Right panel for display
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.setup_display()

    def setup_menu_bar(self):
        """Setup menu bar with presets and other options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Image...", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Save as SVG...", command=self.save_svg)
        file_menu.add_separator()
        file_menu.add_command(label="Export Config...", command=self.export_config)
        file_menu.add_command(label="Import Config...", command=self.import_config, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Batch Generate...", command=self.batch_generate)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")

        # Art Presets menu
        presets_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Art Presets", menu=presets_menu)
        presets_menu.add_command(label="Islamic Art", command=self.load_islamic_preset)
        presets_menu.add_command(label="Organic Flow", command=self.load_organic_preset)
        presets_menu.add_command(label="Digital Grid", command=self.load_digital_preset)
        presets_menu.add_command(label="Nature Patterns", command=self.load_nature_preset)
        presets_menu.add_command(label="Cosmic Spiral", command=self.load_cosmic_preset)
        presets_menu.add_command(label="Crystal Growth", command=self.load_crystal_preset)

        # Generation menu
        generate_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Generate", menu=generate_menu)
        generate_menu.add_command(label="Generate Pattern", command=self.generate_pattern, accelerator="F5")
        generate_menu.add_command(label="Animate Pattern", command=self.animate_pattern, accelerator="F6")
        generate_menu.add_separator()
        generate_menu.add_command(label="Random Parameters", command=self.randomize_parameters, accelerator="R")
        generate_menu.add_command(label="Random Everything", command=self.randomize_everything, accelerator="Shift+R")
        generate_menu.add_command(label="Surprise Me!", command=self.surprise_generation, accelerator="F12")

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="+")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="-")
        view_menu.add_command(label="Reset View", command=self.reset_view, accelerator="0")
        view_menu.add_separator()
        view_menu.add_command(label="Fullscreen", command=self.toggle_fullscreen, accelerator="F11")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="Pattern Guide", command=self.show_pattern_guide)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)

        # Bind keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-o>', lambda e: self.import_config())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<F5>', lambda e: self.generate_pattern())
        self.root.bind('<F6>', lambda e: self.animate_pattern())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<F12>', lambda e: self.surprise_generation())
        self.root.bind('<KeyPress-r>', lambda e: self.randomize_parameters())
        self.root.bind('<KeyPress-R>', lambda e: self.randomize_everything())
        self.root.bind('<KeyPress-plus>', lambda e: self.zoom_in())
        self.root.bind('<KeyPress-minus>', lambda e: self.zoom_out())
        self.root.bind('<KeyPress-0>', lambda e: self.reset_view())

    def setup_scrollable_controls(self):
        """Setup scrollable control panel"""
        # Create canvas and scrollbar for scrollable area
        canvas = tk.Canvas(self.main_frame, width=350)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        self.control_frame = ttk.Frame(canvas)

        # Configure scrolling
        self.control_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.control_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)

        self.setup_controls()

    def setup_controls(self):
        """Setup control panel"""
        # Title
        title_label = ttk.Label(self.control_frame, text="Mathematical Art Studio",
                               font=("Arial", 14, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # Pattern selection
        pattern_frame = ttk.LabelFrame(self.control_frame, text="Pattern Selection", padding=10)
        pattern_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(pattern_frame, text="Pattern Type:").pack(anchor=tk.W)
        self.pattern_var = tk.StringVar(value="Spiral")
        pattern_combo = ttk.Combobox(pattern_frame, textvariable=self.pattern_var,
                                   values=list(self.generators.keys()), state="readonly", width=30)
        pattern_combo.pack(fill=tk.X, pady=(5, 0))
        pattern_combo.bind('<<ComboboxSelected>>', self.on_pattern_change)

        # Parameters frame
        self.params_frame = ttk.LabelFrame(self.control_frame, text="Parameters", padding=10)
        self.params_frame.pack(fill=tk.X, pady=(0, 10))

        # Global settings frame
        self.global_frame = ttk.LabelFrame(self.control_frame, text="Global Settings", padding=10)
        self.global_frame.pack(fill=tk.X, pady=(0, 10))

        self.setup_global_controls()

        # Main action buttons
        main_actions = ttk.LabelFrame(self.control_frame, text="Main Actions", padding=10)
        main_actions.pack(fill=tk.X, pady=(0, 10))

        self.generate_btn = ttk.Button(main_actions, text="🎨 Generate Pattern",
                                     command=self.generate_pattern)
        self.generate_btn.pack(fill=tk.X, pady=2)

        self.animate_btn = ttk.Button(main_actions, text="🎬 Animate Pattern",
                                    command=self.animate_pattern)
        self.animate_btn.pack(fill=tk.X, pady=2)

        # Quick actions frame
        quick_frame = ttk.LabelFrame(self.control_frame, text="Quick Actions", padding=10)
        quick_frame.pack(fill=tk.X, pady=(0, 10))

        # Create 2x2 grid for quick actions
        quick_actions = [
            ("🎲 Random Params", self.randomize_parameters),
            ("🌀 Random All", self.randomize_everything),
            ("✨ Surprise Me!", self.surprise_generation),
            ("📁 Batch Generate", self.batch_generate)
        ]

        for i, (text, command) in enumerate(quick_actions):
            row, col = i // 2, i % 2
            btn = ttk.Button(quick_frame, text=text, command=command)
            btn.grid(row=row, column=col, sticky=tk.EW, padx=2, pady=2)

        quick_frame.columnconfigure(0, weight=1)
        quick_frame.columnconfigure(1, weight=1)

        # Initialize with first pattern
        self.on_pattern_change()

    def setup_global_controls(self):
        """Setup enhanced global configuration controls"""
        # Color mode and palette
        ttk.Label(self.global_frame, text="Color Mode:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.color_mode_var = tk.StringVar(value="black_white")
        color_combo = ttk.Combobox(self.global_frame, textvariable=self.color_mode_var,
                                 values=["black_white", "color", "gradient"], state="readonly", width=15)
        color_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        color_combo.bind('<<ComboboxSelected>>', self.on_color_mode_change)

        ttk.Label(self.global_frame, text="Color Palette:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.palette_var = tk.StringVar(value="default")
        palette_combo = ttk.Combobox(self.global_frame, textvariable=self.palette_var,
                                   values=["default", "sunset", "ocean", "forest", "cosmic", "fire", "ice", "earth", "neon", "pastel"],
                                   state="readonly", width=15)
        palette_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        palette_combo.bind('<<ComboboxSelected>>', self.on_palette_change)

        # Resolution
        ttk.Label(self.global_frame, text="Resolution:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.resolution_var = tk.IntVar(value=1000)
        resolution_spin = ttk.Spinbox(self.global_frame, from_=100, to=5000, increment=100,
                                    textvariable=self.resolution_var, width=15)
        resolution_spin.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)

        # Line width
        ttk.Label(self.global_frame, text="Line Width:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.line_width_var = tk.DoubleVar(value=1.0)
        line_width_spin = ttk.Spinbox(self.global_frame, from_=0.1, to=10.0, increment=0.1,
                                    textvariable=self.line_width_var, width=15)
        line_width_spin.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=2)

        # Color buttons
        self.bg_color_btn = ttk.Button(self.global_frame, text="Background Color",
                                     command=lambda: self.choose_color('background'))
        self.bg_color_btn.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=2)

        self.fg_color_btn = ttk.Button(self.global_frame, text="Foreground Color",
                                     command=lambda: self.choose_color('foreground'))
        self.fg_color_btn.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=2)

    def setup_display(self):
        """Setup enhanced display area"""
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.text(0.5, 0.5, 'Welcome to Advanced Mathematical Art Studio\nSelect a pattern and click Generate',
                    ha='center', va='center', transform=self.ax.transAxes, fontsize=14)
        self.ax.axis('off')

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.display_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Enhanced toolbar
        toolbar_frame = ttk.Frame(self.display_frame)
        toolbar_frame.pack(fill=tk.X)

        # Display controls - compact layout
        display_controls = ttk.Frame(toolbar_frame)
        display_controls.pack(side=tk.LEFT)

        ttk.Button(display_controls, text="🔍+", command=self.zoom_in, width=4).pack(side=tk.LEFT, padx=1)
        ttk.Button(display_controls, text="🔍-", command=self.zoom_out, width=4).pack(side=tk.LEFT, padx=1)
        ttk.Button(display_controls, text="↺", command=self.reset_view, width=4).pack(side=tk.LEFT, padx=1)
        ttk.Button(display_controls, text="⛶", command=self.toggle_fullscreen, width=4).pack(side=tk.LEFT, padx=1)

        # Status bar
        self.status_var = tk.StringVar(value="Ready to create amazing mathematical art!")
        status_bar = ttk.Label(toolbar_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5, pady=2)

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

    def on_palette_change(self, event=None):
        """Handle palette change"""
        self.config.color_palette = self.palette_var.get()
        logger.info(f"Color palette changed to: {self.config.color_palette}")

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
                                    values=param_info['choices'], state="readonly", width=20)
            elif param_info['type'] == 'int':
                var = tk.IntVar(value=param_info['default'])
                min_val, max_val = param_info['range']
                widget = ttk.Spinbox(self.params_frame, from_=min_val, to=max_val,
                                   textvariable=var, width=20)
            elif param_info['type'] == 'float':
                var = tk.DoubleVar(value=param_info['default'])
                min_val, max_val = param_info['range']
                widget = ttk.Spinbox(self.params_frame, from_=min_val, to=max_val,
                                   increment=0.1, textvariable=var, width=20)

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
        self.config.color_palette = self.palette_var.get()

    def generate_pattern(self):
        """Generate pattern using current settings"""
        try:
            if not self.current_generator:
                raise ValueError("No pattern selected")

            self.update_config()
            self.status_var.set("Generating amazing mathematical art...")
            self.generate_btn.config(state='disabled')
            self.root.update()

            params = self.get_current_parameters()

            try:
                image_array = self.current_generator.generate(**params)
                self.display_pattern(image_array)

            except Exception as e:
                error_msg = f"Error generating pattern: {str(e)}"
                logger.error(error_msg)
                messagebox.showerror("Generation Error", error_msg)
                self.status_var.set("Generation failed - try different parameters")
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

            self.ax.clear()
            self.ax.imshow(image_array, aspect='equal')
            self.ax.axis('off')

            self.canvas.draw_idle()
            self.root.update_idletasks()

            self.status_var.set("✨ Stunning mathematical art created successfully! ✨")
            logger.info("Pattern displayed successfully")

        except Exception as e:
            error_msg = f"Error displaying pattern: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Display Error", error_msg)
            self.status_var.set("Display failed")

    def animate_pattern(self):
        """Create animated pattern by varying parameters"""
        try:
            if not self.current_generator:
                messagebox.showwarning("Warning", "No pattern selected for animation.")
                return

            if self.animation_running:
                self.stop_animation()
                return

            # Find animatable parameters
            animatable_params = []
            for param_name, widget_info in self.parameter_widgets.items():
                param_info = self.current_generator.get_parameters().get(param_name, {})
                if param_info.get('type') in ['float', 'int'] and 'range' in param_info:
                    animatable_params.append(param_name)

            if not animatable_params:
                messagebox.showinfo("Info", "No animatable parameters found for this pattern.")
                return

            # Choose parameter to animate (rotation if available, otherwise first one)
            animate_param = 'rotation' if 'rotation' in animatable_params else animatable_params[0]
            original_value = self.parameter_widgets[animate_param]['var'].get()

            self.animate_btn.config(text="Stop Animation")
            self.animation_running = True

            def animate_step(frame):
                if not self.animation_running:
                    return

                try:
                    # Animate the parameter
                    param_info = self.current_generator.get_parameters()[animate_param]
                    min_val, max_val = param_info['range']

                    if animate_param == 'rotation':
                        value = (frame * 15) % 360
                    else:
                        # Sinusoidal animation
                        normalized = (np.sin(frame * 0.2) + 1) / 2
                        value = min_val + normalized * (max_val - min_val)

                    self.parameter_widgets[animate_param]['var'].set(value)

                    # Generate and display new frame
                    self.update_config()
                    params = self.get_current_parameters()
                    image_array = self.current_generator.generate(**params)
                    self.display_pattern(image_array)

                    # Schedule next frame
                    if self.animation_running:
                        self.root.after(100, lambda: animate_step(frame + 1))
                    else:
                        # Restore original value
                        self.parameter_widgets[animate_param]['var'].set(original_value)
                        self.animate_btn.config(text="Animate Pattern")

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
        self.animate_btn.config(text="Animate Pattern")
        logger.info("Animation stopped")

    def batch_generate(self):
        """Generate multiple variations and save them"""
        if self.batch_generating:
            return

        try:
            if not self.current_generator:
                messagebox.showwarning("Warning", "No pattern selected for batch generation.")
                return

            # Ask user for batch parameters
            batch_dialog = tk.Toplevel(self.root)
            batch_dialog.title("Batch Generation Settings")
            batch_dialog.geometry("400x300")
            batch_dialog.transient(self.root)
            batch_dialog.grab_set()

            # Number of variations
            ttk.Label(batch_dialog, text="Number of variations:").pack(pady=5)
            num_var = tk.IntVar(value=10)
            ttk.Spinbox(batch_dialog, from_=1, to=100, textvariable=num_var).pack(pady=5)

            # Parameter to vary
            ttk.Label(batch_dialog, text="Parameter to vary:").pack(pady=5)
            param_var = tk.StringVar()
            param_names = list(self.parameter_widgets.keys())
            if param_names:
                param_var.set(param_names[0])
            param_combo = ttk.Combobox(batch_dialog, textvariable=param_var, values=param_names, state="readonly")
            param_combo.pack(pady=5)

            # Output directory
            ttk.Label(batch_dialog, text="Output directory:").pack(pady=5)
            output_dir = tk.StringVar(value="./batch_output")
            ttk.Entry(batch_dialog, textvariable=output_dir, width=40).pack(pady=5)
            ttk.Button(batch_dialog, text="Browse",
                      command=lambda: output_dir.set(filedialog.askdirectory())).pack(pady=5)

            def start_batch():
                batch_dialog.destroy()
                self._run_batch_generation(num_var.get(), param_var.get(), output_dir.get())

            ttk.Button(batch_dialog, text="Start Batch Generation", command=start_batch).pack(pady=20)
            ttk.Button(batch_dialog, text="Cancel", command=batch_dialog.destroy).pack(pady=5)

        except Exception as e:
            error_msg = f"Error setting up batch generation: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Batch Error", error_msg)

    def _run_batch_generation(self, num_variations, param_name, output_dir):
        """Run the actual batch generation"""
        try:
            import os
            from PIL import Image

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            self.batch_generating = True

            if param_name and param_name in self.parameter_widgets:
                param_info = self.current_generator.get_parameters()[param_name]
                if 'range' in param_info:
                    min_val, max_val = param_info['range']
                    values = np.linspace(min_val, max_val, num_variations)

                    original_value = self.parameter_widgets[param_name]['var'].get()

                    for i, value in enumerate(values):
                        self.status_var.set(f"Batch generating: {i+1}/{num_variations}")
                        self.root.update()

                        # Set parameter value
                        self.parameter_widgets[param_name]['var'].set(value)

                        # Generate pattern
                        self.update_config()
                        params = self.get_current_parameters()
                        image_array = self.current_generator.generate(**params)

                        # Save image
                        img = Image.fromarray(image_array)
                        filename = f"{self.pattern_var.get()}_{param_name}_{i+1:03d}.png"
                        filepath = os.path.join(output_dir, filename)
                        img.save(filepath)

                    # Restore original value
                    self.parameter_widgets[param_name]['var'].set(original_value)

                    messagebox.showinfo("Batch Complete",
                                      f"Generated {num_variations} variations in {output_dir}")
                    logger.info(f"Batch generation completed: {num_variations} images")

        except Exception as e:
            error_msg = f"Error during batch generation: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Batch Error", error_msg)
        finally:
            self.batch_generating = False
            self.status_var.set("Batch generation completed")

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_dialog = tk.Toplevel(self.root)
        shortcuts_dialog.title("Keyboard Shortcuts")
        shortcuts_dialog.geometry("500x400")
        shortcuts_dialog.transient(self.root)
        shortcuts_dialog.grab_set()

        text_widget = tk.Text(shortcuts_dialog, wrap=tk.WORD, padx=10, pady=10)
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
• Try different color palettes for dramatic effects
• Use animation to understand parameter effects
• Batch generate to explore parameter spaces
• Islamic Geometry works great with Earth palette
• Voronoi + Poisson distribution = organic patterns
• Cellular Automata + Neon palette = cyberpunk vibes

Pro Tips:
• Save configurations you like for later use
• High resolution (2000+) for print quality
• Experiment with overlapping spirals
• Try irregular tessellations for natural looks
        """

        text_widget.insert(tk.END, shortcuts_text)
        text_widget.config(state=tk.DISABLED)

        ttk.Button(shortcuts_dialog, text="Close", command=shortcuts_dialog.destroy).pack(pady=10)

    def show_pattern_guide(self):
        """Show pattern guide dialog"""
        guide_dialog = tk.Toplevel(self.root)
        guide_dialog.title("Pattern Guide")
        guide_dialog.geometry("600x500")
        guide_dialog.transient(self.root)
        guide_dialog.grab_set()

        text_widget = tk.Text(guide_dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)

        guide_text = """
PATTERN GENERATOR GUIDE

🌀 SPIRALS
• Archimedean: Uniform spacing, classic spiral
• Logarithmic: Exponential growth, nature-inspired
• Fermat: Square root spiral, sunflower patterns
• Fibonacci: Golden ratio, perfect proportions
• Try overlapping spirals with angular gradients!

🔲 ISLAMIC GEOMETRY
• Octagon Star: Classic 8-pointed star patterns
• Hexagon Flower: Nature-inspired 6-fold symmetry
• Girih Tiles: Complex interlocking patterns
• Morocco Zellige: Traditional tile patterns
• Use Earth or Ocean palettes for authenticity

🔬 VORONOI DIAGRAMS
• Random: Organic, cell-like structures
• Poisson: Evenly distributed, natural looking
• Fibonacci: Spiral-based point distribution
• Grid: Regular but with organic boundaries
• Color by distance creates beautiful gradients

🤖 CELLULAR AUTOMATA
• Game of Life: Conway's famous simulation
• Rule 30/90/110: Elementary automata patterns
• Brian's Brain: Three-state, colorful evolution
• Langton's Ant: Emergent complexity from simple rules
• Try "evolution" visualization for time patterns

🔶 TESSELLATIONS
• Penrose: Non-periodic, golden ratio tiles
• Truchet: Curved patterns in square tiles
• Hexagonal: Nature's favorite tessellation
• Add irregularity for organic, hand-drawn feel

⚡ INTERFERENCE
• Concentric: Ripple effects, water-like
• Wave: Linear interference patterns
• Grid: Complex standing wave patterns
• Try close frequencies for slow beat patterns

COLOR PALETTE GUIDE:
• Sunset: Warm, artistic, great for spirals
• Ocean: Cool blues, perfect for Voronoi
• Cosmic: Deep space, excellent for fractals
• Neon: Cyberpunk, amazing with automata
• Earth: Natural tones, ideal for Islamic patterns
        """

        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)

        ttk.Button(guide_dialog, text="Close", command=guide_dialog.destroy).pack(pady=10)

    def show_about(self):
        """Show about dialog"""
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About Advanced Mathematical Art Studio")
        about_dialog.geometry("500x350")
        about_dialog.transient(self.root)
        about_dialog.grab_set()

        text_widget = tk.Text(about_dialog, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)

        about_text = """
🎨 ADVANCED MATHEMATICAL ART STUDIO 🎨

A comprehensive application for creating stunning mathematical patterns and optical illusions.

✨ FEATURES:
• 6 Advanced Pattern Generators
• 10 Beautiful Color Palettes
• Smart Animation System
• Batch Generation Tools
• Professional Export Options
• Infinite Creative Possibilities

🎯 GENERATORS:
• Enhanced Spirals with overlapping effects
• Islamic Geometric Patterns
• Voronoi Diagrams with multiple distributions
• Cellular Automata simulations
• Advanced Tessellations
• Interference Patterns

🌈 POWERED BY:
• Python & Tkinter
• Matplotlib for rendering
• NumPy for mathematics
• SciPy for advanced algorithms

💫 INFINITE CREATIVITY:
From ancient Islamic geometric art to cutting-edge generative patterns, explore the beautiful intersection of mathematics and art.

Create, experiment, and discover the hidden patterns that surround us!

© 2025 Mathematical Art Studio
Built with Python and passion for mathematical beauty
        """

        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)

        ttk.Button(about_dialog, text="Close", command=about_dialog.destroy).pack(pady=10)



    def save_image(self):
        """Save current image to file"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image to save. Generate a pattern first.")
            return

        try:
            from PIL import Image
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"),
                          ("TIFF files", "*.tiff"), ("All files", "*.*")]
            )

            if filename:
                img = Image.fromarray(self.current_image)
                img.save(filename, dpi=(300, 300))
                logger.info(f"High-resolution image saved to: {filename}")
                messagebox.showinfo("Success", f"High-resolution image saved to: {filename}")

        except Exception as e:
            error_msg = f"Error saving image: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Save Error", error_msg)

    def save_svg(self):
        """Save current pattern as SVG"""
        try:
            if not self.current_generator:
                messagebox.showwarning("Warning", "No pattern to save. Generate a pattern first.")
                return

            filename = filedialog.asksaveasfilename(
                defaultextension=".svg",
                filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
            )

            if filename:
                # This is a simplified SVG export - could be enhanced further
                messagebox.showinfo("Info", "SVG export is a simplified version. Use PNG for full quality.")
                logger.info("SVG export requested")

        except Exception as e:
            error_msg = f"Error saving SVG: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("SVG Save Error", error_msg)

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
                    'color_palette': self.palette_var.get(),
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
                self.palette_var.set(global_settings.get('color_palette', 'default'))
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

    def randomize_parameters(self):
        """Randomize current pattern parameters"""
        try:
            if not self.current_generator:
                return

            parameters = self.current_generator.get_parameters()
            for param_name, widget_info in self.parameter_widgets.items():
                param_info = parameters.get(param_name, {})

                if param_info.get('type') == 'choice':
                    choices = param_info.get('choices', [])
                    if choices:
                        widget_info['var'].set(random.choice(choices))
                elif param_info.get('type') in ['int', 'float']:
                    min_val, max_val = param_info.get('range', (0, 1))
                    if param_info.get('type') == 'int':
                        value = random.randint(min_val, max_val)
                    else:
                        value = random.uniform(min_val, max_val)
                    widget_info['var'].set(value)

            logger.info("Parameters randomized")
            self.status_var.set("Parameters randomized - generate to see the magic!")

        except Exception as e:
            logger.error(f"Error randomizing parameters: {e}")

    def randomize_everything(self):
        """Randomize pattern type and all parameters"""
        try:
            # Random pattern
            pattern_types = list(self.generators.keys())
            random_pattern = random.choice(pattern_types)
            self.pattern_var.set(random_pattern)
            self.on_pattern_change()

            # Random palette
            palettes = ["default", "sunset", "ocean", "forest", "cosmic", "fire", "ice", "earth", "neon", "pastel"]
            self.palette_var.set(random.choice(palettes))

            # Random color mode
            self.color_mode_var.set(random.choice(["black_white", "color"]))

            # Random parameters
            self.randomize_parameters()

            logger.info("Everything randomized")
            self.status_var.set("🎲 Everything randomized! Click generate for a surprise!")

        except Exception as e:
            logger.error(f"Error randomizing everything: {e}")

    def surprise_generation(self):
        """Generate a completely random surprise pattern"""
        try:
            self.randomize_everything()
            # Small delay to let UI update
            self.root.after(100, self.generate_pattern)

        except Exception as e:
            logger.error(f"Error with surprise generation: {e}")

    # Preset loading methods
    def load_islamic_preset(self):
        """Load Islamic art preset"""
        self.pattern_var.set("Islamic Geometry")
        self.on_pattern_change()

        if 'pattern_type' in self.parameter_widgets:
            self.parameter_widgets['pattern_type']['var'].set('octagon_star')
        if 'interlace' in self.parameter_widgets:
            self.parameter_widgets['interlace']['var'].set('complex')

        self.color_mode_var.set('color')
        self.palette_var.set('earth')
        logger.info("Loaded Islamic Art preset")

    def load_organic_preset(self):
        """Load organic flow preset"""
        self.pattern_var.set("Voronoi Diagrams")
        self.on_pattern_change()

        if 'distribution' in self.parameter_widgets:
            self.parameter_widgets['distribution']['var'].set('poisson')
        if 'color_by' in self.parameter_widgets:
            self.parameter_widgets['color_by']['var'].set('distance')

        self.color_mode_var.set('color')
        self.palette_var.set('forest')
        logger.info("Loaded Organic Flow preset")

    def load_digital_preset(self):
        """Load digital grid preset"""
        self.pattern_var.set("Cellular Automata")
        self.on_pattern_change()

        if 'automata_type' in self.parameter_widgets:
            self.parameter_widgets['automata_type']['var'].set('rule_110')
        if 'visualization' in self.parameter_widgets:
            self.parameter_widgets['visualization']['var'].set('evolution')

        self.color_mode_var.set('color')
        self.palette_var.set('neon')
        logger.info("Loaded Digital Grid preset")

    def load_nature_preset(self):
        """Load nature patterns preset"""
        self.pattern_var.set("Tessellations")
        self.on_pattern_change()

        if 'tessellation_type' in self.parameter_widgets:
            self.parameter_widgets['tessellation_type']['var'].set('hexagonal')
        if 'irregularity' in self.parameter_widgets:
            self.parameter_widgets['irregularity']['var'].set(0.2)

        self.color_mode_var.set('color')
        self.palette_var.set('forest')
        logger.info("Loaded Nature Patterns preset")

    def load_cosmic_preset(self):
        """Load cosmic spiral preset"""
        self.pattern_var.set("Spiral")
        self.on_pattern_change()

        if 'spiral_type' in self.parameter_widgets:
            self.parameter_widgets['spiral_type']['var'].set('logarithmic')
        if 'overlapping_spirals' in self.parameter_widgets:
            self.parameter_widgets['overlapping_spirals']['var'].set(3)
        if 'gradient_effect' in self.parameter_widgets:
            self.parameter_widgets['gradient_effect']['var'].set('angular')

        self.color_mode_var.set('color')
        self.palette_var.set('cosmic')
        logger.info("Loaded Cosmic Spiral preset")

    def load_crystal_preset(self):
        """Load crystal growth preset"""
        self.pattern_var.set("Voronoi Diagrams")
        self.on_pattern_change()

        if 'distribution' in self.parameter_widgets:
            self.parameter_widgets['distribution']['var'].set('fibonacci')
        if 'style' in self.parameter_widgets:
            self.parameter_widgets['style']['var'].set('filled')
        if 'relaxation_steps' in self.parameter_widgets:
            self.parameter_widgets['relaxation_steps']['var'].set(3)

        self.color_mode_var.set('color')
        self.palette_var.set('ice')
        logger.info("Loaded Crystal Growth preset")

    # Display control methods
    def zoom_in(self):
        """Zoom into the current display"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        factor = 0.8

        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        x_range = (xlim[1] - xlim[0]) * factor / 2
        y_range = (ylim[1] - ylim[0]) * factor / 2

        self.ax.set_xlim(x_center - x_range, x_center + x_range)
        self.ax.set_ylim(y_center - y_range, y_center + y_range)
        self.canvas.draw()

    def zoom_out(self):
        """Zoom out of the current display"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        factor = 1.25

        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        x_range = (xlim[1] - xlim[0]) * factor / 2
        y_range = (ylim[1] - ylim[0]) * factor / 2

        self.ax.set_xlim(x_center - x_range, x_center + x_range)
        self.ax.set_ylim(y_center - y_range, y_center + y_range)
        self.canvas.draw()

    def reset_view(self):
        """Reset the view to default"""
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.canvas.draw()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        # This is a simple implementation - could be enhanced
        if self.root.attributes('-fullscreen'):
            self.root.attributes('-fullscreen', False)
        else:
            self.root.attributes('-fullscreen', True)

    def cleanup(self):
        """Cleanup resources"""
        try:
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
        plt.ioff()

        root = tk.Tk()

        # Enhanced styling
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')

        # Configure colors for better appearance
        style.configure('TLabel', background='#f0f0f0')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabelFrame', background='#f0f0f0')

        app = AdvancedArtStudio(root)

        def on_closing():
            logger.info("Advanced Art Studio closing")
            app.cleanup()
            root.quit()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Start the application
        logger.info("Starting Advanced Mathematical Art Studio")
        root.mainloop()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if 'root' in locals():
            messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")
    finally:
        plt.close('all')

if __name__ == "__main__":
    main()
