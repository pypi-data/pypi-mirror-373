import os
import requests
from io import BytesIO
from typing import Tuple, Optional, Dict, Any, Union, List
from PIL import Image, ImageOps, ImageDraw
from cairosvg import svg2png  # For SVG support
from .base import Component
from .shapes import GradientUtils


class ImageComponent(Component):
    """Component for rendering images (including SVG) with optional borders, rounded corners, and tints.

    Supports local images, URLs (including SVG), rotation, opacity, borders, and solid or gradient tints.
    The border is drawn inside the image bounds to maintain dimensions. For visible borders, ensure the image has padding.
    """

    def _parse_color(
        self, color: Union[str, Tuple[int, ...]]
    ) -> Tuple[int, int, int, int]:
        """Parse color from hex string or RGB/RGBA tuple to RGBA tuple.

        Args:
            color: Color in one of these formats:
                - Hex string (e.g., '#RRGGBB' or '#RRGGBBAA')
                - RGB tuple (3 integers 0-255)
                - RGBA tuple (4 integers 0-255)

        Returns:
            Tuple[int, int, int, int]: RGBA color tuple with values 0-255
        """
        if isinstance(color, str):
            color = color.lstrip("#")
            if len(color) in (6, 8):
                values = tuple(
                    int(color[i : i + 2], 16) for i in range(0, len(color), 2)
                )
                return (*values[:3], values[3] if len(values) == 4 else 255)
        elif isinstance(color, (list, tuple)) and 3 <= len(color) <= 4:
            return (*color[:3], color[3] if len(color) == 4 else 255)
        return (0, 0, 0, 255)  # Default to opaque black

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
        border_color: Union[str, Tuple[int, ...]] = (0, 0, 0, 255),
        tint_color: Optional[Union[str, Tuple[int, ...]]] = None,
        tint_opacity: float = 0.5,
        gradient_tint_config: Optional[Dict[str, Any]] = None,
        rotate: float = 0.0,
        aspect_ratio: str = "stretch",
    ) -> None:
        """Initialize an image component with support for SVG images.

        Args:
            image_path: Path to a local image file (e.g., PNG, JPG)
            image_url: URL of an image to download (supports PNG, JPG, SVG)
            position: (x, y) coordinates to place the image
            size: Optional (width, height) to resize the image
            circle_crop: If True, crop the image to a circle
            opacity: Image opacity (0.0 to 1.0)
            border_radius: Radius for rounded corners in pixels (0 for no rounding)
            border_width: Border width in pixels (drawn inside image bounds)
            border_color: Border color as hex string or RGB/RGBA tuple
            tint_color: Solid tint color as hex string or RGB/RGBA tuple (None for no tint)
            tint_opacity: Opacity of the tint overlay (0.0 to 1.0)
            gradient_tint_config: Configuration for gradient tint overlay. Format:
                {
                    "type": "linear" or "radial",
                    "colors": List[str] (hex colors),
                    "direction": float (0-360, for linear gradient),
                    "center": List[float] (normalized [x, y] for radial gradient),
                    "opacity": float (0.0-1.0, overrides tint_opacity)
                }
            rotate: Rotation angle in degrees (0-360)
            aspect_ratio: Image scaling mode:
                - "stretch": Stretch to fill specified size
                - "auto": Maintain aspect ratio, use specified width
                - "contain": Fit within specified size, maintain aspect ratio
        """
        super().__init__(position)
        self.image_path: Optional[str] = image_path
        self.image_url: Optional[str] = image_url
        self.size: Optional[Tuple[int, int]] = size
        self.circle_crop: bool = circle_crop
        self.opacity: float = max(0.0, min(1.0, float(opacity)))
        self.border_radius: int = max(0, int(border_radius))
        self.border_width: int = max(0, int(border_width))
        self.border_color: Tuple[int, int, int, int] = self._parse_color(border_color)
        self.tint_color: Optional[Tuple[int, int, int, int]] = (
            self._parse_color(tint_color) if tint_color else None
        )
        self.tint_opacity: float = max(0.0, min(1.0, float(tint_opacity)))
        self.gradient_tint_config: Optional[Dict[str, Any]] = gradient_tint_config
        self.rotate: float = float(rotate) % 360
        self.aspect_ratio: str = aspect_ratio
        self._cached_image: Optional[Image.Image] = None
        self._original_size: Optional[Tuple[int, int]] = None

    def _load_image(self) -> Optional[Image.Image]:
        """Load image from path or URL, supporting SVG, and apply rotation and opacity.

        Returns:
            Optional[Image.Image]: Loaded PIL Image or None if loading fails
        """
        if self._cached_image:
            return self._cached_image

        try:
            if self.image_path and os.path.exists(self.image_path):
                img = Image.open(self.image_path)
            elif self.image_url:
                response = requests.get(self.image_url, timeout=5)
                response.raise_for_status()
                content = response.content
                if self.image_url.lower().endswith(".svg"):
                    output = BytesIO()
                    svg2png(bytestring=content, write_to=output)
                    img = Image.open(output)
                else:
                    img = Image.open(BytesIO(content))
            else:
                return None

            if img.mode != "RGBA":
                img = img.convert("RGBA")

            self._original_size = img.size

            if self.rotate:
                img = img.rotate(
                    self.rotate, resample=Image.Resampling.BICUBIC, expand=True
                )
                self._original_size = img.size

            if self.opacity < 1.0:
                alpha = img.split()[3]
                img.putalpha(Image.eval(alpha, lambda x: int(x * self.opacity)))

            if self.gradient_tint_config:
                try:
                    gradient_type = self.gradient_tint_config.get(
                        "type", "linear"
                    ).lower()
                    colors = [
                        self._parse_color(c)
                        for c in self.gradient_tint_config.get("colors", [])
                    ]
                    if not colors:
                        print("Warning: No colors specified for gradient tint")
                        return img

                    gradient_opacity = max(
                        0.0,
                        min(
                            1.0,
                            self.gradient_tint_config.get("opacity", self.tint_opacity),
                        ),
                    )
                    if gradient_type == "radial":
                        gradient = GradientUtils.create_radial_gradient(
                            img.size,
                            colors,
                            self.gradient_tint_config.get("center", [0.5, 0.5]),
                        )
                    else:
                        gradient = GradientUtils.create_linear_gradient(
                            img.size,
                            colors,
                            self.gradient_tint_config.get("direction", 0),
                        )

                    if gradient_opacity < 1.0:
                        alpha = gradient.split()[3]
                        gradient.putalpha(
                            Image.eval(alpha, lambda x: int(x * gradient_opacity))
                        )

                    img = Image.alpha_composite(img, gradient)
                except Exception as e:
                    print(f"Gradient tint error: {e}")
                    if self.tint_color and self.tint_opacity:
                        img = self._apply_solid_tint(img)
            elif self.tint_color and self.tint_opacity:
                img = self._apply_solid_tint(img)

            self._cached_image = img
            return img

        except (IOError, requests.RequestException, ValueError) as e:
            print(f"Image loading error: {e}")
            return None

    def _apply_solid_tint(self, img: Image.Image) -> Image.Image:
        """Apply a solid color tint to the image.

        Args:
            img: Input PIL Image in RGBA mode

        Returns:
            Image.Image: Image with solid tint applied
        """
        tint_layer = Image.new("RGBA", img.size, self.tint_color)
        if self.tint_opacity < 1.0:
            alpha = tint_layer.split()[3]
            tint_layer.putalpha(Image.eval(alpha, lambda x: int(x * self.tint_opacity)))
        return Image.alpha_composite(img, tint_layer)

    def render(self, image: Image.Image) -> Image.Image:
        """Render the image with border onto the base image.

        Args:
            image: Base PIL Image to render onto

        Returns:
            Image.Image: Base image with the component rendered
        """
        if not (self.image_path or self.image_url) or not self.size:
            return image

        b = self.border_width
        content_size = (max(0, self.size[0] - 2 * b), max(0, self.size[1] - 2 * b))
        result_img = Image.new("RGBA", self.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(result_img, "RGBA")

        if b > 0:
            box = [b, b, self.size[0] - b - 1, self.size[1] - b - 1]
            radius = max(0, self.border_radius - b // 2) if self.border_radius else 0
            if self.circle_crop:
                draw.ellipse(box, outline=self.border_color, width=b)
            else:
                draw.rounded_rectangle(
                    box, radius=radius, outline=self.border_color, width=b
                )

        if content_size[0] > 0 and content_size[1] > 0:
            img = self._load_image()
            if img:
                orig_width, orig_height = self._original_size
                new_width, new_height = content_size

                if self.aspect_ratio == "auto" and self.size[0]:
                    new_height = int(content_size[0] * (orig_height / orig_width))
                elif self.aspect_ratio == "contain":
                    aspect_ratio = orig_width / orig_height
                    target_aspect = content_size[0] / content_size[1]
                    if aspect_ratio > target_aspect:
                        new_height = int(content_size[0] / aspect_ratio)
                    else:
                        new_width = int(content_size[1] * aspect_ratio)

                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                img_mask = Image.new("L", (new_width, new_height), 0)
                img_draw = ImageDraw.Draw(img_mask)

                if self.circle_crop:
                    img_draw.ellipse([0, 0, new_width, new_height], fill=255)
                elif self.border_radius:
                    radius_ratio = min(new_width, new_height) / max(*content_size)
                    img_draw.rounded_rectangle(
                        [0, 0, new_width, new_height],
                        radius=max(0, int((self.border_radius - b) * radius_ratio)),
                        fill=255,
                    )
                else:
                    img_draw.rectangle([0, 0, new_width, new_height], fill=255)

                paste_x = b + (content_size[0] - new_width) // 2
                paste_y = b + (content_size[1] - new_height) // 2
                result_img.paste(img, (paste_x, paste_y), img_mask)

        image.paste(result_img, self.position, result_img)
        return image

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "ImageComponent":
        """Create an ImageComponent from a configuration dictionary.

        Args:
            config: Dictionary with the following structure:
                {
                    "image_path": str,  # Optional local image path
                    "image_url": str,  # Optional image URL (supports SVG)
                    "position": {"x": int, "y": int},
                    "size": {"width": int, "height": int},  # Optional
                    "circle_crop": bool,
                    "opacity": float,  # 0.0 to 1.0
                    "border_radius": int,
                    "border_width": int,
                    "border_color": str or List[int],  # Hex or RGB/RGBA tuple
                    "tint": {
                        "type": str,  # "solid", "linear", or "radial"
                        "color": str,  # For solid tint
                        "colors": List[str],  # For gradient tint
                        "opacity": float,  # 0.0 to 1.0
                        "direction": float,  # For linear gradient (degrees)
                        "center": List[float]  # For radial gradient (normalized)
                    },
                    "rotate": float,  # Degrees
                    "aspect_ratio": str  # "stretch", "auto", or "contain"
                }

        Returns:
            ImageComponent: A new instance configured from the dictionary
        """
        position = (
            config.get("position", {}).get("x", 0),
            config.get("position", {}).get("y", 0),
        )
        size = (
            (config["size"].get("width"), config["size"].get("height"))
            if "size" in config
            else None
        )

        tint_config = config.get("tint", {})
        tint_color = (
            tint_config.get("color")
            if tint_config.get("type", "solid").lower() == "solid"
            else None
        )
        gradient_tint_config = None
        tint_opacity = float(tint_config.get("opacity", 0.5))

        if tint_config.get("type", "solid").lower() in ["linear", "radial"]:
            gradient_tint_config = {
                "type": tint_config["type"],
                "colors": tint_config.get("colors", []),
                "opacity": tint_opacity,
                **(
                    {"direction": tint_config.get("direction", 0)}
                    if tint_config["type"] == "linear"
                    else {"center": tint_config.get("center", [0.5, 0.5])}
                ),
            }

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
