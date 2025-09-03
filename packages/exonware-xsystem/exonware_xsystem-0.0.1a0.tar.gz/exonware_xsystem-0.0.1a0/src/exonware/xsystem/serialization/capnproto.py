"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Enhanced Cap'n Proto serialization with security, validation and performance optimizations.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type

try:
    import capnp
except ImportError:
    capnp = None

from .aSerialization import aSerialization, SerializationError
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.serialization.capnproto")


class CapnProtoError(SerializationError):
    """Cap'n Proto-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "CAPNPROTO", original_error)


class CapnProtoSerializer(aSerialization):
    """
    Enhanced Cap'n Proto serializer with schema validation and xSystem integration.
    
    Cap'n Proto is an infinitely fast data interchange format and capability-based RPC system.
    
    Features:
    - Zero-copy deserialization
    - Extremely fast serialization/deserialization
    - Schema evolution support
    - Memory-safe access patterns
    - Cross-language compatibility
    
    🚨 PRODUCTION LIBRARY: Uses pycapnp - the official Python implementation
    """

    def __init__(
        self,
        schema_file: Optional[Union[str, Path]] = None,
        struct_name: Optional[str] = None,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 100.0,  # Cap'n Proto is very efficient
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
        traversal_limit: int = 64 * 1024 * 1024,  # 64MB traversal limit
    ) -> None:
        """
        Initialize Cap'n Proto serializer with schema and security options.
        
        Raises:
            CapnProtoError: If pycapnp is not available

        Args:
            schema_file: Path to .capnp schema file
            struct_name: Name of the struct to serialize (required if schema_file provided)
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
            traversal_limit: Message traversal limit for security
        """
        # Check if pycapnp is available
        if capnp is None:
            raise CapnProtoError(
                "Cap'n Proto requires pycapnp which needs C++ build tools.\n"
                "Install with: pip install pycapnp\n"
                "Note: This is optional - you have 23 other serialization formats available!"
            )
            
        # Initialize base class with xSystem integration
        super().__init__(
            validate_input=validate_input,
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            use_atomic_writes=use_atomic_writes,
            validate_paths=validate_paths,
            base_path=base_path,
        )
        
        # Cap'n Proto-specific configuration
        self.schema_file = Path(schema_file) if schema_file else None
        self.struct_name = struct_name
        self.traversal_limit = traversal_limit
        self._schema_module = None
        self._struct_class = None
        
        # Load schema if provided
        if self.schema_file and self.struct_name:
            self._load_schema()
        
        # Update configuration with Cap'n Proto-specific options
        self._config.update({
            'schema_file': str(self.schema_file) if self.schema_file else None,
            'struct_name': struct_name,
            'traversal_limit': traversal_limit,
        })

    def _load_schema(self) -> None:
        """Load Cap'n Proto schema from file."""
        try:
            if not self.schema_file or not self.schema_file.exists():
                raise CapnProtoError(f"Schema file not found: {self.schema_file}")
            
            # Load schema module
            self._schema_module = capnp.load(str(self.schema_file))
            
            # Get struct class
            if not hasattr(self._schema_module, self.struct_name):
                raise CapnProtoError(f"Struct '{self.struct_name}' not found in schema")
            
            self._struct_class = getattr(self._schema_module, self.struct_name)
            
        except Exception as e:
            raise CapnProtoError(f"Failed to load Cap'n Proto schema: {e}", e)

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "CAPNPROTO"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return ['.capnp', '.cnp']

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/x-capnproto"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return True

    def _validate_schema_loaded(self) -> None:
        """Validate that schema is loaded."""
        if not self._schema_module or not self._struct_class:
            raise CapnProtoError("Schema must be loaded before serialization. Provide schema_file and struct_name.")

    def _dict_to_capnp(self, data: Dict[str, Any]):
        """Convert dictionary to Cap'n Proto message."""
        self._validate_schema_loaded()
        
        try:
            # Create new message builder
            message = self._struct_class.new_message()
            
            # Set fields from dictionary
            for key, value in data.items():
                if hasattr(message, key):
                    if isinstance(value, dict):
                        # Nested structure - recursively convert
                        nested_field = getattr(message, key)
                        self._set_nested_fields(nested_field, value)
                    elif isinstance(value, list):
                        # List field
                        list_field = getattr(message, key)
                        if hasattr(list_field, 'init'):
                            list_field.init(len(value))
                            for i, item in enumerate(value):
                                if isinstance(item, dict):
                                    self._set_nested_fields(list_field[i], item)
                                else:
                                    list_field[i] = item
                        else:
                            setattr(message, key, value)
                    else:
                        # Simple field
                        setattr(message, key, value)
                else:
                    logger.warning(f"Cap'n Proto struct has no field '{key}'")
            
            return message
            
        except Exception as e:
            raise CapnProtoError(f"Failed to convert dict to Cap'n Proto message: {e}", e)

    def _set_nested_fields(self, nested_obj, data: Dict[str, Any]) -> None:
        """Set fields in nested Cap'n Proto object."""
        for key, value in data.items():
            if hasattr(nested_obj, key):
                if isinstance(value, dict):
                    nested_field = getattr(nested_obj, key)
                    self._set_nested_fields(nested_field, value)
                else:
                    setattr(nested_obj, key, value)

    def _capnp_to_dict(self, message) -> Dict[str, Any]:
        """Convert Cap'n Proto message to dictionary."""
        try:
            result = {}
            
            # Get schema to iterate over fields
            schema = message.schema
            
            for field in schema.fields:
                field_name = field.name
                
                if hasattr(message, field_name):
                    value = getattr(message, field_name)
                    
                    # Handle different field types
                    if hasattr(value, 'schema') and hasattr(value.schema, 'fields'):
                        # Nested struct
                        result[field_name] = self._capnp_to_dict(value)
                    elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                        # List field
                        result[field_name] = [
                            self._capnp_to_dict(item) if hasattr(item, 'schema') else item
                            for item in value
                        ]
                    else:
                        # Simple field
                        result[field_name] = value
            
            return result
            
        except Exception as e:
            raise CapnProtoError(f"Failed to convert Cap'n Proto message to dict: {e}", e)

    def dumps(self, data: Any) -> str:
        """
        Serialize data to Cap'n Proto and return as base64-encoded string.

        Args:
            data: Data to serialize

        Returns:
            Base64-encoded Cap'n Proto string

        Raises:
            CapnProtoError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            
            # Serialize to Cap'n Proto bytes
            capnp_bytes = self.dumps_binary(data)
            
            # Encode to base64 string for string interface
            import base64
            return base64.b64encode(capnp_bytes).decode('ascii')
            
        except SerializationError as e:
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> Any:
        """
        Deserialize Cap'n Proto data to Python object.

        Args:
            data: Cap'n Proto bytes or base64-encoded string to deserialize

        Returns:
            Dictionary representation of Cap'n Proto message

        Raises:
            CapnProtoError: If deserialization fails
        """
        try:
            # Handle both bytes and base64 string
            if isinstance(data, str):
                import base64
                capnp_bytes = base64.b64decode(data.encode('ascii'))
            else:
                capnp_bytes = data
            
            return self.loads_bytes(capnp_bytes)
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def dumps_binary(self, data: Any) -> bytes:
        """
        Serialize data to Cap'n Proto bytes directly.

        Args:
            data: Data to serialize

        Returns:
            Cap'n Proto bytes

        Raises:
            CapnProtoError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            self._validate_schema_loaded()
            
            # Convert data to Cap'n Proto message
            if isinstance(data, dict):
                message = self._dict_to_capnp(data)
            elif hasattr(data, 'schema'):
                # Already a Cap'n Proto message
                message = data
            else:
                # Try to convert other types to dict first
                if hasattr(data, '__dict__'):
                    message = self._dict_to_capnp(data.__dict__)
                else:
                    raise CapnProtoError(f"Cannot serialize data of type {type(data)} to Cap'n Proto")
            
            # Serialize to bytes
            return message.to_bytes()
            
        except SerializationError as e:
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads_bytes(self, data: bytes) -> Dict[str, Any]:
        """
        Deserialize Cap'n Proto bytes to Python dictionary.

        Args:
            data: Cap'n Proto bytes to deserialize

        Returns:
            Dictionary representation of Cap'n Proto message

        Raises:
            CapnProtoError: If deserialization fails
        """
        try:
            self._validate_schema_loaded()
            
            # Deserialize from bytes with traversal limit for security
            with self._struct_class.from_bytes(
                data, 
                traversal_limit_in_words=self.traversal_limit // 8
            ) as message:
                # Convert to dictionary for consistent API
                return self._capnp_to_dict(message)
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def loads_message(self, data: Union[bytes, str]):
        """
        Deserialize Cap'n Proto data to Cap'n Proto message object.

        Args:
            data: Cap'n Proto bytes or base64-encoded string to deserialize

        Returns:
            Cap'n Proto message object

        Raises:
            CapnProtoError: If deserialization fails
        """
        try:
            self._validate_schema_loaded()
            
            # Handle both bytes and base64 string
            if isinstance(data, str):
                import base64
                capnp_bytes = base64.b64decode(data.encode('ascii'))
            else:
                capnp_bytes = data
            
            # Deserialize from bytes with traversal limit for security
            return self._struct_class.from_bytes(
                capnp_bytes,
                traversal_limit_in_words=self.traversal_limit // 8
            )
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)


