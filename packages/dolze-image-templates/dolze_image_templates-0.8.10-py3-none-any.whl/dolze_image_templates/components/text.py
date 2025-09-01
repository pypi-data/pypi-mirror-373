"""
Text component for rendering text in templates.
"""

import os
import re
import random
from typing import Tuple, Optional, Dict, Any, Union
from PIL import Image, ImageDraw, ImageFont
from .base import Component
from dolze_image_templates.core.font_manager import get_font_manager


class TextComponent(Component):
    """Component for rendering text"""

    def __init__(
        self,
        text: str,
        position: Tuple[int, int] = (0, 0),
        font_size: int = 24,
        color: Tuple[int, int, int] = (0, 0, 0),
        max_width: Optional[int] = None,
        font_path: Optional[str] = None,
        alignment: str = "left",
        line_height: Optional[float] = None,
        underline: Optional[Union[bool, str]] = None,  # None/False: no underline, "normal", "funky"
        rotate: float = 0.0,
    ):
        """
        Initialize a text component.

        Args:
            text: Text to render
            position: Position (x, y) to place the text
            font_size: Font size in points
            color: RGB color tuple (0-255, 0-255, 0-255)
            max_width: Maximum width for text wrapping in pixels
            font_path: Path to a TTF/OTF font file or font name
            alignment: Text alignment ('left', 'center', 'right')
            line_height: Line height as a multiplier of font size (e.g., 1.2 for 120% of font size).
                       If None, a default of 1.2 will be used.
            underline: Whether to underline the text and which style to use
            rotate: Rotation angle in degrees (0-360)
        """
        super().__init__(position)
        self.text = text
        self.font_size = font_size
        self.color = color
        self.max_width = max_width
        self.font_path = font_path
        self.alignment = alignment.lower()
        self.line_height = line_height if line_height is not None else 1.2
        self.underline = str(underline).lower() if underline else None

        # Validate alignment and line height
        if self.alignment not in ["left", "center", "right"]:
            print(f"Warning: Invalid alignment '{alignment}'. Defaulting to 'left'.")
            self.alignment = "left"
            
        if self.line_height <= 0:
            print(f"Warning: Invalid line height {self.line_height}. Must be > 0. Defaulting to 1.2.")
            self.line_height = 1.2
            
        # Store and normalize rotation angle
        self.rotate = float(rotate) % 360

    def render(self, image: Image.Image) -> Image.Image:
        """Render text onto an image"""
        if not self.text:  # Skip rendering if text is None or empty
            return image

        result = image.copy()
        
        # If rotation is needed, we'll create a transparent layer for the text
        # then rotate it and paste it onto the result
        if self.rotate != 0:
            # Create a transparent layer for text rendering
            text_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(text_layer)
        else:
            draw = ImageDraw.Draw(result)

        # Use font manager to get the font
        font_manager = get_font_manager()
        font = font_manager.get_font(self.font_path, self.font_size)

        # Handle text wrapping if max_width is specified
        if self.max_width:
            lines = []
            words = self.text.split()

            if not words:
                return result

            current_line = words[0]

            for word in words[1:]:
                # Check if adding this word exceeds max_width
                test_line = current_line + " " + word
                text_width = draw.textlength(test_line, font=font)

                if text_width <= self.max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

            lines.append(current_line)

            # Draw each line with proper alignment
            y_offset = self.position[1]
            for line in lines:
                line_width = draw.textlength(line, font=font)

                # Calculate x position based on alignment
                if self.alignment == "center":
                    x = self.position[0] + (self.max_width - line_width) // 2
                elif self.alignment == "right":
                    x = self.position[0] + (self.max_width - line_width)
                else:  # left alignment (default)
                    x = self.position[0]

                # Draw text
                draw.text((x, y_offset), line, font=font, fill=self.color)
                
                # Draw underline if specified
                if self.underline:
                    self._draw_underline(draw, line, x, y_offset, font)
                
                # Calculate line spacing based on line height
                line_spacing = int(self.font_size * (self.line_height - 1) + 0.5)  # rounded to nearest int
                y_offset += self.font_size + line_spacing
        else:
            # For single line without max_width, just draw the text at the given position
            # (alignment doesn't apply as there's no width constraint)
            draw.text(self.position, self.text, font=font, fill=self.color)
            
            # Draw underline if specified for single line text
            if self.underline:
                self._draw_underline(draw, self.text, self.position[0], self.position[1], font)
        
        # Apply rotation if needed
        if self.rotate != 0:
            # Rotate the text layer
            rotated_text = text_layer.rotate(self.rotate, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))
            
            # Calculate the new position to maintain the text's original position after rotation
            # This is a simple approach - the text will rotate around its original position
            width, height = text_layer.size
            rotated_width, rotated_height = rotated_text.size
            paste_x = self.position[0] - (rotated_width - width) // 2
            paste_y = self.position[1] - (rotated_height - height) // 2
            
            # Paste the rotated text onto the result image
            result.paste(rotated_text, (paste_x, paste_y), rotated_text)

        return result

    @staticmethod
    def _parse_color(color: Union[str, list, tuple, None]) -> Tuple[int, int, int]:
        """Parse a color value from various formats to an RGB tuple.

        Args:
            color: Color value in one of these formats:
                - Hex string (e.g., "#FF0000" or "#F00")
                - List/tuple of RGB values (e.g., [255, 0, 0] or (255, 0, 0))
                - None (returns black)

        Returns:
            Tuple of (R, G, B) values in range 0-255
        """
        if color is None:
            return (0, 0, 0)

        # Handle hex color strings
        if isinstance(color, str) and color.startswith("#"):
            hex_color = color.lstrip("#")
            if len(hex_color) == 3:  # Short form (e.g. #ABC)
                hex_color = "".join([c * 2 for c in hex_color])
            try:
                # Convert hex to RGB
                return (
                    int(hex_color[0:2], 16),
                    int(hex_color[2:4], 16),
                    int(hex_color[4:6], 16),
                )
            except (ValueError, IndexError):
                return (0, 0, 0)

        # Handle RGB lists/tuples
        if isinstance(color, (list, tuple)) and len(color) >= 3:
            return tuple(int(c) for c in color[:3])

        return (0, 0, 0)  # Default to black if invalid

    def _draw_underline(self, draw: ImageDraw.Draw, text: str, x: int, y: int, font: ImageFont.FreeTypeFont) -> None:
        """Draw an underline for the given text.
        
        Args:
            draw: ImageDraw instance
            text: Text to underline
            x: X position of text
            y: Y position of text
            font: Font used for the text
        """
        # Get text metrics
        text_bbox = draw.textbbox((x, y), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Underline position (slightly below the text)
        underline_y = y + text_height + 12  # 2px below text
        
        draw.line([(x, underline_y), (x + text_width, underline_y)], 
                     fill=self.color, width=1)

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "TextComponent":
        """
        Create a text component from a configuration dictionary.
        
        Args:
            config: Dictionary containing text component configuration
            
        Returns:
            Configured TextComponent instance
            
        Config keys:
            - text: The text to display
            - position: Dict with x, y coordinates
            - font_size: Font size in points
            - color: Color as hex string or RGB list/tuple
            - max_width: Optional max width in pixels
            - font_path: Path to font file or font name
            - alignment: Text alignment ('left', 'center', 'right')
            - line_height: Optional line height multiplier (e.g., 1.5)
        """
        position = (
            config.get("position", {}).get("x", 0),
            config.get("position", {}).get("y", 0),
        )

        # Handle color which might be a hex string, list, or tuple
        color = cls._parse_color(config.get("color", (0, 0, 0)))

        return cls(
            text=config.get("text", ""),
            position=position,
            font_size=config.get("font_size", 24),
            color=color,
            max_width=config.get("max_width"),
            font_path=config.get("font_path"),
            alignment=config.get("alignment", "left"),
            line_height=config.get("line_height"),
            underline=config.get("underline"),
            rotate=float(config.get("rotate", 0.0)),
        )
