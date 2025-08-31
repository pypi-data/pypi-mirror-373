"""
GIF Generator for Dolze Templates

This script generates animated GIFs using Dolze templates.

To add a new animation:
1. Create a template JSON file in dolze_image_templates/templates/
2. Add a function that calls create_animation() with your variations
3. Add your function to the templates list in main()

Example template (save as hello_world.json in templates/):
{
  "name": "hello_world",
  "size": {"width": 400, "height": 200},
  "components": [
    {
      "type": "text",
      "text": "${message}",
      "x": 200,
      "y": 100,
      "color": ${color},
      "font_size": 36,
      "align": "center"
    }
  ]
}
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from PIL import Image

# Add the parent directory to the path so we can import the template engine
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dolze_image_templates.core import Template, TemplateEngine, get_template_registry

def get_template_registry() -> 'TemplateRegistry':
    """Get a template registry instance."""
    from dolze_image_templates.core import TemplateRegistry
    return TemplateRegistry()

def generate_animation_frames(
    template_name: str, 
    variations: List[Dict[str, Any]], 
    duration: int = 500, 
    loop: int = 0, 
    template_data: Optional[Dict] = None
) -> str:
    """
    Generate an animated GIF from template variations.
    
    Args:
        template_name: Name of the template to use
        variations: List of dictionaries with template data for each frame
        duration: Duration of each frame in milliseconds
        loop: Number of loops (0 = infinite)
        template_data: Optional template data to use instead of registry
        
    Returns:
        Path to the generated GIF file
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    frames = _render_frames(template_name, variations, template_data, output_dir)
    
    if not frames:
        print("No frames were generated successfully.")
        return ""
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{template_name}_animation_{timestamp}.gif"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save as GIF
    print(f"\nGenerating GIF: {output_path}")
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop,
        optimize=True,
        disposal=2  # Background disposal (restore to background)
    )
    
    return str(output_path)

def _render_frames(
    template_name: str, 
    variations: List[Dict[str, Any]], 
    template_data: Optional[Dict],
    output_dir: str
) -> List[Image.Image]:
    """Render frames for the animation."""
    from dolze_image_templates.core.template_registry import get_template_registry
    import json
    
    registry = get_template_registry()
    frames = []
    
    # Get the template config from the registry or use the provided template_data
    if template_data:
        template_config = template_data
    else:
        template_config = registry.get_template(template_name)
        if not template_config:
            print(f"Error: Template '{template_name}' not found and no template data provided")
            return []
    
    for variation in variations:
        try:
            # Create a deep copy of the template config to avoid modifying the original
            import copy
            current_config = copy.deepcopy(template_config)
            
            # Recursively update the config with variables for this frame
            def update_config(config, vars_dict):
                if isinstance(config, dict):
                    for key, value in list(config.items()):
                        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                            var_name = value[2:-1]  # Remove ${ and }
                            if var_name in vars_dict:
                                config[key] = vars_dict[var_name]
                        elif isinstance(value, (dict, list)):
                            update_config(value, vars_dict)
                elif isinstance(config, list):
                    for i, item in enumerate(config):
                        if isinstance(item, str) and item.startswith('${') and item.endswith('}'):
                            var_name = item[2:-1]
                            if var_name in vars_dict:
                                config[i] = vars_dict[var_name]
                        elif isinstance(item, (dict, list)):
                            update_config(item, vars_dict)
            
            if variation:
                update_config(current_config, variation)
            
            # Create and render the template
            img = _render_template(current_config)
            if img is not None:
                frames.append(img)
                
        except Exception as e:
            print(f"Error generating frame: {str(e)}")
            continue
    
    return frames



def _render_template(config: Dict) -> Optional[Image.Image]:
    """Render a single frame from a template config."""
    try:
        engine = TemplateEngine()
        template = Template.from_config(config)
        engine.add_template(template)
        img = template.render()
        
        # Make sure the image is in RGBA mode
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        return img
        
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
        return None

def create_animation(template_name: str, variations: List[Dict], duration: int = 500, loop: int = 0) -> str:
    """Helper function to create an animation from a template and variations.
    
    Args:
        template_name: Name of the template JSON file (without .json extension)
        variations: List of dictionaries with variable values for each frame
        duration: Duration of each frame in milliseconds
        loop: Number of loops (0 = infinite)
    """
    # Load the template
    template_path = os.path.join(
        os.path.dirname(__file__), 
        "..", 
        "dolze_image_templates", 
        "templates", 
        f"{template_name}.json"
    )
    with open(template_path, "r") as f:
        template_data = json.load(f)
    
    # Generate the animation
    return generate_animation_frames(
        template_name=template_name,
        variations=variations,
        duration=duration,
        loop=loop,
        template_data=template_data
    )

