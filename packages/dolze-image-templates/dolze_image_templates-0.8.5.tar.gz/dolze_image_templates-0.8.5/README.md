Dolze Templates
A powerful Python library for generating stunning, dynamic images using JSON templates

Overview
Dolze Templates is a versatile Python library designed to simplify the creation of dynamic, visually appealing images through intuitive JSON templates. Perfect for generating social media posts, marketing materials, product showcases, and more, Dolze Templates empowers developers to craft professional-grade visuals with minimal effort.
✨ Features

Dynamic Image Generation: Create stunning images programmatically using JSON templates.
Rich Component Library: Includes text, images, buttons, shapes, and more for flexible designs.
High Performance: Optimized with intelligent caching for fast image generation.
Extensible Architecture: Easily add custom components and templates to suit your needs.
Advanced Styling: Supports transparency, gradients, shadows, and other visual effects.
Responsive Design: Templates adapt seamlessly to various dimensions and resolutions.
Robust Validation: Comprehensive input validation with clear, helpful error messages.
CLI Support: Process templates efficiently using the built-in command-line interface.

📦 Installation
Dolze Templates requires Python 3.8 or higher. Install the latest version from PyPI:
pip install dolze-templates

Optional Dependencies
Enhance functionality with additional dependencies:

# For image processing

pip install dolze-templates[images]

# For advanced text rendering

pip install dolze-templates[text]

# For all optional dependencies

pip install dolze-templates[all]

Development Setup
To contribute or modify the source code:
git clone https://github.com/yourusername/dolze-templates.git
cd dolze-templates
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
pytest # Run tests

🚀 Quick Start
Basic Usage
Render a template with a few lines of code:
from dolze_image_templates import TemplateEngine

# Initialize the template engine

engine = TemplateEngine(output_dir="./output", cache_dir="./cache")

# Process a template

result = engine.process_from_file("templates/social_media_post.json")
print(f"Generated: {result}")

Rendering with Variables
Dynamically populate templates with custom data:
from dolze_image_templates import TemplateEngine

engine = TemplateEngine()
context = {
"heading": "Welcome to Dolze",
"subheading": "Create amazing images with ease",
"image_url": "https://example.com/hero.jpg"
}
result = engine.process_template("brand_info", template_config, context)
print(f"Image saved to: {result}")

Command-Line Interface
Use the CLI for quick template processing:

# Render a single template

dolze-templates render templates/post.json -o output/

# Process all templates in a directory

dolze-templates render templates/ -o output/ --recursive

# Clear cache

dolze-templates cache clear

🎨 Available Templates

Template Name
Description
Sample

brand_info
Professional brand information card
View Sample

quote_template
Elegant quote display with styling
View Sample

product_showcase
Product showcase with details and images
View Sample

Explore more templates in the examples/ directory.
🧩 Components
Dolze Templates provides a rich set of built-in components:
Text Component
{
"type": "text",
"text": "Hello, World!",
"position": [100, 200],
"font_size": 36,
"color": [0, 0, 0, 255],
"font_path": "Poppins-Bold",
"max_width": 800
}

Image Component
{
"type": "image",
"image_url": "https://example.com/image.jpg",
"position": [0, 0],
"size": [800, 600],
"border_radius": 10,
"opacity": 0.9
}

Button Component
{
"type": "cta_button",
"text": "Click Me",
"position": [100, 400],
"size": [200, 50],
"bg_color": [33, 150, 243, 255],
"text_color": [255, 255, 255, 255],
"corner_radius": 25
}

🛠️ Advanced Usage
Custom Components
Extend functionality by creating custom components:
from dolze_image_templates.components import Component
from PIL import Image, ImageDraw

class CustomShapeComponent(Component):
def **init**(self, position, size, color, **kwargs):
super().**init**(position=position, **kwargs)
self.size = size
self.color = color

    def render(self, image, context):
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            [self.x, self.y, self.x + self.size[0], self.y + self.size[1]],
            fill=tuple(self.color)
        )
        return image

# Register the component

from dolze_image_templates import get_template_registry
registry = get_template_registry()
registry.register_component('custom_shape', CustomShapeComponent)

Template Structure
Define templates using JSON:
{
"name": "social_media_post",
"settings": {
"size": [1080, 1080],
"background_color": [255, 255, 255, 255]
},
"components": [
{
"type": "text",
"text": "${greeting}",
"position": [100, 100],
"font_size": 64,
"color": [0, 0, 0, 255]
}
]
}

📋 Template Variables
Templates support dynamic variables for flexible content:

logo_url: URL to your logo
image_url: URL to the main image
heading: Primary text
subheading: Secondary text
cta_text: Call-to-action text
contact_email: Contact email
contact_phone: Contact phone
website_url: Website URL
quote: Quote text for quote templates

📚 API Reference
TemplateEngine
The core class for processing templates:
engine = TemplateEngine(
output_dir='output',
cache_dir='.cache',
auto_create_dirs=True
)
result = engine.process_from_file('template.json')

TemplateRegistry
Manages components and template loaders:
registry = get_template_registry()
registry.register_component('custom', CustomComponent)

🤝 Contributing
We welcome contributions! To get started:

Fork the repository
Create a feature branch: git checkout -b feature/your-feature
Commit changes: git commit -m 'Add your feature'
Push to the branch: git push origin feature/your-feature
Open a pull request

See Contributing Guidelines for details.
📄 License
This project is licensed under the MIT License. See the LICENSE file for details.
📬 Contact
For support or inquiries, open an issue on GitHub or email us at support@dolze.com.

Made with ❤️ by the Dolze Team
