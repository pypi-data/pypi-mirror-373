"""
Path utilities for OpenFiles SDK
Handles S3-style path conventions and base path resolution
"""

from typing import Optional


def join_paths(base_path: str, relative_path: str) -> str:
    """
    Joins base path and relative path using S3-style conventions
    - No leading slashes (S3-style)
    - Handles empty paths gracefully
    - Normalizes duplicate slashes
    - Preserves trailing slashes only when meaningful

    Args:
        base_path: The base path to prefix with
        relative_path: The relative path to append

    Returns:
        Combined path following S3-style conventions

    Examples:
        >>> join_paths("projects/website", "config.json")
        "projects/website/config.json"
        >>> join_paths("", "config.json")
        "config.json"
        >>> join_paths("projects", "")
        "projects"
        >>> join_paths("projects/", "config.json")
        "projects/config.json"
        >>> join_paths("projects//", "/config.json")
        "projects/config.json"
    """
    # Handle empty cases
    if not base_path and not relative_path:
        return ""
    if not base_path:
        return normalize_path(relative_path)
    if not relative_path:
        return normalize_path(base_path)

    # Remove leading and trailing slashes, then normalize
    normalized_base = normalize_path(base_path)
    normalized_relative = normalize_path(relative_path)

    # If base path is empty after normalization, just return relative
    if not normalized_base:
        return normalized_relative
    if not normalized_relative:
        return normalized_base

    # Join with single slash
    return f"{normalized_base}/{normalized_relative}"


def normalize_path(path: str) -> str:
    """
    Normalizes a path by removing leading slashes and collapsing duplicate slashes
    Follows S3-style path conventions (no leading slashes)

    Args:
        path: The path to normalize

    Returns:
        Normalized path

    Examples:
        >>> normalize_path("/projects/website")
        "projects/website"
        >>> normalize_path("projects//website")
        "projects/website"
        >>> normalize_path("///projects/")
        "projects"
    """
    if not path:
        return ""

    # Remove leading slashes (S3-style: no leading slashes)
    # Replace multiple slashes with single slash
    # Remove trailing slashes (unless it's a meaningful directory indicator)
    return path.lstrip("/").replace("//", "/").rstrip("/")  # Replace double slashes


def resolve_path(path: str, base_path: Optional[str] = None) -> str:
    """
    Resolves the final path by combining base path and relative path

    Args:
        path: The relative path from the operation
        base_path: Optional base path to prefix

    Returns:
        Final resolved path

    Examples:
        >>> resolve_path("file.txt", "projects/website")
        "projects/website/file.txt"
        >>> resolve_path("file.txt", None)
        "file.txt"
        >>> resolve_path("file.txt", "")
        "file.txt"
    """
    if not base_path:
        return normalize_path(path)

    return join_paths(base_path, path)
