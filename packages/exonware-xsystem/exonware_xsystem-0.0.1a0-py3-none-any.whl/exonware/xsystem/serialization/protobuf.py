"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Enhanced Protocol Buffers serialization with security, validation and performance optimizations.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type

import google.protobuf.message
from google.protobuf import json_format
from google.protobuf.descriptor import Descriptor
from google.protobuf.message import Message

from .aSerialization import aSerialization, SerializationError
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.serialization.protobuf")


class ProtobufError(SerializationError):
    """Protocol Buffers-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "PROTOBUF", original_error)


class ProtobufSerializer(aSerialization):
    """
    Enhanced Protocol Buffers serializer with schema validation and xSystem integration.
    
    Protocol Buffers (protobuf) is Google's language-neutral, platform-neutral,
    extensible mechanism for serializing structured data.
    
    Features:
    - Compact binary encoding
    - Schema evolution support
    - Strong typing with validation
    - Cross-language compatibility
    
    🚨 PRODUCTION LIBRARY: Uses official google.protobuf library
    """

    def __init__(
        self,
        message_type: Optional[Type] = None,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 64.0,  # Protobuf can handle large messages
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
        include_default_values: bool = False,
        preserve_proto_field_names: bool = False,
    ) -> None:
        """
        Initialize Protocol Buffers serializer with message type and security options.

        Args:
            message_type: Protobuf message class (required for serialization)
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
            include_default_values: Include fields with default values in JSON output
            preserve_proto_field_names: Use proto field names instead of camelCase
        """

            
        # Initialize base class with xSystem integration
        super().__init__(
            validate_input=validate_input,
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            use_atomic_writes=use_atomic_writes,
            validate_paths=validate_paths,
            base_path=base_path,
        )
        
        # Protobuf-specific configuration
        self.message_type = message_type
        self.include_default_values = include_default_values
        self.preserve_proto_field_names = preserve_proto_field_names
        
        # Update configuration with Protobuf-specific options
        self._config.update({
            'message_type': message_type.__name__ if message_type else None,
            'include_default_values': include_default_values,
            'preserve_proto_field_names': preserve_proto_field_names,
        })

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "PROTOBUF"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return ['.pb', '.protobuf']

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/x-protobuf"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return True

    def _validate_message_type(self) -> None:
        """Validate message type."""
        if not self.message_type or not issubclass(self.message_type, google.protobuf.message.Message):
            raise ProtobufError("Valid protobuf Message class is required")

    def dumps(self, data: Any) -> str:
        """
        Serialize data to Protocol Buffers and return as base64-encoded string.

        Args:
            data: Data to serialize (dict or protobuf Message)

        Returns:
            Base64-encoded protobuf string

        Raises:
            ProtobufError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            
            # Serialize to protobuf bytes
            protobuf_bytes = self.dumps_binary(data)
            
            # Encode to base64 string for string interface
            import base64
            return base64.b64encode(protobuf_bytes).decode('ascii')
            
        except SerializationError as e:
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> Any:
        """
        Deserialize Protocol Buffers data to Python object.

        Args:
            data: Protobuf bytes or base64-encoded string to deserialize

        Returns:
            Dictionary representation of protobuf message

        Raises:
            ProtobufError: If deserialization fails
        """
        try:
            # Handle both bytes and base64 string
            if isinstance(data, str):
                import base64
                protobuf_bytes = base64.b64decode(data.encode('ascii'))
            else:
                protobuf_bytes = data
            
            return self.loads_bytes(protobuf_bytes)
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def dumps_binary(self, data: Any) -> bytes:
        """Serialize data to protobuf bytes."""
        try:
            self._validate_data_security(data)
            self._validate_message_type()
            
            # Convert to protobuf message
            if isinstance(data, dict):
                message = self.message_type()
                json_format.ParseDict(data, message, ignore_unknown_fields=True)
            elif isinstance(data, google.protobuf.message.Message):
                message = data
            else:
                message = self.message_type()
                json_format.ParseDict(data.__dict__ if hasattr(data, '__dict__') else {"value": data}, message)
            
            return message.SerializeToString()
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads_bytes(self, data: bytes) -> Dict[str, Any]:
        """Deserialize protobuf bytes to dictionary."""
        try:
            self._validate_message_type()
            message = self.message_type()
            message.ParseFromString(data)
            return json_format.MessageToDict(message, include_default_values=self.include_default_values, preserving_proto_field_name=self.preserve_proto_field_names)
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def loads_message(self, data: Union[bytes, str]) -> Message:
        """
        Deserialize Protocol Buffers data to protobuf Message object.

        Args:
            data: Protobuf bytes or base64-encoded string to deserialize

        Returns:
            Protobuf Message object

        Raises:
            ProtobufError: If deserialization fails
        """
        try:
            self._validate_message_type()
            
            # Handle both bytes and base64 string
            if isinstance(data, str):
                import base64
                protobuf_bytes = base64.b64decode(data.encode('ascii'))
            else:
                protobuf_bytes = data
            
            # Create message instance and parse from bytes
            message = self.message_type()
            message.ParseFromString(protobuf_bytes)
            return message
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)


# Convenience functions for common use cases
def dumps(data: Any, message_type: Optional[Type] = None, **kwargs: Any) -> str:
    """Serialize data to Protocol Buffers base64-encoded string with default settings."""
    serializer = ProtobufSerializer(message_type=message_type, **kwargs)
    return serializer.dumps(data)


def loads(s: str, message_type: Optional[Type] = None, **kwargs: Any) -> Any:
    """Deserialize Protocol Buffers string with default settings.""" 
    serializer = ProtobufSerializer(message_type=message_type, **kwargs)
    return serializer.loads(s)


def dumps_bytes(data: Any, message_type: Optional[Type] = None, **kwargs: Any) -> bytes:
    """Serialize data to Protocol Buffers bytes with default settings."""
    serializer = ProtobufSerializer(message_type=message_type, **kwargs)
    return serializer.dumps_binary(data)


def loads_bytes(data: bytes, message_type: Optional[Type] = None, **kwargs: Any) -> Any:
    """Deserialize Protocol Buffers bytes with default settings."""
    serializer = ProtobufSerializer(message_type=message_type, **kwargs)
    return serializer.loads_bytes(data)


def loads_message(data: Union[bytes, str], message_type: Optional[Type] = None, **kwargs: Any) -> Message:
    """Deserialize Protocol Buffers data to Message object with default settings."""
    serializer = ProtobufSerializer(message_type=message_type, **kwargs)
    return serializer.loads_message(data)


def load_file(file_path: Union[str, Path], message_type: Optional[Type] = None, **kwargs: Any) -> Any:
    """Load Protocol Buffers from file with default settings."""
    serializer = ProtobufSerializer(message_type=message_type, **kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], message_type: Optional[Type] = None, **kwargs: Any) -> None:
    """Save data to Protocol Buffers file with default settings."""
    serializer = ProtobufSerializer(message_type=message_type, **kwargs)
    return serializer.save_file(data, file_path)
