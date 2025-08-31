"""
Button components for interactive elements in templates.
"""

from typing import Tuple, Optional, Dict, Any, Union
from PIL import Image, ImageDraw, ImageFont
from .base import Component
from dolze_image_templates.core.font_manager import get_font_manager


class CTAButtonComponent(Component):
    """Component for rendering CTA buttons"""

    def __init__(
        self,
        text: str,
        position: Tuple[int, int] = (0, 0),
        size: Optional[Tuple[int, int]] = None,
        bg_color: Union[Tuple[int, int, int], str] = (0, 123, 255),  # Can be RGB tuple or hex string
        text_color: Tuple[int, int, int] = (255, 255, 255),
        corner_radius: int = 10,
        font_size: int = 18,
        font_path: Optional[str] = None,
        url: Optional[str] = None,
        alignment: str = "center",
        auto_width: bool = False,
        padding: int = 40  # Horizontal padding on each side when auto_width is True
    ):
        """
        Initialize a CTA button component.

        Args:
            text: Button text
            position: Position (x, y) of the button
            size: Optional[Tuple[int, int]] = None. Size (width, height) of the button. 
                  If None, size will be calculated based on text content and padding.
            bg_color: RGB color tuple for button background
            text_color: RGB color tuple for button text
            corner_radius: Radius for rounded corners
            font_size: Font size in points
            font_path: Path to a TTF font file or font name
            url: URL to link to (for metadata)
        """
        super().__init__(position)
        self.text = text
        self.size = size
        
        # If size is not provided, calculate it based on text content
        if self.size is None and self.text:
            dummy_img = Image.new('RGB', (1, 1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            font = self._get_font()
            text_bbox = dummy_draw.textbbox((0, 0), self.text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            # Set default size with padding and minimum dimensions
            self.size = (text_width + 40, max(50, text_height + 20))
        # Convert hex color to RGB if needed
        if isinstance(bg_color, str) and bg_color.startswith('#'):
            self.bg_color = self._hex_to_rgb(bg_color)
        else:
            self.bg_color = bg_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.font_size = font_size
        self.font_path = font_path
        self.url = url
        self.alignment = alignment
        self.auto_width = auto_width
        self.padding = max(0, padding)  # Ensure padding is not negative
        self._font = None
        
        # Validate alignment
        if self.alignment not in ["left", "center", "right"]:
            print(f"Warning: Invalid alignment '{alignment}'. Defaulting to 'center'.")
            self.alignment = "center"
            
        # If auto_width is True, calculate the width based on text length
        if self.auto_width and self.text and self.size is not None:
            # Create a dummy image to calculate text size
            dummy_img = Image.new('RGB', (1, 1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            font = self._get_font()
            text_bbox = dummy_draw.textbbox((0, 0), self.text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            # Reduce padding for a tighter fit
            self.size = (text_width + self.padding, self.size[1])  # Removed *2 to have padding only on right side

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _get_font(self) -> ImageFont.FreeTypeFont:
        """Get the font for the button text"""
        if self._font is None:
            font_manager = get_font_manager()
            self._font = font_manager.get_font(self.font_path, self.font_size)
        return self._font

    def _draw_rounded_rect(
        self,
        draw: ImageDraw.Draw,
        bbox: Tuple[int, int, int, int],
        radius: int,
        **kwargs,
    ):
        """Draw a rounded rectangle"""
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        # Ensure radius is not larger than half the width or height
        radius = min(radius, width // 2, height // 2)
        
        # If radius is 0 or negative, just draw a regular rectangle
        if radius <= 0:
            draw.rectangle(bbox, **kwargs)
            return
            
        # Draw four rounded corners
        draw.ellipse((x1, y1, x1 + 2 * radius, y1 + 2 * radius), **kwargs)  # Top-left
        draw.ellipse((x2 - 2 * radius, y1, x2, y1 + 2 * radius), **kwargs)  # Top-right
        draw.ellipse(
            (x1, y2 - 2 * radius, x1 + 2 * radius, y2), **kwargs
        )  # Bottom-left
        draw.ellipse(
            (x2 - 2 * radius, y2 - 2 * radius, x2, y2), **kwargs
        )  # Bottom-right

        # Draw rectangles for the sides and center
        if width > 2 * radius:  # Only draw horizontal rectangle if there's space
            draw.rectangle((x1 + radius, y1, x2 - radius, y2), **kwargs)  # Horizontal
        if height > 2 * radius:  # Only draw vertical rectangle if there's space
            draw.rectangle((x1, y1 + radius, x2, y2 - radius), **kwargs)  # Vertical

    def render(self, image: Image.Image) -> Image.Image:
        """Render a CTA button onto an image"""
        result = image.copy()
        draw = ImageDraw.Draw(result, "RGBA")

        # Calculate button position and size
        x, y = self.position
        width, height = self.size
        bbox = [x, y, x + width, y + height]

        # Draw the button background with rounded corners
        self._draw_rounded_rect(
            draw,
            bbox,
            self.corner_radius,
            fill=self.bg_color + (255,),  # Add alpha channel
        )

        # Draw the button text
        font = self._get_font()
        text_width = draw.textlength(self.text, font=font)
        
        # Calculate text position based on alignment
        if self.alignment == "left":
            text_x = x + 20  # 10px padding from left
        elif self.alignment == "right":
            text_x = x + width - text_width - 20  # 10px padding from right
        else:  # center
            text_x = x + (width - text_width) // 2
            
        text_y = y + (height - self.font_size) // 2 - 6  # Small vertical adjustment

        draw.text(
            (text_x, text_y),
            self.text,
            font=font,
            fill=self.text_color,
        )

        return result

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "CTAButtonComponent":
        """Create a CTA button component from a configuration dictionary"""
        position = (
            config.get("position", {}).get("x", 0),
            config.get("position", {}).get("y", 0),
        )

        size = (
            config.get("size", {}).get("width", 200),
            config.get("size", {}).get("height", 50),
        )

        # Handle colors which might be lists or tuples
        bg_color = config.get("bg_color", (0, 123, 255))
        if isinstance(bg_color, (list, tuple)) and len(bg_color) >= 3:
            bg_color = tuple(bg_color[:3])

        text_color = config.get("text_color", (255, 255, 255))
        if isinstance(text_color, (list, tuple)) and len(text_color) >= 3:
            text_color = tuple(text_color[:3])

        return cls(
            text=config.get("text", "Click Here"),
            position=position,
            size=size,
            bg_color=bg_color,
            text_color=text_color,
            corner_radius=config.get("corner_radius", 10),
            font_size=config.get("font_size", 18),
            font_path=config.get("font_path"),
            url=config.get("url"),
            alignment=config.get("alignment", "center"),
            auto_width=config.get("auto_width", False),
            padding=config.get("padding", 40)
        )
