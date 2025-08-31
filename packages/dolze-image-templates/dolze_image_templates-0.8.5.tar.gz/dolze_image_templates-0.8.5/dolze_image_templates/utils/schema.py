"""
JSON Schema validation for template configuration.
Regenerated to match current components and props.
"""

from typing import Dict, Any

# ----- Reusable bits -----
RGBA_255 = {
    "type": "array",
    "items": {"type": "number", "minimum": 0, "maximum": 255},
    "minItems": 4,
    "maxItems": 4,
}

RGB_255 = {
    "type": "array",
    "items": {"type": "number", "minimum": 0, "maximum": 255},
    "minItems": 3,
    "maxItems": 3,
}

POSITION = {
    "type": "object",
    "properties": {
        "x": {"type": "number"},
        "y": {"type": "number"},
    },
    "required": ["x", "y"],
    "additionalProperties": False,
}

SIZE = {
    "type": "object",
    "properties": {
        "width": {"type": "number", "minimum": 1},
        "height": {"type": "number", "minimum": 1},
    },
    "required": ["width", "height"],
    "additionalProperties": False,
}

GRADIENT_COMMON = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["linear", "radial"]},
        # colors can be RGBA arrays or hex strings resolved upstream
        "colors": {
            "type": "array",
            "minItems": 2,
            "items": {
                "anyOf": [
                    RGBA_255,
                    {"type": "string"},        # allow "#RRGGBB" / "#RRGGBBAA"
                ]
            },
        },
        "direction": {"type": "number"},      # linear
        "center": {
            "type": "array",                  # radial
            "items": {"type": "number"},
            "minItems": 2,
            "maxItems": 2,
        },
    },
    "additionalProperties": True,
}

# ----- Component Schemas -----

TEXT_COMPONENT = {
    "type": "object",
    "properties": {
        "type": {"const": "text"},
        "position": POSITION,
        "text": {"type": "string"},
        "font_size": {"type": "number", "minimum": 1},
        "color": RGBA_255,
        "font_path": {"type": "string"},
        "alignment": {"type": "string", "enum": ["left", "center", "right"]},
        "max_width": {"type": "number", "minimum": 1},
        "line_height": {"type": "number", "minimum": 0.6, "maximum": 3.0},
        "underline": {"type": "string"},  # renderer treats as string flag
    },
    "required": ["type", "text", "font_size", "color"],
    "additionalProperties": True,
}

IMAGE_COMPONENT = {
    "type": "object",
    "properties": {
        "type": {"const": "image"},
        "position": POSITION,
        "size": SIZE,
        "image_url": {"type": "string"},
        "image_path": {"type": "string"},
        "circle_crop": {"type": "boolean"},
        "opacity": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "border_radius": {"type": "number", "minimum": 0},
        "border_width": {"type": "number", "minimum": 0},
        "border_color": {
            "anyOf": [
                RGB_255,
                RGBA_255,
                {"type": "string"},  # hex
            ]
        },
        # Solid tint
        "tint_color": {
            "anyOf": [RGB_255, RGBA_255, {"type": "string"}]
        },
        "tint_opacity": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        # Gradient tint overlay
        "gradient_tint_config": GRADIENT_COMMON,
        # Transform
        "rotate": {"type": "number"},
        "aspect_ratio": {"type": "string", "enum": ["stretch", "contain", "cover"]},
    },
    "required": ["type"],
    "anyOf": [
        {"required": ["image_url"]},
        {"required": ["image_path"]},
    ],
    "additionalProperties": True,
}

RECTANGLE_COMPONENT = {
    "type": "object",
    "properties": {
        "type": {"const": "rectangle"},
        "position": POSITION,
        "size": SIZE,
        "fill_color": {
            "anyOf": [RGB_255, RGBA_255, {"type": "null"}]
        },
        "outline_color": {
            "anyOf": [RGB_255, RGBA_255, {"type": "null"}]
        },
        "outline_width": {"type": "number", "minimum": 0},
        "border_radius": {"type": "number", "minimum": 0},
        # Preferred in code
        "gradient_config": GRADIENT_COMMON,
        # Backward compatibles some templates use:
        "fill_gradient": GRADIENT_COMMON,
        "gradient": GRADIENT_COMMON,
    },
    "required": ["type", "position", "size"],
    "additionalProperties": True,
}

# Circle (from shapes.CircleComponent)
CIRCLE_COMPONENT = {
    "type": "object",
    "properties": {
        "type": {"const": "circle"},
        "position": POSITION,
        # Support either radius or size (many JSONs use size W x H)
        "radius": {"type": "number", "minimum": 1},
        "size": SIZE,
        "fill_color": {
            "anyOf": [RGB_255, RGBA_255, {"type": "null"}]
        },
        "outline_color": {
            "anyOf": [RGB_255, RGBA_255, {"type": "null"}]
        },
        "outline_width": {"type": "number", "minimum": 0},
        "image_url": {"type": "string"},
        "image_path": {"type": "string"},
        "gradient_config": GRADIENT_COMMON,
    },
    "required": ["type", "position"],
    "additionalProperties": True,
}

