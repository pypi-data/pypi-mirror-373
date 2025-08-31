"""
Validation utilities for template and component configurations.
"""

import os
import re
import json
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar, Type, Callable
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageFont

from dolze_image_templates.exceptions import ValidationError, ResourceError

# Constants for validation
MIN_FONT_SIZE = 6
MAX_FONT_SIZE = 400
MIN_IMAGE_DIMENSION = 1
MAX_IMAGE_DIMENSION = 10000
MIN_OPACITY = 0.0
MAX_OPACITY = 1.0
MIN_BLUR_RADIUS = 0
MAX_BLUR_RADIUS = 100

VALID_FONT_WEIGHTS = [
    "normal",
    "bold",
    "bolder",
    "lighter",
    "100",
    "200",
    "300",
    "400",
    "500",
    "600",
    "700",
    "800",
    "900",
]

VALID_TEXT_ALIGNS = ["left", "center", "right", "justify"]
VALID_BORDER_STYLES = ["solid", "dashed", "dotted", "double", "none"]
VALID_EFFECTS = ["blur", "shadow", "glow", "grayscale", "sepia"]

# Regular expressions
HEX_COLOR_PATTERN = re.compile(r"^#([A-Fa-f0-9]{3,4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$")
URL_PATTERN = re.compile(
    r"^(https?|ftp)://"  # http:// or https:// or ftp://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

T = TypeVar("T")  # Generic type variable
URL_PATTERN = re.compile(
    r"^(https?|ftp)://"  # http:// or https:// or ftp://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def validate_type(
    value: Any, expected_type: Union[Type, Tuple[Type, ...]], field: str
) -> None:
    """Validate that a value is of the expected type."""
    if not isinstance(value, expected_type):
        raise ValidationError(
            field=field,
            message=f"Expected type {expected_type}, got {type(value).__name__}",
            value=value,
        )


def validate_range(
    value: Union[int, float],
    min_val: Union[int, float],
    max_val: Union[int, float],
    field: str,
) -> None:
    """Validate that a numeric value is within the specified range."""
    if not (min_val <= value <= max_val):
        raise ValidationError(
            field=field,
            message=f"Value must be between {min_val} and {max_val}, got {value}",
            value=value,
        )


def validate_choice(
    value: Any, valid_choices: Union[list, set, tuple], field: str
) -> None:
    """Validate that a value is one of the valid choices."""
    if value not in valid_choices:
        raise ValidationError(
            field=field,
            message=f"Invalid choice. Must be one of: {', '.join(map(str, valid_choices))}",
            value=value,
        )


def validate_color(color: Any, field: str = "color") -> Tuple[int, int, int, int]:
    """
    Validate and normalize a color value to RGBA tuple.

    Args:
        color: Color value to validate (can be list, tuple, or hex string)
        field: Field name for error messages

    Returns:
        Normalized RGBA tuple (r, g, b, a)

    Raises:
        ValidationError: If the color format is invalid
    """
    if color is None:
        return (0, 0, 0, 0)  # Transparent

    if isinstance(color, str):
        if not HEX_COLOR_PATTERN.match(color):
            raise ValidationError(
                field=field,
                message="Invalid hex color format. Expected #RGB, #RGBA, #RRGGBB, or #RRGGBBAA",
                value=color,
            )

        # Handle hex color (e.g., "#RRGGBB" or "#RRGGBBAA")
        hex_color = color.lstrip("#")

        # Expand shorthand (e.g., "#RGB" -> "RRGGBB")
        if len(hex_color) in (3, 4):
            hex_color = "".join(c * 2 for c in hex_color)

        # Convert to RGBA
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16) if len(hex_color) > 4 else 255
            a = int(hex_color[6:8], 16) if len(hex_color) > 6 else 255
            return (r, g, b, a)
        except (ValueError, IndexError) as e:
            raise ValidationError(
                field=field, message=f"Failed to parse hex color: {str(e)}", value=color
            ) from e

    if isinstance(color, (list, tuple)):
        if len(color) not in (3, 4):
            raise ValidationError(
                field=field,
                message="Color must be a 3 (RGB) or 4 (RGBA) element list/tuple",
                value=color,
            )

        try:
            # Convert all values to float first to handle both int and float inputs
            values = [float(c) for c in color]

            # Validate each component is in 0-255 range
            for i, val in enumerate(values[:3]):  # RGB components
                if not 0 <= val <= 255:
                    raise ValidationError(
                        field=f"{field}[{i}]",
                        message=f"Color component must be between 0 and 255, got {val}",
                        value=val,
                    )

            # Validate alpha if present
            if len(values) == 4 and not (0 <= values[3] <= 1.0):
                raise ValidationError(
                    field=f"{field}[3]",
                    message=f"Alpha channel must be between 0.0 and 1.0, got {values[3]}",
                    value=values[3],
                )

            # Convert to integers (except alpha)
            r, g, b = map(int, values[:3])
            a = int(values[3] * 255) if len(values) == 4 else 255

            return (r, g, b, a)

        except (ValueError, TypeError) as e:
            raise ValidationError(
                field=field, message=f"Invalid color value: {str(e)}", value=color
            ) from e

    raise ValidationError(
        field=field,
        message="Color must be a hex string (e.g., '#RRGGBB') or list/tuple of RGB/RGBA values",
        value=color,
    )


