"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Multipart (HTTP) Serializer Implementation

Provides multipart/form-data serialization with file upload support,
boundary management, and integration with xSystem utilities.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import email.mime.multipart
import email.mime.text
import email.mime.application
import email.parser
import uuid
import io
from pathlib import Path

from .iSerialization import iSerialization
from .aSerialization import aSerialization


class MultipartSerializer(aSerialization):
    """
    Multipart/form-data serializer for HTTP file uploads.
    
    Features:
    - Multipart/form-data format
    - File upload support
    - Custom boundary generation
    - MIME type handling
    - Binary data support
    - Security validation
    - Atomic file operations
    """
    
    def __init__(
        self,
        boundary: Optional[str] = None,
        encoding: str = "utf-8",
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 5,
        max_size_mb: int = 100
    ) -> None:
        """
        Initialize Multipart serializer.
        
        Args:
            boundary: Custom boundary string (auto-generated if None)
            encoding: Character encoding for text fields
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
        
        self._boundary = boundary or self._generate_boundary()
        self._encoding = encoding
    
    def _generate_boundary(self) -> str:
        """Generate a unique boundary string."""
        return f"----xSystemBoundary{uuid.uuid4().hex}"
    
    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "Multipart"
    
    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".multipart", ".mpart")
    
    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return f"multipart/form-data; boundary={self._boundary}"
    
    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return False  # Text format with binary sections
    
    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True
    
    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to multipart string.
        
        Args:
            data: Data to serialize (dict with field names and values)
            
        Returns:
            Multipart string
            
        Raises:
            ValueError: If data validation fails
        """
        if self.validate_input:
            self._validate_data_security(data)
        
        if not isinstance(data, dict):
            raise ValueError("Multipart data must be a dictionary")
        
        try:
            parts = []
            
            for field_name, field_value in data.items():
                part = self._create_part(field_name, field_value)
                parts.append(part)
            
            # Combine parts with boundary
            multipart_data = f"--{self._boundary}\r\n"
            multipart_data += f"\r\n--{self._boundary}\r\n".join(parts)
            multipart_data += f"\r\n--{self._boundary}--\r\n"
            
            return multipart_data
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)
    
    def _create_part(self, name: str, value: Any) -> str:
        """
        Create a multipart part for a field.
        
        Args:
            name: Field name
            value: Field value
            
        Returns:
            Multipart part string
        """
        if isinstance(value, dict) and 'content' in value:
            # File-like object with metadata
            content = value['content']
            filename = value.get('filename', 'file')
            content_type = value.get('content_type', 'application/octet-stream')
            
            if isinstance(content, bytes):
                content = content.decode('latin1')  # Preserve binary data
            
            return (
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                f'Content-Type: {content_type}\r\n'
                f'\r\n'
                f'{content}'
            )
        
        elif isinstance(value, bytes):
            # Binary data
            content = value.decode('latin1')  # Preserve binary data
            return (
                f'Content-Disposition: form-data; name="{name}"; filename="binary_data"\r\n'
                f'Content-Type: application/octet-stream\r\n'
                f'\r\n'
                f'{content}'
            )
        
        else:
            # Text field
            content = str(value)
            return (
                f'Content-Disposition: form-data; name="{name}"\r\n'
                f'\r\n'
                f'{content}'
            )
    
    def loads_text(self, data: str) -> Dict[str, Any]:
        """
        Deserialize multipart data.
        
        Args:
            data: Multipart string to deserialize
            
        Returns:
            Dictionary with field names and values
            
        Raises:
            ValueError: If data is invalid or validation fails
        """
        if isinstance(data, bytes):
            data = data.decode(self._encoding)
        
        if not isinstance(data, str):
            raise ValueError(f"Expected string or bytes, got {type(data)}")
        
        try:
            # Parse multipart data using email parser
            # Add required headers for email parser
            email_data = f"Content-Type: {self.mime_type}\r\n\r\n{data}"
            
            parser = email.parser.Parser()
            message = parser.parsestr(email_data)
            
            result = {}
            
            if message.is_multipart():
                for part in message.get_payload():
                    field_name = self._extract_field_name(part)
                    field_value = self._extract_field_value(part)
                    
                    if field_name:
                        result[field_name] = field_value
            
            if self.validate_input:
                self._validate_data_security(result)
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)
    
    def _extract_field_name(self, part) -> Optional[str]:
        """
        Extract field name from multipart part.
        
        Args:
            part: Email message part
            
        Returns:
            Field name or None
        """
        content_disposition = part.get('Content-Disposition', '')
        
        # Parse Content-Disposition header
        import re
        name_match = re.search(r'name="([^"]*)"', content_disposition)
        if name_match:
            return name_match.group(1)
        
        return None
    
    def _extract_field_value(self, part) -> Any:
        """
        Extract field value from multipart part.
        
        Args:
            part: Email message part
            
        Returns:
            Field value
        """
        content_disposition = part.get('Content-Disposition', '')
        content_type = part.get_content_type()
        content = part.get_payload()
        
        # Check if it's a file upload
        if 'filename=' in content_disposition:
            import re
            filename_match = re.search(r'filename="([^"]*)"', content_disposition)
            filename = filename_match.group(1) if filename_match else 'unknown'
            
            return {
                'content': content.encode('latin1') if isinstance(content, str) else content,
                'filename': filename,
                'content_type': content_type
            }
        
        # Regular text field
        return content
    
    # 🎯 OPTIMIZATION: save_file and load_file inherited from base class!
    # Base class automatically handles text format based on is_binary_format flag
    
    def create_file_field(self, content: bytes, filename: str, content_type: str = "application/octet-stream") -> Dict[str, Any]:
        """
        Create a file field for multipart data.
        
        Args:
            content: File content as bytes
            filename: File name
            content_type: MIME type of the file
            
        Returns:
            File field dictionary
        """
        return {
            'content': content,
            'filename': filename,
            'content_type': content_type
        }
    
    def get_boundary(self) -> str:
        """
        Get the current boundary string.
        
        Returns:
            Boundary string
        """
        return self._boundary
    
    def set_boundary(self, boundary: str) -> None:
        """
        Set a new boundary string.
        
        Args:
            boundary: New boundary string
        """
        self._boundary = boundary
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get Multipart format schema information.
        
        Returns:
            Schema information dictionary
        """
        return {
            "format": "Multipart",
            "version": "RFC 7578",
            "description": "Multipart/form-data for HTTP file uploads",
            "features": {
                "binary": False,
                "file_upload": True,
                "boundary_based": True,
                "streaming": True,
                "mixed_content": True
            },
            "supported_types": [
                "string", "bytes", "file_objects", "mixed"
            ],
            "boundary": self._boundary,
            "encoding": self._encoding,
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
            "boundary": self._boundary,
            "encoding": self._encoding
        })
        return config


# Error classes for consistency with other serializers
class MultipartError(Exception):
    """Base exception for Multipart serialization errors."""
    pass
