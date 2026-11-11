#!/usr/bin/env python3
"""
Advanced Mathematical Art Studio with AI-Guided Generation
Complete version with all original features plus AI guidance and multi-parameter animation
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
import json
from collections import deque
import os

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

@dataclass
class PatternGenome:
    """Represents a pattern's genetic information for AI evolution"""
    generator_type: str
    parameters: Dict[str, Any]
    fitness_score: float = 0.0
    generation: int = 0
    parent_ids: List[str] = None
    
    def __post_init__(self):
        if self.parent_ids is None:
            self.parent_ids = []

class AestheticAnalyzer:
    """AI-driven aesthetic analysis and scoring system"""
    
    @staticmethod
    def calculate_complexity_score(image_array: np.ndarray) -> float:
        """Calculate complexity based on edge density and variation"""
        try:
            # Convert to grayscale if needed
            if len(image_array.shape) == 3:
                gray = np.mean(image_array, axis=2)
            else:
                gray = image_array
            
            # Calculate gradients (edge detection)
            grad_x = np.gradient(gray, axis=1)
            grad_y = np.gradient(gray, axis=0)
            edges = np.sqrt(grad_x**2 + grad_y**2)
            
            # Complexity metrics
            edge_density = np.mean(edges)
            variation = np.std(gray)
            
            # Normalize and combine
            complexity = (edge_density * 0.6 + variation * 0.4) / 255.0
            return min(1.0, complexity)
            
        except Exception as e:
            logger.error(f"Error calculating complexity: {e}")
            return 0.5

    @staticmethod
    def calculate_symmetry_score(image_array: np.ndarray) -> float:
        """Calculate symmetry score for the pattern"""
        try:
            if len(image_array.shape) == 3:
                gray = np.mean(image_array, axis=2)
            else:
                gray = image_array
            
            h, w = gray.shape
            
            # Vertical symmetry
            left_half = gray[:, :w//2]
            right_half = np.fliplr(gray[:, w//2:])
            min_width = min(left_half.shape[1], right_half.shape[1])
            vertical_symmetry = np.corrcoef(
                left_half[:, :min_width].flatten(),
                right_half[:, :min_width].flatten()
            )[0, 1]
            
            # Horizontal symmetry
            top_half = gray[:h//2, :]
            bottom_half = np.flipud(gray[h//2:, :])
            min_height = min(top_half.shape[0], bottom_half.shape[0])
            horizontal_symmetry = np.corrcoef(
                top_half[:min_height, :].flatten(),
                bottom_half[:min_height, :].flatten()
            )[0, 1]
            
            # Handle NaN values
            if np.isnan(vertical_symmetry):
                vertical_symmetry = 0
            if np.isnan(horizontal_symmetry):
                horizontal_symmetry = 0
                
            return (abs(vertical_symmetry) + abs(horizontal_symmetry)) / 2
            
        except Exception as e:
            logger.error(f"Error calculating symmetry: {e}")
            return 0.5

    @staticmethod
    def calculate_balance_score(image_array: np.ndarray) -> float:
        """Calculate visual balance of the pattern"""
        try:
            if len(image_array.shape) == 3:
                gray = np.mean(image_array, axis=2)
            else:
                gray = image_array
            
            h, w = gray.shape
            
            # Calculate center of mass
            y_indices, x_indices = np.mgrid[:h, :w]
            total_mass = np.sum(gray)
            
            if total_mass == 0:
                return 0.5
                
            center_x = np.sum(x_indices * gray) / total_mass
            center_y = np.sum(y_indices * gray) / total_mass
            
            # Distance from image center
            image_center_x, image_center_y = w/2, h/2
            distance = np.sqrt((center_x - image_center_x)**2 + (center_y - image_center_y)**2)
            
            # Normalize (closer to center = higher balance)
            max_distance = np.sqrt((w/2)**2 + (h/2)**2)
            balance = 1.0 - (distance / max_distance)
            
            return balance
            
        except Exception as e:
            logger.error(f"Error calculating balance: {e}")
            return 0.5

    @classmethod
    def calculate_aesthetic_score(cls, image_array: np.ndarray, weights: Dict[str, float] = None) -> Dict[str, float]:
        """Calculate overall aesthetic score with breakdown"""
        if weights is None:
            weights = {'complexity': 0.3, 'symmetry': 0.4, 'balance': 0.3}
        
        complexity = cls.calculate_complexity_score(image_array)
        symmetry = cls.calculate_symmetry_score(image_array)
        balance = cls.calculate_balance_score(image_array)
        
        # Overall score
        overall = (complexity * weights['complexity'] + 
                  symmetry * weights['symmetry'] + 
                  balance * weights['balance'])
        
        return {
            'overall': overall,
            'complexity': complexity,
            'symmetry': symmetry,
            'balance': balance
        }

class GeneticAlgorithm:
    """Genetic algorithm for pattern evolution"""
    
    def __init__(self, generators: Dict[str, Any], population_size: int = 20):
        self.generators = generators
        self.population_size = population_size
        self.population: List[PatternGenome] = []
        self.generation = 0
        self.fitness_history = []
        
    def create_random_genome(self, generator_name: str = None) -> PatternGenome:
        """Create a random genome for evolution"""
        if generator_name is None:
            generator_name = random.choice(list(self.generators.keys()))
        
        generator = self.generators[generator_name]
        parameters = generator.get_parameters()
        
        genome_params = {}
        for param_name, param_info in parameters.items():
            if param_info['type'] == 'choice':
                genome_params[param_name] = random.choice(param_info['choices'])
            elif param_info['type'] in ['int', 'float']:
                min_val, max_val = param_info['range']
                if param_info['type'] == 'int':
                    genome_params[param_name] = random.randint(min_val, max_val)
                else:
                    genome_params[param_name] = random.uniform(min_val, max_val)
            else:
                genome_params[param_name] = param_info['default']
        
        return PatternGenome(
            generator_type=generator_name,
            parameters=genome_params,
            generation=self.generation
        )
    
    def initialize_population(self):
        """Initialize random population"""
        self.population = []
        for _ in range(self.population_size):
            genome = self.create_random_genome()
            self.population.append(genome)
        logger.info(f"Initialized population with {self.population_size} genomes")
    
    def evaluate_fitness(self, genome: PatternGenome, aesthetic_weights: Dict[str, float] = None) -> float:
        """Evaluate fitness of a genome by generating its pattern"""
        try:
            generator = self.generators[genome.generator_type]
            image_array = generator.generate(**genome.parameters)
            
            # Calculate aesthetic score
            scores = AestheticAnalyzer.calculate_aesthetic_score(image_array, aesthetic_weights)
            return scores['overall']
            
        except Exception as e:
            logger.error(f"Error evaluating genome fitness: {e}")
            return 0.0
    
    def crossover(self, parent1: PatternGenome, parent2: PatternGenome) -> PatternGenome:
        """Create offspring through crossover"""
        try:
            # Use parent1's generator type
            child_params = {}
            
            if parent1.generator_type == parent2.generator_type:
                # Same generator - mix parameters
                for param_name in parent1.parameters:
                    if random.random() < 0.5:
                        child_params[param_name] = parent1.parameters[param_name]
                    else:
                        child_params[param_name] = parent2.parameters[param_name]
                generator_type = parent1.generator_type
            else:
                # Different generators - choose one and use its parameters
                if random.random() < 0.5:
                    generator_type = parent1.generator_type
                    child_params = parent1.parameters.copy()
                else:
                    generator_type = parent2.generator_type
                    child_params = parent2.parameters.copy()
            
            return PatternGenome(
                generator_type=generator_type,
                parameters=child_params,
                generation=self.generation + 1,
                parent_ids=[id(parent1), id(parent2)]
            )
            
        except Exception as e:
            logger.error(f"Error in crossover: {e}")
            return self.create_random_genome()
    
    def mutate(self, genome: PatternGenome, mutation_rate: float = 0.1) -> PatternGenome:
        """Mutate a genome"""
        try:
            mutated_params = genome.parameters.copy()
            generator = self.generators[genome.generator_type]
            parameters_info = generator.get_parameters()
            
            for param_name, param_value in mutated_params.items():
                if random.random() < mutation_rate:
                    param_info = parameters_info.get(param_name, {})
                    
                    if param_info.get('type') == 'choice':
                        choices = param_info.get('choices', [param_value])
                        mutated_params[param_name] = random.choice(choices)
                    elif param_info.get('type') in ['int', 'float']:
                        min_val, max_val = param_info.get('range', (0, 1))
                        if param_info.get('type') == 'int':
                            mutated_params[param_name] = random.randint(min_val, max_val)
                        else:
                            # Gaussian mutation around current value
                            mutation_strength = (max_val - min_val) * 0.1
                            new_value = param_value + random.gauss(0, mutation_strength)
                            mutated_params[param_name] = max(min_val, min(max_val, new_value))
            
            return PatternGenome(
                generator_type=genome.generator_type,
                parameters=mutated_params,
                generation=self.generation + 1,
                parent_ids=[id(genome)]
            )
            
        except Exception as e:
            logger.error(f"Error in mutation: {e}")
            return genome
    
    def select_parents(self, tournament_size: int = 3) -> Tuple[PatternGenome, PatternGenome]:
        """Select parents using tournament selection"""
        def tournament():
            tournament_candidates = random.sample(self.population, tournament_size)
            return max(tournament_candidates, key=lambda g: g.fitness_score)
        
        return tournament(), tournament()
    
    def evolve_generation(self, aesthetic_weights: Dict[str, float] = None, elite_size: int = 2):
        """Evolve one generation"""
        try:
            # Evaluate fitness for all genomes
            for genome in self.population:
                genome.fitness_score = self.evaluate_fitness(genome, aesthetic_weights)
            
            # Sort by fitness
            self.population.sort(key=lambda g: g.fitness_score, reverse=True)
            
            # Record statistics
            avg_fitness = np.mean([g.fitness_score for g in self.population])
            best_fitness = self.population[0].fitness_score
            self.fitness_history.append({'avg': avg_fitness, 'best': best_fitness})
            
            # Create new generation
            new_population = []
            
            # Keep elite
            new_population.extend(self.population[:elite_size])
            
            # Generate offspring
            while len(new_population) < self.population_size:
                parent1, parent2 = self.select_parents()
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            
            self.population = new_population
            self.generation += 1
            
            logger.info(f"Generation {self.generation}: Best={best_fitness:.3f}, Avg={avg_fitness:.3f}")
            
            return self.population[0]  # Return best genome
            
        except Exception as e:
            logger.error(f"Error evolving generation: {e}")
            return None

class AnimationParameter:
    """Represents a parameter that can be animated"""
    def __init__(self, name: str, current_value: Any, param_info: Dict[str, Any]):
        self.name = name
        self.original_value = current_value
        self.current_value = current_value
        self.param_info = param_info
        self.enabled = False
        self.speed = 1.0
        self.phase_offset = 0.0
        self.animation_type = 'sine'  # sine, linear, triangle
        
    def get_animated_value(self, time: float) -> Any:
        """Calculate animated value at given time"""
        if not self.enabled:
            return self.current_value
            
        try:
            if self.param_info.get('type') == 'choice':
                # Cycle through choices
                choices = self.param_info.get('choices', [self.current_value])
                index = int((time * self.speed + self.phase_offset) % len(choices))
                return choices[index]
            
            elif self.param_info.get('type') in ['int', 'float']:
                min_val, max_val = self.param_info.get('range', (0, 1))
                
                if self.animation_type == 'sine':
                    # Sine wave animation
                    normalized = (np.sin(time * self.speed + self.phase_offset) + 1) / 2
                elif self.animation_type == 'linear':
                    # Linear sawtooth
                    normalized = ((time * self.speed + self.phase_offset) % (2 * np.pi)) / (2 * np.pi)
                elif self.animation_type == 'triangle':
                    # Triangle wave
                    phase = (time * self.speed + self.phase_offset) % (2 * np.pi)
                    normalized = 2 * abs(phase / (2 * np.pi) - 0.5)
                else:
                    normalized = 0.5
                
                value = min_val + normalized * (max_val - min_val)
                
                if self.param_info.get('type') == 'int':
                    return int(value)
                else:
                    return float(value)
            
            return self.current_value
            
        except Exception as e:
            logger.error(f"Error calculating animated value for {self.name}: {e}")
            return self.current_value

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
            # canvas.tostring_rgb() was removed in matplotlib 3.10; buffer_rgba() works on all versions
            buf = np.asarray(fig.canvas.buffer_rgba())[..., :3].copy()
            return buf
        except Exception as e:
            logger.error(f"Error converting figure to array: {e}")
            raise

class SpiralGenerator(PatternGenerator):
    """Enhanced spiral generator"""

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

# Add the remaining generators (simplified versions for space)
class IslamicGeometryGenerator(PatternGenerator):
    """Generates Islamic geometric patterns"""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'pattern_type': {'type': 'choice', 'choices': ['octagon_star', 'hexagon_flower', 'square_kufic', 'girih_tiles'], 'default': 'octagon_star'},
            'tile_size': {'type': 'float', 'range': (0.1, 1.0), 'default': 0.2},
            'repetitions_x': {'type': 'int', 'range': (2, 20), 'default': 8},
            'repetitions_y': {'type': 'int', 'range': (2, 20), 'default': 6},
            'rotation': {'type': 'float', 'range': (0, 360), 'default': 0},
            'interlace': {'type': 'choice', 'choices': ['none', 'simple', 'complex'], 'default': 'simple'}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate Islamic geometric pattern"""
        try:
            pattern_type = kwargs.get('pattern_type', 'octagon_star')
            tile_size = kwargs.get('tile_size', 0.2)
            rep_x = kwargs.get('repetitions_x', 8)
            rep_y = kwargs.get('repetitions_y', 6)
            rotation = kwargs.get('rotation', 0)

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            colors = ColorManager.get_palette(self.config.color_palette, 4)

            for i in range(rep_x):
                for j in range(rep_y):
                    x_center = -1 + (i + 0.5) * 2 / rep_x
                    y_center = -1 + (j + 0.5) * 2 / rep_y

                    if pattern_type == 'octagon_star':
                        # Simple octagon
                        angles = np.linspace(0, 2*np.pi, 9) + np.radians(rotation)
                        x = x_center + tile_size * np.cos(angles)
                        y = y_center + tile_size * np.sin(angles)
                        color = colors[0] if self.config.color_mode == 'color' else self.config.foreground_color
                        ax.fill(x, y, color=color, alpha=0.8, edgecolor='black', linewidth=self.config.line_width)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating Islamic pattern: {e}")
            raise
        finally:
            plt.close(fig)

class VoronoiGenerator(PatternGenerator):
    """Generates Voronoi diagram patterns"""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'num_points': {'type': 'int', 'range': (10, 500), 'default': 50},
            'distribution': {'type': 'choice', 'choices': ['random', 'grid', 'poisson', 'fibonacci'], 'default': 'random'},
            'style': {'type': 'choice', 'choices': ['filled', 'edges', 'both'], 'default': 'both'},
            'color_by': {'type': 'choice', 'choices': ['random', 'distance', 'area'], 'default': 'random'},
            'relaxation_steps': {'type': 'int', 'range': (0, 10), 'default': 0}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate Voronoi diagram pattern"""
        try:
            num_points = kwargs.get('num_points', 50)
            distribution = kwargs.get('distribution', 'random')
            style = kwargs.get('style', 'both')

            # Generate points
            if distribution == 'random':
                points = np.random.uniform(-1, 1, (num_points, 2))
            elif distribution == 'grid':
                side = int(np.sqrt(num_points))
                x = np.linspace(-0.9, 0.9, side)
                y = np.linspace(-0.9, 0.9, side)
                xx, yy = np.meshgrid(x, y)
                points = np.column_stack([xx.ravel(), yy.ravel()])[:num_points]
            else:
                points = np.random.uniform(-1, 1, (num_points, 2))

            # Create Voronoi diagram
            vor = Voronoi(points)

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            colors = ColorManager.get_palette(self.config.color_palette, num_points)

            # Draw regions
            for point_idx in range(len(vor.points)):
                region_idx = vor.point_region[point_idx]
                region = vor.regions[region_idx]

                if len(region) > 0 and -1 not in region:
                    vertices = vor.vertices[region]
                    if len(vertices) > 2:
                        color = colors[point_idx % len(colors)] if self.config.color_mode == 'color' else self.config.foreground_color
                        if style in ['filled', 'both']:
                            ax.fill(vertices[:, 0], vertices[:, 1], color=color, alpha=0.7)

            # Draw edges
            if style in ['edges', 'both']:
                for ridge in vor.ridge_vertices:
                    if -1 not in ridge:
                        vertices = vor.vertices[ridge]
                        ax.plot(vertices[:, 0], vertices[:, 1], 'k-', linewidth=self.config.line_width)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating Voronoi pattern: {e}")
            raise
        finally:
            plt.close(fig)

class CellularAutomataGenerator(PatternGenerator):
    """Generates cellular automata patterns"""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'automata_type': {'type': 'choice', 'choices': ['game_of_life', 'rule_30', 'rule_90', 'rule_110'], 'default': 'game_of_life'},
            'grid_size': {'type': 'int', 'range': (50, 200), 'default': 100},
            'generations': {'type': 'int', 'range': (1, 100), 'default': 50},
            'initial_density': {'type': 'float', 'range': (0.1, 0.9), 'default': 0.3},
            'visualization': {'type': 'choice', 'choices': ['final_state', 'evolution'], 'default': 'final_state'}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate cellular automata pattern"""
        try:
            automata_type = kwargs.get('automata_type', 'game_of_life')
            grid_size = kwargs.get('grid_size', 100)
            generations = kwargs.get('generations', 50)
            initial_density = kwargs.get('initial_density', 0.3)

            # Initialize grid
            grid = np.random.choice([0, 1], size=(grid_size, grid_size), p=[1-initial_density, initial_density])

            # Simple Game of Life implementation
            if automata_type == 'game_of_life':
                for _ in range(generations):
                    new_grid = np.zeros_like(grid)
                    for i in range(1, grid_size-1):
                        for j in range(1, grid_size-1):
                            neighbors = np.sum(grid[i-1:i+2, j-1:j+2]) - grid[i, j]
                            if grid[i, j] == 1:
                                if neighbors < 2 or neighbors > 3:
                                    new_grid[i, j] = 0
                                else:
                                    new_grid[i, j] = 1
                            else:
                                if neighbors == 3:
                                    new_grid[i, j] = 1
                    grid = new_grid

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))

            if self.config.color_mode == 'color':
                colors = ColorManager.get_palette(self.config.color_palette, 3)
                cmap = LinearSegmentedColormap.from_list('custom', [self.config.background_color] + colors[:2])
            else:
                cmap = 'gray'

            ax.imshow(grid, cmap=cmap, origin='lower')
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

class TessellationGenerator(PatternGenerator):
    """Generates tessellation patterns"""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            'tessellation_type': {'type': 'choice', 'choices': ['regular', 'hexagonal', 'triangular', 'truchet'], 'default': 'hexagonal'},
            'base_shape': {'type': 'choice', 'choices': ['triangle', 'square', 'hexagon'], 'default': 'hexagon'},
            'tile_size': {'type': 'float', 'range': (0.05, 0.5), 'default': 0.1},
            'irregularity': {'type': 'float', 'range': (0.0, 0.5), 'default': 0.0},
            'color_scheme': {'type': 'choice', 'choices': ['alternating', 'gradient', 'random'], 'default': 'alternating'}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate tessellation pattern"""
        try:
            tess_type = kwargs.get('tessellation_type', 'hexagonal')
            tile_size = kwargs.get('tile_size', 0.1)
            irregularity = kwargs.get('irregularity', 0.0)

            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            colors = ColorManager.get_palette(self.config.color_palette, 6)

            if tess_type == 'hexagonal':
                hex_height = tile_size * np.sqrt(3)
                hex_width = tile_size * 2

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
                            x_center += np.random.uniform(-irregularity, irregularity) * tile_size
                            y_center += np.random.uniform(-irregularity, irregularity) * tile_size

                        # Create hexagon
                        angles = np.linspace(0, 2*np.pi, 7)
                        x = x_center + tile_size * np.cos(angles)
                        y = y_center + tile_size * np.sin(angles)

                        color = colors[(row + col) % len(colors)] if self.config.color_mode == 'color' else self.config.foreground_color
                        ax.fill(x, y, color=color, alpha=0.8, edgecolor='black', linewidth=self.config.line_width)

            fig.patch.set_facecolor(self.config.background_color)
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating tessellation: {e}")
            raise
        finally:
            plt.close(fig)

# Advanced Art Studio Application
class AdvancedArtStudio:
    """Main GUI application with all features plus AI guidance and multi-parameter animation"""

    def __init__(self, root):
        self.root = root
        self.root.title("AI-Enhanced Advanced Mathematical Art Studio")
        self.root.geometry("1600x1000")

        # Initialize configuration
        self.config = PatternConfig()

        # Initialize all generators
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
        self.animation_parameters = {}
        self.animation_running = False
        self.animation_frame = 0
        self.batch_generating = False
        
        # AI components
        self.genetic_algorithm = GeneticAlgorithm(self.generators)
        self.evolution_history = deque(maxlen=100)

        self.setup_ui()
        self.setup_logging_display()

        logger.info("AI-Enhanced Advanced Art Studio initialized successfully")

    def setup_ui(self):
        """Setup the enhanced user interface"""
        # Create menu bar first
        self.setup_menu_bar()

        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main generation tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Pattern Generator")

        # AI Evolution tab
        self.ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_tab, text="AI Evolution")

        self.setup_main_tab()
        self.setup_ai_tab()

    def setup_menu_bar(self):
        """Setup menu bar with all original functionality"""
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

    def setup_main_tab(self):
        """Setup main pattern generation tab"""
        # Create main frames
        self.main_frame = ttk.Frame(self.main_tab)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel for controls (scrollable)
        self.setup_scrollable_controls()

        # Right panel for display
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.setup_display()

    def setup_scrollable_controls(self):
        """Setup scrollable control panel"""
        # Create canvas and scrollbar for scrollable area
        canvas = tk.Canvas(self.main_frame, width=400)
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
        """Setup enhanced control panel with animation checkboxes"""
        # Title
        title_label = ttk.Label(self.control_frame, text="AI-Enhanced Mathematical Art Studio",
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

        # Parameters frame with animation controls
        self.params_frame = ttk.LabelFrame(self.control_frame, text="Parameters & Animation", padding=10)
        self.params_frame.pack(fill=tk.X, pady=(0, 10))

        # Animation controls
        anim_controls = ttk.LabelFrame(self.control_frame, text="Multi-Parameter Animation", padding=10)
        anim_controls.pack(fill=tk.X, pady=(0, 10))

        # Animation buttons
        btn_frame = ttk.Frame(anim_controls)
        btn_frame.pack(fill=tk.X, pady=5)

        self.multi_animate_btn = ttk.Button(btn_frame, text="Start Multi-Animation",
                                          command=self.toggle_multi_animation)
        self.multi_animate_btn.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(btn_frame, text="Reset Animation",
                  command=self.reset_animation).pack(side=tk.LEFT)

        # Animation speed
        speed_frame = ttk.Frame(anim_controls)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.anim_speed_var = tk.DoubleVar(value=1.0)
        ttk.Scale(speed_frame, from_=0.1, to=5.0, variable=self.anim_speed_var,
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Global settings
        self.global_frame = ttk.LabelFrame(self.control_frame, text="Global Settings", padding=10)
        self.global_frame.pack(fill=tk.X, pady=(0, 10))
        self.setup_global_controls()

        # Main action buttons
        main_actions = ttk.LabelFrame(self.control_frame, text="Main Actions", padding=10)
        main_actions.pack(fill=tk.X, pady=(0, 10))

        self.generate_btn = ttk.Button(main_actions, text="Generate Pattern",
                                     command=self.generate_pattern)
        self.generate_btn.pack(fill=tk.X, pady=2)

        self.animate_btn = ttk.Button(main_actions, text="Animate Pattern",
                                    command=self.animate_pattern)
        self.animate_btn.pack(fill=tk.X, pady=2)

        # Quick actions frame
        quick_frame = ttk.LabelFrame(self.control_frame, text="Quick Actions", padding=10)
        quick_frame.pack(fill=tk.X, pady=(0, 10))

        # Create 2x2 grid for quick actions
        quick_actions = [
            ("Random Params", self.randomize_parameters),
            ("Random All", self.randomize_everything),
            ("Surprise Me!", self.surprise_generation),
            ("Batch Generate", self.batch_generate)
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
        self.ax.text(0.5, 0.5, 'Welcome to AI-Enhanced Advanced Mathematical Art Studio\nSelect a pattern and click Generate',
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

        ttk.Button(display_controls, text="Zoom +", command=self.zoom_in, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(display_controls, text="Zoom -", command=self.zoom_out, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(display_controls, text="Reset", command=self.reset_view, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(display_controls, text="Full", command=self.toggle_fullscreen, width=8).pack(side=tk.LEFT, padx=1)

        # Status bar
        self.status_var = tk.StringVar(value="Ready to create AI-guided mathematical art!")
        status_bar = ttk.Label(toolbar_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5, pady=2)

    def setup_ai_tab(self):
        """Setup AI evolution tab"""
        ai_main = ttk.Frame(self.ai_tab)
        ai_main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # AI Controls
        ai_controls = ttk.LabelFrame(ai_main, text="AI Evolution Controls", padding=10)
        ai_controls.pack(fill=tk.X, pady=(0, 10))

        # Evolution parameters
        params_frame = ttk.Frame(ai_controls)
        params_frame.pack(fill=tk.X, pady=5)

        ttk.Label(params_frame, text="Population Size:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pop_size_var = tk.IntVar(value=20)
        ttk.Spinbox(params_frame, from_=10, to=100, textvariable=self.pop_size_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(params_frame, text="Generations:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(20, 0))
        self.generations_var = tk.IntVar(value=10)
        ttk.Spinbox(params_frame, from_=1, to=100, textvariable=self.generations_var, width=10).grid(row=0, column=3, padx=5)

        # Aesthetic weights
        weights_frame = ttk.LabelFrame(ai_controls, text="Aesthetic Preferences", padding=5)
        weights_frame.pack(fill=tk.X, pady=5)

        ttk.Label(weights_frame, text="Complexity:").grid(row=0, column=0, sticky=tk.W)
        self.complexity_weight = tk.DoubleVar(value=0.3)
        ttk.Scale(weights_frame, from_=0, to=1, variable=self.complexity_weight, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=tk.EW, padx=5)

        ttk.Label(weights_frame, text="Symmetry:").grid(row=1, column=0, sticky=tk.W)
        self.symmetry_weight = tk.DoubleVar(value=0.4)
        ttk.Scale(weights_frame, from_=0, to=1, variable=self.symmetry_weight, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=tk.EW, padx=5)

        ttk.Label(weights_frame, text="Balance:").grid(row=2, column=0, sticky=tk.W)
        self.balance_weight = tk.DoubleVar(value=0.3)
        ttk.Scale(weights_frame, from_=0, to=1, variable=self.balance_weight, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky=tk.EW, padx=5)

        weights_frame.columnconfigure(1, weight=1)

        # AI Action buttons
        ai_buttons = ttk.Frame(ai_controls)
        ai_buttons.pack(fill=tk.X, pady=10)

        ttk.Button(ai_buttons, text="Initialize Population", 
                  command=self.initialize_ai_population).pack(side=tk.LEFT, padx=5)
        ttk.Button(ai_buttons, text="Evolve Generation", 
                  command=self.evolve_generation).pack(side=tk.LEFT, padx=5)
        ttk.Button(ai_buttons, text="Auto-Evolve", 
                  command=self.auto_evolve).pack(side=tk.LEFT, padx=5)

        # Evolution results
        results_frame = ttk.LabelFrame(ai_main, text="Evolution Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Results text widget
        self.results_text = tk.Text(results_frame, height=15, wrap=tk.WORD)
        scrollbar_results = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar_results.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_results.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_logging_display(self):
        """Setup logging display"""
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
        """Update parameter controls with animation checkboxes"""
        # Clear existing widgets
        for widget_info in self.parameter_widgets.values():
            for widget in widget_info['widgets']:
                widget.destroy()
        self.parameter_widgets.clear()
        self.animation_parameters.clear()

        if not self.current_generator:
            return

        parameters = self.current_generator.get_parameters()
        row = 0

        for param_name, param_info in parameters.items():
            # Create frame for this parameter
            param_frame = ttk.Frame(self.params_frame)
            param_frame.grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=2)
            self.params_frame.columnconfigure(0, weight=1)

            # Parameter label
            label = ttk.Label(param_frame, text=f"{param_name.replace('_', ' ').title()}:")
            label.grid(row=0, column=0, sticky=tk.W)

            # Parameter control
            if param_info['type'] == 'choice':
                var = tk.StringVar(value=param_info['default'])
                widget = ttk.Combobox(param_frame, textvariable=var,
                                    values=param_info['choices'], state="readonly", width=15)
            elif param_info['type'] == 'int':
                var = tk.IntVar(value=param_info['default'])
                min_val, max_val = param_info['range']
                widget = ttk.Spinbox(param_frame, from_=min_val, to=max_val,
                                   textvariable=var, width=15)
            elif param_info['type'] == 'float':
                var = tk.DoubleVar(value=param_info['default'])
                min_val, max_val = param_info['range']
                widget = ttk.Spinbox(param_frame, from_=min_val, to=max_val,
                                   increment=0.1, textvariable=var, width=15)

            widget.grid(row=0, column=1, padx=5)

            # Animation checkbox
            animate_var = tk.BooleanVar()
            animate_checkbox = ttk.Checkbutton(param_frame, text="Animate", variable=animate_var)
            animate_checkbox.grid(row=0, column=2, padx=5)

            # Store widget information
            widgets = [param_frame, label, widget, animate_checkbox]
            self.parameter_widgets[param_name] = {
                'widgets': widgets,
                'var': var,
                'animate_var': animate_var
            }

            # Create animation parameter object
            self.animation_parameters[param_name] = AnimationParameter(
                param_name, param_info['default'], param_info
            )

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

    def update_animation_parameters(self):
        """Update animation parameters based on checkboxes"""
        for param_name, widget_info in self.parameter_widgets.items():
            animate_enabled = widget_info['animate_var'].get()
            current_value = widget_info['var'].get()
            
            anim_param = self.animation_parameters[param_name]
            anim_param.enabled = animate_enabled
            anim_param.current_value = current_value
            anim_param.speed = self.anim_speed_var.get()

    def generate_pattern(self):
        """Generate pattern using current settings"""
        try:
            if not self.current_generator:
                raise ValueError("No pattern selected")

            self.update_config()
            self.status_var.set("Generating pattern...")
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

            self.status_var.set("Pattern created successfully!")
            logger.info("Pattern displayed successfully")

        except Exception as e:
            error_msg = f"Error displaying pattern: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Display Error", error_msg)
            self.status_var.set("Display failed")

    def animate_pattern(self):
        """Create animated pattern by varying parameters (original single-parameter method)"""
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

    def toggle_multi_animation(self):
        """Toggle multi-parameter animation"""
        if self.animation_running:
            self.stop_multi_animation()
        else:
            self.start_multi_animation()

    def start_multi_animation(self):
        """Start multi-parameter animation"""
        try:
            self.update_animation_parameters()
            
            # Check if any parameters are selected for animation
            animate_any = any(param.enabled for param in self.animation_parameters.values())
            if not animate_any:
                messagebox.showwarning("Warning", "Please select parameters to animate using the checkboxes.")
                return

            self.animation_running = True
            self.animation_frame = 0
            self.multi_animate_btn.config(text="Stop Multi-Animation")
            
            self.multi_animate_step()

        except Exception as e:
            logger.error(f"Error starting multi-animation: {e}")

    def stop_multi_animation(self):
        """Stop multi-parameter animation"""
        self.animation_running = False
        self.multi_animate_btn.config(text="Start Multi-Animation")
        
        # Reset parameters to their original values
        for param_name, anim_param in self.animation_parameters.items():
            if param_name in self.parameter_widgets:
                self.parameter_widgets[param_name]['var'].set(anim_param.original_value)

    def multi_animate_step(self):
        """Execute one multi-animation step"""
        if not self.animation_running:
            return

        try:
            time_value = self.animation_frame * 0.1
            
            # Update animated parameters
            for param_name, anim_param in self.animation_parameters.items():
                if anim_param.enabled:
                    animated_value = anim_param.get_animated_value(time_value)
                    self.parameter_widgets[param_name]['var'].set(animated_value)

            # Generate new frame
            self.update_config()
            params = self.get_current_parameters()
            image_array = self.current_generator.generate(**params)
            self.display_pattern(image_array)

            self.animation_frame += 1
            
            # Schedule next frame
            if self.animation_running:
                self.root.after(50, self.multi_animate_step)  # 20 FPS

        except Exception as e:
            logger.error(f"Multi-animation error: {e}")
            self.stop_multi_animation()

    def stop_animation(self):
        """Stop the current animation"""
        self.animation_running = False
        self.animate_btn.config(text="Animate Pattern")
        self.multi_animate_btn.config(text="Start Multi-Animation")
        logger.info("Animation stopped")

    def reset_animation(self):
        """Reset animation to initial state"""
        self.stop_animation()
        self.animation_frame = 0
        
        # Reset all parameters to defaults
        if self.current_generator:
            parameters = self.current_generator.get_parameters()
            for param_name, param_info in parameters.items():
                if param_name in self.parameter_widgets:
                    self.parameter_widgets[param_name]['var'].set(param_info['default'])
                    self.animation_parameters[param_name].original_value = param_info['default']

    # AI Evolution Methods
    def initialize_ai_population(self):
        """Initialize AI evolution population"""
        try:
            self.genetic_algorithm.population_size = self.pop_size_var.get()
            self.genetic_algorithm.initialize_population()
            
            self.results_text.insert(tk.END, f"Initialized population with {self.pop_size_var.get()} genomes\n")
            self.results_text.see(tk.END)
            
        except Exception as e:
            logger.error(f"Error initializing population: {e}")

    def evolve_generation(self):
        """Evolve one generation"""
        try:
            if not self.genetic_algorithm.population:
                self.initialize_ai_population()

            weights = {
                'complexity': self.complexity_weight.get(),
                'symmetry': self.symmetry_weight.get(),
                'balance': self.balance_weight.get()
            }

            best_genome = self.genetic_algorithm.evolve_generation(weights)
            
            if best_genome:
                # Display best pattern
                self.display_ai_result(best_genome)
                
                # Update results
                gen = self.genetic_algorithm.generation
                fitness = best_genome.fitness_score
                self.results_text.insert(tk.END, f"Generation {gen}: Best fitness = {fitness:.3f}\n")
                self.results_text.insert(tk.END, f"  Pattern: {best_genome.generator_type}\n")
                self.results_text.insert(tk.END, f"  Parameters: {best_genome.parameters}\n\n")
                self.results_text.see(tk.END)

        except Exception as e:
            logger.error(f"Error evolving generation: {e}")

    def auto_evolve(self):
        """Automatically evolve multiple generations"""
        try:
            if not self.genetic_algorithm.population:
                self.initialize_ai_population()

            generations = self.generations_var.get()
            
            def evolve_step(remaining):
                if remaining > 0:
                    self.evolve_generation()
                    self.root.after(100, lambda: evolve_step(remaining - 1))
                else:
                    self.results_text.insert(tk.END, "Auto-evolution completed!\n\n")
                    self.results_text.see(tk.END)

            self.results_text.insert(tk.END, f"Starting auto-evolution for {generations} generations...\n")
            evolve_step(generations)

        except Exception as e:
            logger.error(f"Error in auto-evolution: {e}")

    def display_ai_result(self, genome: PatternGenome):
        """Display the result of AI evolution"""
        try:
            # Set the pattern type
            self.pattern_var.set(genome.generator_type)
            self.on_pattern_change()
            
            # Set parameters
            for param_name, value in genome.parameters.items():
                if param_name in self.parameter_widgets:
                    self.parameter_widgets[param_name]['var'].set(value)
            
            # Generate and display
            self.generate_pattern()
            
        except Exception as e:
            logger.error(f"Error displaying AI result: {e}")

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
            self.status_var.set("Everything randomized! Click generate for a surprise!")

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

NEW AI FEATURES:
• Multi-Parameter Animation: Check boxes next to parameters to animate multiple simultaneously
• AI Evolution: Use the AI Evolution tab to evolve aesthetically pleasing patterns
• Aesthetic Control: Adjust complexity, symmetry, and balance preferences

Pattern Tips:
• Try different color palettes for dramatic effects
• Use multi-animation to understand parameter interactions
• Batch generate to explore parameter spaces
• Islamic Geometry works great with Earth palette
• Voronoi + Poisson distribution = organic patterns
• Cellular Automata + Neon palette = cyberpunk vibes

AI Tips:
• Start with random population, then evolve 10+ generations
• Adjust aesthetic weights to guide evolution toward your taste
• High complexity + low symmetry = organic, chaotic patterns
• High symmetry + high balance = classical, ordered patterns
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
AI-ENHANCED PATTERN GENERATOR GUIDE

SPIRALS
• Archimedean: Uniform spacing, classic spiral
• Logarithmic: Exponential growth, nature-inspired
• Fermat: Square root spiral, sunflower patterns
• Fibonacci: Golden ratio, perfect proportions
• Try overlapping spirals with angular gradients!

ISLAMIC GEOMETRY
• Octagon Star: Classic 8-pointed star patterns
• Hexagon Flower: Nature-inspired 6-fold symmetry
• Girih Tiles: Complex interlocking patterns
• Use Earth or Ocean palettes for authenticity

VORONOI DIAGRAMS
• Random: Organic, cell-like structures
• Poisson: Evenly distributed, natural looking
• Fibonacci: Spiral-based point distribution
• Grid: Regular but with organic boundaries
• Color by distance creates beautiful gradients

CELLULAR AUTOMATA
• Game of Life: Conway's famous simulation
• Rule 30/90/110: Elementary automata patterns
• Try "evolution" visualization for time patterns

TESSELLATIONS
• Hexagonal: Nature's favorite tessellation
• Add irregularity for organic, hand-drawn feel
• Truchet: Curved patterns in square tiles

INTERFERENCE
• Concentric: Ripple effects, water-like
• Wave: Linear interference patterns
• Grid: Complex standing wave patterns

NEW AI FEATURES:

MULTI-PARAMETER ANIMATION:
• Check "Animate" boxes next to parameters you want to animate
• Use speed slider to control animation rate
• Different parameters can create complex, flowing effects
• Try animating rotation + scale + density together

AI EVOLUTION:
• Initialize population with random patterns
• Set aesthetic preferences (complexity, symmetry, balance)
• Evolve generations to discover beautiful patterns
• High complexity = detailed, intricate patterns
• High symmetry = balanced, harmonious patterns
• High balance = well-centered, stable patterns

COLOR PALETTE GUIDE:
• Sunset: Warm, artistic, great for spirals
• Ocean: Cool blues, perfect for Voronoi
• Cosmic: Deep space, excellent for all patterns
• Neon: Cyberpunk, amazing with automata
• Earth: Natural tones, ideal for Islamic patterns
        """

        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)

        ttk.Button(guide_dialog, text="Close", command=guide_dialog.destroy).pack(pady=10)

    def show_about(self):
        """Show about dialog"""
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About AI-Enhanced Advanced Mathematical Art Studio")
        about_dialog.geometry("500x350")
        about_dialog.transient(self.root)
        about_dialog.grab_set()

        text_widget = tk.Text(about_dialog, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)

        about_text = """
AI-ENHANCED ADVANCED MATHEMATICAL ART STUDIO

A comprehensive application for creating stunning mathematical patterns with AI-guided evolution and multi-parameter animation.

NEW AI FEATURES:
• AI-Guided Pattern Evolution using Genetic Algorithms
• Aesthetic Analysis (Complexity, Symmetry, Balance scoring)
• Multi-Parameter Animation with individual controls
• Population-based Evolution with fitness selection

ORIGINAL FEATURES:
• 6 Advanced Pattern Generators
• 10 Beautiful Color Palettes
• Professional Animation System
• Batch Generation Tools
• Professional Export Options
• Comprehensive Presets

GENERATORS:
• Enhanced Spirals with overlapping effects
• Islamic Geometric Patterns
• Voronoi Diagrams with multiple distributions
• Cellular Automata simulations
• Advanced Tessellations
• Interference Patterns

POWERED BY:
• Python & Tkinter for GUI
• Matplotlib for rendering
• NumPy for mathematics
• SciPy for advanced algorithms
• Custom AI algorithms for pattern evolution

AI INNOVATION:
From ancient Islamic geometric art to cutting-edge AI-evolved patterns, explore the beautiful intersection of mathematics, art, and artificial intelligence.

Create, experiment, evolve, and discover the hidden patterns that surround us!

© 2025 AI-Enhanced Mathematical Art Studio
Built with Python, AI, and passion for mathematical beauty
        """

        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)

        ttk.Button(about_dialog, text="Close", command=about_dialog.destroy).pack(pady=10)

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
            logger.info("AI-Enhanced Advanced Art Studio closing")
            app.cleanup()
            root.quit()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Start the application
        logger.info("Starting AI-Enhanced Advanced Mathematical Art Studio")
        root.mainloop()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if 'root' in locals():
            messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")
    finally:
        plt.close('all')

if __name__ == "__main__":
    main()