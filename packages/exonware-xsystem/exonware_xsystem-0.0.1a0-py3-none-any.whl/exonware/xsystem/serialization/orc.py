"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Enhanced Apache ORC serialization with security, validation and performance optimizations.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pyorc
import pandas as pd

from .aSerialization import aSerialization, SerializationError
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.serialization.orc")


class OrcError(SerializationError):
    """ORC-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "ORC", original_error)


class OrcSerializer(aSerialization):
    """
    Enhanced Apache ORC serializer with schema validation and xSystem integration.
    
    Apache ORC (Optimized Row Columnar) is a columnar storage format optimized for Hive.
    
    Features:
    - Highly efficient columnar storage
    - Built-in compression and encoding
    - Predicate pushdown support
    - ACID transaction support
    - Rich type system with complex types
    
    🚨 PRODUCTION LIBRARY: Uses PyORC - the official Python implementation
    """

    def __init__(
        self,
        schema: Optional[str] = None,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 1000.0,  # ORC is designed for large datasets
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
        compression: str = "zlib",  # Compression: none, zlib, snappy, lzo, lz4, zstd
        compression_block_size: int = 65536,  # 64KB blocks
        stripe_size: int = 67108864,  # 64MB stripes
    ) -> None:
        """
        Initialize ORC serializer with compression and performance options.

        Args:
            schema: ORC schema string (optional, will be inferred if not provided)
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
            compression: Compression algorithm
            compression_block_size: Size of compression blocks
            stripe_size: Size of ORC stripes
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
        
        # ORC-specific configuration
        self.schema = schema
        self.compression = compression
        self.compression_block_size = compression_block_size
        self.stripe_size = stripe_size
        
        # Update configuration with ORC-specific options
        self._config.update({
            'schema': schema,
            'compression': compression,
            'compression_block_size': compression_block_size,
            'stripe_size': stripe_size,
        })

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "ORC"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return ['.orc']

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/orc"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return True

    def _prepare_data_for_orc(self, data: Any) -> List[Dict[str, Any]]:
        """Convert data to list of dictionaries for ORC serialization."""
        try:
            if isinstance(data, pd.DataFrame):
                return data.to_dict('records')
            elif isinstance(data, dict):
                # Handle different dict structures
                if all(isinstance(v, list) for v in data.values()):
                    # Dictionary of lists (column-oriented) - convert to rows
                    rows = []
                    max_len = max(len(v) for v in data.values()) if data.values() else 0
                    for i in range(max_len):
                        row = {}
                        for key, values in data.items():
                            row[key] = values[i] if i < len(values) else None
                        rows.append(row)
                    return rows
                else:
                    # Dictionary of values (single row)
                    return [data]
            elif isinstance(data, list):
                if all(isinstance(item, dict) for item in data):
                    # List of dictionaries (row-oriented)
                    return data
                else:
                    # List of values (single column)
                    return [{'values': item} for item in data]
            else:
                # Single value
                return [{'value': data}]
                
        except Exception as e:
            raise OrcError(f"Failed to prepare data for ORC: {e}", e)

    def _infer_orc_schema(self, data: List[Dict[str, Any]]) -> str:
        """Infer ORC schema from data."""
        if not data:
            return "struct<>"
        
        try:
            sample = data[0]
            fields = []
            
            for key, value in sample.items():
                if isinstance(value, str):
                    field_type = "string"
                elif isinstance(value, int):
                    field_type = "bigint"
                elif isinstance(value, float):
                    field_type = "double"
                elif isinstance(value, bool):
                    field_type = "boolean"
                elif isinstance(value, list):
                    field_type = "array<string>"
                elif isinstance(value, dict):
                    field_type = "map<string,string>"
                else:
                    field_type = "string"  # Default to string
                
                fields.append(f"{key}:{field_type}")
            
            return f"struct<{','.join(fields)}>"
            
        except Exception as e:
            raise OrcError(f"Failed to infer ORC schema: {e}", e)

    def dumps(self, data: Any) -> str:
        """
        Serialize data to ORC and return as base64-encoded string.

        Args:
            data: Data to serialize

        Returns:
            Base64-encoded ORC string

        Raises:
            OrcError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            
            # Serialize to ORC bytes
            orc_bytes = self.dumps_binary(data)
            
            # Encode to base64 string for string interface
            import base64
            return base64.b64encode(orc_bytes).decode('ascii')
            
        except SerializationError as e:
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> Any:
        """
        Deserialize ORC data to Python object.

        Args:
            data: ORC bytes or base64-encoded string to deserialize

        Returns:
            Deserialized Python object

        Raises:
            OrcError: If deserialization fails
        """
        try:
            # Handle both bytes and base64 string
            if isinstance(data, str):
                import base64
                orc_bytes = base64.b64decode(data.encode('ascii'))
            else:
                orc_bytes = data
            
            return self.loads_bytes(orc_bytes)
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def dumps_binary(self, data: Any) -> bytes:
        """
        Serialize data to ORC bytes directly.

        Args:
            data: Data to serialize

        Returns:
            ORC bytes

        Raises:
            OrcError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            
            # Convert to list of dictionaries
            rows = self._prepare_data_for_orc(data)
            
            if not rows:
                raise OrcError("No data to serialize")
            
            # Infer schema if not provided
            schema = self.schema or self._infer_orc_schema(rows)
            
            # Serialize using PyORC
            import io
            buffer = io.BytesIO()
            
            with pyorc.Writer(
                buffer, 
                schema,
                compression=pyorc.CompressionKind.__members__.get(self.compression.upper(), pyorc.CompressionKind.ZLIB),
                compression_block_size=self.compression_block_size,
                stripe_size=self.stripe_size
            ) as writer:
                for row in rows:
                    # Convert row to tuple based on schema field order
                    writer.write(tuple(row.get(field, None) for field in self._get_field_names(schema)))
            
            return buffer.getvalue()
            
        except SerializationError as e:
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads_bytes(self, data: bytes) -> List[Dict[str, Any]]:
        """
        Deserialize ORC bytes to Python object.

        Args:
            data: ORC bytes to deserialize

        Returns:
            List of dictionaries representing the data

        Raises:
            OrcError: If deserialization fails
        """
        try:
            import io
            buffer = io.BytesIO(data)
            
            rows = []
            with pyorc.Reader(buffer) as reader:
                schema_fields = self._get_field_names(str(reader.schema))
                
                for row in reader:
                    # Convert tuple to dictionary
                    row_dict = {}
                    for i, field_name in enumerate(schema_fields):
                        if i < len(row):
                            row_dict[field_name] = row[i]
                    rows.append(row_dict)
            
            # Return single item if only one row, otherwise return list
            if len(rows) == 1 and len(rows[0]) == 1 and 'value' in rows[0]:
                return rows[0]['value']
            elif len(rows) == 1:
                return rows[0]
            else:
                return rows
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def _get_field_names(self, schema: str) -> List[str]:
        """Extract field names from ORC schema string."""
        try:
            # Simple schema parsing - extract field names between struct< and >
            if schema.startswith('struct<') and schema.endswith('>'):
                fields_str = schema[7:-1]  # Remove 'struct<' and '>'
                if not fields_str:
                    return []
                
                fields = []
                for field in fields_str.split(','):
                    field = field.strip()
                    if ':' in field:
                        field_name = field.split(':')[0].strip()
                        fields.append(field_name)
                
                return fields
            else:
                return []
                
        except Exception as e:
            logger.warning(f"Failed to parse schema field names: {e}")
            return []

    def loads_dataframe(self, data: Union[bytes, str]) -> pd.DataFrame:
        """
        Deserialize ORC data to pandas DataFrame.

        Args:
            data: ORC bytes or base64-encoded string to deserialize

        Returns:
            pandas DataFrame

        Raises:
            OrcError: If deserialization fails
        """
        try:
            # Handle both bytes and base64 string
            if isinstance(data, str):
                import base64
                orc_bytes = base64.b64decode(data.encode('ascii'))
            else:
                orc_bytes = data
            
            import io
            buffer = io.BytesIO(orc_bytes)
            
            rows = []
            with pyorc.Reader(buffer) as reader:
                schema_fields = self._get_field_names(str(reader.schema))
                
                for row in reader:
                    # Convert tuple to dictionary
                    row_dict = {}
                    for i, field_name in enumerate(schema_fields):
                        if i < len(row):
                            row_dict[field_name] = row[i]
                    rows.append(row_dict)
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)


