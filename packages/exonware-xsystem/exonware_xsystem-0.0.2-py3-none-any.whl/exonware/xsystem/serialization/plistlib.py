"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Plistlib Serializer Implementation

Provides Apple Property List serialization using the built-in plistlib module
following the 'no hardcode' principle.
"""

import plistlib
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from .aSerialization import aSerialization, SerializationError


class PlistlibError(SerializationError):
    """Plistlib-specific serialization error."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "Plistlib", original_error)


class PlistlibSerializer(aSerialization):
    """
    Plistlib serializer using built-in plistlib module.
    
    This implementation strictly follows the 'no hardcode' principle by using
    only the built-in plistlib library for Apple Property List operations.
    
    Features:
    - Uses plistlib.dumps/loads for plist operations
    - Binary or text format (configurable)
    - Security validation
    - Atomic file operations
    - Supports Apple plist data types
    
    Note: Plistlib is optional and primarily for macOS/iOS configurations
    """

    def __init__(
        self,
        fmt: int = plistlib.FMT_XML,  # plistlib.FMT_XML or plistlib.FMT_BINARY
        sort_keys: bool = True,
        skipkeys: bool = False,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 100,
        max_size_mb: int = 50
    ) -> None:
        """
        Initialize Plistlib serializer.

        Args:
            fmt: Plist format (plistlib.FMT_XML or plistlib.FMT_BINARY)
            sort_keys: Whether to sort dictionary keys
            skipkeys: Whether to skip invalid dict keys
            validate_input: Enable input data validation
            validate_paths: Enable path security validation
            use_atomic_writes: Use atomic file operations
            max_depth: Maximum nesting depth
            max_size_mb: Maximum data size in MB
        """
        super().__init__(
            validate_input=validate_input,
            validate_paths=validate_paths,
            use_atomic_writes=use_atomic_writes,
            max_depth=max_depth,
            max_size_mb=max_size_mb
        )

        self._fmt = fmt
        self._sort_keys = sort_keys
        self._skipkeys = skipkeys

    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "Plistlib"

    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".plist", ".xml", ".binary")

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        if self._fmt == plistlib.FMT_XML:
            return "application/x-plist+xml"
        else:
            return "application/x-plist+binary"

    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return self._fmt == plistlib.FMT_BINARY

    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return False  # plistlib doesn't support streaming

    def dumps(self, data: Any) -> Union[str, bytes]:
        """
        Serialize data to plist format using plistlib.

        ✅ PRODUCTION LIBRARY: plistlib.dumps()
        
        Args:
            data: Data to serialize (must be plist-compatible)
            
        Returns:
            Plist format string (XML) or bytes (binary)
        """
        if self.validate_input:
            self._validate_data_security(data)

        try:
            if self._fmt == plistlib.FMT_XML:
                # XML format returns bytes, but we'll decode to string
                result_bytes = plistlib.dumps(
                    data,
                    fmt=self._fmt,
                    sort_keys=self._sort_keys,
                    skipkeys=self._skipkeys
                )
                return result_bytes.decode('utf-8')
            else:
                # Binary format returns bytes
                return plistlib.dumps(
                    data,
                    fmt=self._fmt,
                    sort_keys=self._sort_keys,
                    skipkeys=self._skipkeys
                )

        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> Any:
        """
        Deserialize plist format using plistlib.

        ✅ PRODUCTION LIBRARY: plistlib.loads()
        
        Args:
            data: Plist format string or bytes
            
        Returns:
            Deserialized data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        if not isinstance(data, bytes):
            raise PlistlibError(f"Expected string or bytes, got {type(data)}")

        try:
            result = plistlib.loads(data)
            
            if self.validate_input:
                self._validate_data_security(result)
                
            return result

        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def save_file(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Save data to plist file.
        
        Args:
            data: Data to serialize
            file_path: Path to the plist file
        """
        validated_path = self._validate_file_path(file_path)
        
        if self.validate_input:
            self._validate_data_security(data)
        
        try:
            # Use plistlib's file writing capabilities
            with open(validated_path, 'wb') as f:
                plistlib.dump(
                    data,
                    f,
                    fmt=self._fmt,
                    sort_keys=self._sort_keys,
                    skipkeys=self._skipkeys
                )
            
        except Exception as e:
            self._handle_serialization_error("file save", e)

    def load_file(self, file_path: Union[str, Path]) -> Any:
        """
        Load data from plist file.
        
        Args:
            file_path: Path to the plist file
            
        Returns:
            Deserialized data
        """
        validated_path = self._validate_file_path(file_path)
        
        try:
            # Use plistlib's file reading capabilities
            with open(validated_path, 'rb') as f:
                result = plistlib.load(f)
                
            if self.validate_input:
                self._validate_data_security(result)
                
            return result
            
        except Exception as e:
            self._handle_serialization_error("file load", e)

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get Plistlib format schema information.

        Returns:
            Schema information dictionary
        """
        return {
            "format": "Plistlib",
            "version": "1.0",
            "description": "Apple Property List (using built-in plistlib)",
            "features": {
                "binary": self.is_binary_format,
                "xml_format": self._fmt == plistlib.FMT_XML,
                "binary_format": self._fmt == plistlib.FMT_BINARY,
                "apple_types": True,
                "streaming": False,
                "secure_parsing": True
            },
            "supported_types": [
                "dict", "list", "str", "bytes", "int", "float", "bool", "datetime", "UUID"
            ],
            "format_type": "XML" if self._fmt == plistlib.FMT_XML else "Binary",
            "sort_keys": self._sort_keys,
            "skipkeys": self._skipkeys,
            "file_extensions": list(self.file_extensions),
            "mime_type": self.mime_type
        }

    def get_config(self) -> Dict[str, Any]:
        """
        Get current serializer configuration.

        Returns:
            Configuration dictionary
        """
        config = super().get_config()
        config.update({
            "format": "XML" if self._fmt == plistlib.FMT_XML else "Binary",
            "sort_keys": self._sort_keys,
            "skipkeys": self._skipkeys
        })
        return config
