"""
Utility functions for image processing.
"""
from typing import Tuple, Optional
from PIL import Image, ImageOps, ImageFilter


def resize_image(
    image: Image.Image,
    size: Tuple[int, int],
    keep_aspect_ratio: bool = True,
    resample: int = Image.Resampling.LANCZOS,
) -> Image.Image:
    """
    Resize an image while optionally maintaining aspect ratio.

    Args:
        image: Input image
        size: Target size as (width, height)
        keep_aspect_ratio: Whether to maintain the aspect ratio
        resample: Resampling filter to use

    Returns:
        Resized image
    """
    if not keep_aspect_ratio:
        return image.resize(size, resample=resample)

    # Calculate aspect ratio
    orig_width, orig_height = image.size
    target_width, target_height = size
    
    # Calculate new dimensions maintaining aspect ratio
    ratio = min(target_width / orig_width, target_height / orig_height)
    new_size = (int(orig_width * ratio), int(orig_height * ratio))
    
    return image.resize(new_size, resample=resample)


def apply_rounded_corners(
    image: Image.Image,
    radius: int = 10,
    background: Tuple[int, int, int, int] = (255, 255, 255, 0)
) -> Image.Image:
    """
    Apply rounded corners to an image.

    Args:
        image: Input image (must be RGBA)
        radius: Corner radius in pixels
        background: Background color (RGBA) for the corners

    Returns:
        Image with rounded corners
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create a mask for rounded corners
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw a white rounded rectangle on the mask
    draw.rounded_rectangle(
        [(0, 0), image.size],
        radius=radius,
        fill=255
    )
    
    # Create a new image with transparent background
    result = Image.new('RGBA', image.size, background)
    
    # Apply the mask to the original image
    result.paste(image, mask=mask)
    
    return result


def add_drop_shadow(
    image: Image.Image,
    offset: Tuple[int, int] = (5, 5),
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 128),
    blur_radius: int = 10,
    background: Tuple[int, int, int, int] = (255, 255, 255, 0)
) -> Image.Image:
    """
    Add a drop shadow to an image.

    Args:
        image: Input image (must be RGBA)
        offset: Shadow offset as (x, y)
        shadow_color: Shadow color (RGBA)
        blur_radius: Radius for the blur effect
        background: Background color (RGBA)

    Returns:
        Image with drop shadow
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create a new image with shadow
    shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    
    # Create a mask from the alpha channel
    mask = image.split()[3]
    
    # Apply blur to the mask
    if blur_radius > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
    
    # Draw the shadow
    shadow_draw.bitmap(offset, mask, fill=shadow_color)
    
    # Create the result image
    result = Image.new('RGBA', image.size, background)
    
    # Paste the shadow first, then the original image
    result.alpha_composite(shadow)
    result.alpha_composite(image)
    
    return result


def create_gradient(
    size: Tuple[int, int],
    colors: Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int]],
    direction: str = 'horizontal'
) -> Image.Image:
    """
    Create a gradient image.

    Args:
        size: Size of the gradient image (width, height)
        colors: Tuple of two RGBA colors for the gradient
        direction: Gradient direction ('horizontal' or 'vertical')

    Returns:
        Gradient image
    """
    width, height = size
    gradient = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    
    if direction == 'horizontal':
        for x in range(width):
            # Calculate the interpolation factor
            t = x / (width - 1)
            # Interpolate between the two colors
            r = int(colors[0][0] * (1 - t) + colors[1][0] * t)
            g = int(colors[0][1] * (1 - t) + colors[1][1] * t)
            b = int(colors[0][2] * (1 - t) + colors[1][2] * t)
            a = int(colors[0][3] * (1 - t) + colors[1][3] * t)
            # Draw a vertical line
            draw.line([(x, 0), (x, height)], fill=(r, g, b, a))
    else:  # vertical
        for y in range(height):
            # Calculate the interpolation factor
            t = y / (height - 1)
            # Interpolate between the two colors
            r = int(colors[0][0] * (1 - t) + colors[1][0] * t)
            g = int(colors[0][1] * (1 - t) + colors[1][1] * t)
            b = int(colors[0][2] * (1 - t) + colors[1][2] * t)
            a = int(colors[0][3] * (1 - t) + colors[1][3] * t)
            # Draw a horizontal line
            draw.line([(0, y), (width, y)], fill=(r, g, b, a))
    
    return gradient
