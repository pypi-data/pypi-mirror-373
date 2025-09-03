"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Enhanced Apache Thrift serialization with security, validation and performance optimizations.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type

from thrift.protocol import TBinaryProtocol, TCompactProtocol, TJSONProtocol
from thrift.transport import TTransport
from thrift.Thrift import TException, TMessageType, TType

# Use TException as base class since TBase doesn't exist in this Thrift version
TBase = TException

from .aSerialization import aSerialization, SerializationError
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.serialization.thrift")


class ThriftError(SerializationError):
    """Thrift-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "THRIFT", original_error)


class ThriftSerializer(aSerialization):
    """
    Enhanced Apache Thrift serializer with protocol selection and xSystem integration.
    
    Apache Thrift is a software framework for scalable cross-language services development.
    It combines a software stack with a code generation engine to build services.
    
    Features:
    - Multiple protocol support (Binary, Compact, JSON)
    - Cross-language compatibility
    - Efficient serialization
    - Service definition and RPC support
    
    🚨 PRODUCTION LIBRARY: Uses official Apache Thrift Python library
    """

    def __init__(
        self,
        thrift_class: Optional[Type] = None,
        protocol: str = "binary",  # binary, compact, json
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 32.0,
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Initialize Thrift serializer with protocol and security options.

        Args:
            thrift_class: Thrift struct/class (required for serialization)
            protocol: Thrift protocol to use (binary, compact, json)
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
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
        
        # Thrift-specific configuration
        self.thrift_class = thrift_class
        self.protocol = protocol.lower()
        
        # Validate protocol
        if self.protocol not in ['binary', 'compact', 'json']:
            raise ThriftError(f"Unsupported protocol: {protocol}. Use 'binary', 'compact', or 'json'")
        
        # Update configuration with Thrift-specific options
        self._config.update({
            'thrift_class': thrift_class.__name__ if thrift_class else None,
            'protocol': self.protocol,
        })

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "THRIFT"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return ['.thrift', '.thr']

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        if self.protocol == 'json':
            return "application/json"
        else:
            return "application/x-thrift"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return self.protocol != 'json'

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return True

    def _validate_thrift_class(self) -> None:
        """Validate that thrift class is provided and valid."""
        if not self.thrift_class:
            raise ThriftError("Thrift class is required for Thrift serialization")
        
        if not issubclass(self.thrift_class, TBase):
            raise ThriftError(f"Thrift class must inherit from TBase, got {type(self.thrift_class)}")

    def _get_protocol_factory(self):
        """Get the appropriate protocol factory based on configuration."""
        if self.protocol == 'binary':
            return TBinaryProtocol.TBinaryProtocolFactory()
        elif self.protocol == 'compact':
            return TCompactProtocol.TCompactProtocolFactory()
        elif self.protocol == 'json':
            return TJSONProtocol.TJSONProtocolFactory()
        else:
            raise ThriftError(f"Unknown protocol: {self.protocol}")

    def _dict_to_thrift(self, data: Dict[str, Any]) -> TBase:
        """Convert dictionary to thrift object."""
        self._validate_thrift_class()
        
        try:
            thrift_obj = self.thrift_class()
            
            # Set attributes from dictionary
            for key, value in data.items():
                if hasattr(thrift_obj, key):
                    setattr(thrift_obj, key, value)
                else:
                    logger.warning(f"Thrift class {self.thrift_class.__name__} has no attribute '{key}'")
            
            return thrift_obj
            
        except Exception as e:
            raise ThriftError(f"Failed to convert dict to thrift object: {e}", e)

    def _thrift_to_dict(self, thrift_obj: TBase) -> Dict[str, Any]:
        """Convert thrift object to dictionary."""
        try:
            result = {}
            
            # Get all thrift spec attributes
            if hasattr(thrift_obj, '__dict__'):
                for key, value in thrift_obj.__dict__.items():
                    if not key.startswith('_'):
                        result[key] = value
            
            return result
            
        except Exception as e:
            raise ThriftError(f"Failed to convert thrift object to dict: {e}", e)

    def dumps(self, data: Any) -> str:
        """
        Serialize data to Thrift format.

        Args:
            data: Data to serialize (dict or thrift object)

        Returns:
            Serialized string (base64 for binary protocols, JSON for JSON protocol)

        Raises:
            ThriftError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            
            if self.protocol == 'json':
                # JSON protocol returns text directly
                return self.dumps_text(data)
            else:
                # Binary protocols return base64-encoded string
                thrift_bytes = self.dumps_binary(data)
                import base64
                return base64.b64encode(thrift_bytes).decode('ascii')
            
        except SerializationError as e:
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> Any:
        """
        Deserialize Thrift data to Python object.

        Args:
            data: Thrift data to deserialize

        Returns:
            Dictionary representation of thrift object

        Raises:
            ThriftError: If deserialization fails
        """
        try:
            if self.protocol == 'json' and isinstance(data, str):
                # JSON protocol handles text directly
                return self.loads_text(data)
            else:
                # Binary protocols handle bytes or base64 string
                if isinstance(data, str):
                    import base64
                    thrift_bytes = base64.b64decode(data.encode('ascii'))
                else:
                    thrift_bytes = data
                return self.loads_bytes(thrift_bytes)
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to Thrift JSON string (only for JSON protocol).

        Args:
            data: Data to serialize

        Returns:
            Thrift JSON string

        Raises:
            ThriftError: If serialization fails or protocol is not JSON
        """
        if self.protocol != 'json':
            raise ThriftError("dumps_text is only supported for JSON protocol")
        
        try:
            # Validate data using base class
            self._validate_data_security(data)
            self._validate_thrift_class()
            
            # Convert data to thrift object if needed
            if isinstance(data, dict):
                thrift_obj = self._dict_to_thrift(data)
            elif isinstance(data, TBase):
                thrift_obj = data
            else:
                raise ThriftError(f"Cannot serialize data of type {type(data)} to thrift")
            
            # Serialize using JSON protocol
            transport = TTransport.TMemoryBuffer()
            protocol_factory = self._get_protocol_factory()
            protocol = protocol_factory.getProtocol(transport)
            
            thrift_obj.write(protocol)
            
            return transport.getvalue().decode('utf-8')
            
        except SerializationError as e:
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads_text(self, data: str) -> Dict[str, Any]:
        """
        Deserialize Thrift JSON string (only for JSON protocol).

        Args:
            data: Thrift JSON string

        Returns:
            Dictionary representation

        Raises:
            ThriftError: If deserialization fails or protocol is not JSON
        """
        if self.protocol != 'json':
            raise ThriftError("loads_text is only supported for JSON protocol")
        
        try:
            self._validate_thrift_class()
            
            # Deserialize using JSON protocol
            transport = TTransport.TMemoryBuffer(data.encode('utf-8'))
            protocol_factory = self._get_protocol_factory()
            protocol = protocol_factory.getProtocol(transport)
            
            thrift_obj = self.thrift_class()
            thrift_obj.read(protocol)
            
            # Convert to dictionary for consistent API
            return self._thrift_to_dict(thrift_obj)
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def dumps_binary(self, data: Any) -> bytes:
        """
        Serialize data to Thrift bytes.

        Args:
            data: Data to serialize

        Returns:
            Thrift bytes

        Raises:
            ThriftError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            self._validate_thrift_class()
            
            # Convert data to thrift object if needed
            if isinstance(data, dict):
                thrift_obj = self._dict_to_thrift(data)
            elif isinstance(data, TBase):
                thrift_obj = data
            else:
                raise ThriftError(f"Cannot serialize data of type {type(data)} to thrift")
            
            # Serialize using appropriate protocol
            transport = TTransport.TMemoryBuffer()
            protocol_factory = self._get_protocol_factory()
            protocol = protocol_factory.getProtocol(transport)
            
            thrift_obj.write(protocol)
            
            return transport.getvalue()
            
        except SerializationError as e:
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads_bytes(self, data: bytes) -> Dict[str, Any]:
        """
        Deserialize Thrift bytes to Python dictionary.

        Args:
            data: Thrift bytes to deserialize

        Returns:
            Dictionary representation

        Raises:
            ThriftError: If deserialization fails
        """
        try:
            self._validate_thrift_class()
            
            # Deserialize using appropriate protocol
            transport = TTransport.TMemoryBuffer(data)
            protocol_factory = self._get_protocol_factory()
            protocol = protocol_factory.getProtocol(transport)
            
            thrift_obj = self.thrift_class()
            thrift_obj.read(protocol)
            
            # Convert to dictionary for consistent API
            return self._thrift_to_dict(thrift_obj)
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def loads_thrift(self, data: Union[bytes, str]) -> TBase:
        """
        Deserialize Thrift data to thrift object.

        Args:
            data: Thrift data to deserialize

        Returns:
            Thrift object

        Raises:
            ThriftError: If deserialization fails
        """
        try:
            self._validate_thrift_class()
            
            if self.protocol == 'json' and isinstance(data, str):
                # JSON protocol
                transport = TTransport.TMemoryBuffer(data.encode('utf-8'))
            else:
                # Binary protocols
                if isinstance(data, str):
                    import base64
                    thrift_bytes = base64.b64decode(data.encode('ascii'))
                else:
                    thrift_bytes = data
                transport = TTransport.TMemoryBuffer(thrift_bytes)
            
            protocol_factory = self._get_protocol_factory()
            protocol = protocol_factory.getProtocol(transport)
            
            thrift_obj = self.thrift_class()
            thrift_obj.read(protocol)
            return thrift_obj
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)


