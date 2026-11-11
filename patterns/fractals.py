"""
Fractal generator (Mandelbrot, Julia, Sierpinski chaos game, Barnsley fern, dragon curve).

Moved verbatim from optical_illusion_generator_V2.py (which now imports it from here) so the
web interface can use it without tkinter. _fig_to_array comes from patterns.base.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any

from patterns.base import PatternGenerator

logger = logging.getLogger(__name__)


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
