"""
Template engine for rendering templates with components.
"""

import os
import json
import logging
import time
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from PIL import Image

from dolze_image_templates.components import create_component_from_config, Component
from dolze_image_templates.resources import load_image, load_font
from dolze_image_templates.exceptions import ResourceError
from dolze_image_templates.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)


class Template:
    """
    A template that can be composed of multiple components.
    """

    def __init__(
        self,
        name: str,
        size: Tuple[int, int] = (800, 600),
        background_color: Tuple[int, int, int] = (255, 255, 255),
    ):
        """
        Initialize a template.

        Args:
            name: Template name
            size: Size (width, height) of the template
            background_color: RGB color tuple for the background
        """
        self.name = name
        self.size = size
        self.background_color = background_color
        self.components: List[Component] = []

    def add_component(self, component: Component) -> None:
        """
        Add a component to the template.

        Args:
            component: Component to add
        """
        self.components.append(component)

    def render(self, base_image: Optional[Image.Image] = None) -> Image.Image:
        """
        Render the template with all its components.

        Args:
            base_image: Optional base image to use instead of creating a new one

        Returns:
            Rendered image
        """
        # Create a new image if no base image is provided
        if base_image is None:
            result = Image.new("RGBA", self.size, self.background_color)
        else:
            # Resize the base image if needed
            if base_image.size != self.size:
                base_image = base_image.resize(self.size, Image.Resampling.LANCZOS)

            # Convert to RGBA if needed
            if base_image.mode != "RGBA":
                result = base_image.convert("RGBA")
            else:
                result = base_image.copy()

        # Render each component
        for component in self.components:
            result = component.render(result)

        return result

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "Template":
        """
        Create a template from a configuration dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            A new template instance
        """
        name = config.get("name", "unnamed")

        size = (
            config.get("size", {}).get("width", 800),
            config.get("size", {}).get("height", 600),
        )

        background_color = tuple(config.get("background_color", (255, 255, 255)))

        template = cls(name=name, size=size, background_color=background_color)

        # Add components
        for component_config in config.get("components", []):
            component = create_component_from_config(component_config)
            if component:
                template.add_component(component)

        return template


