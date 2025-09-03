"""
xSystem Patterns Package

Provides design patterns and utilities for common programming patterns.
"""

from .context_manager import (
    ContextualLogger,
    ThreadSafeSingleton,
    combine_contexts,
    create_operation_logger,
    enhanced_error_context,
)
from .handler_factory import GenericHandlerFactory
from .import_registry import (
    register_imports_batch,
    register_imports_flat,
    register_imports_tree,
)
from .object_pool import (
    ObjectPool,
    PooledObject,
    clear_object_pool,
    get_all_pool_stats,
    get_object_pool,
)

__all__ = [
    # Handler Factory
    "GenericHandlerFactory",
    # Context Manager
    "combine_contexts",
    "enhanced_error_context",
    "ContextualLogger",
    "create_operation_logger",
    "ThreadSafeSingleton",
    # Import Registry
    "register_imports_flat",
    "register_imports_tree",
    "register_imports_batch",
    # Object Pool
    "ObjectPool",
    "PooledObject",
    "get_object_pool",
    "clear_object_pool",
    "get_all_pool_stats",
]
