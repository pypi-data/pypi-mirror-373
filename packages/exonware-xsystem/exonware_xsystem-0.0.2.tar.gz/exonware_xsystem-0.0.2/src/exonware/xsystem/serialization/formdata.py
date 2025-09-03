"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

FormData (URL-encoded) Serializer Implementation

Provides URL-encoded form data serialization with proper encoding,
nested data support, and integration with xSystem utilities.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import urllib.parse
from pathlib import Path

from .iSerialization import iSerialization
from .aSerialization import aSerialization


class FormDataSerializer(aSerialization):
    """
    FormData (application/x-www-form-urlencoded) serializer.
    
    ⚠️  REFACTORING NEEDED: This serializer has extensive custom flattening/unflattening
        logic that violates the 'no hardcode' principle. Future versions should:
        1. Use a production library for nested form data handling
        2. Simplify to basic urllib.parse functionality only
        3. Remove custom parsing logic (_flatten_data, _unflatten_data, _convert_value)
    
    Current implementation:
    ✅ Uses urllib.parse for core encoding/decoding (production library)
    ❌ Has custom logic for nested structures (hardcoded)
    
    Features:
    - URL-encoded form data serialization
    - Nested data flattening (❌ custom hardcoded logic)
    - Array handling (❌ custom hardcoded logic)
    - Proper URL encoding/decoding (✅ urllib.parse)
    - Text format
    - Security validation
    - Atomic file operations
    """
    
    def __init__(
        self,
        encoding: str = "utf-8",
        quote_plus: bool = True,
        keep_blank_values: bool = False,
        strict_parsing: bool = False,
        max_num_fields: Optional[int] = None,
        separator: str = "&",
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 10,
        max_size_mb: int = 10
    ) -> None:
        """
        Initialize FormData serializer.
        
        Args:
            encoding: Character encoding for URL encoding
            quote_plus: Use '+' for spaces instead of '%20'
            keep_blank_values: Keep blank values in parsing
            strict_parsing: Raise error on parsing errors
            max_num_fields: Maximum number of fields to parse
            separator: Field separator character
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
        
        self._encoding = encoding
        self._quote_plus = quote_plus
        self._keep_blank_values = keep_blank_values
        self._strict_parsing = strict_parsing
        self._max_num_fields = max_num_fields
        self._separator = separator
    
    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "FormData"
    
    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".form", ".urlencoded")
    
    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/x-www-form-urlencoded"
    
    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return False
    
    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return False
    
    def _flatten_data(self, data: Any, parent_key: str = "", separator: str = ".") -> Dict[str, str]:
        """
        Flatten nested data structure for form encoding.
        
        Args:
            data: Data to flatten
            parent_key: Parent key prefix
            separator: Key separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                if isinstance(value, (dict, list)):
                    items.extend(self._flatten_data(value, new_key, separator).items())
                else:
                    items.append((new_key, str(value) if value is not None else ""))
        
        elif isinstance(data, (list, tuple)):
            for i, value in enumerate(data):
                new_key = f"{parent_key}[{i}]"
                if isinstance(value, (dict, list)):
                    items.extend(self._flatten_data(value, new_key, separator).items())
                else:
                    items.append((new_key, str(value) if value is not None else ""))
        
        else:
            # Simple value
            items.append((parent_key, str(data) if data is not None else ""))
        
        return dict(items)
    
    def _unflatten_data(self, flat_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Unflatten form data back to nested structure.
        
        Args:
            flat_data: Flattened form data
            
        Returns:
            Nested data structure
        """
        result = {}
        
        for key, value in flat_data.items():
            # Parse nested keys like "user.name" or "items[0].name"
            keys = self._parse_nested_key(key)
            current = result
            
            for i, k in enumerate(keys[:-1]):
                if k not in current:
                    # Determine if next key is numeric (array index)
                    next_key = keys[i + 1]
                    if next_key.isdigit():
                        current[k] = []
                    else:
                        current[k] = {}
                current = current[k]
            
            final_key = keys[-1]
            if isinstance(current, list):
                # Extend list if necessary
                index = int(final_key)
                while len(current) <= index:
                    current.append(None)
                current[index] = self._convert_value(value)
            else:
                current[final_key] = self._convert_value(value)
        
        return result
    
    def _parse_nested_key(self, key: str) -> List[str]:
        """
        Parse nested key into components.
        
        Args:
            key: Nested key string
            
        Returns:
            List of key components
        """
        import re
        
        # Handle array notation: "items[0].name" -> ["items", "0", "name"]
        # Handle dot notation: "user.name" -> ["user", "name"]
        
        # Replace array notation with dots
        key = re.sub(r'\[(\d+)\]', r'.\1', key)
        
        # Split by dots
        return key.split('.')
    
    def _convert_value(self, value: str) -> Any:
        """
        Convert string value to appropriate type.
        
        Args:
            value: String value to convert
            
        Returns:
            Converted value
        """
        if value == "":
            return "" if self._keep_blank_values else None
        
        # Try to convert to number
        if value.isdigit():
            return int(value)
        
        try:
            if '.' in value:
                return float(value)
        except ValueError:
            pass
        
        # Try to convert to boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        if value.lower() in ('null', 'none'):
            return None
        
        return value
    
    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to URL-encoded string.
        
        ⚠️  CONTAINS HARDCODED LOGIC: This method uses custom flattening logic
            instead of a production library. Uses urllib.parse for encoding only.
        
        Args:
            data: Data to serialize (dict, list, or simple values)
            
        Returns:
            URL-encoded string
            
        Raises:
            ValueError: If data validation fails
        """
        if self.validate_input:
            self._validate_data_security(data)
        
        try:
            # Flatten nested data
            if isinstance(data, dict):
                flat_data = self._flatten_data(data)
            elif isinstance(data, (list, tuple)):
                flat_data = self._flatten_data({"items": data})
            else:
                flat_data = {"value": str(data)}
            
            # URL encode
            if self._quote_plus:
                encoded_pairs = [
                    f"{urllib.parse.quote_plus(str(k), encoding=self._encoding)}="
                    f"{urllib.parse.quote_plus(str(v), encoding=self._encoding)}"
                    for k, v in flat_data.items()
                ]
            else:
                encoded_pairs = [
                    f"{urllib.parse.quote(str(k), encoding=self._encoding)}="
                    f"{urllib.parse.quote(str(v), encoding=self._encoding)}"
                    for k, v in flat_data.items()
                ]
            
            return self._separator.join(encoded_pairs)
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)
    
    def loads_text(self, data: str) -> Dict[str, Any]:
        """
        Deserialize URL-encoded data.
        
        ⚠️  CONTAINS HARDCODED LOGIC: This method uses custom unflattening logic
            instead of a production library. Uses urllib.parse for decoding only.
        
        Args:
            data: URL-encoded string to deserialize
            
        Returns:
            Deserialized data
            
        Raises:
            ValueError: If data is invalid or validation fails
        """
        if isinstance(data, bytes):
            data = data.decode(self._encoding)
        
        if not isinstance(data, str):
            raise ValueError(f"Expected string or bytes, got {type(data)}")
        
        try:
            # Parse URL-encoded data
            parsed = urllib.parse.parse_qs(
                data,
                keep_blank_values=self._keep_blank_values,
                strict_parsing=self._strict_parsing,
                encoding=self._encoding,
                max_num_fields=self._max_num_fields,
                separator=self._separator
            )
            
            # Convert lists with single items to single values
            flat_data = {}
            for key, values in parsed.items():
                if len(values) == 1:
                    flat_data[key] = values[0]
                else:
                    flat_data[key] = values
            
            # Unflatten the data
            result = self._unflatten_data(flat_data)
            
            if self.validate_input:
                self._validate_data_security(result)
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)
    
    # 🎯 OPTIMIZATION: save_file and load_file inherited from base class!
    # Base class automatically handles text format based on is_binary_format flag
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get FormData format schema information.
        
        Returns:
            Schema information dictionary
        """
        return {
            "format": "FormData",
            "version": "URL-encoded",
            "description": "Application/x-www-form-urlencoded format",
            "features": {
                "binary": False,
                "nested_data": True,
                "array_support": True,
                "url_safe": True,
                "streaming": False
            },
            "supported_types": [
                "string", "number", "boolean", "dict", "list"
            ],
            "encoding": self._encoding,
            "quote_plus": self._quote_plus,
            "separator": self._separator,
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
            "encoding": self._encoding,
            "quote_plus": self._quote_plus,
            "keep_blank_values": self._keep_blank_values,
            "strict_parsing": self._strict_parsing,
            "max_num_fields": self._max_num_fields,
            "separator": self._separator
        })
        return config


# Error classes for consistency with other serializers
class FormDataError(Exception):
    """Base exception for FormData serialization errors."""
    pass
