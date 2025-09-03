"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Enhanced YAML serialization with security, validation and performance optimizations.
"""

import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TextIO

try:
    import yaml
    from yaml import SafeLoader, SafeDumper
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    # Define dummy classes for type hints when YAML is not available
    class SafeLoader:
        pass
    class SafeDumper:
        pass

from .aSerialization import aSerialization, SerializationError
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.serialization.yaml")


class YamlError(SerializationError):
    """YAML-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "YAML", original_error)


class YamlSerializer(aSerialization):
    """
    Enhanced YAML serializer with security validation, custom encoders,
    and performance optimizations for production use.
    """

    def __init__(
        self,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 10.0,
        default_flow_style: Optional[bool] = None,
        sort_keys: bool = False,
        width: Optional[int] = None,
        indent: int = 2,
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Initialize YAML serializer with security and performance options.

        Args:
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            default_flow_style: YAML flow style (None for auto)
            sort_keys: Whether to sort dictionary keys
            width: Line width for YAML output
            indent: Indentation for nested structures
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
        """
        if not YAML_AVAILABLE:
            raise YamlError("PyYAML is required for YAML serialization. Install with: pip install PyYAML")
            
        # Initialize base class with xSystem integration
        super().__init__(
            validate_input=validate_input,
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            use_atomic_writes=use_atomic_writes,
            validate_paths=validate_paths,
            base_path=base_path,
        )
        
        # YAML-specific configuration
        self.default_flow_style = default_flow_style
        self.sort_keys = sort_keys
        self.width = width
        self.indent = indent
        
        # Update configuration with YAML-specific options
        self._config.update({
            'default_flow_style': default_flow_style,
            'sort_keys': sort_keys,
            'width': width,
            'indent': indent,
        })

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "YAML"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return ['.yaml', '.yml']

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/x-yaml"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return False

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return True

    def _validate_data(self, data: Any) -> None:
        """Validate data before serialization using base class validation."""
        try:
            self._validate_data_security(data)
        except SerializationError as e:
            raise YamlError(str(e), e.original_error) from e

    def _custom_representer(self, dumper: SafeDumper, obj: Any) -> Any:
        """Custom representer for non-standard types."""
        if isinstance(obj, Decimal):
            return dumper.represent_float(float(obj))
        elif isinstance(obj, Path):
            return dumper.represent_str(str(obj))
        elif hasattr(obj, '__dict__'):
            return dumper.represent_dict(obj.__dict__)
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return dumper.represent_str(obj.isoformat())
        
        return dumper.represent_str(str(obj))

    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to YAML string.

        Args:
            data: Data to serialize

        Returns:
            YAML string

        Raises:
            YamlError: If serialization fails
        """
        try:
            self._validate_data(data)
            
            # Configure custom representer
            SafeDumper.add_representer(Decimal, self._custom_representer)
            SafeDumper.add_representer(Path, self._custom_representer)
            
            return yaml.dump(
                data,
                Dumper=SafeDumper,
                default_flow_style=self.default_flow_style,
                sort_keys=self.sort_keys,
                width=self.width,
                indent=self.indent,
                encoding=None,
                allow_unicode=True
            )
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def dump(self, data: Any, fp: TextIO) -> None:
        """
        Serialize data to YAML file.

        Args:
            data: Data to serialize
            fp: File-like object to write to

        Raises:
            YamlError: If serialization fails
        """
        try:
            self._validate_data(data)
            
            # Configure custom representer
            SafeDumper.add_representer(Decimal, self._custom_representer)
            SafeDumper.add_representer(Path, self._custom_representer)
            
            yaml.dump(
                data,
                fp,
                Dumper=SafeDumper,
                default_flow_style=self.default_flow_style,
                sort_keys=self.sort_keys,
                width=self.width,
                indent=self.indent,
                encoding=None,
                allow_unicode=True
            )
            
        except yaml.YAMLError as e:
            raise YamlError(f"YAML encoding failed: {e}") from e
        except Exception as e:
            raise YamlError(f"Serialization error: {e}") from e

    def loads_text(self, data: str) -> Any:
        """
        Deserialize YAML string to Python object.

        Args:
            data: YAML string to deserialize

        Returns:
            Deserialized Python object

        Raises:
            YamlError: If deserialization fails
        """
        try:
            result = yaml.load(data, Loader=SafeLoader)
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)




# Convenience functions for common use cases
def dumps(data: Any, **kwargs: Any) -> str:
    """Serialize data to YAML string with default settings."""
    serializer = YamlSerializer(**kwargs)
    return serializer.dumps(data)


def loads(s: str, **kwargs: Any) -> Any:
    """Deserialize YAML string with default settings.""" 
    serializer = YamlSerializer(**kwargs)
    return serializer.loads(s)


def load_file(file_path: Union[str, Path], **kwargs: Any) -> Any:
    """Load YAML from file with default settings."""
    serializer = YamlSerializer(**kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], **kwargs: Any) -> None:
    """Save data to YAML file with default settings."""
    serializer = YamlSerializer(**kwargs)
    return serializer.save_file(data, file_path)
