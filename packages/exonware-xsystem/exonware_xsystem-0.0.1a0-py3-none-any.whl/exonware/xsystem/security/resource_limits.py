"""
Generic resource limits and DoS protection.

This module provides resource limit enforcement to prevent DoS attacks
and resource exhaustion in any application.
"""

from typing import Any

from ..config.logging_setup import get_logger


class GenericLimitError(Exception):
    """Exception raised when resource limits are exceeded."""

    pass


class ResourceLimits:
    """Enforces resource limits to prevent DoS attacks."""

    def __init__(
        self,
        component_name: str = "generic",
        max_depth: int = 1000,
        max_resources: int = 1000000,
        max_path_length: int = 1000,
    ):
        self.component_name = component_name
        self.max_depth = max_depth
        self.max_resources = max_resources
        self.max_path_length = max_path_length
        self._logger = get_logger(f"{component_name}.limits")
        self._resource_count = 0
        self._depth_count = 0

    def check_depth(self, depth: int) -> None:
        """
        Check if depth exceeds maximum allowed.

        Args:
            depth: Current depth to check

        Raises:
            GenericLimitError: If depth exceeds limit
        """
        if depth > self.max_depth:
            raise GenericLimitError(f"Maximum depth {self.max_depth} exceeded: {depth}")
        self._depth_count = max(self._depth_count, depth)

    def check_resource_count(self, count: int) -> None:
        """
        Check if resource count exceeds maximum allowed.

        Args:
            count: Current resource count to check

        Raises:
            GenericLimitError: If count exceeds limit
        """
        if count > self.max_resources:
            raise GenericLimitError(
                f"Maximum resource count {self.max_resources} exceeded: {count}"
            )
        self._resource_count = max(self._resource_count, count)

    def check_path_length(self, path: str) -> None:
        """
        Check if path length exceeds maximum allowed.

        Args:
            path: Path to check

        Raises:
            GenericLimitError: If path exceeds limit
        """
        if len(path) > self.max_path_length:
            raise GenericLimitError(
                f"Path length {len(path)} exceeds maximum {self.max_path_length}"
            )

    def increment_resource_count(self) -> None:
        """Increment resource count and check limit."""
        self._resource_count += 1
        self.check_resource_count(self._resource_count)

    def get_stats(self) -> dict:
        """Get current resource usage statistics."""
        return {
            "component": self.component_name,
            "resource_count": self._resource_count,
            "max_depth": self._depth_count,
            "limits": {
                "max_resources": self.max_resources,
                "max_depth": self.max_depth,
                "max_path_length": self.max_path_length,
            },
        }


# Global resource limits registry
_limits_registry = {}


def get_resource_limits(
    component_name: str = "generic",
    max_depth: int = 1000,
    max_resources: int = 1000000,
    max_path_length: int = 1000,
) -> ResourceLimits:
    """Get resource limits instance for a component."""
    global _limits_registry
    if component_name not in _limits_registry:
        _limits_registry[component_name] = ResourceLimits(
            component_name, max_depth, max_resources, max_path_length
        )
    return _limits_registry[component_name]


def reset_resource_limits(component_name: str = None) -> None:
    """Reset resource limits for a component or all components."""
    global _limits_registry
    if component_name:
        if component_name in _limits_registry:
            del _limits_registry[component_name]
    else:
        _limits_registry.clear()
