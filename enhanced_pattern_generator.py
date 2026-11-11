#!/usr/bin/env python3
"""
Advanced Mathematical Art Studio with AI-Guided Generation
Enhanced version with AI pattern guidance and multi-parameter animation
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

# Include all the original generator classes here (PatternGenerator, IslamicGeometryGenerator, etc.)
# [The original classes would be included here - I'm showing the structure]

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

# Simplified pattern generator for demo
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
            'spiral_type': {'type': 'choice', 'choices': ['archimedean', 'logarithmic', 'fermat'], 'default': 'archimedean'},
            'arms': {'type': 'int', 'range': (1, 8), 'default': 3},
            'density': {'type': 'float', 'range': (0.1, 5.0), 'default': 1.0},
            'rotation': {'type': 'float', 'range': (0, 360), 'default': 0},
            'scale': {'type': 'float', 'range': (0.1, 3.0), 'default': 1.0}
        }

    def generate(self, **kwargs) -> np.ndarray:
        """Generate spiral pattern"""
        try:
            spiral_type = kwargs.get('spiral_type', 'archimedean')
            arms = kwargs.get('arms', 3)
            density = kwargs.get('density', 1.0)
            rotation = kwargs.get('rotation', 0)
            scale = kwargs.get('scale', 1.0)

            fig, ax = plt.subplots(figsize=(8, 8))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            t = np.linspace(0, 10 * np.pi * density, 1000)

            for arm in range(arms):
                arm_rotation = rotation + (arm * 360 / arms)
                arm_rotation_rad = np.radians(arm_rotation)

                if spiral_type == 'archimedean':
                    r = 0.05 * t * scale
                elif spiral_type == 'logarithmic':
                    r = 0.1 * np.exp(0.1 * t) * scale
                elif spiral_type == 'fermat':
                    r = 0.2 * np.sqrt(t) * scale

                x = r * np.cos(t + arm_rotation_rad)
                y = r * np.sin(t + arm_rotation_rad)

                # Filter points within bounds
                mask = (x**2 + y**2) <= 1
                x, y = x[mask], y[mask]

                if len(x) > 0:
                    ax.plot(x, y, color='black', linewidth=1.0)

            fig.patch.set_facecolor('white')
            plt.tight_layout()

            return self._fig_to_array(fig)

        except Exception as e:
            logger.error(f"Error generating spiral: {e}")
            raise
        finally:
            plt.close(fig)

# Enhanced Art Studio Application
class AdvancedArtStudio:
    """Main GUI application with AI guidance and multi-parameter animation"""

    def __init__(self, root):
        self.root = root
        self.root.title("AI-Enhanced Mathematical Art Studio")
        self.root.geometry("1600x1000")

        # Initialize configuration
        self.config = PatternConfig()

        # Initialize generators (simplified for demo)
        self.generators = {
            'Spiral': SpiralGenerator(self.config)
        }

        self.current_generator = None
        self.current_image = None
        self.parameter_widgets = {}
        self.animation_parameters = {}
        self.animation_running = False
        self.animation_frame = 0
        
        # AI components
        self.genetic_algorithm = GeneticAlgorithm(self.generators)
        self.evolution_history = deque(maxlen=100)
        self.batch_generating = False

        self.setup_ui()
        self.setup_logging_display()

        logger.info("AI-Enhanced Art Studio initialized successfully")

    def setup_ui(self):
        """Setup the enhanced user interface"""
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

    def setup_main_tab(self):
        """Setup main pattern generation tab"""
        # Create main frames
        self.main_frame = ttk.Frame(self.main_tab)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel for controls
        self.control_frame = ttk.Frame(self.main_frame, width=400)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.control_frame.pack_propagate(False)

        # Right panel for display
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.setup_controls()
        self.setup_display()

    def setup_controls(self):
        """Setup enhanced control panel with animation checkboxes"""
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
        anim_controls = ttk.LabelFrame(self.control_frame, text="Animation Controls", padding=10)
        anim_controls.pack(fill=tk.X, pady=(0, 10))

        # Animation buttons
        btn_frame = ttk.Frame(anim_controls)
        btn_frame.pack(fill=tk.X, pady=5)

        self.animate_btn = ttk.Button(btn_frame, text="Start Animation",
                                    command=self.toggle_animation)
        self.animate_btn.pack(side=tk.LEFT, padx=(0, 5))

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

        # Main actions
        main_actions = ttk.LabelFrame(self.control_frame, text="Actions", padding=10)
        main_actions.pack(fill=tk.X, pady=(0, 10))

        self.generate_btn = ttk.Button(main_actions, text="Generate Pattern",
                                     command=self.generate_pattern)
        self.generate_btn.pack(fill=tk.X, pady=2)

        # Initialize with first pattern
        self.on_pattern_change()

    def setup_global_controls(self):
        """Setup global configuration controls"""
        # Color mode
        ttk.Label(self.global_frame, text="Color Mode:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.color_mode_var = tk.StringVar(value="black_white")
        color_combo = ttk.Combobox(self.global_frame, textvariable=self.color_mode_var,
                                 values=["black_white", "color"], state="readonly", width=15)
        color_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)

        # Resolution
        ttk.Label(self.global_frame, text="Resolution:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.resolution_var = tk.IntVar(value=800)
        resolution_spin = ttk.Spinbox(self.global_frame, from_=400, to=2000, increment=100,
                                    textvariable=self.resolution_var, width=15)
        resolution_spin.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)

    def setup_display(self):
        """Setup display area"""
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.text(0.5, 0.5, 'Welcome to AI-Enhanced Mathematical Art Studio\nSelect a pattern and click Generate',
                    ha='center', va='center', transform=self.ax.transAxes, fontsize=14)
        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, self.display_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Ready to create AI-guided mathematical art!")
        status_bar = ttk.Label(self.display_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=2)

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
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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

    def get_current_parameters(self) -> Dict[str, Any]:
        """Get current parameter values"""
        params = {}
        for param_name, widget_info in self.parameter_widgets.items():
            params[param_name] = widget_info['var'].get()
        return params

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

            self.status_var.set("Generating pattern...")
            self.generate_btn.config(state='disabled')
            self.root.update()

            params = self.get_current_parameters()
            image_array = self.current_generator.generate(**params)
            self.display_pattern(image_array)

        except Exception as e:
            error_msg = f"Error generating pattern: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Generation Error", error_msg)
        finally:
            self.generate_btn.config(state='normal')

    def display_pattern(self, image_array):
        """Display generated pattern"""
        try:
            self.current_image = image_array

            self.ax.clear()
            self.ax.imshow(image_array, aspect='equal')
            self.ax.axis('off')

            self.canvas.draw_idle()
            self.status_var.set("Pattern generated successfully!")

        except Exception as e:
            logger.error(f"Error displaying pattern: {e}")

    def toggle_animation(self):
        """Toggle multi-parameter animation"""
        if self.animation_running:
            self.stop_animation()
        else:
            self.start_animation()

    def start_animation(self):
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
            self.animate_btn.config(text="Stop Animation")
            
            self.animate_step()

        except Exception as e:
            logger.error(f"Error starting animation: {e}")

    def stop_animation(self):
        """Stop animation"""
        self.animation_running = False
        self.animate_btn.config(text="Start Animation")
        
        # Reset parameters to their original values
        for param_name, anim_param in self.animation_parameters.items():
            if param_name in self.parameter_widgets:
                self.parameter_widgets[param_name]['var'].set(anim_param.original_value)

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

    def animate_step(self):
        """Execute one animation step"""
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
            params = self.get_current_parameters()
            image_array = self.current_generator.generate(**params)
            self.display_pattern(image_array)

            self.animation_frame += 1
            
            # Schedule next frame
            if self.animation_running:
                self.root.after(50, self.animate_step)  # 20 FPS

        except Exception as e:
            logger.error(f"Animation error: {e}")
            self.stop_animation()

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

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = AdvancedArtStudio(root)

        def on_closing():
            logger.info("AI-Enhanced Art Studio closing")
            app.stop_animation()
            root.quit()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        logger.info("Starting AI-Enhanced Mathematical Art Studio")
        root.mainloop()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if 'root' in locals():
            messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")

if __name__ == "__main__":
    main()