def validate_position(
    position: Any, field: str = "position"
) -> Tuple[Union[int, float, str], Union[int, float, str]]:
    """
    Validate and normalize a position value.

    Args:
        position: Position value to validate (can be dict with x,y or tuple/list)
        field: Field name for error messages

    Returns:
        Normalized position tuple (x, y)

    Raises:
        ValidationError: If the position format is invalid
    """
    if position is None:
        return (0, 0)  # Default position

    try:
        if isinstance(position, dict):
            if "x" not in position or "y" not in position:
                raise ValueError("Position must contain 'x' and 'y' keys")
            x, y = position["x"], position["y"]
        elif isinstance(position, (list, tuple)):
            if len(position) != 2:
                raise ValueError("Position must be a 2-element list/tuple")
            x, y = position
        else:
            raise ValueError(
                "Position must be a dict with x,y or a 2-element list/tuple"
            )

        # Validate x and y values
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            # Numeric position
            return (float(x), float(y))
        elif isinstance(x, str) and isinstance(y, str):
            # String position (could be percentages or other units)
            if x.endswith("%") and y.endswith("%"):
                try:
                    x_pct = float(x.rstrip("%"))
                    y_pct = float(y.rstrip("%"))
                    if not (0 <= x_pct <= 100 and 0 <= y_pct <= 100):
                        raise ValueError(
                            "Percentage values must be between 0% and 100%"
                        )
                    return (x, y)  # Keep as strings with %
                except ValueError as e:
                    raise ValueError(f"Invalid percentage values: {e}") from e
            raise ValueError("String positions must be percentages (e.g., '50%')")
        else:
            raise ValueError(
                "Position values must both be numbers or both be percentage strings"
            )

    except (TypeError, ValueError) as e:
        raise ValidationError(field=field, message=str(e), value=position) from e


def validate_size(
    size: Any, field: str = "size"
) -> Tuple[Union[int, float, str], Union[int, float, str]]:
    """
    Validate and normalize a size value.

    Args:
        size: Size value to validate (can be dict with width,height or tuple/list)
        field: Field name for error messages

    Returns:
        Normalized size tuple (width, height)

    Raises:
        ValidationError: If the size format is invalid
    """
    if size is None:
        raise ValidationError(field=field, message="Size cannot be None", value=size)

    try:
        if isinstance(size, dict):
            if "width" not in size or "height" not in size:
                raise ValueError("Size must contain 'width' and 'height' keys")
            width, height = size["width"], size["height"]
        elif isinstance(size, (list, tuple)):
            if len(size) != 2:
                raise ValueError("Size must be a 2-element list/tuple")
            width, height = size
        else:
            raise ValueError(
                "Size must be a dict with width,height or a 2-element list/tuple"
            )

        # Validate width and height values
        if isinstance(width, (int, float)) and isinstance(height, (int, float)):
            # Numeric size
            width = float(width)
            height = float(height)

            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive numbers")

            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                raise ValueError(
                    f"Dimensions cannot exceed {MAX_IMAGE_DIMENSION} pixels"
                )

            if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                raise ValueError(
                    f"Dimensions must be at least {MIN_IMAGE_DIMENSION} pixels"
                )

            return (width, height)

        elif isinstance(width, str) and isinstance(height, str):
            # String size (could be percentages or other units)
            if width.endswith("%") and height.endswith("%"):
                try:
                    width_pct = float(width.rstrip("%"))
                    height_pct = float(height.rstrip("%"))
                    if width_pct <= 0 or height_pct <= 0:
                        raise ValueError("Percentage values must be positive")
                    return (width, height)  # Keep as strings with %
                except ValueError as e:
                    raise ValueError(f"Invalid percentage values: {e}") from e
            raise ValueError("String dimensions must be percentages (e.g., '100%')")
        else:
            raise ValueError(
                "Dimension values must both be numbers or both be percentage strings"
            )

    except (TypeError, ValueError) as e:
        raise ValidationError(field=field, message=str(e), value=size) from e


