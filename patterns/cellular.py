"""
Cellular automata pattern generator.

Supports Game of Life, elementary CAs (rules 30/90/110), Brian's Brain,
and Langton's Ant with multiple initialization and visualization modes.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from typing import Dict, Any

from config import ColorManager
from patterns.base import PatternGenerator

logger = logging.getLogger(__name__)


class CellularAutomataGenerator(PatternGenerator):
    """Generates cellular automata patterns."""

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
        """Generate cellular automata pattern."""
        fig = None
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

            grid = self._initialize_grid(grid_size, initial_pattern, initial_density)

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

            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))

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
            if fig is not None:
                plt.close(fig)

    # --- Grid initialization ---

    def _initialize_grid(self, size, pattern, density):
        grid = np.zeros((size, size), dtype=int)
        if pattern == 'random':
            grid = np.random.choice([0, 1], size=(size, size), p=[1 - density, density])
        elif pattern == 'center_dot':
            grid[size // 2, size // 2] = 1
        elif pattern == 'glider':
            glider = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]])
            s = size // 4
            grid[s:s + 3, s:s + 3] = glider
        elif pattern == 'pulsar':
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
            end_x = min(start_x + gun_pattern.shape[0], size)
            end_y = min(start_y + gun_pattern.shape[1], size)
            grid[start_x:end_x, start_y:end_y] = gun_pattern[:end_x - start_x, :end_y - start_y]
        return grid

    # --- Automata runners ---

    def _run_game_of_life(self, initial_grid, generations, neighborhood):
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
                    if grid[i, j] == 1:
                        if 2 <= neighbors <= 3:
                            new_grid[i, j] = 1
                    else:
                        if neighbors == 3:
                            new_grid[i, j] = 1
            grid = new_grid
            evolution.append(grid.copy())
        return grid, evolution

    def _run_elementary_ca(self, initial_grid, generations, rule_number):
        width = initial_grid.shape[1]
        grid = np.zeros((generations, width))
        grid[0] = initial_grid[initial_grid.shape[0] // 2]
        rule = format(rule_number, '08b')
        rule_dict = {format(i, '03b'): int(rule[7 - i]) for i in range(8)}
        for gen in range(1, generations):
            for i in range(width):
                left = grid[gen - 1][(i - 1) % width]
                center = grid[gen - 1][i]
                right = grid[gen - 1][(i + 1) % width]
                pattern = f"{int(left)}{int(center)}{int(right)}"
                grid[gen][i] = rule_dict[pattern]
        evolution = [
            np.tile(grid[i], (initial_grid.shape[0] // generations + 1, 1))[:initial_grid.shape[0]]
            for i in range(generations)
        ]
        return grid[-1:], evolution

    def _run_brian_brain(self, initial_grid, generations):
        grid = initial_grid.copy().astype(int)
        evolution = [grid.copy()]
        for _ in range(generations):
            new_grid = np.zeros_like(grid)
            for i in range(grid.shape[0]):
                for j in range(grid.shape[1]):
                    if grid[i, j] == 0:
                        alive_neighbors = self._count_alive_neighbors_brian(grid, i, j)
                        if alive_neighbors == 2:
                            new_grid[i, j] = 1
                    elif grid[i, j] == 1:
                        new_grid[i, j] = 2
            grid = new_grid
            evolution.append(grid.copy())
        return grid, evolution

    def _run_langton_ant(self, initial_grid, generations):
        grid = initial_grid.copy()
        ant_x, ant_y = grid.shape[0] // 2, grid.shape[1] // 2
        ant_dir = 0
        evolution = [grid.copy()]
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for _ in range(generations):
            if 0 <= ant_x < grid.shape[0] and 0 <= ant_y < grid.shape[1]:
                if grid[ant_x, ant_y] == 0:
                    ant_dir = (ant_dir + 1) % 4
                    grid[ant_x, ant_y] = 1
                else:
                    ant_dir = (ant_dir - 1) % 4
                    grid[ant_x, ant_y] = 0
                dx, dy = directions[ant_dir]
                ant_x += dx
                ant_y += dy
            evolution.append(grid.copy())
        return grid, evolution

    # --- Neighbor counting ---

    def _count_moore_neighbors(self, grid, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % grid.shape[0], (y + dy) % grid.shape[1]
                count += grid[nx, ny]
        return count

    def _count_neumann_neighbors(self, grid, x, y):
        count = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = (x + dx) % grid.shape[0], (y + dy) % grid.shape[1]
            count += grid[nx, ny]
        return count

    def _count_alive_neighbors_brian(self, grid, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % grid.shape[0], (y + dy) % grid.shape[1]
                if grid[nx, ny] == 1:
                    count += 1
        return count

    # --- Visualization ---

    def _visualize_grid(self, ax, grid):
        if self.config.color_mode == 'color':
            colors = ColorManager.get_palette(self.config.color_palette, 3)
            cmap = LinearSegmentedColormap.from_list('custom', [self.config.background_color] + colors[:2])
        else:
            cmap = 'gray'
        ax.imshow(grid, cmap=cmap, origin='lower')

    def _visualize_evolution(self, ax, evolution):
        if len(evolution) > 1:
            evolution_array = np.array(evolution)
            if len(evolution_array.shape) == 3:
                middle_slice = evolution_array[:, evolution_array.shape[1] // 2, :]
                ax.imshow(middle_slice, cmap='hot', origin='lower', aspect='auto')
            else:
                ax.imshow(evolution_array, cmap='hot', origin='lower', aspect='auto')

    def _visualize_trail(self, ax, evolution):
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
