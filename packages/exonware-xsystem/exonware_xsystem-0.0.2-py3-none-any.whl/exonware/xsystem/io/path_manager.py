"""
Universal path and URI management utilities for xsystem.

This module provides common path and URI handling functionality that can be
reused across different xLib components, extracted from xData to reduce complexity.
"""

import logging
import os
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Constants
URI_SCHEME_SEPARATOR = "://"
JSON_POINTER_PREFIX = "#"


class PathManager:
    """
    Centralized path and URI management utilities.

    This class provides static methods for common path operations that were
    previously embedded in xData but are generally useful across xLib components.
    """

    @staticmethod
    def looks_like_file_path(source: str) -> bool:
        """
        Determines if a string looks like a file path rather than raw content.

        This method uses heuristics to distinguish between file paths and
        raw data content based on common patterns.

        Args:
            source: String to check

        Returns:
            True if the string appears to be a file path, False if it looks like raw content
        """
        # Skip empty strings
        if not source or not source.strip():
            return False

        source = source.strip()

        # Check for absolute paths
        if os.path.isabs(source):
            return True

        # Check for path separators
        if "/" in source or "\\" in source:
            return True

        # Check for file extensions (dot followed by 1-5 alphanumeric characters)
        if re.match(r".*\.[a-zA-Z0-9]{1,5}$", source):
            return True

        # Check if it looks like a relative file path with directory components
        if "." in source and (
            source.count(".") <= 2
        ):  # Allow up to 2 dots (e.g., ../file.ext)
            parts = source.split(".")
            if len(parts) >= 2 and parts[-1].isalnum() and len(parts[-1]) <= 5:
                return True

        # If it's a very short string without special characters, likely raw content
        if len(source) < 3:
            return False

        # If it contains newlines, likely raw content
        if "\n" in source or "\r" in source:
            return False

        # If it contains typical data format indicators, likely raw content
        data_indicators = ["{", "[", "<", "=", ":", "true", "false", "null"]
        for indicator in data_indicators:
            if indicator in source.lower():
                return False

        return False

    @staticmethod
    def resolve_base_path(path: Optional[str]) -> Optional[str]:
        """
        Resolve and normalize a base path for reference resolution.

        This method handles both local file system paths and URI schemes,
        converting them to a normalized form suitable for base path resolution.

        Args:
            path: Path to resolve (can be file path, directory path, or URI)

        Returns:
            Resolved base path or None if path is None/empty
        """
        if not path:
            return None

        try:
            if URI_SCHEME_SEPARATOR in path:  # URI scheme (http://, file://, etc.)
                logger.debug(f"PathManager: Base path treated as URI scheme: {path}")
                return path

            # Process as local file system path
            normalized_path = os.path.normpath(path)
            abs_path = os.path.abspath(normalized_path)

            if os.path.isfile(abs_path):
                # If it's a file, use its directory as base
                result = os.path.dirname(abs_path)
                logger.debug(
                    f"PathManager: Base path resolved from file: {path} -> {result}"
                )
                return result
            elif os.path.isdir(abs_path):
                # If it's a directory, use it directly
                logger.debug(
                    f"PathManager: Base path resolved as directory: {path} -> {abs_path}"
                )
                return abs_path
            else:
                # Path doesn't exist - determine if it looks like a file path
                if "." in os.path.basename(normalized_path):
                    # Has extension, treat as file and use directory
                    result = os.path.dirname(abs_path)
                    logger.debug(
                        f"PathManager: Base path resolved from non-existent file: {path} -> {result}"
                    )
                    return result
                else:
                    # No extension, treat as intended directory
                    logger.debug(
                        f"PathManager: Base path resolved as intended directory: {path} -> {abs_path}"
                    )
                    return abs_path

        except Exception as e:
            logger.warning(
                f"PathManager: Could not resolve base path for '{path}': {e}. Using as-is."
            )
            return path  # Fallback to using the path as given

    @staticmethod
    def get_canonical_uri(ref_uri: str, ref_base_path: Optional[str]) -> str:
        """
        Create a canonical, absolute URI for a reference.

        This method handles different types of URIs including JSON pointers,
        absolute URIs, absolute file paths, and relative paths that need to
        be resolved against a base path.

        Args:
            ref_uri: The reference URI to canonicalize
            ref_base_path: Base path to resolve relative URIs against

        Returns:
            Canonical, absolute URI
        """
        # Internal JSON pointers are already canonical within their document context
        if ref_uri.startswith(JSON_POINTER_PREFIX):
            return ref_uri

        # Absolute URLs/URIs are already canonical
        if URI_SCHEME_SEPARATOR in ref_uri:
            return ref_uri

        # Absolute file paths are canonical after normalization
        if os.path.isabs(ref_uri):
            return os.path.normpath(ref_uri)

        # Relative paths need to be resolved against the base path
        if ref_base_path:
            # Determine the effective base directory
            effective_base_dir = ref_base_path

            # If base path is a URI scheme, use it directly
            if URI_SCHEME_SEPARATOR not in ref_base_path:
                # For local file system paths, check if base is a file or directory
                if os.path.exists(ref_base_path) and os.path.isfile(ref_base_path):
                    effective_base_dir = os.path.dirname(ref_base_path)
                elif not os.path.exists(ref_base_path) and "." in os.path.basename(
                    ref_base_path
                ):
                    # Non-existent path that looks like a file
                    effective_base_dir = os.path.dirname(ref_base_path)

            # Join the paths appropriately
            if URI_SCHEME_SEPARATOR in effective_base_dir:
                # URL-style joining
                canonical_uri = (
                    f"{effective_base_dir.rstrip('/')}/{ref_uri.lstrip('/')}"
                )
                logger.debug(
                    f"PathManager: Canonical URI (URL): {ref_uri} + {ref_base_path} -> {canonical_uri}"
                )
                return canonical_uri
            else:
                # File system path joining
                try:
                    canonical_uri = os.path.normpath(
                        os.path.join(effective_base_dir, ref_uri)
                    )
                    logger.debug(
                        f"PathManager: Canonical URI (FS): {ref_uri} + {ref_base_path} -> {canonical_uri}"
                    )
                    return canonical_uri
                except Exception as e:
                    logger.warning(
                        f"PathManager: Failed to join base_path '{effective_base_dir}' and ref_uri '{ref_uri}': {e}"
                    )
                    return ref_uri

        # No base path provided, return relative URI as-is
        logger.debug(f"PathManager: No base path for relative URI: {ref_uri}")
        return ref_uri

    @staticmethod
    def is_uri_scheme(path: str) -> bool:
        """
        Check if a path contains a URI scheme (like http://, file://, etc.).

        Args:
            path: Path to check

        Returns:
            True if path contains a URI scheme separator
        """
        return URI_SCHEME_SEPARATOR in path

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize a file system path.

        Args:
            path: Path to normalize

        Returns:
            Normalized path, or original path if normalization fails
        """
        try:
            return os.path.normpath(path)
        except Exception:
            return path

    @staticmethod
    def get_absolute_path(path: str) -> str:
        """
        Get absolute path from relative or absolute path.

        Args:
            path: Path to make absolute

        Returns:
            Absolute path, or original path if conversion fails
        """
        try:
            return os.path.abspath(path)
        except Exception:
            return path

    @staticmethod
    def get_relative_path_from_project_root(file_path: str) -> Path:
        """
        Get the relative path from the project root to the directory containing the given file.

        This method finds the project root by looking for common project indicators
        (like .git, setup.py, pyproject.toml, etc.) and returns the relative path
        from that root to the directory containing the specified file.

        Args:
            file_path: Path to the file (typically __file__)

        Returns:
            Path object representing the relative path from project root to the file's directory
        """
        current_path = Path(file_path).resolve().parent

        # Primary project root indicators (strong indicators)
        primary_indicators = [
            ".git",
            "setup.py",
            "pyproject.toml",
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
            "main.py",
        ]

        # Secondary indicators (need multiple to be confident)
        secondary_indicators = ["src", "tests"]

        # Walk up the directory tree to find project root
        for parent in [current_path] + list(current_path.parents):
            # Check for primary indicators
            primary_found = [
                ind for ind in primary_indicators if (parent / ind).exists()
            ]
            secondary_found = [
                ind for ind in secondary_indicators if (parent / ind).exists()
            ]

            # Special case: if we find .git, that's almost certainly the project root
            if ".git" in primary_found:
                return current_path.relative_to(parent)

            # If we find multiple primary indicators, that's likely the project root
            if len(primary_found) >= 2:
                return current_path.relative_to(parent)

            # If we find a primary indicator plus secondary indicators, that's good
            if len(primary_found) >= 1 and len(secondary_found) >= 1:
                return current_path.relative_to(parent)

        # If no clear project root found, return just the directory name
        return Path(current_path.name)