def validate_font_path(font_path: Any, field: str = "font_path") -> Optional[str]:
    """
    Validate a font path.

    Args:
        font_path: Font path to validate
        field: Field name for error messages

    Returns:
        Normalized font path if valid

    Raises:
        ValidationError: If the font path is invalid
    """
    if not font_path:
        return None

    if not isinstance(font_path, str):
        raise ValidationError(
            field=field, message="Font path must be a string", value=font_path
        )

    try:
        path = Path(font_path)

        # Check if path exists
        if not path.exists():
            raise ValidationError(
                field=field,
                message=f"Font file not found: {font_path}",
                value=font_path,
            )

        # Check file extension
        if path.suffix.lower() not in (".ttf", ".otf"):
            raise ValidationError(
                field=field,
                message=f"Unsupported font format: {path.suffix}. Only .ttf and .otf are supported.",
                value=font_path,
            )

        # Check if file is readable
        try:
            # Try to load the font to verify it's a valid font file
            ImageFont.truetype(str(path), 10)  # Small size just for validation
        except Exception as e:
            raise ValidationError(
                field=field, message=f"Invalid font file: {str(e)}", value=font_path
            )

        return str(path.absolute())

    except Exception as e:
        if not isinstance(e, ValidationError):
            raise ValidationError(
                field=field,
                message=f"Failed to validate font path: {str(e)}",
                value=font_path,
            ) from e


def validate_component(component: Dict[str, Any], index: int = 0) -> Dict[str, Any]:
    """
    Validate and normalize a component configuration.

    Args:
        component: Component configuration to validate
        index: Index of the component in the components list (for error messages)

    Returns:
        Normalized component configuration

    Raises:
        ValidationError: If the component configuration is invalid
    """
    if not isinstance(component, dict):
        raise ValidationError(
            field=f"components[{index}]",
            message="Component must be a dictionary",
            value=component,
        )

    # Create a copy to avoid modifying the original
    component = component.copy()
    field_prefix = f"components[{index}]"

    # Validate component type
    if "type" not in component:
        raise ValidationError(
            field=f"{field_prefix}.type",
            message="Component type is required",
            value=None,
        )

    component_type = component["type"]
    if not isinstance(component_type, str):
        raise ValidationError(
            field=f"{field_prefix}.type",
            message="Component type must be a string",
            value=component_type,
        )

    # Common validations for all components
    if "position" in component:
        try:
            component["position"] = validate_position(
                component["position"], f"{field_prefix}.position"
            )
        except ValidationError as e:
            e.field = (
                f"{field_prefix}.position.{e.field}"
                if e.field
                else f"{field_prefix}.position"
            )
            raise e

    # Type-specific validations
    if component_type == "text":
        component = validate_text_component(component, field_prefix)
    elif component_type == "image":
        component = validate_image_component(component, field_prefix)
    elif component_type in ["rectangle", "circle"]:
        component = validate_shape_component(component, field_prefix, component_type)
    elif component_type == "cta_button":
        # CTA buttons are already validated by the component class
        pass
    elif component_type == "cta_button_group":
        component = validate_button_group_component(component, field_prefix)
    else:
        raise ValidationError(
            field=f"{field_prefix}.type",
            message=f"Unknown component type: {component_type}",
            value=component_type,
        )

    return component


