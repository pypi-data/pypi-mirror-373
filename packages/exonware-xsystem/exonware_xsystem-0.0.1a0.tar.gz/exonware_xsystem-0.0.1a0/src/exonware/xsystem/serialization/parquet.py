"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Enhanced Apache Parquet serialization with security, validation and performance optimizations.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

from .aSerialization import aSerialization, SerializationError
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.serialization.parquet")


class ParquetError(SerializationError):
    """Parquet-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "PARQUET", original_error)


class ParquetSerializer(aSerialization):
    """
    Enhanced Apache Parquet serializer with schema validation and xSystem integration.
    
    Apache Parquet is a columnar storage format optimized for analytics workloads.
    
    Features:
    - Columnar storage for efficient compression and encoding
    - Schema evolution support
    - Predicate pushdown for query optimization
    - Cross-platform compatibility
    - Built-in statistics for each column
    
    🚨 PRODUCTION LIBRARY: Uses PyArrow - the official Python implementation
    """

    def __init__(
        self,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 1000.0,  # Parquet is designed for large datasets
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
        compression: str = "snappy",  # Compression: snappy, gzip, lzo, brotli, lz4, zstd
        use_dictionary: bool = True,
        row_group_size: int = 64 * 1024 * 1024,  # 64MB row groups
        use_pandas_metadata: bool = True,
    ) -> None:
        """
        Initialize Parquet serializer with compression and performance options.

        Args:
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
            compression: Compression algorithm
            use_dictionary: Whether to use dictionary encoding
            row_group_size: Size of row groups in bytes
            use_pandas_metadata: Whether to store pandas metadata
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
        
        # Parquet-specific configuration
        self.compression = compression
        self.use_dictionary = use_dictionary
        self.row_group_size = row_group_size
        self.use_pandas_metadata = use_pandas_metadata
        
        # Update configuration with Parquet-specific options
        self._config.update({
            'compression': compression,
            'use_dictionary': use_dictionary,
            'row_group_size': row_group_size,
            'use_pandas_metadata': use_pandas_metadata,
        })

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "PARQUET"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return ['.parquet', '.pq']

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/parquet"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return True

    def _to_dataframe(self, data: Any) -> pd.DataFrame:
        """Convert data to DataFrame using pandas intelligence."""
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
            return pd.DataFrame(data)  # Column-oriented
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            return pd.DataFrame(data)  # Row-oriented
        else:
            return pd.DataFrame([data] if isinstance(data, dict) else {'value': [data]})

    def dumps(self, data: Any) -> str:
        """
        Serialize data to Parquet and return as base64-encoded string.

        Args:
            data: Data to serialize

        Returns:
            Base64-encoded Parquet string

        Raises:
            ParquetError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            
            # Serialize to Parquet bytes
            parquet_bytes = self.dumps_binary(data)
            
            # Encode to base64 string for string interface
            import base64
            return base64.b64encode(parquet_bytes).decode('ascii')
            
        except SerializationError as e:
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> Any:
        """
        Deserialize Parquet data to Python object.

        Args:
            data: Parquet bytes or base64-encoded string to deserialize

        Returns:
            Deserialized Python object

        Raises:
            ParquetError: If deserialization fails
        """
        try:
            # Handle both bytes and base64 string
            if isinstance(data, str):
                import base64
                parquet_bytes = base64.b64decode(data.encode('ascii'))
            else:
                parquet_bytes = data
            
            return self.loads_bytes(parquet_bytes)
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def dumps_binary(self, data: Any) -> bytes:
        """Serialize data to Parquet bytes."""
        try:
            self._validate_data_security(data)
            df = self._to_dataframe(data)
            table = pa.Table.from_pandas(df, preserve_index=False)
            
            import io
            buffer = io.BytesIO()
            pq.write_table(table, buffer, compression=self.compression, use_dictionary=self.use_dictionary, row_group_size=self.row_group_size)
            return buffer.getvalue()
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads_bytes(self, data: bytes) -> Any:
        """Deserialize Parquet bytes."""
        try:
            import io
            df = pq.read_table(io.BytesIO(data)).to_pandas()
            # Smart conversion back to original structure
            if len(df.columns) == 1 and len(df) == 1 and 'value' in df.columns:
                return df.iloc[0, 0]
            elif len(df) == 1:
                return df.iloc[0].to_dict()
            else:
                return df.to_dict('records')
        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def loads_dataframe(self, data: Union[bytes, str]) -> pd.DataFrame:
        """
        Deserialize Parquet data to pandas DataFrame.

        Args:
            data: Parquet bytes or base64-encoded string to deserialize

        Returns:
            pandas DataFrame

        Raises:
            ParquetError: If deserialization fails
        """
        try:
            # Handle both bytes and base64 string
            if isinstance(data, str):
                import base64
                parquet_bytes = base64.b64decode(data.encode('ascii'))
            else:
                parquet_bytes = data
            
            import io
            buffer = io.BytesIO(parquet_bytes)
            
            # Read Parquet from bytes
            table = pq.read_table(buffer)
            return table.to_pandas()
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)


# Convenience functions for common use cases
def dumps(data: Any, **kwargs: Any) -> str:
    """Serialize data to Parquet base64-encoded string with default settings."""
    serializer = ParquetSerializer(**kwargs)
    return serializer.dumps(data)


def loads(s: str, **kwargs: Any) -> Any:
    """Deserialize Parquet string with default settings.""" 
    serializer = ParquetSerializer(**kwargs)
    return serializer.loads(s)


def dumps_bytes(data: Any, **kwargs: Any) -> bytes:
    """Serialize data to Parquet bytes with default settings."""
    serializer = ParquetSerializer(**kwargs)
    return serializer.dumps_binary(data)


def loads_bytes(data: bytes, **kwargs: Any) -> Any:
    """Deserialize Parquet bytes with default settings."""
    serializer = ParquetSerializer(**kwargs)
    return serializer.loads_bytes(data)


def loads_dataframe(data: Union[bytes, str], **kwargs: Any) -> pd.DataFrame:
    """Deserialize Parquet data to DataFrame with default settings."""
    serializer = ParquetSerializer(**kwargs)
    return serializer.loads_dataframe(data)


def load_file(file_path: Union[str, Path], **kwargs: Any) -> Any:
    """Load Parquet from file with default settings."""
    serializer = ParquetSerializer(**kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], **kwargs: Any) -> None:
    """Save data to Parquet file with default settings."""
    serializer = ParquetSerializer(**kwargs)
    return serializer.save_file(data, file_path)
