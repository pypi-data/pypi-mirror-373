"""
Base component module containing the abstract Component class.
"""
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from PIL import Image


class Component(ABC):
    """Base class for all template components"""

    def __init__(self, position: Tuple[int, int] = (0, 0)):
        """
        Initialize a component.

        Args:
            position: Position (x, y) of the component on the template
        """
        self.position = position

    @abstractmethod
    def render(self, image: Image.Image) -> Image.Image:
        """
        Render the component onto an image.

        Args:
            image: The image to render the component on

        Returns:
            The image with the component rendered on it
        """
        pass

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'Component':
        """
        Create a component from a configuration dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            A new component instance
        """
        position = (
            config.get("position", {}).get("x", 0),
            config.get("position", {}).get("y", 0),
        )
        return cls(position=position)