def validate_text_component(
    component: Dict[str, Any], field_prefix: str
) -> Dict[str, Any]:
    """Validate a text component configuration."""
    # Required fields
    if "text" not in component:
        raise ValidationError(
            field=f"{field_prefix}.text",
            message="Text content is required for text components",
            value=None,
        )

    # Validate text content
    if not isinstance(component["text"], (str, int, float)):
        raise ValidationError(
            field=f"{field_prefix}.text",
            message="Text must be a string or number",
            value=component["text"],
        )

    # Convert to string if it's a number
    if isinstance(component["text"], (int, float)):
        component["text"] = str(component["text"])

    # Validate optional fields
    if "font_size" in component:
        try:
            validate_range(
                component["font_size"],
                MIN_FONT_SIZE,
                MAX_FONT_SIZE,
                f"{field_prefix}.font_size",
            )
        except ValidationError as e:
            e.field = (
                f"{field_prefix}.font_size.{e.field}"
                if e.field
                else f"{field_prefix}.font_size"
            )
            raise e

    if "color" in component:
        try:
            component["color"] = validate_color(
                component["color"], f"{field_prefix}.color"
            )
        except ValidationError as e:
            e.field = (
                f"{field_prefix}.color.{e.field}"
                if e.field
                else f"{field_prefix}.color"
            )
            raise e

    if "font_weight" in component:
        try:
            validate_choice(
                str(component["font_weight"]).lower(),
                VALID_FONT_WEIGHTS,
                f"{field_prefix}.font_weight",
            )
            component["font_weight"] = component["font_weight"].lower()
        except ValidationError as e:
            e.field = (
                f"{field_prefix}.font_weight.{e.field}"
                if e.field
                else f"{field_prefix}.font_weight"
            )
            raise e

    if "align" in component:
        try:
            validate_choice(
                str(component["align"]).lower(),
                VALID_TEXT_ALIGNS,
                f"{field_prefix}.align",
            )
            component["align"] = component["align"].lower()
        except ValidationError as e:
            e.field = (
                f"{field_prefix}.align.{e.field}"
                if e.field
                else f"{field_prefix}.align"
            )
            raise e

    return component


def validate_image_component(
    component: Dict[str, Any], field_prefix: str
) -> Dict[str, Any]:
    """Validate an image component configuration."""
    # Required fields
    if "image_url" not in component:
        raise ValidationError(
            field=f"{field_prefix}.image_url",
            message="Image URL is required for image components",
            value=None,
        )

    # Validate image URL
    try:
        component["image_url"] = validate_url(
            component["image_url"], f"{field_prefix}.image_url"
        )
    except ValidationError as e:
        e.field = (
            f"{field_prefix}.image_url.{e.field}"
            if e.field
            else f"{field_prefix}.image_url"
        )
        raise e

    # Validate size if present
    if "size" in component:
        try:
            size = validate_size(component["size"], f"{field_prefix}.size")
            component["size"] = size

            # Validate dimensions
            for dim in ["width", "height"]:
                if dim in size:
                    validate_range(
                        size[dim],
                        MIN_IMAGE_DIMENSION,
                        MAX_IMAGE_DIMENSION,
                        f"{field_prefix}.size.{dim}",
                    )
        except ValidationError as e:
            e.field = (
                f"{field_prefix}.size.{e.field}" if e.field else f"{field_prefix}.size"
            )
            raise e

    return component


def validate_shape_component(
    component: Dict[str, Any], field_prefix: str, shape_type: str
) -> Dict[str, Any]:
    """Validate a shape component (rectangle or circle) configuration."""
    if "fill_color" in component:
        try:
            component["fill_color"] = validate_color(
                component["fill_color"], f"{field_prefix}.fill_color"
            )
        except ValidationError as e:
            e.field = (
                f"{field_prefix}.fill_color.{e.field}"
                if e.field
                else f"{field_prefix}.fill_color"
            )
            raise e

    if "border_style" in component:
        try:
            validate_choice(
                str(component["border_style"]).lower(),
                VALID_BORDER_STYLES,
                f"{field_prefix}.border_style",
            )
            component["border_style"] = component["border_style"].lower()
        except ValidationError as e:
            e.field = (
                f"{field_prefix}.border_style.{e.field}"
                if e.field
                else f"{field_prefix}.border_style"
            )
            raise e

    if "border_radius" in component and shape_type == "rectangle":
        try:
            validate_range(
                component["border_radius"],
                0,
                float("inf"),
                f"{field_prefix}.border_radius",
            )
        except ValidationError as e:
            e.field = (
                f"{field_prefix}.border_radius.{e.field}"
                if e.field
                else f"{field_prefix}.border_radius"
            )
            raise e

    return component