class TemplateEngine:
    """
    Engine for processing templates and generating images.
    """

    def __init__(self, output_dir: str = "output"):
        """
        Initialize the template engine.

        Args:
            output_dir: Directory to store generated images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.templates: Dict[str, Template] = {}

    def add_template(self, template: Template) -> None:
        """
        Add a template to the engine.

        Args:
            template: Template to add
        """
        self.templates[template.name] = template

    def download_image(self, url: str) -> Optional[Image.Image]:
        """
        Download an image from a URL with caching.

        Args:
            url: URL of the image to download

        Returns:
            PIL Image object or None if download fails
        """
        try:
            # Use the cached image loading function which handles caching automatically
            return load_image(url)
        except ResourceError as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return None

    def process_json(self, json_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Process JSON input to generate images.

        Args:
            json_data: JSON data containing template configurations

        Returns:
            Dictionary with paths to generated images
        """
        results = {}

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Process each template in the JSON
        for template_name, template_data in json_data.items():
            try:
                logger.info(f"Processing template: {template_name}")

                # Create a new template
                template = Template(
                    name=template_name,
                    size=template_data.get("size", (800, 600)),
                    background_color=template_data.get(
                        "background_color", (255, 255, 255)
                    ),
                )

                # Add components
                for component_data in template_data.get("components", []):
                    try:
                        component = create_component_from_config(component_data)
                        if component:
                            template.add_component(component)
                    except Exception as e:
                        logger.error(
                            f"Error creating component in {template_name}: {e}"
                        )
                        continue

                # Render the template
                output_path = os.path.join(self.output_dir, f"{template_name}.png")

                try:
                    # Handle base image if specified
                    base_image = None
                    if template_data.get("use_base_image"):
                        base_image_path = template_data.get("base_image_path")
                        if base_image_path:
                            if base_image_path.startswith(("http://", "https://")):
                                base_image = self.download_image(base_image_path)
                            else:
                                base_image = load_image(base_image_path)

                    # Render with or without base image
                    rendered_image = template.render(base_image=base_image)

                    # Save the result
                    rendered_image.save(output_path)
                    results[template_name] = output_path
                    logger.info(f"Successfully generated: {output_path}")

                except Exception as e:
                    error_msg = f"Error rendering template {template_name}: {e}"
                    logger.error(error_msg)
                    results[template_name] = f"Error: {error_msg}"

            except Exception as e:
                error_msg = f"Error processing template {template_name}: {e}"
                logger.error(error_msg)
                results[template_name] = f"Error: {error_msg}"

        return results

    def process_from_file(self, json_file: str) -> Dict[str, str]:
        """
        Process JSON from a file.

        Args:
            json_file: Path to JSON file or directory containing JSON files

        Returns:
            Dictionary with paths to generated images
        """
        json_path = Path(json_file)
        results = {}

        try:
            if json_path.is_file():
                # Process a single file
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                results.update(self.process_json(json_data))

            elif json_path.is_dir():
                # Process all JSON files in the directory
                for file_path in json_path.glob("*.json"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            json_data = json.load(f)
                        results.update(self.process_json(json_data))
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {e}")
                        results[str(file_path)] = f"Error: {e}"
            else:
                error_msg = f"File or directory not found: {json_file}"
                logger.error(error_msg)
                results[json_file] = f"Error: {error_msg}"

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {json_file}: {e}"
            logger.error(error_msg)
            results[json_file] = f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Error processing {json_file}: {e}"
            logger.error(error_msg)
            results[json_file] = f"Error: {error_msg}"

        return results

    def clear_templates(self) -> None:
        """Clear all registered templates."""
        self.templates.clear()

    def render_template(
        self,
        template_name: str,
        variables: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None,
        output_format: str = "png",
        return_bytes: bool = False,
    ) -> Union[str, bytes]:
        """
        Render a template with the given variables.

        Args:
            template_name: Name of the template to render (must be in the templates directory)
            variables: Dictionary of variables to substitute in the template
            output_path: Path to save the rendered image. If None and return_bytes is False, a path will be generated.
            output_format: Output image format (e.g., 'png', 'jpg', 'jpeg')
            return_bytes: If True, returns the image as bytes instead of saving to disk

        Returns:
            If return_bytes is True: Image bytes
            If return_bytes is False: Path to the rendered image

        Raises:
            ValueError: If the template is not found or configuration is invalid
            IOError: If there's an error saving the image
            RuntimeError: If there's an error during rendering
        """
        try:
            from dolze_image_templates.core.template_registry import get_template_registry
            
            registry = get_template_registry()
            variables = variables or {}
            
            # Log start of rendering
            logger.info(f"Rendering template: {template_name}")
            start_time = time.time()
            
            # Render the template
            image = registry.render_template(template_name, variables)
            if image is None:
                error_msg = f"Template '{template_name}' not found or failed to render"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Handle output based on return_bytes flag
            if return_bytes:
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format=output_format.upper())
                logger.debug(f"Rendered template to bytes: {template_name}")
                return img_byte_arr.getvalue()
            
            # Generate output path if not provided
            if output_path is None:
                os.makedirs(self.output_dir, exist_ok=True)
                output_path = os.path.join(
                    self.output_dir,
                    f"{template_name}_{int(time.time())}.{output_format.lower()}",
                )
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save the image
            image.save(output_path, format=output_format.upper())
            logger.info(f"Saved rendered template to: {output_path} (took {time.time() - start_time:.2f}s)")
            
            return output_path
            
        except Exception as e:
            error_msg = f"Error rendering template '{template_name}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            if not isinstance(e, (ValueError, IOError, RuntimeError)):
                raise RuntimeError(error_msg) from e
            raise
