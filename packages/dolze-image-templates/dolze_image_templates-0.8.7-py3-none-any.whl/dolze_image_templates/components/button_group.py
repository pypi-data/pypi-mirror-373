"""
Button group components for arranging multiple text and button elements in templates.
"""

from typing import Tuple, Optional, Dict, Any, List, Union
from PIL import Image,ImageDraw

from .base import Component
from .text import TextComponent
from .buttons import CTAButtonComponent


class CTAButtonGroupComponent(Component):
    """Component for rendering groups of text and CTA buttons in a configurable layout"""

    def __init__(
        self,
        items: List[Dict[str, Any]],
        position: Tuple[int, int] = (0, 0),
        spacing: int = 10,
        max_width: Optional[int] = None,
        line_height: float = 1.5,
        align: str = "left",
    ):
        """
        Initialize a CTA button group component.

        Args:
            items: List of item configurations (text or cta_button)
            position: Position (x, y) of the group
            spacing: Horizontal spacing between items in pixels
            max_width: Maximum width before wrapping to next line (None for no limit)
            line_height: Vertical spacing multiplier between lines
            align: Alignment of items ('left', 'center', 'right')
        """
        super().__init__(position)
        self.items = items
        self.spacing = max(0, spacing)  # Ensure spacing is not negative
        self.max_width = max_width
        self.line_height = max(1.0, line_height)  # Ensure line_height is at least 1.0
        self.align = align.lower()
        
        # Validate alignment
        if self.align not in ["left", "center", "right"]:
            print(f"Warning: Invalid alignment '{align}'. Defaulting to 'left'.")
            self.align = "left"
        
        # Initialize components list
        self._components = []
        self._parse_items()
    
    def _parse_items(self):
        """Parse the items list and create appropriate components"""
        for item in self.items:
            item_type = item.get("type", "text")
            
            if item_type == "text":
                # Create a text component
                self._components.append({
                    "type": "text",
                    "component": TextComponent.from_config(item)
                })
            elif item_type == "cta_button":
                # Create a CTA button component
                self._components.append({
                    "type": "cta_button",
                    "component": CTAButtonComponent.from_config(item)
                })
            else:
                print(f"Warning: Unknown item type '{item_type}'. Skipping.")
    
    def _calculate_layout(self, image: Image.Image):
        """
        Calculate the layout of components based on max_width, spacing, and alignment.
        
        Returns:
            List of components with their calculated positions
        """
        if not self._components:
            return []
            
        draw = image.draw if hasattr(image, 'draw') else ImageDraw.Draw(image)
        
        # Initialize variables for layout calculation
        current_x = self.position[0]
        current_y = self.position[1]
        current_line_height = 0
        current_line_components = []
        all_positioned_components = []
        
        for comp_info in self._components:
            component = comp_info["component"]
            comp_type = comp_info["type"]
            
            # Calculate component width
            if comp_type == "text":
                # For text components, calculate width based on text content
                text = component.text
                font = None
                
                # Get font from TextComponent
                if hasattr(component, "font_path") and hasattr(component, "font_size"):
                    from dolze_image_templates.core.font_manager import get_font_manager
                    font_manager = get_font_manager()
                    font = font_manager.get_font(component.font_path, component.font_size)
                
                if font and text:
                    # Create a dummy draw to measure text
                    dummy_img = Image.new('RGB', (1, 1))
                    dummy_draw = ImageDraw.Draw(dummy_img)
                    text_bbox = dummy_draw.textbbox((0, 0), text, font=font)
                    comp_width = text_bbox[2] - text_bbox[0]
                else:
                    comp_width = 0
            elif comp_type == "cta_button":
                # For button components, use the size attribute
                comp_width = component.size[0] if hasattr(component, "size") and component.size else 0
            else:
                comp_width = 0
                
            # Calculate component height
            if comp_type == "text":
                comp_height = component.font_size if hasattr(component, "font_size") else 0
            elif comp_type == "cta_button":
                comp_height = component.size[1] if hasattr(component, "size") and component.size else 0
            else:
                comp_height = 0
                
            # Check if adding this component would exceed max_width
            if self.max_width and current_x + comp_width > self.position[0] + self.max_width:
                # Position components in the current line based on alignment
                self._position_line_components(current_line_components, current_y, current_line_height)
                all_positioned_components.extend(current_line_components)
                
                # Start a new line
                current_x = self.position[0]
                current_y += current_line_height + int(current_line_height * (self.line_height - 1))
                current_line_height = 0
                current_line_components = []
            
            # Add component to current line
            current_line_components.append({
                "component": component,
                "width": comp_width,
                "height": comp_height,
                "x": current_x,
                "y": current_y
            })
            
            # Update current_x for next component
            current_x += comp_width + self.spacing
            
            # Update current line height if this component is taller
            current_line_height = max(current_line_height, comp_height)
        
        # Position the last line of components
        if current_line_components:
            self._position_line_components(current_line_components, current_y, current_line_height)
            all_positioned_components.extend(current_line_components)
        
        return all_positioned_components
    
    def _position_line_components(self, line_components, y, line_height):
        """Position components in a line based on alignment"""
        if not line_components:
            return
            
        # Calculate total width of components in this line (including spacing)
        total_width = sum(comp["width"] for comp in line_components)
        total_width += self.spacing * (len(line_components) - 1)
        
        # Calculate starting x based on alignment
        start_x = self.position[0]
        if self.align == "center" and self.max_width:
            start_x = self.position[0] + (self.max_width - total_width) // 2
        elif self.align == "right" and self.max_width:
            start_x = self.position[0] + (self.max_width - total_width)
            
        # Update x positions based on alignment
        current_x = start_x
        for comp in line_components:
            comp["x"] = current_x
            
            # Center component vertically within the line
            comp["y"] = y + (line_height - comp["height"]) // 2
            
            current_x += comp["width"] + self.spacing
    
    def render(self, image: Image.Image) -> Image.Image:
        """Render the button group onto an image"""
        result = image.copy()
        
        # Calculate layout
        positioned_components = self._calculate_layout(result)
        
        # Render each component at its calculated position
        for comp_info in positioned_components:
            component = comp_info["component"]
            original_position = component.position
            
            # Temporarily update component position for rendering
            component.position = (comp_info["x"], comp_info["y"])
            
            # Render the component
            result = component.render(result)
            
            # Restore original position
            component.position = original_position
            
        return result

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "CTAButtonGroupComponent":
        """Create a CTA button group component from a configuration dictionary"""
        position = (
            config.get("position", {}).get("x", 0),
            config.get("position", {}).get("y", 0),
        )

        return cls(
            items=config.get("items", []),
            position=position,
            spacing=config.get("spacing", 10),
            max_width=config.get("max_width"),
            line_height=config.get("line_height", 1.5),
            align=config.get("align", "left"),
        )
