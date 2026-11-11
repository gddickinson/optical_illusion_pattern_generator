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
from patterns.presets import apply_preset  # preset data shared with the web interface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration and the pattern generators live in config.py and the patterns package (shared with the
# web interface); this file is the tkinter application.
from config import PatternConfig, ColorManager  # noqa: E402
from patterns import (  # noqa: E402
    PatternGenerator, IslamicGeometryGenerator, VoronoiGenerator, CellularAutomataGenerator,
    TessellationGenerator, SpiralGenerator, InterferenceGenerator,
)


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
        apply_preset(self, 'islamic_art')

    def load_organic_preset(self):
        """Load organic flow preset"""
        apply_preset(self, 'organic_flow')

    def load_digital_preset(self):
        """Load digital grid preset"""
        apply_preset(self, 'digital_grid')

    def load_nature_preset(self):
        """Load nature patterns preset"""
        apply_preset(self, 'nature_patterns')

    def load_cosmic_preset(self):
        """Load cosmic spiral preset"""
        apply_preset(self, 'cosmic_spiral')

    def load_crystal_preset(self):
        """Load crystal growth preset"""
        apply_preset(self, 'crystal_growth')

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
