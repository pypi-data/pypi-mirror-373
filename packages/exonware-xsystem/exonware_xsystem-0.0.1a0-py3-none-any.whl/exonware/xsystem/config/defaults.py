"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Default configuration constants for xSystem framework.

These constants provide default values and limits for system operations.
All modules should import from this central location to ensure consistency.
"""

from typing import Final

# ======================
# Core Configuration
# ======================

# Default configuration values
DEFAULT_ENCODING: Final[str] = "utf-8"
DEFAULT_PATH_DELIMITER: Final[str] = "."
DEFAULT_LOCK_TIMEOUT: Final[float] = 10.0

# ======================
# Memory Safety Limits
# ======================

# Memory safety limits
DEFAULT_MAX_FILE_SIZE_MB: Final[int] = 100  # 100MB default limit
DEFAULT_MAX_MEMORY_USAGE_MB: Final[int] = 500  # 500MB default limit
DEFAULT_MAX_DICT_DEPTH: Final[int] = 50  # Maximum nesting depth

# ======================
# Path and Resolution Limits
# ======================

# RG operation safety limits
DEFAULT_MAX_PATH_DEPTH: Final[int] = 20  # Maximum path nesting depth
DEFAULT_MAX_PATH_LENGTH: Final[int] = 500  # Maximum path string length
DEFAULT_MAX_RESOLUTION_DEPTH: Final[int] = (
    10  # Maximum reference resolution depth per get_value call
)
DEFAULT_MAX_TO_DICT_SIZE_MB: Final[int] = 50  # Maximum memory for to_dict operations

# ======================
# Data Structure Limits
# ======================

DEFAULT_MAX_CIRCULAR_DEPTH: Final[int] = 100
DEFAULT_MAX_EXTENSION_LENGTH: Final[int] = 5
DEFAULT_CONTENT_SNIPPET_LENGTH: Final[int] = 200
DEFAULT_MAX_TRAVERSAL_DEPTH: Final[int] = 100

# ======================
# Protocol and Format Identifiers
# ======================

# Protocol and format identifiers
URI_SCHEME_SEPARATOR: Final[str] = "://"
JSON_POINTER_PREFIX: Final[str] = "#"
PATH_SEPARATOR_FORWARD: Final[str] = "/"
PATH_SEPARATOR_BACKWARD: Final[str] = "\\"

# ======================
# Placeholder Messages
# ======================

# Placeholder messages
CIRCULAR_REFERENCE_PLACEHOLDER: Final[str] = "[Circular Reference]"
MAX_DEPTH_EXCEEDED_PLACEHOLDER: Final[str] = "[Max Depth Exceeded]"

# ======================
# Logging Configuration
# ======================

# Logging control
LOGGING_ENABLED: Final[bool] = True
LOGGING_LEVEL: Final[str] = "INFO"
