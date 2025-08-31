"""
Resource loading and caching for templates.
"""

import os
import io
import requests
from typing import Optional, Union, Tuple, Dict, Any
from pathlib import Path

from PIL import Image, ImageFont

from dolze_image_templates.exceptions import ResourceError
from dolze_image_templates.utils.cache import cached_resource


def load_font(
    path: str, size: int = 12, fallback_font: Optional[str] = None
) -> ImageFont.FreeTypeFont:
    """
    Load a font with caching support.

    Args:
        path: Path to the font file or system font name.
        size: Font size in points.
        fallback_font: Fallback font name if the primary font fails to load.

    Returns:
        A PIL ImageFont object.

    Raises:
        ResourceError: If the font cannot be loaded.
    """
    # Try to load the font with caching
    try:
        return _load_font_cached(path, size)
    except Exception as e:
        if fallback_font and fallback_font != path:
            try:
                return _load_font_cached(fallback_font, size)
            except Exception:
                pass
        raise ResourceError(f"Failed to load font '{path}': {e}")


@cached_resource("font")
def _load_font_cached(path: str, size: int) -> ImageFont.FreeTypeFont:
    """
    Internal function to load a font with caching.
    """
    # Check if it's a system font
    try:
        return ImageFont.truetype(path, size=size)
    except (IOError, OSError):
        # If not a file path, try to load as a system font
        try:
            return ImageFont.load_default()
        except Exception as e:
            raise ResourceError(f"Failed to load font: {e}")


def load_image(
    source: Union[str, bytes, io.BytesIO, Path],
    size: Optional[Tuple[int, int]] = None,
    **kwargs: Any,
) -> Image.Image:
    """
    Load an image from a file path, URL, or binary data with caching support.

    Args:
        source: Image source (file path, URL, or binary data).
        size: Optional target size as (width, height). If provided, the image will be resized.
        **kwargs: Additional arguments for image processing.

    Returns:
        A PIL Image object.

    Raises:
        ResourceError: If the image cannot be loaded.
    """
    try:
        if isinstance(source, (str, Path)):
            if str(source).startswith(("http://", "https://")):
                return _load_remote_image(str(source), size, **kwargs)
            return _load_local_image(str(source), size, **kwargs)
        elif isinstance(source, (bytes, io.BytesIO)):
            return _load_binary_image(source, size, **kwargs)
        else:
            raise ValueError("Unsupported image source type")
    except Exception as e:
        raise ResourceError(f"Failed to load image: {e}")


def _load_remote_image(
    url: str, size: Optional[Tuple[int, int]] = None, **kwargs: Any
) -> Image.Image:
    """Load an image from a URL with caching."""
    # Generate a cache key based on URL and size
    cache_key = f"{url}_{size if size else ''}"

    try:
        # Try to load from cache first
        return _load_cached_image(cache_key, size, **kwargs)
    except ResourceError:
        # If not in cache, download and cache it
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # Load the image
        img = Image.open(io.BytesIO(response.content))

        # Convert to RGB if necessary
        if img.mode != "RGBA" and img.mode != "RGB":
            img = img.convert("RGBA")

        # Resize if needed
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)

        # Save to cache
        _save_to_cache(cache_key, img, "image")

        return img


def _load_local_image(
    path: str, size: Optional[Tuple[int, int]] = None, **kwargs: Any
) -> Image.Image:
    """Load an image from a local file path with caching."""
    # Use the file path and modification time as part of the cache key
    file_path = Path(path)
    mtime = file_path.stat().st_mtime if file_path.exists() else 0
    cache_key = f"local_{path}_{mtime}_{size if size else ''}"

    try:
        return _load_cached_image(cache_key, size, **kwargs)
    except ResourceError:
        # If not in cache, load from disk
        img = Image.open(file_path)

        # Convert to RGB if necessary
        if img.mode != "RGBA" and img.mode != "RGB":
            img = img.convert("RGBA")

        # Resize if needed
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)

        # Save to cache
        _save_to_cache(cache_key, img, "image")

        return img


def _load_binary_image(
    data: Union[bytes, io.BytesIO],
    size: Optional[Tuple[int, int]] = None,
    **kwargs: Any,
) -> Image.Image:
    """Load an image from binary data with caching."""
    if isinstance(data, bytes):
        data = io.BytesIO(data)

    # For binary data, we don't cache by default as there's no good cache key
    img = Image.open(data)

    # Convert to RGB if necessary
    if img.mode != "RGBA" and img.mode != "RGB":
        img = img.convert("RGBA")

    # Resize if needed
    if size:
        img = img.resize(size, Image.Resampling.LANCZOS)

    return img


def _load_cached_image(
    cache_key: str, size: Optional[Tuple[int, int]] = None, **kwargs: Any
) -> Image.Image:
    """Load an image from the cache."""
    from dolze_image_templates.utils.cache import _resource_cache

    # Try to load from memory cache first
    if cache_key in _resource_cache._in_memory_cache:
        img = _resource_cache._in_memory_cache[cache_key]
        if size and img.size != size:
            return img.resize(size, Image.Resampling.LANCZOS)
        return img

    # Not in memory cache, try disk cache
    raise ResourceError("Image not found in cache")


def _save_to_cache(key: str, resource: Any, resource_type: str, **kwargs: Any) -> None:
    """Save a resource to the cache."""
    from dolze_image_templates.utils.cache import _resource_cache

    # Save to memory cache
    _resource_cache._in_memory_cache[key] = resource

    # Save to disk cache if it's an image
    if resource_type == "image" and isinstance(resource, Image.Image):
        cache_path = _resource_cache._get_cache_path(key, ".png")
        resource.save(cache_path, "PNG")

        # Update metadata
        _resource_cache._metadata[key] = {
            "last_access": 0,  # Will be updated on access
            "extension": ".png",
            "resource_type": "image",
        }
        _resource_cache._save_metadata()