def validate_button_group_component(
    component: Dict[str, Any], field_prefix: str
) -> Dict[str, Any]:
    """
    Validate a button group component configuration.
    
    Args:
        component: Button group component configuration to validate
        field_prefix: Prefix for field names in error messages
        
    Returns:
        Normalized button group component configuration
        
    Raises:
        ValidationError: If the configuration is invalid
    """
    # Validate required fields
    if "items" not in component:
        raise ValidationError(
            field=f"{field_prefix}.items",
            message="Button group must have 'items' field",
        )
        
    # Validate items is a list
    try:
        validate_type(component["items"], list, f"{field_prefix}.items")
    except ValidationError as e:
        e.field = f"{field_prefix}.items"
        raise e
        
    # Validate spacing (optional)
    if "spacing" in component:
        try:
            validate_type(component["spacing"], (int, float), f"{field_prefix}.spacing")
            validate_range(component["spacing"], 0, 1000, f"{field_prefix}.spacing")
        except ValidationError as e:
            e.field = f"{field_prefix}.spacing"
            raise e
            
    # Validate max_width (optional)
    if "max_width" in component:
        try:
            validate_type(component["max_width"], (int, float), f"{field_prefix}.max_width")
            validate_range(component["max_width"], 0, 10000, f"{field_prefix}.max_width")
        except ValidationError as e:
            e.field = f"{field_prefix}.max_width"
            raise e
            
    # Validate line_height (optional)
    if "line_height" in component:
        try:
            validate_type(component["line_height"], (int, float), f"{field_prefix}.line_height")
            validate_range(component["line_height"], 0.5, 5, f"{field_prefix}.line_height")
        except ValidationError as e:
            e.field = f"{field_prefix}.line_height"
            raise e
            
    # Validate align (optional)
    if "align" in component:
        try:
            validate_type(component["align"], str, f"{field_prefix}.align")
            validate_choice(component["align"], ["left", "center", "right"], f"{field_prefix}.align")
        except ValidationError as e:
            e.field = f"{field_prefix}.align"
            raise e
            
    # We don't validate individual items here as they will be validated by their respective component classes
    # when the button group component is instantiated
            
    return component


def validate_template_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize a template configuration.

    Args:
        config: Template configuration to validate

    Returns:
        Normalized template configuration

    Raises:
        ValidationError: If the configuration is invalid
    """
    if not isinstance(config, dict):
        raise ValidationError(
            field="config", message="Template config must be a dictionary", value=config
        )

    # Create a copy to avoid modifying the original
    config = config.copy()

    # Validate required fields
    required_fields = ["name", "components"]
    for field in required_fields:
        if field not in config:
            raise ValidationError(
                field=field, message="This field is required", value=None
            )

    # Validate name
    if not isinstance(config["name"], str) or not config["name"].strip():
        raise ValidationError(
            field="name",
            message="Template name must be a non-empty string",
            value=config.get("name"),
        )

    # Validate components
    if not isinstance(config["components"], list):
        raise ValidationError(
            field="components",
            message="Components must be a list",
            value=config.get("components"),
        )

    # Validate each component
    for i, component in enumerate(config["components"]):
        try:
            config["components"][i] = validate_component(component, i)
        except ValidationError as e:
            # Add component index to the field path if not already present
            if not e.field.startswith("components["):
                e.field = f"components[{i}].{e.field}"
            raise e

    # Validate size if present
    if "size" in config:
        try:
            config["size"] = validate_size(config["size"], "size")
        except ValidationError as e:
            e.field = f"size.{e.field}" if e.field != "size" else "size"
            raise e from None

    # Validate background color if present
    if "background_color" in config:
        try:
            config["background_color"] = validate_color(
                config["background_color"], "background_color"
            )
        except ValidationError as e:
            e.field = (
                f"background_color.{e.field}"
                if e.field != "background_color"
                else "background_color"
            )
            raise e from None

    # Validate use_base_image if present
    if "use_base_image" in config and not isinstance(config["use_base_image"], bool):
        raise ValidationError(
            field="use_base_image",
            message="use_base_image must be a boolean",
            value=config["use_base_image"],
        )

    # Validate effects if present
    if "effects" in config:
        effects = config["effects"]
        if not isinstance(effects, dict):
            raise ValidationError(
                field="effects", message="Effects must be a dictionary", value=effects
            )

        for effect_name, effect_config in effects.items():
            try:
                validate_choice(effect_name, VALID_EFFECTS, f"effects.{effect_name}")

                # Validate effect-specific configurations
                if effect_name == "blur" and "radius" in effect_config:
                    validate_range(
                        effect_config["radius"],
                        MIN_BLUR_RADIUS,
                        MAX_BLUR_RADIUS,
                        "effects.blur.radius",
                    )
                # Add more effect validations as needed

            except ValidationError as e:
                e.field = (
                    f"effects.{effect_name}.{e.field}"
                    if e.field
                    else f"effects.{effect_name}"
                )
                raise e

    return config
