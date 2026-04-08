"""
Configuration and color management for the Advanced Mathematical Art Studio.

Contains PatternConfig dataclass and ColorManager utility class.
"""

import colorsys
from dataclasses import dataclass
from typing import List


@dataclass
class PatternConfig:
    """Configuration class for pattern parameters."""
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
    """Advanced color management and palette generation."""

    PALETTES = {
        'default': ["red", "blue", "green", "purple", "orange", "cyan", "magenta", "yellow"],
        'sunset': ["#FF6B35", "#F7931E", "#FFD23F", "#EE4B6A", "#963D97", "#009DDC"],
        'ocean': ["#003F5C", "#2F4B7C", "#665191", "#A05195", "#D45087", "#F95D6A", "#FF7C43", "#FFA600"],
        'forest': ["#1B4332", "#2D5016", "#40531B", "#52734D", "#74A892", "#B7CE63"],
        'cosmic': ["#0B0C10", "#1F2833", "#C5C6C7", "#66FCF1", "#45A29E", "#FF6B6B"],
        'fire': ["#8B0000", "#DC143C", "#FF4500", "#FF6347", "#FFD700", "#FFFF00"],
        'ice': ["#E0F6FF", "#87CEEB", "#4682B4", "#1E90FF", "#0000FF", "#000080"],
        'earth': ["#8B4513", "#A0522D", "#CD853F", "#D2B48C", "#F4A460", "#DEB887"],
        'neon': ["#FF0080", "#00FF80", "#8000FF", "#FF8000", "#0080FF", "#80FF00"],
        'pastel': ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", "#E1BAFF"],
    }

    @staticmethod
    def get_palette(palette_name: str, num_colors: int = 8) -> List[str]:
        """Get color palette by name."""
        if palette_name in ColorManager.PALETTES:
            colors = ColorManager.PALETTES[palette_name]
            return (colors * ((num_colors // len(colors)) + 1))[:num_colors]
        else:
            return ColorManager.generate_hsv_palette(num_colors)

    @staticmethod
    def generate_hsv_palette(num_colors: int, saturation: float = 0.8,
                             value: float = 0.9) -> List[str]:
        """Generate HSV-based color palette."""
        colors = []
        for i in range(num_colors):
            hue = i / num_colors
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            hex_color = '#%02x%02x%02x' % (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            colors.append(hex_color)
        return colors

    @staticmethod
    def interpolate_colors(color1: str, color2: str, steps: int) -> List[str]:
        """Interpolate between two hex colors."""
        c1 = [int(color1[i:i + 2], 16) for i in (1, 3, 5)]
        c2 = [int(color2[i:i + 2], 16) for i in (1, 3, 5)]

        colors = []
        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            colors.append(f'#{r:02x}{g:02x}{b:02x}')
        return colors
