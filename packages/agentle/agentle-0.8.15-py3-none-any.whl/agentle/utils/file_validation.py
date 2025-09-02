"""File validation utilities for robust path handling and security checks.

This module provides centralized file validation functionality with industry-standard
path resolution, security checks, and comprehensive error handling.
"""

import os
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse


class FileValidationError(Exception):
    """Custom exception for file validation errors."""

    def __init__(self, message: str, path: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message)
        self.path = path
        self.error_code = error_code


class FileNotFoundError(FileValidationError):
    """Exception raised when a file is not found."""

    def __init__(self, path: str, resolved_path: Optional[str] = None):
        message = f"File not found: '{path}'"
        if resolved_path and resolved_path != path:
            message += f" (resolved to: '{resolved_path}')"
        super().__init__(message, path, "FILE_NOT_FOUND")
        self.resolved_path = resolved_path


class InvalidPathError(FileValidationError):
    """Exception raised when a path is invalid or unsafe."""

    def __init__(self, path: str, reason: str):
        message = f"Invalid path: '{path}' - {reason}"
        super().__init__(message, path, "INVALID_PATH")
        self.reason = reason


def resolve_file_path(file_path: str, base_path: Optional[str] = None) -> str:
    """Resolve a file path to an absolute path with proper validation.

    Args:
        file_path: The file path to resolve (can be relative or absolute)
        base_path: Optional base path for resolving relative paths.
                  If None, uses the current working directory.

    Returns:
        The resolved absolute path

    Raises:
        InvalidPathError: If the path is invalid or contains unsafe components
    """
    if not file_path:
        raise InvalidPathError(str(file_path), "Path must be a non-empty string")

    # Check for potentially dangerous path components
    if ".." in file_path:
        raise InvalidPathError(file_path, "Path traversal detected (contains '..')")

    try:
        path_obj = Path(file_path)

        # If path is not absolute, resolve it relative to base_path or cwd
        if not path_obj.is_absolute():
            if base_path:
                base_path_obj = Path(base_path).resolve()
                resolved_path = (base_path_obj / path_obj).resolve()
            else:
                resolved_path = path_obj.resolve()
        else:
            resolved_path = path_obj.resolve()

        return str(resolved_path)

    except (OSError, ValueError) as e:
        raise InvalidPathError(file_path, f"Path resolution failed: {str(e)}")


def validate_file_exists(
    file_path: str, base_path: Optional[str] = None
) -> Tuple[str, bool]:
    """Validate that a file exists and return its resolved path.

    Args:
        file_path: The file path to validate
        base_path: Optional base path for resolving relative paths

    Returns:
        Tuple of (resolved_path, exists)

    Raises:
        InvalidPathError: If the path is invalid
        FileNotFoundError: If the file does not exist
    """
    resolved_path = resolve_file_path(file_path, base_path)

    try:
        exists = Path(resolved_path).exists()
        if not exists:
            raise FileNotFoundError(file_path, resolved_path)

        return resolved_path, True

    except OSError as e:
        raise InvalidPathError(file_path, f"File access error: {str(e)}")


def is_url(content: str) -> bool:
    """Check if content is a URL.

    Args:
        content: The content to check

    Returns:
        True if content is a valid URL, False otherwise
    """
    try:
        parsed_url = urlparse(content)
        return parsed_url.scheme in ["http", "https"]
    except Exception:
        return False


def is_file_path(content: str, base_path: Optional[str] = None) -> bool:
    """Check if content is a valid file path that exists.

    Args:
        content: The content to check
        base_path: Optional base path for resolving relative paths

    Returns:
        True if content is a valid existing file path, False otherwise
    """
    if is_url(content):
        return False

    try:
        resolved_path = resolve_file_path(content, base_path)
        return Path(resolved_path).exists()
    except (FileValidationError, OSError):
        return False


def validate_content_type(
    content: str, base_path: Optional[str] = None
) -> Tuple[str, str]:
    """Determine and validate the type of content (URL, file path, or raw text).

    Args:
        content: The content to analyze
        base_path: Optional base path for resolving relative paths

    Returns:
        Tuple of (content_type, resolved_content) where:
        - content_type is one of: 'url', 'file_path', 'raw_text'
        - resolved_content is the original content or resolved file path

    Raises:
        FileNotFoundError: If content appears to be a file path but doesn't exist
        InvalidPathError: If content appears to be a file path but is invalid
    """
    if is_url(content):
        return "url", content

    # Check if it looks like a file path (contains path separators or file extensions)
    looks_like_path = (
        os.sep in content
        or "/" in content
        or "." in content
        and not content.startswith(".")
        and " " not in content
    )

    if looks_like_path:
        try:
            resolved_path, _ = validate_file_exists(content, base_path)
            return "file_path", resolved_path
        except FileValidationError:
            # Re-raise file validation errors for paths that look like file paths
            raise

    # If it doesn't look like a path or URL, treat as raw text
    return "raw_text", content


def get_file_info(file_path: str, base_path: Optional[str] = None) -> Dict[str, Any]:
    """Get comprehensive information about a file.

    Args:
        file_path: The file path to analyze
        base_path: Optional base path for resolving relative paths

    Returns:
        Dictionary containing file information:
        - resolved_path: The absolute resolved path
        - exists: Whether the file exists
        - size: File size in bytes (if exists)
        - extension: File extension
        - is_readable: Whether the file is readable

    Raises:
        InvalidPathError: If the path is invalid
    """
    resolved_path = resolve_file_path(file_path, base_path)
    path_obj = Path(resolved_path)

    info: dict[str, Any] = {
        "resolved_path": resolved_path,
        "exists": False,
        "size": None,
        "extension": path_obj.suffix.lower(),
        "is_readable": False,
    }

    try:
        if path_obj.exists():
            info["exists"] = True
            info["size"] = int(path_obj.stat().st_size)
            info["is_readable"] = os.access(resolved_path, os.R_OK)
    except OSError:
        # File exists but we can't access it
        pass

    return info
