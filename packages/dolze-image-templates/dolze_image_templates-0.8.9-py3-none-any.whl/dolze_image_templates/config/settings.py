"""
Application settings and default configurations.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Base directory for the package
BASE_DIR = Path(__file__).parent.parent

# Default directories
DEFAULT_TEMPLATES_DIR = str(BASE_DIR / "templates")
DEFAULT_FONTS_DIR = str(BASE_DIR / "fonts")
DEFAULT_OUTPUT_DIR = str(BASE_DIR.parent / "output")

# Default template configuration
DEFAULT_TEMPLATE_CONFIG: Dict[str, Any] = {
    "size": {"width": 1080, "height": 1080},
    "background_color": (255, 255, 255, 255),
    "use_base_image": False,
    "components": [],
}

# Default font configuration
DEFAULT_FONT_CONFIG: Dict[str, Any] = {
    "default_font_size": 24,
    "default_font_family": "Roboto",
    "fallback_fonts": [
        "Arial",
        "Helvetica",
        "sans-serif",
    ],
}

# Default component styles
DEFAULT_COMPONENT_STYLES: Dict[str, Dict[str, Any]] = {
    "text": {
        "font_size": 24,
        "color": (0, 0, 0, 255),  # Black
        "alignment": "left",
    },
    "button": {
        "bg_color": (0, 123, 255, 255),  # Blue
        "text_color": (255, 255, 255, 255),  # White
        "corner_radius": 5,
        "padding": (10, 20),
    },
    "image": {
        "maintain_aspect_ratio": True,
        "resample": "lanczos",
    },
}

# Application settings
class Settings:
    """Application settings manager."""
    
    def __init__(self, **overrides):
        """
        Initialize settings with optional overrides.
        
        Args:
            **overrides: Key-value pairs to override default settings
        """
        # Core settings
        self.templates_dir = overrides.get("templates_dir", DEFAULT_TEMPLATES_DIR)
        self.fonts_dir = overrides.get("fonts_dir", DEFAULT_FONTS_DIR)
        self.output_dir = overrides.get("output_dir", DEFAULT_OUTPUT_DIR)
        
        # Ensure directories exist
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.fonts_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Template defaults
        self.template_config = DEFAULT_TEMPLATE_CONFIG.copy()
        if "template_config" in overrides:
            self.template_config.update(overrides["template_config"])
        
        # Font defaults
        self.font_config = DEFAULT_FONT_CONFIG.copy()
        if "font_config" in overrides:
            self.font_config.update(overrides["font_config"])
        
        # Component styles
        self.component_styles = DEFAULT_COMPONENT_STYLES.copy()
        if "component_styles" in overrides:
            for key, value in overrides["component_styles"].items():
                if key in self.component_styles:
                    self.component_styles[key].update(value)
                else:
                    self.component_styles[key] = value
    
    def update(self, **kwargs) -> None:
        """
        Update settings with new values.
        
        Args:
            **kwargs: Key-value pairs to update settings with
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            elif key in self.template_config:
                self.template_config[key] = value
            elif key in self.font_config:
                self.font_config[key] = value
            elif key in self.component_styles:
                if isinstance(self.component_styles[key], dict) and isinstance(value, dict):
                    self.component_styles[key].update(value)
                else:
                    self.component_styles[key] = value


# Default settings instance
default_settings = Settings()


def get_settings() -> Settings:
    """
    Get the default settings instance.
    
    Returns:
        Settings: The default settings instance
    """
    return default_settings


def configure(**overrides) -> None:
    """
    Configure the default settings.
    
    Args:
        **overrides: Key-value pairs to override default settings
    """
    global default_settings
    default_settings = Settings(**overrides)
