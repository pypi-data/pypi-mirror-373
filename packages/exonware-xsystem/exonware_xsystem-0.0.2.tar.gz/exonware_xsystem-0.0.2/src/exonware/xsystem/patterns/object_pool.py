"""
Generic object pool implementation for xSystem framework.

This module provides a reusable object pool that can be used across different
components to reduce memory allocation overhead and improve performance.
"""

import threading
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from ..config.logging_setup import get_logger

T = TypeVar("T")


class ObjectPool:
    """
    Generic object pool for reusing instances to reduce memory allocation overhead.

    This is particularly effective when creating and destroying many objects
    of the same type frequently.
    """

    def __init__(
        self,
        max_size: int = 1000,
        enable_thread_safety: bool = True,
        component_name: str = "generic",
    ):
        """
        Initialize the object pool.

        Args:
            max_size: Maximum number of objects to keep in the pool
            enable_thread_safety: Whether to use thread-safe operations
            component_name: Name for logging purposes
        """
        self._pools: Dict[Type, List[Any]] = {}
        self._max_size = max_size
        self._lock = threading.RLock() if enable_thread_safety else None
        self._logger = get_logger(f"{component_name}.object_pool")
        self._stats = {"created": 0, "reused": 0, "released": 0, "discarded": 0}

    def get(self, obj_type: Type[T], *args, **kwargs) -> T:
        """
        Get an object from the pool or create a new one if the pool is empty.

        Args:
            obj_type: The type of object to get/create
            *args: Arguments to pass to the object constructor
            **kwargs: Keyword arguments to pass to the object constructor

        Returns:
            An instance of the requested type
        """
        pool = self._pools.get(obj_type, [])

        if self._lock:
            with self._lock:
                return self._get_from_pool(obj_type, pool, *args, **kwargs)
        else:
            return self._get_from_pool(obj_type, pool, *args, **kwargs)

    def _get_from_pool(self, obj_type: Type[T], pool: List[Any], *args, **kwargs) -> T:
        """Internal method to get object from pool."""
        if pool:
            obj = pool.pop()
            # Re-initialize the object if it has a reset method
            if hasattr(obj, "reset"):
                obj.reset(*args, **kwargs)
            elif hasattr(obj, "__init__"):
                obj.__init__(*args, **kwargs)
            self._stats["reused"] += 1
            self._logger.debug(f"Reused {obj_type.__name__} from pool")
            return obj

        # Create new object
        obj = obj_type(*args, **kwargs)
        self._stats["created"] += 1
        self._logger.debug(f"Created new {obj_type.__name__}")
        return obj

    def release(self, obj: Any) -> None:
        """
        Return an object to the pool for future reuse.

        Args:
            obj: The object to return to the pool
        """
        obj_type = type(obj)

        # Clear references if object has a cleanup method
        if hasattr(obj, "cleanup"):
            obj.cleanup()

        if self._lock:
            with self._lock:
                self._release_to_pool(obj, obj_type)
        else:
            self._release_to_pool(obj, obj_type)

    def _release_to_pool(self, obj: Any, obj_type: Type) -> None:
        """Internal method to release object to pool."""
        if obj_type not in self._pools:
            self._pools[obj_type] = []

        pool = self._pools[obj_type]

        if len(pool) < self._max_size:
            pool.append(obj)
            self._stats["released"] += 1
            self._logger.debug(f"Released {obj_type.__name__} to pool")
        else:
            self._stats["discarded"] += 1
            self._logger.debug(f"Discarded {obj_type.__name__} (pool full)")

    def clear(self, obj_type: Optional[Type] = None) -> None:
        """
        Clear objects from the pool.

        Args:
            obj_type: Specific type to clear, or None to clear all
        """
        if self._lock:
            with self._lock:
                self._clear_pool(obj_type)
        else:
            self._clear_pool(obj_type)

    def _clear_pool(self, obj_type: Optional[Type] = None) -> None:
        """Internal method to clear pool."""
        if obj_type is None:
            # Clear all pools
            for pool in self._pools.values():
                pool.clear()
            self._logger.info("Cleared all object pools")
        else:
            # Clear specific pool
            if obj_type in self._pools:
                self._pools[obj_type].clear()
                self._logger.info(f"Cleared pool for {obj_type.__name__}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get pool statistics.

        Returns:
            Dictionary containing pool statistics
        """
        if self._lock:
            with self._lock:
                return self._get_pool_stats()
        else:
            return self._get_pool_stats()

    def _get_pool_stats(self) -> Dict[str, Any]:
        """Internal method to get pool statistics."""
        pool_sizes = {t.__name__: len(pool) for t, pool in self._pools.items()}

        return {
            "stats": self._stats.copy(),
            "pool_sizes": pool_sizes,
            "max_size": self._max_size,
            "total_pools": len(self._pools),
        }

    def reset_stats(self) -> None:
        """Reset pool statistics."""
        if self._lock:
            with self._lock:
                self._stats = {"created": 0, "reused": 0, "released": 0, "discarded": 0}
        else:
            self._stats = {"created": 0, "reused": 0, "released": 0, "discarded": 0}


class PooledObject:
    """
    Base class for objects that can be pooled.

    Objects that inherit from this class can be automatically managed
    by the ObjectPool with proper cleanup and reset functionality.
    """

    def cleanup(self) -> None:
        """
        Clean up the object before returning to pool.

        Override this method to implement custom cleanup logic.
        """
        pass

    def reset(self, *args, **kwargs) -> None:
        """
        Reset the object to initial state.

        Override this method to implement custom reset logic.
        """
        pass


# Global object pool registry
_pool_registry: Dict[str, ObjectPool] = {}
_pool_registry_lock = threading.RLock()


def get_object_pool(
    component_name: str = "generic",
    max_size: int = 1000,
    enable_thread_safety: bool = True,
) -> ObjectPool:
    """
    Get or create an object pool for a specific component.

    Args:
        component_name: Name of the component
        max_size: Maximum pool size
        enable_thread_safety: Whether to use thread-safe operations

    Returns:
        ObjectPool instance for the component
    """
    with _pool_registry_lock:
        if component_name not in _pool_registry:
            _pool_registry[component_name] = ObjectPool(
                max_size=max_size,
                enable_thread_safety=enable_thread_safety,
                component_name=component_name,
            )
        return _pool_registry[component_name]


def clear_object_pool(component_name: str) -> None:
    """
    Clear a specific object pool.

    Args:
        component_name: Name of the component pool to clear
    """
    with _pool_registry_lock:
        if component_name in _pool_registry:
            _pool_registry[component_name].clear()
            del _pool_registry[component_name]


def get_all_pool_stats() -> Dict[str, Dict[str, Any]]:
    """
    Get statistics for all object pools.

    Returns:
        Dictionary mapping component names to their pool statistics
    """
    with _pool_registry_lock:
        return {name: pool.get_stats() for name, pool in _pool_registry.items()}