# Convenience functions for common use cases
def dumps(data: Any, schema: Optional[str] = None, **kwargs: Any) -> str:
    """Serialize data to ORC base64-encoded string with default settings."""
    serializer = OrcSerializer(schema=schema, **kwargs)
    return serializer.dumps(data)


def loads(s: str, **kwargs: Any) -> Any:
    """Deserialize ORC string with default settings.""" 
    serializer = OrcSerializer(**kwargs)
    return serializer.loads(s)


def dumps_bytes(data: Any, schema: Optional[str] = None, **kwargs: Any) -> bytes:
    """Serialize data to ORC bytes with default settings."""
    serializer = OrcSerializer(schema=schema, **kwargs)
    return serializer.dumps_binary(data)


def loads_bytes(data: bytes, **kwargs: Any) -> Any:
    """Deserialize ORC bytes with default settings."""
    serializer = OrcSerializer(**kwargs)
    return serializer.loads_bytes(data)


def loads_dataframe(data: Union[bytes, str], **kwargs: Any) -> pd.DataFrame:
    """Deserialize ORC data to DataFrame with default settings."""
    serializer = OrcSerializer(**kwargs)
    return serializer.loads_dataframe(data)


def load_file(file_path: Union[str, Path], **kwargs: Any) -> Any:
    """Load ORC from file with default settings."""
    serializer = OrcSerializer(**kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], schema: Optional[str] = None, **kwargs: Any) -> None:
    """Save data to ORC file with default settings."""
    serializer = OrcSerializer(schema=schema, **kwargs)
    return serializer.save_file(data, file_path)