# Polygon (from shapes.PolygonComponent)
POLYGON_COMPONENT = {
    "type": "object",
    "properties": {
        "type": {"const": "polygon"},
        "position": POSITION,
        "points": {
            "type": "array",
            "minItems": 3,
            "items": {
                "type": "array",
                "items": {"type": "number"},
                "minItems": 2,
                "maxItems": 2,
            },
        },
        "fill_color": {
            "anyOf": [RGB_255, RGBA_255, {"type": "null"}]
        },
        "outline_color": {
            "anyOf": [RGB_255, RGBA_255, {"type": "null"}]
        },
        "outline_width": {"type": "number", "minimum": 0},
        # Code uses 'gradient' key for polygon
        "gradient": GRADIENT_COMMON,
        # Also accept gradient_config for consistency
        "gradient_config": GRADIENT_COMMON,
    },
    "required": ["type", "points"],
    "additionalProperties": True,
}

# CTA Button (components/buttons.py)
CTA_BUTTON_COMPONENT = {
    "type": "object",
    "properties": {
        "type": {"const": "cta_button"},
        "position": POSITION,
        "size": SIZE,
        "text": {"type": "string"},
        "bg_color": {
            "anyOf": [RGB_255, RGBA_255, {"type": "string"}]  # hex allowed
        },
        "text_color": {
            "anyOf": [RGB_255, RGBA_255, {"type": "string"}]
        },
        "corner_radius": {"type": "number", "minimum": 0},
        "font_size": {"type": "number", "minimum": 1},
        "font_path": {"type": "string"},
        "url": {"type": "string"},
        "alignment": {"type": "string", "enum": ["left", "center", "right"]},
        "auto_width": {"type": "boolean"},
        "padding": {"type": "number", "minimum": 0}
    },
    "required": ["type", "text"],
    "additionalProperties": True,
}

# Footer (components/footer.py)
FOOTER_COMPONENT = {
    "type": "object",
    "properties": {
        "type": {"const": "footer"},
        "position": POSITION,
        "text": {"type": "string"},
        "font_size": {"type": "number", "minimum": 1},
        "color": RGB_255,
        "bg_color": {
            "anyOf": [RGB_255, {"type": "null"}]
        },
        "padding": {"type": "number", "minimum": 0},
        "font_path": {"type": "string"},
    },
    "required": ["type", "text"],
    "additionalProperties": True,
}

# Button Group (components/button_group.py)
BUTTON_GROUP_COMPONENT = {
    "type": "object",
    "properties": {
        "type": {"const": "button_group"},
        "position": POSITION,
        "items": {
            "type": "array",
            "minItems": 1,
            # items are mini components (text | cta_button)
            "items": {
                "anyOf": [
                    TEXT_COMPONENT,
                    CTA_BUTTON_COMPONENT,
                ]
            },
        },
        "spacing": {"type": "number", "minimum": 0},
        "max_width": {"type": "number", "minimum": 1},
        "line_height": {"type": "number", "minimum": 0.6, "maximum": 3.0},
        "align": {"type": "string", "enum": ["left", "center", "right"]},
    },
    "required": ["type", "items"],
    "additionalProperties": True,
}

# Ribbon Frame (components/shapes.py::RibbonFrame)
RIBBON_FRAME_COMPONENT = {
    "type": "object",
    "properties": {
        "type": {"const": "ribbon_frame"},
        "position": POSITION,
        "text": {"type": "string"},
        "font_size": {"type": "number", "minimum": 1},
        "font_path": {"type": "string"},
        "text_color": RGB_255,
        "fill_color": RGB_255,
        "outline_color": {"anyOf": [RGB_255, {"type": "null"}]},
        "padding": {"type": "number", "minimum": 0},
        "pointer_size": {"type": "number", "minimum": 0},
        "rotation": {"type": "number"},
        "triangle_direction": {"type": "string", "enum": ["open", "closed"]},
    },
    "required": ["type", "text"],
    "additionalProperties": True,
}

# ----- Main Component Union -----

COMPONENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "oneOf": [
        TEXT_COMPONENT,
        IMAGE_COMPONENT,
        RECTANGLE_COMPONENT,
        CIRCLE_COMPONENT,
        POLYGON_COMPONENT,
        CTA_BUTTON_COMPONENT,
        FOOTER_COMPONENT,
        BUTTON_GROUP_COMPONENT,
        RIBBON_FRAME_COMPONENT,
    ]
}

# ----- Template Schema -----

TEMPLATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "size": SIZE,
        "background_color": RGBA_255,
        "use_base_image": {"type": "boolean"},
        "base_image_url": {"type": "string"},
        "components": {
            "type": "array",
            "minItems": 1,
            "items": COMPONENT_SCHEMA,
        },
    },
    "required": ["name", "size", "components"],
    "additionalProperties": False,
}

def get_template_schema() -> Dict[str, Any]:
    """Return the main template JSON schema."""
    return TEMPLATE_SCHEMA

def get_component_schema() -> Dict[str, Any]:
    """Return the component JSON schema (union)."""
    return COMPONENT_SCHEMA
