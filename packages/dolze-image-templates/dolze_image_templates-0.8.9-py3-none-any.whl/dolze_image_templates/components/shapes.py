"""
Shape components for rendering basic shapes in templates with gradient support.
"""

from typing import Tuple, Optional, Dict, Any, List, Union
from PIL import Image, ImageDraw, ImageFont
import colorsys
import re
import os
from .base import Component
from dolze_image_templates.core.font_manager import get_font_manager


class GradientUtils:
    """Utility class for handling gradient operations"""

    @staticmethod
    def parse_color(color: Union[str, List, Tuple]) -> Tuple[int, int, int, int]:
        """
        Parse color from various formats to RGBA tuple.

        Args:
            color: Color in hex (#FF0000), rgba list [255, 0, 0, 1], or rgb tuple (255, 0, 0)

        Returns:
            RGBA tuple (r, g, b, a) where a is 0-255
        """
        if isinstance(color, str):
            # Handle hex colors
            color = color.lstrip("#")
            if len(color) == 3:
                color = "".join([c * 2 for c in color])
            if len(color) == 6:
                r, g, b = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
                return (r, g, b, 255)
            elif len(color) == 8:
                r, g, b, a = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4, 6))
                return (r, g, b, a)

        elif isinstance(color, (list, tuple)):
            if len(color) >= 3:
                r, g, b = int(color[0]), int(color[1]), int(color[2])
                a = int(color[3] * 255) if len(color) > 3 else 255
                # Handle normalized RGBA values (0-1 range)
                if all(isinstance(c, float) and 0 <= c <= 1 for c in color[:3]):
                    r, g, b = int(r * 255), int(g * 255), int(b * 255)
                return (r, g, b, a)

        # Default to black if parsing fails
        return (0, 0, 0, 255)

    @staticmethod
    def interpolate_color(
        color1: Tuple[int, int, int, int], color2: Tuple[int, int, int, int], t: float
    ) -> Tuple[int, int, int, int]:
        """
        Interpolate between two RGBA colors.

        Args:
            color1: First color as RGBA tuple
            color2: Second color as RGBA tuple
            t: Interpolation factor (0.0 to 1.0)

        Returns:
            Interpolated RGBA color
        """
        r1, g1, b1, a1 = color1
        r2, g2, b2, a2 = color2

        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        a = int(a1 + (a2 - a1) * t)

        return (r, g, b, a)

    @staticmethod
    def create_linear_gradient(
        size: Tuple[int, int],
        colors: List[Tuple[int, int, int, int]],
        direction: float = 0,
    ) -> Image.Image:
        """
        Create a linear gradient image.

        Args:
            size: Size of the gradient image (width, height)
            colors: List of RGBA color tuples
            direction: Gradient direction in degrees (0 = horizontal, 90 = vertical)

        Returns:
            PIL Image with linear gradient
        """
        width, height = size
        gradient = Image.new("RGBA", size)

        # Convert direction to radians
        angle = direction * 3.14159 / 180

        # Calculate gradient vector
        cos_a = abs(cos(angle)) if "cos" in dir(__builtins__) else abs(direction / 90)
        sin_a = (
            abs(sin(angle)) if "sin" in dir(__builtins__) else abs(1 - direction / 90)
        )

        # Simplified gradient calculation
        for y in range(height):
            for x in range(width):
                # Calculate position along gradient (0.0 to 1.0)
                if direction == 0:  # Horizontal
                    t = x / width
                elif direction == 90:  # Vertical
                    t = y / height
                else:  # Diagonal approximation
                    t = (x * cos_a + y * sin_a) / (width * cos_a + height * sin_a)

                t = max(0, min(1, t))

                # Find which color segment we're in
                segment = t * (len(colors) - 1)
                idx = int(segment)
                local_t = segment - idx

                if idx >= len(colors) - 1:
                    color = colors[-1]
                else:
                    color = GradientUtils.interpolate_color(
                        colors[idx], colors[idx + 1], local_t
                    )

                gradient.putpixel((x, y), color)

        return gradient

    @staticmethod
    def create_radial_gradient(
        size: Tuple[int, int],
        colors: List[Tuple[int, int, int, int]],
        center: Optional[Tuple[float, float]] = None,
    ) -> Image.Image:
        """
        Create a radial gradient image.

        Args:
            size: Size of the gradient image (width, height)
            colors: List of RGBA color tuples
            center: Center point as (x, y) ratios (0.0 to 1.0), defaults to (0.5, 0.5)

        Returns:
            PIL Image with radial gradient
        """
        width, height = size
        gradient = Image.new("RGBA", size)

        if center is None:
            center = (0.5, 0.5)

        center_x = center[0] * width
        center_y = center[1] * height

        # Calculate maximum distance from center to corners
        max_dist = max(
            ((0 - center_x) ** 2 + (0 - center_y) ** 2) ** 0.5,
            ((width - center_x) ** 2 + (0 - center_y) ** 2) ** 0.5,
            ((0 - center_x) ** 2 + (height - center_y) ** 2) ** 0.5,
            ((width - center_x) ** 2 + (height - center_y) ** 2) ** 0.5,
        )

        for y in range(height):
            for x in range(width):
                # Calculate distance from center
                dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                t = min(1.0, dist / max_dist)

                # Find which color segment we're in
                segment = t * (len(colors) - 1)
                idx = int(segment)
                local_t = segment - idx

                if idx >= len(colors) - 1:
                    color = colors[-1]
                else:
                    color = GradientUtils.interpolate_color(
                        colors[idx], colors[idx + 1], local_t
                    )

                gradient.putpixel((x, y), color)

        return gradient


