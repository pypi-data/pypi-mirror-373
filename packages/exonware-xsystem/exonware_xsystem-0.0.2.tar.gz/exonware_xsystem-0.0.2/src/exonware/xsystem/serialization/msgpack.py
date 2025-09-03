"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

MessagePack Serializer Implementation

Provides MessagePack serialization with binary format support, compression,
and integration with xSystem utilities for security and validation.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import io
from pathlib import Path

from .iSerialization import iSerialization
from .aSerialization import aSerialization

try:
    import msgpack
    _MSGPACK_AVAILABLE = True
except ImportError:
    _MSGPACK_AVAILABLE = False
    
    # Define dummy classes for type hints when msgpack is not available
    class _DummyPacker:
        pass
    
    class _DummyUnpacker:
        pass
    
    msgpack = type('msgpack', (), {
        'packb': lambda *args, **kwargs: None,
        'unpackb': lambda *args, **kwargs: None,
        'Packer': _DummyPacker,
        'Unpacker': _DummyUnpacker,
    })()


class MsgPackSerializer(aSerialization):
    """
    MessagePack serializer with binary format support and compression.
    
    Features:
    - Efficient binary serialization
    - Optional compression
    - Raw/binary data handling
    - Streaming support for large data
    - Security validation
    - Atomic file operations
    """
    
    def __init__(
        self,
        use_compression: bool = False,
        raw: bool = False,
        strict_map_key: bool = True,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 100,
        max_size_mb: int = 50
    ) -> None:
        """
        Initialize MessagePack serializer.
        
        Args:
            use_compression: Enable compression for smaller output
            raw: Return raw bytes instead of strings
            strict_map_key: Enforce string keys in mappings
            validate_input: Enable input data validation
            validate_paths: Enable path security validation
            use_atomic_writes: Use atomic file operations
            max_depth: Maximum nesting depth for security
            max_size_mb: Maximum data size in MB
        """
        if not _MSGPACK_AVAILABLE:
            raise ImportError(
                "MessagePack serialization requires the 'msgpack' package. "
                "Install it with: pip install msgpack"
            )
        
        super().__init__(
            validate_input=validate_input,
            validate_paths=validate_paths,
            use_atomic_writes=use_atomic_writes,
            max_depth=max_depth,
            max_size_mb=max_size_mb
        )
        
        self._use_compression = use_compression
        self._raw = raw
        self._strict_map_key = strict_map_key
        
        # Configure packer
        self._packer = msgpack.Packer(
            use_bin_type=True,
            strict_types=True
        )
    
    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "MessagePack"
    
    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".msgpack", ".mpack", ".mp")
    
    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/x-msgpack"
    
    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return True
    
    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True
    
    def dumps_binary(self, data: Any) -> bytes:
        """
        Serialize data to MessagePack bytes.
        
        Args:
            data: Data to serialize
            
        Returns:
            MessagePack bytes
            
        Raises:
            ValueError: If data validation fails
            TypeError: If data contains non-serializable types
        """
        if self.validate_input:
            self._validate_data_security(data)
        
        try:
            # Use the configured packer
            result = self._packer.pack(data)
            
            # Apply compression if enabled
            if self._use_compression:
                import zlib
                result = zlib.compress(result)
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)
    
    def loads_bytes(self, data: bytes) -> Any:
        """
        Deserialize MessagePack data.
        
        Args:
            data: MessagePack bytes or string to deserialize
            
        Returns:
            Deserialized data
            
        Raises:
            ValueError: If data is invalid or validation fails
        """
        if isinstance(data, str):
            raise ValueError("MessagePack data must be bytes, not string")
        
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError(f"Expected bytes or bytearray, got {type(data)}")
        
        try:
            # Decompress if compression was used
            if self._use_compression:
                import zlib
                data = zlib.decompress(data)
            
            # Unpack the data
            result = msgpack.unpackb(
                data,
                raw=self._raw,
                strict_map_key=self._strict_map_key
            )
            
            if self.validate_input:
                self._validate_data_security(result)
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)
    
    # 🎯 OPTIMIZATION: save_file and load_file inherited from base class!
    # Base class automatically handles binary format based on is_binary_format flag
    
    def stream_pack(self, data_stream) -> bytes:
        """
        Pack data from a stream.
        
        Args:
            data_stream: Iterable of data objects to pack
            
        Returns:
            Packed bytes
        """
        if not _MSGPACK_AVAILABLE:
            raise ImportError("MessagePack streaming requires the 'msgpack' package")
        
        buffer = io.BytesIO()
        
        for item in data_stream:
            if self.validate_input:
                self._validate_data_security(item)
            
            packed_item = self._packer.pack(item)
            buffer.write(packed_item)
        
        result = buffer.getvalue()
        
        if self._use_compression:
            import zlib
            result = zlib.compress(result)
        
        return result
    
    def stream_unpack(self, data: bytes):
        """
        Unpack data as a stream.
        
        Args:
            data: Packed bytes to unpack
            
        Yields:
            Unpacked objects
        """
        if not _MSGPACK_AVAILABLE:
            raise ImportError("MessagePack streaming requires the 'msgpack' package")
        
        if self._use_compression:
            import zlib
            data = zlib.decompress(data)
        
        unpacker = msgpack.Unpacker(
            raw=self._raw,
            strict_map_key=self._strict_map_key,
            max_buffer_size=int(self.max_size_mb * 1024 * 1024)
        )
        
        unpacker.feed(data)
        
        for item in unpacker:
            if self.validate_input:
                self._validate_data_security(item)
            yield item
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get MessagePack format schema information.
        
        Returns:
            Schema information dictionary
        """
        return {
            "format": "MessagePack",
            "version": "Binary format",
            "description": "Efficient binary serialization format",
            "features": {
                "binary": True,
                "compression": self._use_compression,
                "streaming": True,
                "raw_mode": self._raw,
                "strict_map_keys": self._strict_map_key
            },
            "supported_types": [
                "int", "float", "str", "bytes", "bool", "None",
                "list", "dict", "tuple"
            ],
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
            "use_compression": self._use_compression,
            "raw": self._raw,
            "strict_map_key": self._strict_map_key
        })
        return config