def generate_status_indicator() -> str:
    """Example: Status indicator that toggles between states."""
    return create_animation(
        template_name="status_indicator",
        variations=[
            {"status_text": "DEFAULT", "status_color": [100, 100, 100]},
            {"status_text": "ACTIVE", "status_color": [76, 175, 80]}
        ]
    )

def generate_hello_world() -> str:
    """Example: Simple text animation."""
    return create_animation(
        template_name="hello_world",  # You'll need to create this template
        variations=[
            {"message": "Hello", "color": [255, 0, 0]},
            {"message": "World!", "color": [0, 0, 255]}
        ],
        duration=300  # Faster animation
    )

def generate_juice_poster() -> str:
    """Generate a juice poster with animated text.
    
    The text will change from 'GET 25% OFF' to 'I\'M A GIF' after 0.5 seconds.
    """
    return create_animation(
        template_name="juice_poster_gif",
        variations=[
            {
                "headline": "GET 25% OFF",
                "subtitle": "On your first order!",
                "theme_color": [255, 105, 0],  # Orange color
                "background_image_url": "https://i.postimg.cc/cCN5RtSB/image-24.png",
                "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
                "juice_image_url": "https://i.postimg.cc/9MPBjx6y/Frame-1244832601.png",
                "cta_text": "ORDER NOW"
            },
            {
                "headline": "I'M A GIF",
                "subtitle": "Check out this animation!",
                "theme_color": [0, 150, 255],  # Blue color
                "background_image_url": "https://i.postimg.cc/cCN5RtSB/image-24.png",
                "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
                "juice_image_url": "https://i.postimg.cc/9MPBjx6y/Frame-1244832601.png",
                "cta_text": "ORDER NOW"
            }
        ],
        duration=500,  # 0.5 seconds per frame
        loop=0  # Infinite loop
    )

def generate_education_gif() -> str:
    """Generate an education promotional GIF with text and background color changes."""
    return create_animation(
        template_name="learn_gif_template",
        variations=[
            {
                "headline": "Best way to Learn",
                "feature1": "150+ categories",
                "feature2": "Experienced trainer",
                "feature3": "All time support",
                "feature4": "Big community",
                "cta_text": "Join now",
                "cta_color": [35, 75, 241],
                "cta_text_color": [255, 255, 255],
                "background_color": [255, 210, 76]
            },
            {
                "headline": "Grow your Skills",
                "feature1": "Top educators",
                "feature2": "Flexible schedule",
                "feature3": "Live sessions",
                "feature4": "Career support",
                "cta_text": "Start Learning",
                "cta_color": [15, 76, 129],
                "cta_text_color": [255, 255, 255],
                "background_color": [209, 232, 226]
            },
            {
                "headline": "Learn Anytime",
                "feature1": "Mobile friendly",
                "feature2": "Interactive content",
                "feature3": "Trusted by many",
                "feature4": "Track progress",
                "cta_text": "Get Started",
                "cta_color": [255, 111, 97],
                "cta_text_color": [255, 255, 255],
                "background_color": [255, 226, 226]
            }
        ],
        duration=1000,
        loop=0
    )

def main() -> int:
    """Generate all animated GIFs."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating animated GIFs...\n")
    
    try:
        # List of all template generation functions
        templates = [
            # ("juice_poster", generate_juice_poster),
            ("education_gif", generate_education_gif),
            # ("status_indicator", generate_status_indicator),
            # Add more templates here:
            # ("hello_world", generate_hello_world),
        ]
        
        success_count = 0
        
        for name, generator in templates:
            print(f"\n=== Generating {name} ===\n")
            try:
                output_path = generator()
                if output_path:
                    print(f"\n{name} generated successfully!")
                    print(f"Output file: {output_path}")
                    success_count += 1
                else:
                    print(f"\nFailed to generate {name}.")
            except Exception as e:
                print(f"\nError generating {name}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 50)
        print(f"Generation complete! {success_count}/{len(templates)} templates generated successfully.")
        print("=" * 50)
        
        # Try to open the output directory
        try:
            import platform
            if platform.system() == 'Darwin':  # macOS
                os.system(f'open "{output_dir}"')
            elif platform.system() == 'Windows':
                os.system(f'explorer "{output_dir}"')
            elif platform.system() == 'Linux':
                os.system(f'xdg-open "{output_dir}"')
        except Exception:
            pass  # Ignore errors when trying to open the directory
        
        return 0 if success_count == len(templates) else 1
            
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