# Convenience functions for common use cases
def dumps(data: Any, thrift_class: Optional[Type] = None, protocol: str = "binary", **kwargs: Any) -> str:
    """Serialize data to Thrift string with default settings."""
    serializer = ThriftSerializer(thrift_class=thrift_class, protocol=protocol, **kwargs)
    return serializer.dumps(data)


def loads(s: str, thrift_class: Optional[Type] = None, protocol: str = "binary", **kwargs: Any) -> Any:
    """Deserialize Thrift string with default settings.""" 
    serializer = ThriftSerializer(thrift_class=thrift_class, protocol=protocol, **kwargs)
    return serializer.loads(s)


def dumps_bytes(data: Any, thrift_class: Optional[Type] = None, protocol: str = "binary", **kwargs: Any) -> bytes:
    """Serialize data to Thrift bytes with default settings."""
    serializer = ThriftSerializer(thrift_class=thrift_class, protocol=protocol, **kwargs)
    return serializer.dumps_binary(data)


def loads_bytes(data: bytes, thrift_class: Optional[Type] = None, protocol: str = "binary", **kwargs: Any) -> Any:
    """Deserialize Thrift bytes with default settings."""
    serializer = ThriftSerializer(thrift_class=thrift_class, protocol=protocol, **kwargs)
    return serializer.loads_bytes(data)


def loads_thrift(data: Union[bytes, str], thrift_class: Optional[Type] = None, protocol: str = "binary", **kwargs: Any) -> TBase:
    """Deserialize Thrift data to thrift object with default settings."""
    serializer = ThriftSerializer(thrift_class=thrift_class, protocol=protocol, **kwargs)
    return serializer.loads_thrift(data)


def load_file(file_path: Union[str, Path], thrift_class: Optional[Type] = None, protocol: str = "binary", **kwargs: Any) -> Any:
    """Load Thrift from file with default settings."""
    serializer = ThriftSerializer(thrift_class=thrift_class, protocol=protocol, **kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], thrift_class: Optional[Type] = None, protocol: str = "binary", **kwargs: Any) -> None:
    """Save data to Thrift file with default settings."""
    serializer = ThriftSerializer(thrift_class=thrift_class, protocol=protocol, **kwargs)
    return serializer.save_file(data, file_path)
