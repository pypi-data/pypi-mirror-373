"""
Generic handler factory pattern combining all xsystem utilities.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from ..io.atomic_file import AtomicFileWriter, atomic_write
from ..security.path_validator import PathSecurityError, PathValidator
from ..structures.circular_detector import (
    CircularReferenceDetector,
    has_circular_references,
)
from ..threading.safe_factory import MethodGenerator, ThreadSafeFactory

logger = logging.getLogger(__name__)

T = TypeVar("T")


class GenericHandlerFactory(ThreadSafeFactory[T]):
    """
    Enhanced handler factory that combines all xsystem utilities.

    This factory provides thread-safe handler registration with additional
    features like path validation, atomic operations, and circular reference
    detection.
    """

    def __init__(
        self,
        base_path: Optional[str] = None,
        enable_security: bool = True,
        enable_circular_detection: bool = True,
        max_circular_depth: int = 100,
    ):
        """
        Initialize enhanced handler factory.

        Args:
            base_path: Base path for file operations
            enable_security: Whether to enable path security validation
            enable_circular_detection: Whether to enable circular reference detection
            max_circular_depth: Maximum depth for circular reference detection
        """
        super().__init__()

        # Initialize utilities
        self.path_validator = (
            PathValidator(base_path=base_path) if enable_security else None
        )
        self.circular_detector = (
            CircularReferenceDetector(max_depth=max_circular_depth)
            if enable_circular_detection
            else None
        )

        # Configuration
        self.enable_security = enable_security
        self.enable_circular_detection = enable_circular_detection

        # Statistics
        self._operation_stats = {
            "handlers_registered": 0,
            "safe_operations": 0,
            "security_violations": 0,
            "circular_references_detected": 0,
        }

    def register_safe(
        self,
        name: str,
        handler_class: Type[T],
        extensions: Optional[List[str]] = None,
        validate_class: bool = True,
    ) -> None:
        """
        Safely register a handler with additional validation.

        Args:
            name: Handler name
            handler_class: Handler class to register
            extensions: File extensions this handler supports
            validate_class: Whether to validate the handler class for circular references

        Raises:
            CircularReferenceError: If circular references detected in handler class
            TypeError: If handler class is invalid
        """
        # Validate handler class
        if not isinstance(handler_class, type):
            raise TypeError(
                f"handler_class must be a class type, got {type(handler_class)}"
            )

        # Check for circular references in handler class if enabled
        if self.enable_circular_detection and validate_class:
            if has_circular_references(handler_class, max_depth=50):
                self._operation_stats["circular_references_detected"] += 1
                raise CircularReferenceError(
                    f"Circular references detected in handler class: {handler_class}"
                )

        # Register the handler
        self.register(name, handler_class, extensions)
        self._operation_stats["handlers_registered"] += 1

        logger.debug(f"Safely registered handler: {name} -> {handler_class.__name__}")

    def safe_file_operation(
        self,
        file_path: str,
        operation: Callable,
        for_writing: bool = False,
        create_dirs: bool = False,
    ) -> Any:
        """
        Perform a file operation with path validation and safety checks.

        Args:
            file_path: Path to the file
            operation: Function to perform on the validated path
            for_writing: Whether the operation involves writing
            create_dirs: Whether to create parent directories

        Returns:
            Result of the operation

        Raises:
            PathSecurityError: If path validation fails
        """
        if not self.enable_security:
            return operation(file_path)

        try:
            # Validate the path
            validated_path = self.path_validator.validate_path(
                file_path, for_writing=for_writing, create_dirs=create_dirs
            )

            # Perform the operation with validated path
            result = operation(str(validated_path))
            self._operation_stats["safe_operations"] += 1

            return result

        except PathSecurityError:
            self._operation_stats["security_violations"] += 1
            raise

    def atomic_write_operation(
        self,
        target_path: str,
        writer_func: Callable,
        mode: str = "w",
        encoding: Optional[str] = "utf-8",
        backup: bool = True,
    ) -> None:
        """
        Perform an atomic write operation with path validation.

        Args:
            target_path: Target file path
            writer_func: Function that takes a file handle and writes to it
            mode: File open mode
            encoding: Text encoding
            backup: Whether to create backup
        """

        def validated_write_operation(validated_path: str) -> None:
            with atomic_write(
                validated_path, mode=mode, encoding=encoding, backup=backup
            ) as f:
                writer_func(f)

        self.safe_file_operation(
            target_path, validated_write_operation, for_writing=True, create_dirs=True
        )

    def validate_data_structure(
        self, data: Any, max_depth: Optional[int] = None
    ) -> bool:
        """
        Validate a data structure for circular references.

        Args:
            data: Data structure to validate
            max_depth: Maximum depth to check (uses factory default if None)

        Returns:
            True if data structure is safe

        Raises:
            CircularReferenceError: If circular references are detected
        """
        if not self.enable_circular_detection:
            return True

        detector = self.circular_detector
        if max_depth is not None:
            detector = CircularReferenceDetector(max_depth=max_depth)

        if detector.is_circular(data):
            self._operation_stats["circular_references_detected"] += 1
            raise CircularReferenceError(
                "Circular references detected in data structure"
            )

        return True

    def create_safe_temp_file(
        self, prefix: Optional[str] = None, suffix: Optional[str] = None
    ) -> str:
        """
        Create a safe temporary file path.

        Args:
            prefix: Optional filename prefix
            suffix: Optional filename suffix

        Returns:
            Path to safe temporary file
        """
        if self.enable_security and self.path_validator:
            temp_path = self.path_validator.create_temp_path(
                prefix=prefix, suffix=suffix, as_file=True
            )
            return str(temp_path)
        else:
            import tempfile

            fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
            import os

            os.close(fd)
            return temp_path

    def generate_enhanced_methods(
        self,
        target_class: Type,
        method_template: Callable,
        method_name_pattern: str = "{action}_{format}",
        method_doc_pattern: str = "{action} data to {format} format.",
    ) -> None:
        """
        Generate enhanced dynamic methods with safety features.

        Args:
            target_class: Class to add methods to
            method_template: Template function for generated methods
            method_name_pattern: Pattern for method names
            method_doc_pattern: Pattern for method docstrings
        """

        # Wrap the method template with safety features
        def safe_method_template(self_obj, format_name: str, *args, **kwargs):
            # Add safety checks to the method call
            try:
                return method_template(self_obj, format_name, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in generated method for format {format_name}: {e}")
                raise

        MethodGenerator.generate_export_methods(
            target_class=target_class,
            factory=self,
            method_template=safe_method_template,
            method_name_pattern=method_name_pattern,
            method_doc_pattern=method_doc_pattern,
        )

    def get_operation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about factory operations.

        Returns:
            Dictionary with operation statistics
        """
        base_stats = {
            "registered_handlers": len(self._handlers),
            "registered_extensions": len(self._extensions),
            "available_formats": self.get_available_formats(),
        }

        base_stats.update(self._operation_stats)

        # Add circular detector stats if available
        if self.circular_detector:
            base_stats.update(
                {"circular_detector_stats": self.circular_detector.get_stats()}
            )

        return base_stats

    def reset_stats(self) -> None:
        """Reset operation statistics."""
        self._operation_stats = {
            "handlers_registered": 0,
            "safe_operations": 0,
            "security_violations": 0,
            "circular_references_detected": 0,
        }

        if self.circular_detector:
            self.circular_detector.reset()


class HandlerInterface(ABC):
    """
    Abstract base class for handlers that work with GenericHandlerFactory.

    This provides a standard interface that handlers should implement.
    """

    @abstractmethod
    def can_handle(self, data: Any) -> bool:
        """
        Check if this handler can process the given data.

        Args:
            data: Data to check

        Returns:
            True if handler can process the data
        """
        pass

    @abstractmethod
    def process(self, data: Any, **kwargs) -> Any:
        """
        Process the data.

        Args:
            data: Data to process
            **kwargs: Additional processing options

        Returns:
            Processed data
        """
        pass

    def validate_input(self, data: Any) -> bool:
        """
        Validate input data before processing.

        Args:
            data: Data to validate

        Returns:
            True if data is valid
        """
        return True

    def get_supported_formats(self) -> List[str]:
        """
        Get list of formats this handler supports.

        Returns:
            List of supported format names
        """
        return []
