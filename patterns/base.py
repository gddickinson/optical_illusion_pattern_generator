"""
Abstract base class for all pattern generators.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from typing import Dict, Any

from config import PatternConfig

logger = logging.getLogger(__name__)


class PatternGenerator(ABC):
    """Abstract base class for all pattern generators."""

    def __init__(self, config: PatternConfig):
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    def generate(self, **kwargs) -> np.ndarray:
        """Generate the pattern and return as numpy array."""
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Return dictionary of adjustable parameters for this pattern."""
        pass

    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters."""
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
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Parameter validation failed: {e}")
            return False

    def _fig_to_array(self, fig) -> np.ndarray:
        """Convert matplotlib figure to numpy array."""
        try:
            fig.canvas.draw()
            buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            return buf
        except Exception as e:
            logger.error(f"Error converting figure to array: {e}")
            raise
