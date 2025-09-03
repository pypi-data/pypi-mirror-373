"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Shelve Serializer Implementation

Provides persistent dictionary serialization using the built-in shelve module
following the 'no hardcode' principle.
"""

import shelve
import pickle
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import warnings

from .aSerialization import aSerialization, SerializationError


class ShelveError(SerializationError):
    """Shelve-specific serialization error."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "Shelve", original_error)


class ShelveSerializer(aSerialization):
    """
    Shelve serializer using built-in shelve module.
    
    This implementation strictly follows the 'no hardcode' principle by using
    only the built-in shelve library for persistent dictionary operations.
    
    Features:
    - Uses shelve.open for persistent dictionary operations
    - Binary format (uses pickle internally)
    - Security validation
    - Key-value store semantics with full Python object support
    - Platform-dependent file format
    
    Note: Shelve is marked as optional due to security concerns with pickle
    """

    def __init__(
        self,
        flag: str = 'c',  # 'r'=read, 'w'=write, 'c'=create, 'n'=new
        protocol: Optional[int] = None,
        writeback: bool = False,
        allow_unsafe: bool = False,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 100,
        max_size_mb: int = 100
    ) -> None:
        """
        Initialize Shelve serializer.

        Args:
            flag: Database open flag ('r', 'w', 'c', 'n')
            protocol: Pickle protocol version
            writeback: Enable writeback mode for mutable objects
            allow_unsafe: Allow potentially unsafe pickle operations
            validate_input: Enable input data validation
            validate_paths: Enable path security validation
            use_atomic_writes: Use atomic file operations
            max_depth: Maximum nesting depth
            max_size_mb: Maximum shelf size in MB
        """
        super().__init__(
            validate_input=validate_input,
            validate_paths=validate_paths,
            use_atomic_writes=use_atomic_writes,
            max_depth=max_depth,
            max_size_mb=max_size_mb
        )

        if not allow_unsafe:
            warnings.warn(
                "Shelve uses pickle internally which can execute arbitrary code. "
                "Only use with trusted data or set allow_unsafe=True to acknowledge the risk.",
                UserWarning
            )

        self._flag = flag
        self._protocol = protocol
        self._writeback = writeback
        self._allow_unsafe = allow_unsafe

    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "Shelve"

    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".shelf", ".db", ".shelve")

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/x-shelve"

    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True  # Shelve supports key-by-key access

    def dumps(self, data: Any) -> bytes:
        """
        Serialize data to Shelve database in memory (simulated with temp file).

        ✅ PRODUCTION LIBRARY: shelve.open()
        
        Args:
            data: Dictionary to store as persistent dictionary
            
        Returns:
            Shelve database content as bytes
        """
        if not self._allow_unsafe:
            raise ShelveError(
                "Shelve operations require allow_unsafe=True due to pickle security risks"
            )

        if self.validate_input:
            self._validate_data_security(data)

        if not isinstance(data, dict):
            raise ShelveError(f"Shelve requires dict data, got {type(data)}")

        try:
            import tempfile
            import os
            
            # Create temporary file for shelve
            with tempfile.TemporaryDirectory() as temp_dir:
                shelf_path = os.path.join(temp_dir, "temp_shelf")
                
                # Open shelve database
                with shelve.open(
                    shelf_path, 
                    flag='n',
                    protocol=self._protocol,
                    writeback=self._writeback
                ) as shelf:
                    # Store all data
                    for key, value in data.items():
                        shelf[str(key)] = value
                
                # Collect all shelf files (platform dependent)
                shelf_files = []
                for file in os.listdir(temp_dir):
                    if file.startswith("temp_shelf"):
                        file_path = os.path.join(temp_dir, file)
                        with open(file_path, 'rb') as f:
                            shelf_files.append((file, f.read()))
                
                # Create a simple archive format
                result = b''
                for filename, content in shelf_files:
                    filename_bytes = filename.encode('utf-8')
                    result += len(filename_bytes).to_bytes(4, 'big')
                    result += filename_bytes
                    result += len(content).to_bytes(8, 'big')
                    result += content
                
                return result

        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> Dict[str, Any]:
        """
        Deserialize Shelve database.

        ✅ PRODUCTION LIBRARY: shelve.open()
        
        Args:
            data: Shelve database as bytes or file path as string
            
        Returns:
            Dictionary with key-value pairs
        """
        if not self._allow_unsafe:
            raise ShelveError(
                "Shelve operations require allow_unsafe=True due to pickle security risks"
            )

        try:
            if isinstance(data, str):
                # Assume it's a file path
                with shelve.open(data, flag='r') as shelf:
                    result = {}
                    for key in shelf.keys():
                        result[key] = shelf[key]
                    
                    if self.validate_input:
                        self._validate_data_security(result)
                        
                    return result
                    
            elif isinstance(data, bytes):
                # Restore from our archive format
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Parse archive format
                    offset = 0
                    while offset < len(data):
                        if offset + 4 > len(data):
                            break
                        
                        filename_length = int.from_bytes(data[offset:offset+4], 'big')
                        offset += 4
                        
                        if offset + filename_length > len(data):
                            break
                        
                        filename = data[offset:offset+filename_length].decode('utf-8')
                        offset += filename_length
                        
                        if offset + 8 > len(data):
                            break
                        
                        content_length = int.from_bytes(data[offset:offset+8], 'big')
                        offset += 8
                        
                        if offset + content_length > len(data):
                            break
                        
                        content = data[offset:offset+content_length]
                        offset += content_length
                        
                        # Write file
                        file_path = os.path.join(temp_dir, filename)
                        with open(file_path, 'wb') as f:
                            f.write(content)
                    
                    # Open the main shelf file
                    shelf_path = os.path.join(temp_dir, "temp_shelf")
                    if not os.path.exists(shelf_path):
                        # Try to find any file that looks like a shelf file
                        for file in os.listdir(temp_dir):
                            if file.startswith("temp_shelf"):
                                shelf_path = os.path.join(temp_dir, file.split('.')[0])
                                break
                    
                    with shelve.open(shelf_path, flag='r') as shelf:
                        result = {}
                        for key in shelf.keys():
                            result[key] = shelf[key]
                        
                        if self.validate_input:
                            self._validate_data_security(result)
                            
                        return result
            else:
                raise ShelveError(f"Expected bytes or string, got {type(data)}")

        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def save_file(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Save data to Shelve database file.
        
        🗄️ DATABASE FORMAT: Shelve overrides base class save_file() because it creates
        actual persistent dictionary files, not just serialized data dumps.
        
        Args:
            data: Dictionary to store
            file_path: Path to the shelf file
        """
        if not self._allow_unsafe:
            raise ShelveError(
                "Shelve operations require allow_unsafe=True due to pickle security risks"
            )

        validated_path = self._validate_file_path(file_path)
        
        if self.validate_input:
            self._validate_data_security(data)
        
        if not isinstance(data, dict):
            raise ShelveError(f"Shelve requires dict data, got {type(data)}")
        
        try:
            with shelve.open(
                str(validated_path), 
                flag=self._flag,
                protocol=self._protocol,
                writeback=self._writeback
            ) as shelf:
                # Clear existing data if creating new
                if self._flag in ('n', 'c'):
                    shelf.clear()
                
                # Store all data
                for key, value in data.items():
                    shelf[str(key)] = value
            
        except Exception as e:
            self._handle_serialization_error("file save", e)

    def load_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load data from Shelve database file.
        
        🗄️ DATABASE FORMAT: Shelve overrides base class load_file() because it reads
        actual persistent dictionary files, not just serialized data.
        
        Args:
            file_path: Path to the shelf file
            
        Returns:
            Dictionary with key-value pairs
        """
        validated_path = self._validate_file_path(file_path)
        return self.loads(str(validated_path))

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get Shelve format schema information.

        Returns:
            Schema information dictionary
        """
        return {
            "format": "Shelve",
            "version": "1.0",
            "description": "Persistent dictionary (using built-in shelve + pickle)",
            "features": {
                "binary": True,
                "persistent_dict": True,
                "full_python_objects": True,
                "platform_dependent": True,
                "streaming": True,
                "secure_parsing": False,  # Uses pickle internally
                "security_warning": "Uses pickle - only for trusted data"
            },
            "supported_types": [
                "all_python_objects", "persistent_dictionary"
            ],
            "flag": self._flag,
            "protocol": self._protocol,
            "writeback": self._writeback,
            "allow_unsafe": self._allow_unsafe,
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
            "flag": self._flag,
            "protocol": self._protocol,
            "writeback": self._writeback,
            "allow_unsafe": self._allow_unsafe
        })
        return config