class CircleComponent(Component):
    """Component for rendering circles with optional background images and gradients"""

    def __init__(
        self,
        position: Tuple[int, int] = (0, 0),
        radius: int = 50,
        fill_color: Optional[Tuple[int, int, int]] = (200, 200, 200),
        outline_color: Optional[Tuple[int, int, int]] = None,
        outline_width: int = 2,
        image_url: Optional[str] = None,
        image_path: Optional[str] = None,
        gradient_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a circle component.

        Args:
            position: Position (x, y) of the center of the circle
            radius: Radius of the circle in pixels
            fill_color: RGB color tuple for the circle fill (None for transparent)
            outline_color: RGB color tuple for the circle outline (None for no outline)
            outline_width: Width of the outline in pixels
            image_url: URL of an image to display inside the circle
            image_path: Path to a local image file to display inside the circle
            gradient_config: Configuration for gradient background
        """
        super().__init__(position)
        self.radius = radius
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.image_url = image_url
        self.image_path = image_path
        self.gradient_config = gradient_config
        self._cached_image = None

    def _load_image(self) -> Optional[Image.Image]:
        """Load image from URL or path if not already loaded"""
        if self._cached_image is not None:
            return self._cached_image

        # Try to load from URL first, then from path
        if self.image_url:
            try:
                response = requests.get(self.image_url)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                self._cached_image = img.convert("RGBA")
                return self._cached_image
            except (requests.RequestException, IOError):
                pass

        if self.image_path and os.path.exists(self.image_path):
            try:
                img = Image.open(self.image_path)
                self._cached_image = img.convert("RGBA")
                return self._cached_image
            except IOError:
                pass

        return None

    def _create_gradient_fill(self) -> Optional[Image.Image]:
        """Create gradient fill image for the circle"""
        if not self.gradient_config:
            return None

        gradient_type = self.gradient_config.get("type", "linear")
        colors_config = self.gradient_config.get("colors", [])

        if not colors_config:
            return None

        # Parse colors
        colors = [GradientUtils.parse_color(color) for color in colors_config]

        # Create gradient image
        size = (self.radius * 2, self.radius * 2)

        if gradient_type == "radial":
            center = self.gradient_config.get("center", (0.5, 0.5))
            gradient_img = GradientUtils.create_radial_gradient(size, colors, center)
        else:  # linear
            direction = self.gradient_config.get("direction", 0)
            gradient_img = GradientUtils.create_linear_gradient(size, colors, direction)

        return gradient_img

    def render(self, image: Image.Image) -> Image.Image:
        """Render the circle onto an image"""
        result = image.copy()
        draw = ImageDraw.Draw(result)

        # Calculate bounding box
        x, y = self.position
        bbox = [
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
        ]

        # Check if we should use gradient
        gradient_img = self._create_gradient_fill()

        if gradient_img:
            # Create circular mask
            mask = Image.new("L", (self.radius * 2, self.radius * 2), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, self.radius * 2, self.radius * 2), fill=255)

            # Apply gradient with circular mask
            result.paste(gradient_img, (x - self.radius, y - self.radius), mask)
        elif self.fill_color is not None:
            # Draw solid color circle
            draw.ellipse(bbox, fill=self.fill_color)

        # Draw outline
        if self.outline_color is not None and self.outline_width > 0:
            draw.ellipse(bbox, outline=self.outline_color, width=self.outline_width)

        # If there's an image, draw it inside the circle
        img = self._load_image()
        if img is not None:
            # Resize image to fit the circle
            size = (self.radius * 2, self.radius * 2)
            img = img.resize(size, Image.Resampling.LANCZOS)

            # Create circular mask
            mask = Image.new("L", size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, size[0], size[1]), fill=255)

            # Apply mask and paste
            result.paste(img, (x - self.radius, y - self.radius), mask)

        return result

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "CircleComponent":
        """Create a circle component from a configuration dictionary"""
        position = (
            config.get("position", {}).get("x", 0),
            config.get("position", {}).get("y", 0),
        )

        # Handle color which might be a list or tuple
        fill_color = config.get("fill_color")
        if (
            fill_color
            and isinstance(fill_color, (list, tuple))
            and len(fill_color) >= 3
        ):
            fill_color = tuple(fill_color[:3])

        outline_color = config.get("outline_color")
        if (
            outline_color
            and isinstance(outline_color, (list, tuple))
            and len(outline_color) >= 3
        ):
            outline_color = tuple(outline_color[:3])

        return cls(
            position=position,
            radius=config.get("radius", 50),
            fill_color=fill_color,
            outline_color=outline_color,
            outline_width=config.get("outline_width", 2),
            image_url=config.get("image_url"),
            image_path=config.get("image_path"),
            gradient_config=config.get("gradient"),
        )


class RectangleComponent(Component):
    """Component for rendering rectangles with gradient support"""

    def __init__(
        self,
        position: Tuple[int, int] = (0, 0),
        size: Tuple[int, int] = (100, 50),
        fill_color: Optional[Tuple[int, int, int]] = None,
        outline_color: Optional[Tuple[int, int, int]] = None,
        outline_width: int = 1,
        border_radius: int = 0,
        gradient_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a rectangle component.

        Args:
            position: Position (x, y) of the top-left corner
            size: Size (width, height) of the rectangle
            fill_color: RGB color tuple for the fill color (None for transparent)
            outline_color: RGB color tuple for the outline (None for no outline)
            outline_width: Width of the outline in pixels
            border_radius: Radius of the corners in pixels (0 for square corners)
            gradient_config: Configuration for gradient background
        """
        super().__init__(position)
        self.size = size
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.border_radius = border_radius
        self.gradient_config = gradient_config

    def _create_gradient_fill(self) -> Optional[Image.Image]:
        """Create gradient fill image for the rectangle"""
        if not self.gradient_config:
            return None

        gradient_type = self.gradient_config.get("type", "linear")
        colors_config = self.gradient_config.get("colors", [])

        if not colors_config:
            return None

        # Parse colors
        colors = [GradientUtils.parse_color(color) for color in colors_config]

        # Create gradient image
        if gradient_type == "radial":
            center = self.gradient_config.get("center", (0.5, 0.5))
            gradient_img = GradientUtils.create_radial_gradient(
                self.size, colors, center
            )
        else:  # linear
            direction = self.gradient_config.get("direction", 0)
            gradient_img = GradientUtils.create_linear_gradient(
                self.size, colors, direction
            )

        return gradient_img

    def render(self, image: Image.Image) -> Image.Image:
        """
        Render a rectangle onto an image.

        Args:
            image: The image to render the rectangle on

        Returns:
            The image with the rectangle rendered on it
        """
        print(f"\n=== RENDERING RECTANGLE ===")
        print(f"Position: {self.position}")
        print(f"Size: {self.size}")
        print(f"Fill color: {self.fill_color}")
        print(f"Outline color: {self.outline_color}")
        print(f"Border radius: {self.border_radius}")
        print(f"Image mode: {image.mode}")
        
        result = image.copy()
        draw = ImageDraw.Draw(result)

        # Calculate bounding box
        x, y = self.position
        width, height = self.size
        bbox = [x, y, x + width, y + height]
        print(f"Bounding box: {bbox}")

        # Check if we should use gradient
        gradient_img = self._create_gradient_fill()
        print(f"Using gradient: {'Yes' if gradient_img else 'No'}")

        if gradient_img:
            if self.border_radius > 0:
                # Create rounded rectangle mask
                mask = Image.new("L", self.size, 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rounded_rectangle(
                    (0, 0, width, height), radius=self.border_radius, fill=255
                )
                result.paste(gradient_img, self.position, mask)
            else:
                # Simple rectangular paste
                result.paste(gradient_img, self.position)
        else:
            # Draw with solid color or transparent
            if self.border_radius > 0:
                print(f"Drawing rounded rectangle with radius {self.border_radius} and fill {self.fill_color}")
                draw.rounded_rectangle(
                    bbox,
                    radius=self.border_radius,
                    fill=self.fill_color,
                    outline=None,
                    width=0,
                )
            else:
                print(f"Drawing rectangle with fill {self.fill_color}")
                draw.rectangle(bbox, fill=self.fill_color, outline=None, width=0)

        # Draw outline
        if self.outline_color and self.outline_width > 0:
            half_width = self.outline_width // 2
            outline_bbox = [
                bbox[0] + half_width,
                bbox[1] + half_width,
                bbox[2] - half_width - 1,  # -1 to account for 0-based indexing
                bbox[3] - half_width - 1,
            ]
            print(f"Drawing outline with color {self.outline_color} and width {self.outline_width}")
            draw.rounded_rectangle(
                outline_bbox,
                radius=max(0, self.border_radius - self.outline_width // 2),
                outline=self.outline_color,
                width=self.outline_width,
            )
        elif self.outline_color:
            print(f"Drawing outline with color {self.outline_color} and default width")
            draw.rectangle(
                bbox, outline=self.outline_color, width=self.outline_width
            )
        else:
            print("No outline to draw")

        return result

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "RectangleComponent":
        """
        Create a rectangle component from a configuration dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            A new RectangleComponent instance
        """
        # Handle position - support both {x, y} and direct x, y in the root
        if "position" in config:
            position = (
                config["position"].get("x", 0) if isinstance(config["position"], dict) else 0,
                config["position"].get("y", 0) if isinstance(config["position"], dict) else 0
            )
        else:
            # Support direct x, y in the root for backward compatibility
            position = (
                config.get("x", 0),
                config.get("y", 0)
            )

        # Handle size - support both {width, height} and direct width, height in the root
        if "size" in config and isinstance(config["size"], dict):
            size = (
                config["size"].get("width", 100),
                config["size"].get("height", 50)
            )
        else:
            # Support direct width, height in the root for backward compatibility
            size = (
                config.get("width", 100),
                config.get("height", 50)
            )

        # Handle fill_color - support both string and list/tuple formats
        fill_color = config.get("fill_color")
        if fill_color is not None:
            if isinstance(fill_color, str):
                # Handle hex color strings
                if fill_color.startswith('#'):
                    try:
                        fill_color = tuple(int(fill_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    except (ValueError, IndexError):
                        fill_color = None
            elif isinstance(fill_color, (list, tuple)) and len(fill_color) >= 3:
                fill_color = tuple(fill_color[:3])
            else:
                fill_color = None

        # Handle outline_color - support both string and list/tuple formats
        outline_color = config.get("outline_color")
        if outline_color is not None:
            if isinstance(outline_color, str):
                # Handle hex color strings
                if outline_color.startswith('#'):
                    try:
                        outline_color = tuple(int(outline_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    except (ValueError, IndexError):
                        outline_color = None
            elif isinstance(outline_color, (list, tuple)) and len(outline_color) >= 3:
                outline_color = tuple(outline_color[:3])
            else:
                outline_color = None

        # Get other properties with defaults
        outline_width = config.get("outline_width", 1)
        border_radius = config.get("border_radius", 0)
        gradient_config = config.get("gradient")

        # Debug output
        print(f"\n=== CREATING RECTANGLE COMPONENT ===")
        print(f"Position: {position}")
        print(f"Size: {size}")
        print(f"Fill color: {fill_color}")
        print(f"Outline color: {outline_color}")
        print(f"Outline width: {outline_width}")
        print(f"Border radius: {border_radius}")
        print(f"Gradient config: {gradient_config is not None}")

        return cls(
            position=position,
            size=size,
            fill_color=fill_color,
            outline_color=outline_color,
            outline_width=outline_width,
            border_radius=border_radius,
            gradient_config=gradient_config,
        )


class RibbonFrame(Component):
    """Component for rendering a ribbon frame with text inside.
    
    The ribbon will automatically adjust its width based on the text content.
    """
    
    def __init__(
        self,
        text: str,
        position: Tuple[int, int] = (0, 0),
        font_size: int = 24,
        font_path: Optional[str] = None,
        text_color: Tuple[int, int, int] = (255, 255, 255),
        fill_color: Tuple[int, int, int] = (255, 0, 0),
        outline_color: Optional[Tuple[int, int, int]] = None,
        padding: int = 20,
        pointer_size: int = 20,
        rotation: int = 0,
        triangle_direction: str = 'open',
    ):
        """
        Initialize a ribbon frame component.
        
        Args:
            text: Text to display in the ribbon
            position: Position (x, y) of the ribbon's top-left corner
            font_size: Font size in points
            font_path: Path to a custom font file
            text_color: RGB color tuple for the text
            fill_color: RGB color tuple for the ribbon
            outline_color: RGB color tuple for the outline (None for no outline)
            padding: Padding around the text in pixels
            pointer_size: Size of the ribbon's pointer in pixels
        """
        super().__init__(position)
        self.text = text
        self.font_size = font_size
        self.font_path = font_path
        self.text_color = text_color
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.padding = padding
        self.pointer_size = pointer_size
        self.rotation = rotation % 360  # Normalize to 0-359 degrees
        self.triangle_direction = triangle_direction.lower()  # 'open' or 'closed'
        if self.triangle_direction not in ['open', 'closed']:
            raise ValueError("triangle_direction must be either 'open' or 'closed'")
        self._font = None
        self._ribbon_image = None  # Cached ribbon image
    
    def _get_font(self) -> ImageFont.FreeTypeFont:
        """Get the font with the specified size"""
        if self._font is None:
            font_manager = get_font_manager()
            if self.font_path and os.path.exists(self.font_path):
                self._font = ImageFont.truetype(self.font_path, self.font_size)
            else:
                font_name = self.font_path or "Montserrat-Bold"
                self._font = font_manager.get_font(font_name, self.font_size)
        return self._font
    
    def _get_text_size(self) -> Tuple[int, int]:
        """Calculate the size of the text with padding"""
        font = self._get_font()
        dummy_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        bbox = draw.textbbox((0, 0), self.text, font=font)
        return (
            bbox[2] - bbox[0] + self.padding * 2,
            bbox[3] - bbox[1] + self.padding * 2
        )
    
    def _generate_ribbon_image(self) -> Image.Image:
        """Generate the ribbon image with text"""
        if not self.text:
            return None
            
        # Calculate text size with padding
        text_bbox = self._get_font().getbbox(self.text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Create a new image for the ribbon with extra space for rotation
        ribbon_width = text_width + self.padding * 2 + self.pointer_size * 2
        ribbon_height = text_height + self.padding * 2
        
        # Create points for the ribbon shape based on triangle direction
        if self.triangle_direction == 'open':
            points = [
                (0, ribbon_height // 2),  # Left middle
                (self.pointer_size, 0),  # Top-left pointer
                (ribbon_width - self.pointer_size, 0),  # Top-right before pointer
                (ribbon_width, ribbon_height // 2),  # Right middle
                (ribbon_width - self.pointer_size, ribbon_height),  # Bottom-right before pointer
                (self.pointer_size, ribbon_height),  # Bottom-left pointer
            ]
        else:  # 'closed' - triangles point inwards
            points = [
                (0, 0),  # Top-left corner
                (ribbon_width, 0),  # Top-right corner
                (ribbon_width - self.pointer_size, ribbon_height // 2),  # Right middle
                (ribbon_width, ribbon_height),  # Bottom-right corner
                (0, ribbon_height),  # Bottom-left corner
                (self.pointer_size, ribbon_height // 2),  # Left middle
            ]
        
        # Create a new image for the ribbon with transparency
        ribbon_img = Image.new('RGBA', (ribbon_width, ribbon_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(ribbon_img)
        
        # Draw the ribbon
        draw.polygon(points, fill=tuple(self.fill_color), outline=self.outline_color)
        
        # Draw the text
        font = self._get_font()
        text_x = (ribbon_width - text_width) // 2 - text_bbox[0]
        text_y = (ribbon_height - text_height) // 2 - text_bbox[1]
        
        draw.text(
            (text_x, text_y),
            self.text,
            fill=tuple(self.text_color),
            font=font,
            align='center'
        )
        
        # Apply rotation if needed
        if self.rotation != 0:
            # Expand the image to fit the rotated ribbon
            expanded_size = (
                int(ribbon_width * 1.5),
                int(ribbon_height * 1.5)
            )
            expanded_img = Image.new('RGBA', expanded_size, (0, 0, 0, 0))
            # Center the ribbon in the expanded image
            pos = (
                (expanded_size[0] - ribbon_width) // 2,
                (expanded_size[1] - ribbon_height) // 2
            )
            expanded_img.paste(ribbon_img, pos, ribbon_img)
            # Rotate around the center
            rotated = expanded_img.rotate(
                -self.rotation,  # Negative because PIL uses CCW rotation
                expand=True,
                resample=Image.BICUBIC
            )
            return rotated
            
        return ribbon_img

    def render(self, image: Image.Image) -> Image.Image:
        """
        Render the ribbon with text onto an image.
        
        Args:
            image: The image to render the ribbon on
            
        Returns:
            The image with the ribbon rendered on it
        """
        if not self.text:
            return image
            
        # Generate or use cached ribbon image
        if self._ribbon_image is None:
            self._ribbon_image = self._generate_ribbon_image()
            if self._ribbon_image is None:
                return image
        
        # Calculate position to center the ribbon
        x = self.position[0] - (self._ribbon_image.width // 2)
        y = self.position[1] - (self._ribbon_image.height // 2)
        
        # Paste the ribbon onto the original image
        image.alpha_composite(self._ribbon_image, (x, y))
        return image
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'RibbonFrame':
        """
        Create a ribbon frame component from a configuration dictionary.
        
        Args:
            config: Configuration dictionary with the following structure:
                {
                    "text": "Ribbon Text",
                    "position": {"x": 0, "y": 0},
                    "font_size": 24,
                    "font_path": "path/to/font.ttf",  # optional
                    "text_color": [255, 255, 255],
                    "fill_color": [255, 0, 0],
                    "outline_color": [0, 0, 0],  # optional
                    "padding": 20,
                    "pointer_size": 20,
                    "rotation": 0,  # Rotation in degrees (0-360)
                    "triangle_direction": "open"  # 'open' (triangles out) or 'closed' (triangles in)
                }
                
        Returns:
            A new RibbonFrame instance
        """
        position = (
            config.get("position", {}).get("x", 0),
            config.get("position", {}).get("y", 0),
        )
        
        return cls(
            text=config.get("text", ""),
            position=position,
            font_size=config.get("font_size", 24),
            font_path=config.get("font_path"),
            text_color=tuple(config.get("text_color", (255, 255, 255))),
            fill_color=tuple(config.get("fill_color", (255, 0, 0))),
            outline_color=tuple(config.get("outline_color")) if config.get("outline_color") else None,
            padding=config.get("padding", 20),
            pointer_size=config.get("pointer_size", 20),
            rotation=config.get("rotation", 0),
            triangle_direction=config.get("triangle_direction", "open")
        )


class PolygonComponent(Component):
    """Component for rendering polygons (triangles, etc.) with gradient support"""

    def __init__(
        self,
        position: Tuple[int, int] = (0, 0),
        points: Optional[List[Tuple[int, int]]] = None,
        fill_color: Optional[Union[Tuple[int, int, int], Tuple[int, int, int, int]]] = None,
        outline_color: Optional[Union[Tuple[int, int, int], Tuple[int, int, int, int]]] = None,
        outline_width: int = 1,
        gradient_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a polygon component.

        Args:
            position: Position (x, y) offset for all points
            points: List of (x, y) points relative to position
            fill_color: RGB or RGBA color tuple for the fill color (None for transparent).
                      For RGBA, the alpha channel should be between 0 (transparent) and 255 (opaque).
            outline_color: RGB or RGBA color tuple for the outline (None for no outline).
                         For RGBA, the alpha channel should be between 0 (transparent) and 255 (opaque).
            outline_width: Width of the outline in pixels
            gradient_config: Configuration for gradient background
        """
        super().__init__(position)
        self.points = points or []
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.gradient_config = gradient_config

    def _get_polygon_bounds(self) -> Tuple[int, int, int, int]:
        """Get bounding box of the polygon"""
        if not self.points:
            return (0, 0, 0, 0)

        x_offset, y_offset = self.position
        absolute_points = [(x + x_offset, y + y_offset) for x, y in self.points]

        min_x = min(p[0] for p in absolute_points)
        max_x = max(p[0] for p in absolute_points)
        min_y = min(p[1] for p in absolute_points)
        max_y = max(p[1] for p in absolute_points)

        return (min_x, min_y, max_x, max_y)

    def _create_gradient_fill(self) -> Optional[Tuple[Image.Image, Tuple[int, int]]]:
        """Create gradient fill image for the polygon"""
        if not self.gradient_config or not self.points:
            return None

        gradient_type = self.gradient_config.get("type", "linear")
        colors_config = self.gradient_config.get("colors", [])

        if not colors_config:
            return None

        # Parse colors
        colors = [GradientUtils.parse_color(color) for color in colors_config]

        # Get polygon bounds
        min_x, min_y, max_x, max_y = self._get_polygon_bounds()
        size = (max_x - min_x, max_y - min_y)

        if size[0] <= 0 or size[1] <= 0:
            return None

        # Create gradient image
        if gradient_type == "radial":
            center = self.gradient_config.get("center", (0.5, 0.5))
            gradient_img = GradientUtils.create_radial_gradient(size, colors, center)
        else:  # linear
            direction = self.gradient_config.get("direction", 0)
            gradient_img = GradientUtils.create_linear_gradient(size, colors, direction)

        return gradient_img, (min_x, min_y)

    def render(self, image: Image.Image) -> Image.Image:
        """
        Render a polygon onto an image.

        Args:
            image: The image to render the polygon on

        Returns:
            The image with the polygon rendered on it
        """
        if not self.points:
            return image

        result = image.copy()
        draw = ImageDraw.Draw(result)

        # Convert points to absolute coordinates
        x_offset, y_offset = self.position
        absolute_points = [(x + x_offset, y + y_offset) for x, y in self.points]

        # Check if we should use gradient
        gradient_result = self._create_gradient_fill()

        if gradient_result:
            gradient_img, (min_x, min_y) = gradient_result

            # Create polygon mask
            mask_size = (gradient_img.width, gradient_img.height)
            mask = Image.new("L", mask_size, 0)
            mask_draw = ImageDraw.Draw(mask)

            # Adjust points for mask coordinates
            mask_points = [(x - min_x, y - min_y) for x, y in absolute_points]
            mask_draw.polygon(mask_points, fill=255)

            # Apply gradient with polygon mask
            result.paste(gradient_img, (min_x, min_y), mask)
        else:
            # Draw solid color polygon with optional alpha
            if self.fill_color is not None:
                if len(self.fill_color) == 4:  # RGBA
                    # Create a temporary image for the polygon with alpha
                    polygon_img = Image.new('RGBA', image.size, (0, 0, 0, 0))
                    polygon_draw = ImageDraw.Draw(polygon_img)
                    polygon_draw.polygon(absolute_points, fill=self.fill_color)
                    # Composite the polygon onto the result
                    result = Image.alpha_composite(result.convert('RGBA'), polygon_img).convert('RGB')
                    # Update the draw object since we created a new image
                    draw = ImageDraw.Draw(result)
                else:  # RGB
                    draw.polygon(absolute_points, fill=self.fill_color)

        # Draw outline with optional alpha
        if self.outline_color is not None and self.outline_width > 0:
            if len(self.outline_color) == 4:  # RGBA
                # Create a temporary image for the outline with alpha
                outline_img = Image.new('RGBA', image.size, (0, 0, 0, 0))
                outline_draw = ImageDraw.Draw(outline_img)
                outline_draw.polygon(absolute_points, outline=self.outline_color, width=self.outline_width)
                # Composite the outline onto the result
                result = Image.alpha_composite(result.convert('RGBA'), outline_img).convert('RGB')
            else:  # RGB
                draw.polygon(absolute_points, outline=self.outline_color, width=self.outline_width)

        return result

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "PolygonComponent":
        """
        Create a polygon component from a configuration dictionary.

        Args:
            config: Configuration dictionary with the following structure:
                {
                    "position": {"x": 0, "y": 0},
                    "points": [[x1, y1], [x2, y2], ...],
                    "fill_color": [r, g, b] or [r, g, b, a],  # 0-255 for RGB, 0.0-1.0 for alpha
                    "outline_color": [r, g, b] or [r, g, b, a],  # 0-255 for RGB, 0.0-1.0 for alpha
                    "outline_width": 1,
                    "gradient": {
                        "type": "linear" or "radial",
                        "colors": [[r, g, b, a], ...],
                        "direction": 0,  # degrees for linear gradient
                        "center": [0.5, 0.5]  # for radial gradient
                    }
                }

        Returns:
            A new PolygonComponent instance
        """
        position = (
            config.get("position", {}).get("x", 0),
            config.get("position", {}).get("y", 0),
        )

        # Get points list from config
        points = config.get("points", [])
        if not isinstance(points, list):
            points = []

        # Handle fill color which might be RGB or RGBA
        fill_color = None
        if "fill_color" in config:
            fill_color = config["fill_color"]
            if isinstance(fill_color, (list, tuple)):
                if len(fill_color) >= 3:  # At least RGB
                    # Convert alpha to 0-255 range if it's in 0.0-1.0
                    if len(fill_color) == 4 and isinstance(fill_color[3], float):
                        fill_color = list(fill_color)
                        fill_color[3] = int(fill_color[3] * 255)
                    fill_color = tuple(fill_color[:4] if len(fill_color) > 3 else fill_color[:3])

        # Handle outline color which might be RGB or RGBA
        outline_color = None
        if "outline_color" in config:
            outline_color = config["outline_color"]
            if isinstance(outline_color, (list, tuple)):
                if len(outline_color) >= 3:  # At least RGB
                    # Convert alpha to 0-255 range if it's in 0.0-1.0
                    if len(outline_color) == 4 and isinstance(outline_color[3], float):
                        outline_color = list(outline_color)
                        outline_color[3] = int(outline_color[3] * 255)
                    outline_color = tuple(outline_color[:4] if len(outline_color) > 3 else outline_color[:3])

        return cls(
            position=position,
            points=points,
            fill_color=fill_color,
            outline_color=outline_color,
            outline_width=config.get("outline_width", 1),
            gradient_config=config.get("gradient"),
        )
