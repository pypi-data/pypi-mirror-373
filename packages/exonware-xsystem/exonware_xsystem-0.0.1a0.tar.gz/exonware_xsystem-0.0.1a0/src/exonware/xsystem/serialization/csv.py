"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

CSV (Comma-Separated Values) Serializer Implementation

Provides CSV serialization with dialect support, header management,
and integration with xSystem utilities for security and validation.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import csv
import io
from pathlib import Path

from .iSerialization import iSerialization
from .aSerialization import aSerialization


class CsvSerializer(aSerialization):
    """
    CSV (Comma-Separated Values) serializer.
    
    ✅ FOLLOWS PRODUCTION LIBRARY PRINCIPLE: Uses built-in csv module exclusively
        for reading/writing CSV data with proper dialect support.
    
    Features:
    - Standard CSV format support (✅ built-in csv module)
    - Configurable dialects (excel, unix, etc.) (✅ csv.DictWriter/DictReader)
    - Header row management (✅ csv writeheader/fieldnames)
    - Custom delimiter and quote character support (✅ csv dialect options)
    - Security validation
    - Atomic file operations
    """
    
    def __init__(
        self,
        delimiter: str = ",",
        quotechar: str = '"',
        quoting: int = csv.QUOTE_MINIMAL,
        lineterminator: str = "\n",
        dialect: str = "excel",
        has_header: bool = True,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 2,  # CSV is naturally flat
        max_size_mb: int = 50
    ) -> None:
        """
        Initialize CSV serializer.
        
        Args:
            delimiter: Field delimiter character
            quotechar: Quote character for fields containing delimiters
            quoting: Quoting style (QUOTE_MINIMAL, QUOTE_ALL, etc.)
            lineterminator: Line terminator string
            dialect: CSV dialect ('excel', 'unix', etc.)
            has_header: Whether data includes header row
            validate_input: Enable input data validation
            validate_paths: Enable path security validation
            use_atomic_writes: Use atomic file operations
            max_depth: Maximum nesting depth (CSV is flat)
            max_size_mb: Maximum data size in MB
        """
        super().__init__(
            validate_input=validate_input,
            validate_paths=validate_paths,
            use_atomic_writes=use_atomic_writes,
            max_depth=max_depth,
            max_size_mb=max_size_mb
        )
        
        self._delimiter = delimiter
        self._quotechar = quotechar
        self._quoting = quoting
        self._lineterminator = lineterminator
        self._dialect = dialect
        self._has_header = has_header
    
    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "CSV"
    
    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".csv", ".tsv")
    
    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "text/csv"
    
    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return False
    
    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True
    
    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to CSV string.
        
        ✅ PRODUCTION LIBRARY: csv.DictWriter() / csv.writer()
        
        Args:
            data: Data to serialize (list of dicts or list of lists)
            
        Returns:
            CSV string
            
        Raises:
            ValueError: If data validation fails
            TypeError: If data is not suitable for CSV
        """
        if self.validate_input:
            self._validate_data_security(data)
        
        if not isinstance(data, (list, tuple)):
            raise ValueError("CSV data must be a list or tuple")
        
        if not data:
            return ""
        
        try:
            output = io.StringIO()
            
            # Determine if we have list of dicts or list of lists
            first_row = data[0]
            
            if isinstance(first_row, dict):
                # List of dictionaries
                fieldnames = list(first_row.keys())
                writer = csv.DictWriter(
                    output,
                    fieldnames=fieldnames,
                    delimiter=self._delimiter,
                    quotechar=self._quotechar,
                    quoting=self._quoting,
                    lineterminator=self._lineterminator,
                    dialect=self._dialect
                )
                
                if self._has_header:
                    writer.writeheader()
                
                for row in data:
                    if not isinstance(row, dict):
                        raise ValueError("All rows must be dictionaries when first row is dict")
                    writer.writerow(row)
            
            else:
                # List of lists/tuples
                writer = csv.writer(
                    output,
                    delimiter=self._delimiter,
                    quotechar=self._quotechar,
                    quoting=self._quoting,
                    lineterminator=self._lineterminator,
                    dialect=self._dialect
                )
                
                for row in data:
                    if not isinstance(row, (list, tuple)):
                        raise ValueError("All rows must be lists/tuples when first row is list/tuple")
                    writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)
    
    def loads_text(self, data: str) -> List[Any]:
        """
        Deserialize CSV data.
        
        Args:
            data: CSV string to deserialize
            
        Returns:
            List of dictionaries (if has_header) or list of lists
            
        Raises:
            ValueError: If data is invalid or validation fails
        """
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        if not isinstance(data, str):
            raise ValueError(f"Expected string or bytes, got {type(data)}")
        
        try:
            input_io = io.StringIO(data)
            
            if self._has_header:
                # Return list of dictionaries
                reader = csv.DictReader(
                    input_io,
                    delimiter=self._delimiter,
                    quotechar=self._quotechar,
                    quoting=self._quoting,
                    dialect=self._dialect
                )
                result = list(reader)
            else:
                # Return list of lists
                reader = csv.reader(
                    input_io,
                    delimiter=self._delimiter,
                    quotechar=self._quotechar,
                    quoting=self._quoting,
                    dialect=self._dialect
                )
                result = list(reader)
            
            if self.validate_input:
                self._validate_data_security(result)
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)
    
    # 🎯 OPTIMIZATION: save_file and load_file inherited from base class!
    # Base class automatically handles text format based on is_binary_format flag
    
    def stream_write(self, data_stream, file_path: Union[str, Path]) -> None:
        """
        Write data stream to CSV file.
        
        Args:
            data_stream: Iterable of data rows
            file_path: Path to save the file
        """
        file_path = Path(file_path)
        
        if self.validate_paths:
            self._path_validator.validate_path(str(file_path))
        
        if self.use_atomic_writes:
            temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
            try:
                with open(temp_path, 'w', encoding='utf-8', newline='') as f:
                    self._write_stream_to_file(data_stream, f)
                temp_path.replace(file_path)
            except Exception:
                if temp_path.exists():
                    temp_path.unlink()
                raise
        else:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                self._write_stream_to_file(data_stream, f)
    
    def _write_stream_to_file(self, data_stream, file_obj) -> None:
        """Write data stream to file object."""
        writer = None
        first_row = True
        
        for row in data_stream:
            if self.validate_input:
                self._validate_data_security(row)
            
            if first_row:
                if isinstance(row, dict):
                    fieldnames = list(row.keys())
                    writer = csv.DictWriter(
                        file_obj,
                        fieldnames=fieldnames,
                        delimiter=self._delimiter,
                        quotechar=self._quotechar,
                        quoting=self._quoting,
                        lineterminator=self._lineterminator,
                        dialect=self._dialect
                    )
                    if self._has_header:
                        writer.writeheader()
                else:
                    writer = csv.writer(
                        file_obj,
                        delimiter=self._delimiter,
                        quotechar=self._quotechar,
                        quoting=self._quoting,
                        lineterminator=self._lineterminator,
                        dialect=self._dialect
                    )
                first_row = False
            
            writer.writerow(row)
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get CSV format schema information.
        
        Returns:
            Schema information dictionary
        """
        return {
            "format": "CSV",
            "version": "RFC 4180",
            "description": "Comma-Separated Values text format",
            "features": {
                "binary": False,
                "delimiter_configurable": True,
                "header_support": True,
                "streaming": True,
                "flat_structure": True
            },
            "supported_types": [
                "string", "number", "flat_data"
            ],
            "delimiter": self._delimiter,
            "quotechar": self._quotechar,
            "has_header": self._has_header,
            "dialect": self._dialect,
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
            "delimiter": self._delimiter,
            "quotechar": self._quotechar,
            "quoting": self._quoting,
            "lineterminator": self._lineterminator,
            "dialect": self._dialect,
            "has_header": self._has_header
        })
        return config


# Error classes for consistency with other serializers
class CsvError(Exception):
    """Base exception for CSV serialization errors."""
    pass
