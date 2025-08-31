import os
import requests
from io import BytesIO
from typing import Tuple, Optional, Dict, Any, Union, List
from PIL import Image, ImageOps, ImageDraw
from .base import Component
from .shapes import GradientUtils


class ImageComponent(Component):
    """Component for rendering images with optional borders and rounded corners.

    The border is drawn inside the image bounds, so it won't expand the image dimensions.
    For best results, ensure the image has some padding if you want the border to be visible.
    """

    def _parse_color(
        self, color: Union[str, Tuple[int, int, int, int]]
    ) -> Tuple[int, int, int, int]:
        """Parse color from various formats to RGBA tuple.

        Args:
            color: Color in one of these formats:
                - Hex string (e.g., "#RRGGBB" or "#RRGGBBAA")
                - RGB/RGBA tuple (3 or 4 integers 0-255)

        Returns:
            RGBA tuple with values 0-255
        """
        if isinstance(color, str):
            color = color.strip("#")
            if len(color) == 6:
                r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
                return (r, g, b, 255)
            elif len(color) == 8:
                r, g, b, a = (int(color[i : i + 2], 16) for i in (0, 2, 4, 6))
                return (r, g, b, a)
        elif isinstance(color, (list, tuple)):
            if len(color) == 3:  # RGB
                return (*color, 255)
            elif len(color) == 4:  # RGBA
                return tuple(color)
        return (0, 0, 0, 255)  # Default to black

    def __init__(
        self,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        position: Tuple[int, int] = (0, 0),
        size: Optional[Tuple[int, int]] = None,
        circle_crop: bool = False,
        opacity: float = 1.0,
        border_radius: int = 0,
        border_width: int = 0,
        border_color: Union[str, Tuple[int, int, int, int]] = (0, 0, 0, 255),
        tint_color: Optional[Union[str, Tuple[int, int, int, int]]] = None,
        tint_opacity: float = 0.5,
        gradient_tint_config: Optional[Dict[str, Any]] = None,
        rotate: float = 0.0,
        aspect_ratio: str = "stretch",
    ):
        """
        Initialize an image component.

        Args:
            image_path: Path to a local image file
            image_url: URL of an image to download
            position: Position (x, y) to place the image
            size: Optional size (width, height) to resize the image to
            circle_crop: Whether to crop the image to a circle
            opacity: Opacity of the image (0.0 to 1.0)
            border_radius: Radius for rounded corners in pixels (0 for no rounding)
            border_width: Width of the border in pixels
            border_color: Color of the border (hex string or RGBA tuple)
            tint_color: Color to overlay on the image (None for no tint, hex string or RGBA tuple)
            tint_opacity: Opacity of the tint overlay (0.0 to 1.0)
            gradient_tint_config: Configuration for gradient tint overlay. Format:
                {
                    "type": "linear" or "radial",
                    "colors": ["#color1", "#color2", ...],
                    "direction": 0-360 (for linear, degrees),
                    "center": [x, y] (for radial, normalized 0-1),
                    "opacity": 0.0-1.0 (optional, overrides tint_opacity)
                }
            rotate: Rotation angle in degrees (0-360)
            aspect_ratio: How to handle image aspect ratio:
                         - "stretch": (default) Stretch image to fill the specified size
                         - "auto": Maintain original aspect ratio, using width from size
                         - "contain": Fit within the specified size while maintaining aspect ratio
        """
        super().__init__(position)
        self.image_path = image_path
        self.image_url = image_url
        self.size = size
        self.circle_crop = circle_crop
        self.opacity = max(0.0, min(1.0, opacity))  # Clamp between 0 and 1
        self.border_radius = max(0, int(border_radius))  # Ensure non-negative integer
        self.border_width = max(0, int(border_width))
        self.border_color = self._parse_color(border_color)
        self.tint_color = self._parse_color(tint_color) if tint_color else None
        self.tint_opacity = max(
            0.0, min(1.0, float(tint_opacity))
        )  # Clamp between 0 and 1
        self.gradient_tint_config = gradient_tint_config
        self.rotate = float(rotate) % 360  # Normalize to 0-360 range
        self.aspect_ratio = aspect_ratio
        self._cached_image = None
        self._original_size = None  # Will store original image dimensions

    def _load_image(self) -> Optional[Image.Image]:
        """
        Load the image from path or URL if not already loaded.

        Returns:
            Loaded PIL Image or None if loading fails
        """
        if self._cached_image is not None:
            return self._cached_image

        try:
            if self.image_path and os.path.exists(self.image_path):
                img = Image.open(self.image_path)
            elif self.image_url:
                response = requests.get(self.image_url)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
            else:
                return None

            # Convert to RGBA if needed
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            
            # Store original size for aspect ratio calculations
            self._original_size = img.size
                
            # Apply rotation if needed
            if self.rotate != 0:
                # Use BICUBIC for smoother rotation
                img = img.rotate(self.rotate, resample=Image.Resampling.BICUBIC, expand=True)
                # Update original size if rotation changed dimensions
                self._original_size = img.size

            # Apply opacity if needed
            if self.opacity < 1.0:
                alpha = img.split()[3]
                alpha = Image.eval(alpha, lambda x: int(x * self.opacity))
                img.putalpha(alpha)

            # Apply tint overlay if specified
            if self.gradient_tint_config:
                # Create gradient tint layer
                try:
                    gradient_type = self.gradient_tint_config.get("type", "linear").lower()
                    colors = [GradientUtils.parse_color(c) for c in self.gradient_tint_config.get("colors", [])]
                    
                    if not colors:
                        print("Warning: No colors specified for gradient tint")
                        return img
                    
                    if gradient_type == "radial":
                        center = self.gradient_tint_config.get("center", [0.5, 0.5])
                        gradient = GradientUtils.create_radial_gradient(img.size, colors, center)
                    else:  # default to linear
                        direction = self.gradient_tint_config.get("direction", 0)
                        gradient = GradientUtils.create_linear_gradient(img.size, colors, direction)
                    
                    # Use gradient-specific opacity or fall back to tint_opacity
                    gradient_opacity = self.gradient_tint_config.get("opacity", self.tint_opacity)
                    gradient_opacity = max(0.0, min(1.0, float(gradient_opacity)))
                    
                    # Apply opacity to the gradient
                    if gradient_opacity < 1.0:
                        alpha = gradient.split()[3]
                        alpha = Image.eval(alpha, lambda x: int(x * gradient_opacity))
                        gradient.putalpha(alpha)
                    
                    # Blend the gradient with the image
                    img = Image.alpha_composite(img, gradient)
                    
                except Exception as e:
                    print(f"Error applying gradient tint: {e}")
                    # Fall back to solid color tint if gradient fails
                    if self.tint_color and self.tint_opacity > 0:
                        img = self._apply_solid_tint(img)
                        
            elif self.tint_color and self.tint_opacity > 0:
                img = self._apply_solid_tint(img)

            self._cached_image = img
            return img

        except (IOError, requests.RequestException) as e:
            print(f"Error loading image: {e}")
            return None

    def _apply_solid_tint(self, img: Image.Image) -> Image.Image:
        """Apply a solid color tint to the image."""
        tint_layer = Image.new("RGBA", img.size, self.tint_color)
        if self.tint_opacity < 1.0:
            alpha = tint_layer.split()[3]
            alpha = Image.eval(alpha, lambda x: int(x * self.tint_opacity))
            tint_layer.putalpha(alpha)
        return Image.alpha_composite(img, tint_layer)

    def render(self, image: Image.Image) -> Image.Image:
        """
        Render the image onto the base image with border.
        Renders border first, then renders the image inside the border.

        Args:
            image: Base image to render onto

        Returns:
            Image with the rendered component
        """
        if not self.image_path and not self.image_url:
            return image

        # Create a new layer for the image with border
        result_img = Image.new("RGBA", self.size if self.size else (0, 0), (0, 0, 0, 0))

        # Calculate border width and content bounds
        b = max(0, self.border_width)

        # Create a mask for the content area
        mask = Image.new("L", self.size if self.size else (0, 0), 0)
        draw = ImageDraw.Draw(mask)

        # Calculate content area (inside border)
        content_box = [
            b,  # left
            b,  # top
            (self.size[0] - b - 1) if self.size else (0 - b - 1),  # right
            (self.size[1] - b - 1) if self.size else (0 - b - 1),  # bottom
        ]

        # Draw border first if needed
        if b > 0:
            border_img = Image.new(
                "RGBA", self.size if self.size else (0, 0), (0, 0, 0, 0)
            )
            border_draw = ImageDraw.Draw(border_img, "RGBA")

            if self.circle_crop:
                # Draw circular border
                border_draw.ellipse(
                    [
                        b,
                        b,
                        (self.size[0] - b - 1) if self.size else (0 - b - 1),
                        (self.size[1] - b - 1) if self.size else (0 - b - 1),
                    ],
                    outline=tuple(self.border_color),
                    width=b,
                )
            else:
                # Draw rounded rectangle border
                border_draw.rounded_rectangle(
                    [
                        b,
                        b,
                        (self.size[0] - b - 1) if self.size else (0 - b - 1),
                        (self.size[1] - b - 1) if self.size else (0 - b - 1),
                    ],
                    radius=(
                        max(0, self.border_radius - b // 2)
                        if self.border_radius > 0
                        else 0
                    ),
                    outline=tuple(self.border_color),
                    width=b,
                )
            result_img = border_img

        # Now handle the image content
        if self.size:
            # Calculate size for the image (inside border)
            content_width = max(0, self.size[0] - (2 * b) if self.size[0] > 0 else 0)
            content_height = max(0, self.size[1] - (2 * b) if self.size[1] > 0 else 0)

            if content_width > 0 and content_height > 0:
                # Load the image
                img = self._load_image()
                if img:
                    # Get original image dimensions
                    orig_width, orig_height = self._original_size if hasattr(self, '_original_size') else img.size
                    
                    # Calculate new dimensions based on aspect_ratio setting
                    if self.aspect_ratio == "auto" and self.size and self.size[0] is not None:
                        # Auto: use provided width, calculate height to maintain aspect ratio
                        new_width = content_width
                        new_height = int(content_width * (orig_height / orig_width))
                        # Update content height to match new height plus borders
                        content_height = new_height + (2 * b)
                    elif self.aspect_ratio == "contain":
                        # Contain: fit within specified size while maintaining aspect ratio
                        aspect_ratio = orig_width / orig_height
                        target_aspect_ratio = content_width / content_height
                        
                        if aspect_ratio > target_aspect_ratio:
                            # Image is wider than target, fit to width
                            new_width = content_width
                            new_height = int(content_width / aspect_ratio)
                        else:
                            # Image is taller than target, fit to height
                            new_height = content_height
                            new_width = int(content_height * aspect_ratio)
                        
                        # Ensure dimensions don't exceed target
                        new_width = min(new_width, content_width)
                        new_height = min(new_height, content_height)
                    else:  # stretch (default)
                        # Stretch to fill the specified size
                        new_width = content_width
                        new_height = content_height

                    # Resize image while maintaining aspect ratio
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Create a mask for the image with the same dimensions as the resized image
                    img_mask = Image.new("L", (new_width, new_height), 0)
                    img_draw = ImageDraw.Draw(img_mask)

                    if self.circle_crop:
                        # Create circular mask for image
                        img_draw.ellipse([0, 0, new_width, new_height], fill=255)
                    elif self.border_radius > 0:
                        # Create rounded rectangle mask for image with proportional radius
                        radius_ratio = min(new_width, new_height) / max(
                            content_width, content_height
                        )
                        scaled_radius = max(
                            0, int((self.border_radius - b) * radius_ratio)
                        )
                        img_draw.rounded_rectangle(
                            [0, 0, new_width, new_height],
                            radius=scaled_radius,
                            fill=255,
                        )
                    else:
                        # Rectangle mask
                        img_draw.rectangle([0, 0, new_width, new_height], fill=255)

                    # Calculate position to center the image within the content area
                    paste_x = b + (content_width - new_width) // 2
                    paste_y = b + (content_height - new_height) // 2

                    # Paste the image with the mask
                    result_img.paste(img, (paste_x, paste_y), img_mask)

        # Paste the result onto the base image
        image.paste(result_img, self.position, result_img)
        return image

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "ImageComponent":
        """
        Create an image component from a configuration dictionary.

        Args:
            config: Configuration dictionary with the following structure:
                {
                    "image_path": "path/to/image.jpg",  # optional
                    "image_url": "https://example.com/image.jpg",  # optional
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 100, "height": 100},  # optional
                    "circle_crop": false,
                    "opacity": 1.0,
                    "border_radius": 0,
                    "border_width": 0,
                    "border_color": "#000000" or [0, 0, 0, 255],
                    "tint": {
                        "type": "solid",  # or "linear" or "radial"
                        "color": "#FF0000",  # for solid tint
                        "colors": ["#FF0000", "#00FF00", "#0000FF"],  # for gradient tint
                        "opacity": 0.5,
                        "direction": 45,  # for linear gradient (degrees)
                        "center": [0.5, 0.5]  # for radial gradient (normalized)
                    }
                }

        Returns:
            A new ImageComponent instance
        """
        position = (
            config.get("position", {}).get("x", 0),
            config.get("position", {}).get("y", 0),
        )

        size = None
        if "size" in config:
            size = (
                config["size"].get("width"),
                config["size"].get("height"),
            )
            if None in size:
                size = None

        # Handle tint configuration
        tint_config = config.get("tint", {})
        tint_color = None
        tint_opacity = 0.5
        gradient_tint_config = None

        if tint_config:
            tint_type = tint_config.get("type", "solid").lower()
            tint_opacity = float(tint_config.get("opacity", 0.5))
            
            if tint_type == "solid":
                # Solid color tint
                tint_color = tint_config.get("color")
            elif tint_type in ["linear", "radial"]:
                # Gradient tint
                gradient_tint_config = {
                    "type": tint_type,
                    "colors": tint_config.get("colors", []),
                    "opacity": tint_opacity
                }
                
                if tint_type == "linear":
                    gradient_tint_config["direction"] = tint_config.get("direction", 0)
                elif tint_type == "radial":
                    gradient_tint_config["center"] = tint_config.get("center", [0.5, 0.5])

        return cls(
            image_path=config.get("image_path"),
            image_url=config.get("image_url"),
            position=position,
            size=size,
            circle_crop=config.get("circle_crop", False),
            opacity=float(config.get("opacity", 1.0)),
            border_radius=int(config.get("border_radius", 0)),
            border_width=int(config.get("border_width", 0)),
            border_color=config.get("border_color", (0, 0, 0, 255)),
            tint_color=tint_color,
            tint_opacity=tint_opacity,
            gradient_tint_config=gradient_tint_config,
            rotate=float(config.get("rotate", 0.0)),
            aspect_ratio=config.get("aspect_ratio", "stretch"),
        )