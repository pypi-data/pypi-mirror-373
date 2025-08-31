"""
Footer component for templates.
"""

from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from .base import Component
from dolze_image_templates.core.font_manager import get_font_manager


class FooterComponent(Component):
    """Component for rendering a footer"""

    def __init__(
        self,
        text: str,
        position: Optional[Tuple[int, int]] = None,
        font_size: int = 14,
        color: Tuple[int, int, int] = (100, 100, 100),
        bg_color: Optional[Tuple[int, int, int]] = None,
        padding: int = 10,
        font_path: Optional[str] = None,
    ):
        """
        Initialize a footer component.

        Args:
            text: Footer text
            position: Position (x, y) of the footer (if None, will be placed at bottom)
            font_size: Font size
            color: RGB color tuple for text
            bg_color: RGB color tuple for background (None for transparent)
            padding: Padding around the text
            font_path: Path to a TTF font file or font name
        """
        # If position is None, it will be calculated during render
        super().__init__(position if position else (0, 0))
        self.text = text
        self.font_size = font_size
        self.color = color
        self.bg_color = bg_color
        self.padding = padding
        self.font_path = font_path
        self._auto_position = position is None
        self._font = None

    def _get_font(self) -> ImageFont.FreeTypeFont:
        """Get the font for the footer text"""
        if self._font is None:
            font_manager = get_font_manager()
            self._font = font_manager.get_font(self.font_path, self.font_size)
        return self._font

    def render(self, image: Image.Image) -> Image.Image:
        """Render a footer onto an image"""
        if not self.text:
            return image

        result = image.copy()
        draw = ImageDraw.Draw(result)

        # Get the font
        font = self._get_font()

        # Calculate text size
        text_bbox = draw.textbbox((0, 0), self.text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate position if auto-positioned
        if self._auto_position:
            x = (image.width - text_width) // 2
            y = image.height - text_height - self.padding * 2
            self.position = (x, y)

        # Draw background if specified
        if self.bg_color is not None:
            bg_x1 = self.position[0] - self.padding
            bg_y1 = self.position[1] - self.padding
            bg_x2 = bg_x1 + text_width + self.padding * 2
            bg_y2 = bg_y1 + text_height + self.padding * 2

            draw.rectangle(
                [bg_x1, bg_y1, bg_x2, bg_y2],
                fill=self.bg_color,
                outline=None,
            )

        # Draw the text
        draw.text(
            self.position,
            self.text,
            font=font,
            fill=self.color,
        )

        return result

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "FooterComponent":
        """Create a footer component from a configuration dictionary"""
        position = None
        if "position" in config:
            position = (
                config["position"].get("x", 0),
                config["position"].get("y", 0),
            )

        # Handle colors which might be lists or tuples
        color = config.get("color", (100, 100, 100))
        if isinstance(color, (list, tuple)) and len(color) >= 3:
            color = tuple(color[:3])

        bg_color = config.get("bg_color")
        if (
            bg_color is not None
            and isinstance(bg_color, (list, tuple))
            and len(bg_color) >= 3
        ):
            bg_color = tuple(bg_color[:3])

        return cls(
            text=config.get("text", ""),
            position=position,
            font_size=config.get("font_size", 14),
            color=color,
            bg_color=bg_color,
            padding=config.get("padding", 10),
            font_path=config.get("font_path"),
        )
