"""
Quick-preset data shared by the desktop GUIs and the web interface.

Each preset names the GUI pattern (the key of the app's ``generators`` dict), the
parameter values it sets and the global settings it changes. The values are exactly
those of the original ``load_*_preset`` methods; the GUIs now apply them with
``apply_preset(app, key)`` and the web interface reads the same table.

- app 'v2': optical_illusion_generator_V2.py ("Quick Presets" buttons)
- app 'advanced': advanced_pattern_generator.py ("Art Presets" menu)
"""

import logging

logger = logging.getLogger(__name__)

PRESETS = {
    # optical_illusion_generator_V2.py
    'golden_spiral': {
        'name': 'Golden Spiral', 'app': 'v2', 'pattern': 'Spiral',
        'params': {'spiral_type': 'fibonacci', 'arms': 1, 'gradient_effect': 'radial',
                   'line_variation': 'increasing'},
        'globals': {'color_mode': 'color', 'custom_colors': ['gold', 'orange', 'darkorange']},
    },
    'fractal_art': {
        'name': 'Fractal Art', 'app': 'v2', 'pattern': 'Fractal',
        'params': {'fractal_type': 'mandelbrot', 'iterations': 200, 'color_scheme': 'rainbow'},
        'globals': {'color_mode': 'color', 'resolution': 2000},
    },
    'op_art': {
        'name': 'Op Art', 'app': 'v2', 'pattern': 'Optical Illusion',
        'params': {'illusion_type': 'rotating_snakes', 'intensity': 1.5, 'contrast': 0.9},
        'globals': {'color_mode': 'black_white', 'background_color': 'white', 'foreground_color': 'black'},
    },
    'psychedelic': {
        'name': 'Psychedelic', 'app': 'v2', 'pattern': 'Spiral',
        'params': {'overlapping_spirals': 4, 'gradient_effect': 'angular', 'arms': 8},
        'globals': {'color_mode': 'color',
                    'custom_colors': ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta']},
    },
    # advanced_pattern_generator.py
    'islamic_art': {
        'name': 'Islamic Art', 'app': 'advanced', 'pattern': 'Islamic Geometry',
        'params': {'pattern_type': 'octagon_star', 'interlace': 'complex'},
        'globals': {'color_mode': 'color', 'color_palette': 'earth'},
    },
    'organic_flow': {
        'name': 'Organic Flow', 'app': 'advanced', 'pattern': 'Voronoi Diagrams',
        'params': {'distribution': 'poisson', 'color_by': 'distance'},
        'globals': {'color_mode': 'color', 'color_palette': 'forest'},
    },
    'digital_grid': {
        'name': 'Digital Grid', 'app': 'advanced', 'pattern': 'Cellular Automata',
        'params': {'automata_type': 'rule_110', 'visualization': 'evolution'},
        'globals': {'color_mode': 'color', 'color_palette': 'neon'},
    },
    'nature_patterns': {
        'name': 'Nature Patterns', 'app': 'advanced', 'pattern': 'Tessellations',
        'params': {'tessellation_type': 'hexagonal', 'irregularity': 0.2},
        'globals': {'color_mode': 'color', 'color_palette': 'forest'},
    },
    'cosmic_spiral': {
        'name': 'Cosmic Spiral', 'app': 'advanced', 'pattern': 'Spiral',
        'params': {'spiral_type': 'logarithmic', 'overlapping_spirals': 3, 'gradient_effect': 'angular'},
        'globals': {'color_mode': 'color', 'color_palette': 'cosmic'},
    },
    'crystal_growth': {
        'name': 'Crystal Growth', 'app': 'advanced', 'pattern': 'Voronoi Diagrams',
        'params': {'distribution': 'fibonacci', 'style': 'filled', 'relaxation_steps': 3},
        'globals': {'color_mode': 'color', 'color_palette': 'ice'},
    },
}


def apply_preset(app, key):
    """Apply PRESETS[key] to a running tkinter app (V2 or advanced), as the old load_*_preset methods did."""
    preset = PRESETS[key]
    app.pattern_var.set(preset['pattern'])
    app.on_pattern_change()
    for name, value in preset['params'].items():
        if name in app.parameter_widgets:
            app.parameter_widgets[name]['var'].set(value)
    g = preset['globals']
    if 'color_mode' in g:
        app.color_mode_var.set(g['color_mode'])
    if 'color_palette' in g:
        app.palette_var.set(g['color_palette'])
    if 'resolution' in g:
        app.resolution_var.set(g['resolution'])
    if 'custom_colors' in g:
        app.config.custom_colors = list(g['custom_colors'])
    for attr in ('background_color', 'foreground_color'):
        if attr in g:
            setattr(app.config, attr, g[attr])
    logger.info(f"Loaded {preset['name']} preset")
