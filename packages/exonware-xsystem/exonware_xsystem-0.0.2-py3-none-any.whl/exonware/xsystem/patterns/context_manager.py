"""
Context manager utilities for combining and enhancing context managers.

This module provides reusable context management functionality that was
previously embedded in xData but is generally useful across xLib components.
"""

import contextlib
import logging
import threading
from contextlib import ExitStack, contextmanager
from typing import Any, ContextManager, Dict, Generator, List, Optional, Type, Union

logger = logging.getLogger(__name__)


@contextmanager
def combine_contexts(*contexts) -> "CombinedContextManager":
    """
    Combine multiple context managers into a single context manager.

    This utility allows you to enter multiple contexts simultaneously and
    ensures proper cleanup even if one of the contexts fails.

    Args:
        *contexts: Variable number of context managers to combine

    Yields:
        None (use the individual context managers directly)

    Example:
        with combine_contexts(lock.acquire(), performance_monitor(), error_handler()):
            # All contexts are active here
            do_work()
    """
    with ExitStack() as stack:
        # Enter all contexts
        for context in contexts:
            if context is not None:
                stack.enter_context(context)
        yield


@contextmanager
def safe_context(
    context_manager, default_value: Any = None, error_handler: Optional[callable] = None
):
    """
    Wrap a context manager to handle errors gracefully.

    Args:
        context_manager: The context manager to wrap
        default_value: Value to yield if context manager fails
        error_handler: Optional function to call on error

    Yields:
        Result of context manager or default_value on error
    """
    try:
        with context_manager as value:
            yield value
    except Exception as e:
        if error_handler:
            error_handler(e)
        else:
            logger.warning(f"Context manager failed: {e}")
        yield default_value


@contextmanager
def operation_context(operation_name: str, **context_data: Any):
    """
    Create a context for operation tracking and logging.

    Args:
        operation_name: Name of the operation being performed
        **context_data: Additional context data for logging

    Yields:
        Dictionary containing operation context
    """
    context = {"operation": operation_name, "data": context_data}

    logger.debug(f"Starting operation: {operation_name}")
    if context_data:
        logger.debug(f"Operation context: {context_data}")

    try:
        yield context
    except Exception as e:
        logger.error(f"Operation {operation_name} failed: {e}")
        raise
    finally:
        logger.debug(f"Completed operation: {operation_name}")


@contextmanager
def enhanced_error_context(
    operation: str, **context_data: Any
) -> "EnhancedErrorContext":
    """
    Enhanced error context manager with detailed error information.

    Args:
        operation: Name of the operation
        **context_data: Additional context for error reporting

    Yields:
        Context dictionary
    """
    context = {"operation": operation, "context": context_data}

    try:
        yield context
    except Exception as e:
        # Enhance the exception with context information
        error_msg = f"Operation '{operation}' failed: {e}"
        if context_data:
            context_str = ", ".join(f"{k}={v}" for k, v in context_data.items())
            error_msg += f" (Context: {context_str})"

        logger.error(error_msg)
        # Re-raise with enhanced context
        raise type(e)(error_msg) from e


class ContextualLogger:
    """
    Logger wrapper that adds contextual information to all log messages.

    This class was extracted from xData to provide reusable contextual logging
    across different components.
    """

    def __init__(self, base_logger, operation_name: str, **context: Any):
        """
        Initialize contextual logger.

        Args:
            base_logger: Base logger instance
            operation_name: Name of the operation for context
            **context: Additional context to include in messages
        """
        self.logger = base_logger
        self.operation = operation_name
        self.context = context

    def _format_message(self, msg: str) -> str:
        """Format message with operation context."""
        ctx_str = f" [{self.operation}]"
        if self.context:
            ctx_items = [f"{k}={v}" for k, v in self.context.items()]
            ctx_str += f" ({', '.join(ctx_items)})"
        return f"{msg}{ctx_str}"

    def debug(self, msg: str) -> None:
        """Log debug message with context."""
        self.logger.debug(self._format_message(msg))

    def info(self, msg: str) -> None:
        """Log info message with context."""
        self.logger.info(self._format_message(msg))

    def warning(self, msg: str) -> None:
        """Log warning message with context."""
        self.logger.warning(self._format_message(msg))

    def error(self, msg: str) -> None:
        """Log error message with context."""
        self.logger.error(self._format_message(msg))


def create_operation_logger(
    base_logger: Any, operation_name: str, **context: Any
) -> ContextualLogger:
    """
    Create a contextual logger for consistent operation logging.

    Args:
        base_logger: Base logger instance
        operation_name: Name of the operation
        **context: Additional context to include in log messages

    Returns:
        ContextualLogger instance with operation context
    """
    return ContextualLogger(base_logger, operation_name, **context)


@contextmanager
def conditional_context(condition: bool, context_manager, fallback_context=None):
    """
    Conditionally enter a context manager based on a condition.

    Args:
        condition: Whether to use the primary context manager
        context_manager: Primary context manager to use if condition is True
        fallback_context: Optional fallback context if condition is False

    Yields:
        Result of active context manager or None
    """
    if condition:
        with context_manager as value:
            yield value
    elif fallback_context is not None:
        with fallback_context as value:
            yield value
    else:
        yield None


@contextmanager
def timeout_context(timeout_seconds: float):
    """
    Context manager that tracks operation timeout.

    Args:
        timeout_seconds: Maximum time allowed for operation

    Yields:
        Start time of the operation

    Raises:
        TimeoutError: If operation exceeds timeout
    """
    import time

    start_time = time.time()

    try:
        yield start_time
    finally:
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(
                f"Operation timed out after {elapsed:.2f}s (limit: {timeout_seconds}s)"
            )


@contextmanager
def resource_context(acquire_func: Any, release_func: Any, *args: Any, **kwargs: Any) -> Generator[Any, None, None]:
    """
    Generic resource management context manager.

    Args:
        acquire_func: Function to acquire the resource
        release_func: Function to release the resource
        *args, **kwargs: Arguments for acquire function

    Yields:
        Resource returned by acquire_func
    """
    resource = None
    try:
        resource = acquire_func(*args, **kwargs)
        yield resource
    finally:
        if resource is not None:
            try:
                release_func(resource)
            except Exception as e:
                logger.warning(f"Error releasing resource: {e}")


class MultiContextManager:
    """
    Class-based approach to managing multiple context managers.

    This provides more control than the function-based approach and allows
    for dynamic addition/removal of contexts.
    """

    def __init__(self) -> None:
        """Initialize empty multi-context manager."""
        self.contexts: List[ContextManager] = []
        self.entered_contexts: List[Any] = []
        self.stack: Optional[ExitStack] = None

    def add_context(self, context: ContextManager):
        """Add a context manager to be managed."""
        if self.stack is not None:
            raise RuntimeError("Cannot add contexts after entering")
        self.contexts.append(context)

    def __enter__(self) -> List[Any]:
        """Enter all managed contexts."""
        self.stack = ExitStack()
        self.entered_contexts = []

        try:
            for context in self.contexts:
                result = self.stack.enter_context(context)
                self.entered_contexts.append(result)
            return self.entered_contexts
        except Exception:
            self.stack.__exit__(None, None, None)
            raise

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        """Exit all managed contexts."""
        if self.stack is not None:
            return self.stack.__exit__(exc_type, exc_val, exc_tb)


class ThreadSafeSingleton(type):
    """
    Thread-safe singleton metaclass for use in singleton classes.
    Usage:
        class MyClass(metaclass=ThreadSafeSingleton):
            ...
    """

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
