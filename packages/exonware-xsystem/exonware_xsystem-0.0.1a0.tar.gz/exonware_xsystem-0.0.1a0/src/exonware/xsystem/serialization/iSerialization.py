"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Interface for serialization implementations.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, BinaryIO, Dict, Optional, TextIO, Union


class iSerialization(ABC):
    """
    Interface defining the contract for all serialization implementations.
    
    This interface ensures consistent API across different serialization formats
    with proper support for both text and binary formats.
    
    🚨 CRITICAL IMPLEMENTATION PRINCIPLE:
       NEVER HARDCODE SERIALIZATION/DESERIALIZATION LOGIC!
       
       Always use official, well-tested libraries:
       - Built-in modules (json, pickle, marshal, csv, etc.)
       - Established third-party libraries (PyYAML, tomli-w, etc.)
       
       Hardcoding is dangerous because:
       1. Incomplete specification implementation
       2. Missing edge cases and security vulnerabilities  
       3. Performance issues
       4. Maintenance burden
       5. Compatibility problems
       
       If an official library doesn't exist, use the most established
       community library, not custom implementations.
    while maintaining flexibility for format-specific optimizations.
    """

    # =============================================================================
    # PROPERTIES
    # =============================================================================

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Get the serialization format name (e.g., 'JSON', 'YAML')."""
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """Get supported file extensions for this format."""
        pass

    @property
    @abstractmethod
    def mime_type(self) -> str:
        """Get the MIME type for this serialization format."""
        pass

    @property
    @abstractmethod
    def is_binary_format(self) -> bool:
        """Whether this is a binary or text-based format."""
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether this format supports streaming serialization."""
        pass

    # =============================================================================
    # CORE SERIALIZATION METHODS
    # =============================================================================

    @abstractmethod
    def dumps(self, data: Any) -> Union[str, bytes]:
        """
        Serialize data to string or bytes based on format type.
        
        Automatically delegates to dumps_text() or dumps_binary() based on 
        is_binary_format property.

        Args:
            data: Data to serialize

        Returns:
            Serialized string for text formats, bytes for binary formats

        Raises:
            SerializationError: If serialization fails
        """
        pass

    @abstractmethod
    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to text string.
        
        Should only be implemented by text-based formats.

        Args:
            data: Data to serialize

        Returns:
            Serialized text string

        Raises:
            SerializationError: If serialization fails
            NotImplementedError: If called on binary format
        """
        pass
        
    @abstractmethod
    def dumps_binary(self, data: Any) -> bytes:
        """
        Serialize data to bytes.
        
        Should only be implemented by binary formats.

        Args:
            data: Data to serialize

        Returns:
            Serialized bytes

        Raises:
            SerializationError: If serialization fails
            NotImplementedError: If called on text format
        """
        pass

    @abstractmethod
    def loads(self, data: Union[str, bytes]) -> Any:
        """
        Deserialize from string or bytes.
        
        Automatically handles both text and binary data based on input type
        and format capabilities.

        Args:
            data: String or bytes to deserialize

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
        """
        pass

    @abstractmethod
    def loads_text(self, data: str) -> Any:
        """
        Deserialize from text string.
        
        Should be implemented by all formats (binary formats may convert
        from base64 or other text encoding).

        Args:
            data: Text string to deserialize

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
        """
        pass
        
    @abstractmethod
    def loads_bytes(self, data: bytes) -> Any:
        """
        Deserialize from bytes.
        
        Should only be implemented by binary formats.

        Args:
            data: Bytes to deserialize

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
            NotImplementedError: If called on text-only format
        """
        pass

    # =============================================================================
    # FILE-LIKE OBJECT METHODS
    # =============================================================================

    @abstractmethod
    def dump(self, data: Any, fp: Union[TextIO, BinaryIO]) -> None:
        """
        Serialize data to file-like object.
        
        Automatically chooses text or binary mode based on format type.

        Args:
            data: Data to serialize
            fp: File-like object to write to (text or binary)

        Raises:
            SerializationError: If serialization fails
        """
        pass
        
    @abstractmethod
    def dump_text(self, data: Any, fp: TextIO) -> None:
        """
        Serialize data to text file-like object.

        Args:
            data: Data to serialize
            fp: Text file-like object to write to

        Raises:
            SerializationError: If serialization fails
            NotImplementedError: If called on binary-only format
        """
        pass
        
    @abstractmethod  
    def dump_binary(self, data: Any, fp: BinaryIO) -> None:
        """
        Serialize data to binary file-like object.

        Args:
            data: Data to serialize
            fp: Binary file-like object to write to

        Raises:
            SerializationError: If serialization fails
            NotImplementedError: If called on text-only format
        """
        pass

    @abstractmethod
    def load(self, fp: Union[TextIO, BinaryIO]) -> Any:
        """
        Deserialize from file-like object.
        
        Automatically handles text or binary file-like objects.

        Args:
            fp: File-like object to read from

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
        """
        pass

    @abstractmethod
    def load_text(self, fp: TextIO) -> Any:
        """
        Deserialize from text file-like object.

        Args:
            fp: Text file-like object to read from

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
        """
        pass
        
    @abstractmethod
    def load_binary(self, fp: BinaryIO) -> Any:
        """
        Deserialize from binary file-like object.

        Args:
            fp: Binary file-like object to read from

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
            NotImplementedError: If called on text-only format
        """
        pass

    # =============================================================================
    # FILE PATH METHODS
    # =============================================================================

    @abstractmethod
    def save_file(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Save data to file.
        
        Automatically handles text/binary mode based on format type.

        Args:
            data: Data to serialize
            file_path: Path to save file

        Raises:
            SerializationError: If saving fails
        """
        pass
        
    @abstractmethod  
    def load_file(self, file_path: Union[str, Path]) -> Any:
        """
        Load data from file.
        
        Automatically handles text/binary mode based on format type.

        Args:
            file_path: Path to load from

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If loading fails
        """
        pass

    # =============================================================================
    # VALIDATION AND UTILITY METHODS
    # =============================================================================

    @abstractmethod
    def validate_data(self, data: Any) -> bool:
        """
        Validate data for serialization compatibility.

        Args:
            data: Data to validate

        Returns:
            True if data can be serialized

        Raises:
            SerializationError: If validation fails
        """
        pass

    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get schema information for this serialization format.

        Returns:
            Dictionary with schema information including:
            - supported_types: List of supported Python types
            - format_version: Version of the format specification
            - capabilities: Dict of format capabilities
        """
        pass

    @abstractmethod
    def estimate_size(self, data: Any) -> int:
        """
        Estimate serialized size in bytes.

        Args:
            data: Data to estimate

        Returns:
            Estimated size in bytes
        """
        pass

    # =============================================================================
    # CONFIGURATION METHODS
    # =============================================================================

    @abstractmethod
    def configure(self, **options: Any) -> None:
        """
        Configure serialization options.

        Args:
            **options: Configuration options specific to format
        """
        pass

    @abstractmethod
    def reset_configuration(self) -> None:
        """Reset configuration to defaults."""
        pass

    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration.

        Returns:
            Current configuration dictionary
        """
        pass