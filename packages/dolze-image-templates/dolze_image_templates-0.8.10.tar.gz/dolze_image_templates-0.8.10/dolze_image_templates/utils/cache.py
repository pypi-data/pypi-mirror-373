"""
Caching utilities for frequently used resources like fonts and images.
"""

import os
import hashlib
import json
from typing import Dict, Any, Optional, Tuple, Union, TypeVar, Callable, Type
from pathlib import Path
import tempfile
from functools import wraps
import time

from PIL import Image, ImageFont

from dolze_image_templates.exceptions import ResourceError

T = TypeVar("T")


class ResourceCache:
    """
    A simple cache for resources like fonts and images.

    This cache stores resources in memory and optionally persists them to disk.
    """

    def __init__(
        self, cache_dir: Optional[Union[str, Path]] = None, max_size_mb: int = 100
    ):
        """
        Initialize the resource cache.

        Args:
            cache_dir: Directory to store cached files. If None, uses system temp dir.
            max_size_mb: Maximum cache size in megabytes.
        """
        self._in_memory_cache: Dict[str, Any] = {}
        self._cache_dir = (
            Path(cache_dir)
            if cache_dir
            else Path(tempfile.gettempdir()) / "dolze_image_templates_cache"
        )
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._metadata_file = self._cache_dir / ".cache_metadata.json"
        self._metadata: Dict[str, Dict[str, Any]] = self._load_metadata()

        # Clean up old cache entries if needed
        self._cleanup()

    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load cache metadata from disk."""
        if self._metadata_file.exists():
            try:
                with open(self._metadata_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            with open(self._metadata_file, "w") as f:
                json.dump(self._metadata, f, indent=2)
        except IOError as e:
            raise ResourceError(f"Failed to save cache metadata: {e}")

    def _get_cache_key(self, resource_type: str, *args: Any) -> str:
        """Generate a cache key for the given resource type and arguments."""
        key_parts = [resource_type] + [str(arg) for arg in args]
        key_str = "::".join(key_parts)
        return hashlib.md5(key_str.encode("utf-8")).hexdigest()

    def _get_cache_path(self, key: str, extension: str = "") -> Path:
        """Get the filesystem path for a cache entry."""
        return self._cache_dir / f"{key}{extension}"

    def _get_cache_size(self) -> int:
        """Calculate the total size of the cache in bytes."""
        total_size = 0
        for entry in self._cache_dir.glob("*"):
            if entry.is_file() and entry.name != ".cache_metadata.json":
                total_size += entry.stat().st_size
        return total_size

    def _cleanup(self) -> None:
        """Clean up old cache entries if the cache is too large."""
        current_size = self._get_cache_size()

        if current_size <= self.max_size_bytes:
            return

        # Sort entries by last access time (oldest first)
        entries = []
        for key, meta in self._metadata.items():
            cache_path = self._get_cache_path(key, meta.get("extension", ""))
            if cache_path.exists():
                entries.append(
                    (key, meta.get("last_access", 0), cache_path.stat().st_size)
                )

        entries.sort(key=lambda x: x[1])

        # Remove oldest entries until we're under the limit
        for key, _, size in entries:
            if current_size <= self.max_size_bytes * 0.9:  # Stop at 90% of max size
                break

            try:
                cache_path = self._get_cache_path(
                    key, self._metadata[key].get("extension", "")
                )
                if cache_path.exists():
                    cache_path.unlink()
                del self._metadata[key]
                current_size -= size
            except (KeyError, OSError):
                continue

        self._save_metadata()

    def get(
        self, resource_type: str, loader: Callable[..., T], *args: Any, **kwargs: Any
    ) -> T:
        """
        Get a resource from the cache, loading it if necessary.

        Args:
            resource_type: Type of resource (e.g., 'font', 'image').
            loader: Function to load the resource if not in cache.
            *args: Arguments to pass to the loader.
            **kwargs: Keyword arguments to pass to the loader.

        Returns:
            The loaded resource.

        Raises:
            ResourceError: If the resource cannot be loaded.
        """
        key = self._get_cache_key(resource_type, *args)
        extension = kwargs.pop("extension", "")

        # Check in-memory cache first
        if key in self._in_memory_cache:
            return self._in_memory_cache[key]

        cache_path = self._get_cache_path(key, extension)

        # Try to load from disk cache
        if cache_path.exists():
            try:
                resource = self._load_from_disk(cache_path, resource_type, **kwargs)
                self._in_memory_cache[key] = resource
                self._metadata[key] = {
                    "last_access": time.time(),
                    "extension": extension,
                    "resource_type": resource_type,
                }
                self._save_metadata()
                return resource
            except Exception as e:
                # If loading from disk fails, try to load fresh
                pass

        # Load the resource
        try:
            resource = loader(*args, **kwargs)
            self._in_memory_cache[key] = resource

            # Save to disk if it's a supported type
            if resource is not None:
                self._save_to_disk(resource, cache_path, resource_type)
                self._metadata[key] = {
                    "last_access": time.time(),
                    "extension": extension,
                    "resource_type": resource_type,
                }
                self._save_metadata()

            return resource
        except Exception as e:
            raise ResourceError(f"Failed to load resource: {e}")

    def _load_from_disk(self, path: Path, resource_type: str, **kwargs: Any) -> Any:
        """Load a resource from disk."""
        if resource_type == "image":
            return Image.open(path)
        elif resource_type == "font":
            size = kwargs.get("size", 12)
            return ImageFont.truetype(str(path), size=size)
        elif resource_type == "json":
            with open(path, "r") as f:
                return json.load(f)
        else:
            with open(path, "rb") as f:
                return f.read()

    def _save_to_disk(self, resource: Any, path: Path, resource_type: str) -> None:
        """Save a resource to disk."""
        if resource_type == "image":
            resource.save(path)
        elif resource_type == "font":
            # Fonts are already files, just copy them
            if hasattr(resource, "path"):
                import shutil

                shutil.copy2(resource.path, path)
        elif resource_type == "json":
            with open(path, "w") as f:
                json.dump(resource, f)
        else:
            with open(path, "wb") as f:
                if hasattr(resource, "read"):
                    f.write(resource.read())
                else:
                    f.write(resource)

    def clear(self) -> None:
        """Clear the cache."""
        self._in_memory_cache.clear()
        for path in self._cache_dir.glob("*"):
            if path.is_file() and path.name != ".cache_metadata.json":
                try:
                    path.unlink()
                except OSError:
                    continue
        self._metadata = {}
        self._save_metadata()


# Global cache instance
_resource_cache = ResourceCache()


def cached_resource(
    resource_type: str,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to cache the result of a resource loading function.

    Args:
        resource_type: Type of resource being cached (e.g., 'font', 'image').

    Returns:
        A decorator function.
    """

    def decorator(loader: Callable[..., T]) -> Callable[..., T]:
        @wraps(loader)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            cache_key = (resource_type,) + args + tuple(sorted(kwargs.items()))
            return _resource_cache.get(resource_type, loader, *args, **kwargs)

        return wrapper

    return decorator


def clear_cache() -> None:
    """Clear all cached resources."""
    _resource_cache.clear()


def get_cache_info() -> Dict[str, Any]:
    """Get information about the cache."""
    return {
        "in_memory_entries": len(_resource_cache._in_memory_cache),
        "disk_entries": len(_resource_cache._metadata),
        "cache_dir": str(_resource_cache._cache_dir),
        "max_size_mb": _resource_cache.max_size_bytes / (1024 * 1024),
    }