# Convenience functions for common use cases
def dumps(data: Any, schema_file: Optional[Union[str, Path]] = None, struct_name: Optional[str] = None, **kwargs: Any) -> str:
    """Serialize data to Cap'n Proto base64-encoded string with default settings."""
    serializer = CapnProtoSerializer(schema_file=schema_file, struct_name=struct_name, **kwargs)
    return serializer.dumps(data)


def loads(s: str, schema_file: Optional[Union[str, Path]] = None, struct_name: Optional[str] = None, **kwargs: Any) -> Any:
    """Deserialize Cap'n Proto string with default settings.""" 
    serializer = CapnProtoSerializer(schema_file=schema_file, struct_name=struct_name, **kwargs)
    return serializer.loads(s)


def dumps_bytes(data: Any, schema_file: Optional[Union[str, Path]] = None, struct_name: Optional[str] = None, **kwargs: Any) -> bytes:
    """Serialize data to Cap'n Proto bytes with default settings."""
    serializer = CapnProtoSerializer(schema_file=schema_file, struct_name=struct_name, **kwargs)
    return serializer.dumps_binary(data)


def loads_bytes(data: bytes, schema_file: Optional[Union[str, Path]] = None, struct_name: Optional[str] = None, **kwargs: Any) -> Any:
    """Deserialize Cap'n Proto bytes with default settings."""
    serializer = CapnProtoSerializer(schema_file=schema_file, struct_name=struct_name, **kwargs)
    return serializer.loads_bytes(data)


def loads_message(data: Union[bytes, str], schema_file: Optional[Union[str, Path]] = None, struct_name: Optional[str] = None, **kwargs: Any):
    """Deserialize Cap'n Proto data to message object with default settings."""
    serializer = CapnProtoSerializer(schema_file=schema_file, struct_name=struct_name, **kwargs)
    return serializer.loads_message(data)


def load_file(file_path: Union[str, Path], schema_file: Optional[Union[str, Path]] = None, struct_name: Optional[str] = None, **kwargs: Any) -> Any:
    """Load Cap'n Proto from file with default settings."""
    serializer = CapnProtoSerializer(schema_file=schema_file, struct_name=struct_name, **kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], schema_file: Optional[Union[str, Path]] = None, struct_name: Optional[str] = None, **kwargs: Any) -> None:
    """Save data to Cap'n Proto file with default settings."""
    serializer = CapnProtoSerializer(schema_file=schema_file, struct_name=struct_name, **kwargs)
    return serializer.save_file(data, file_path)
