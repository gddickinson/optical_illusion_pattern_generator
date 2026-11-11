"""
UI components for the Advanced Mathematical Art Studio.

Submodules:
- dialogs: DialogsMixin (shortcuts, about, pattern guide dialogs)

The main application class, AdvancedArtStudio, still lives in advanced_pattern_generator.py
(the planned ui/app.py was never extracted).
"""

from ui.dialogs import DialogsMixin

__all__ = ['DialogsMixin']
