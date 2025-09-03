"""
Generic tree walking utilities for processing nested data structures.

This module provides reusable tree traversal functionality that was
previously embedded in xData but is generally useful across xLib components.
"""

import logging
from collections.abc import Mapping, Sequence
from typing import Any, Callable, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)


class TreeWalker:
    """
    Generic tree walking utility with customizable node processors.

    This class provides safe traversal of nested data structures (dicts, lists)
    with protection against circular references and deep recursion.
    """

    def __init__(
        self,
        max_depth: int = 1000,
        track_visited: bool = True,
        visit_tracker: Optional[Set[int]] = None,
    ):
        """
        Initialize tree walker.

        Args:
            max_depth: Maximum traversal depth to prevent stack overflow
            track_visited: Whether to track visited objects to prevent cycles
            visit_tracker: External set for tracking visited object IDs
        """
        self.max_depth = max_depth
        self.track_visited = track_visited
        self.visited = visit_tracker if visit_tracker is not None else set()
        self._depth = 0

    def walk_and_process(
        self, data: Any, node_processor: Callable[[Any, str, int], Any], path: str = ""
    ) -> Any:
        """
        Walk data structure and apply processor to each node.

        Args:
            data: Root data structure to traverse
            node_processor: Function that takes (node, path, depth) and returns processed node
            path: Current path in the data structure

        Returns:
            Processed data structure

        Raises:
            RecursionError: If maximum depth is exceeded
        """
        self._depth += 1

        try:
            # Check depth limit
            if self._depth > self.max_depth:
                logger.warning(
                    f"Maximum tree depth ({self.max_depth}) exceeded at path: {path}"
                )
                raise RecursionError(
                    f"Tree traversal depth limit exceeded: {self.max_depth}"
                )

            # Check for circular references
            if self.track_visited:
                obj_id = id(data)
                if obj_id in self.visited:
                    logger.debug(f"Circular reference detected at path: {path}")
                    return data  # Return unmodified to break cycle

                # Only track containers that could cause cycles
                if isinstance(data, (dict, list, set, tuple)) and data:
                    self.visited.add(obj_id)

            # Process current node
            processed_data = node_processor(data, path, self._depth)

            # Recursively process children
            if isinstance(processed_data, dict):
                return {
                    key: self.walk_and_process(
                        value, node_processor, f"{path}/{key}" if path else str(key)
                    )
                    for key, value in processed_data.items()
                }
            elif isinstance(processed_data, list):
                return [
                    self.walk_and_process(
                        item, node_processor, f"{path}[{i}]" if path else f"[{i}]"
                    )
                    for i, item in enumerate(processed_data)
                ]
            elif isinstance(processed_data, tuple):
                return tuple(
                    self.walk_and_process(
                        item, node_processor, f"{path}({i})" if path else f"({i})"
                    )
                    for i, item in enumerate(processed_data)
                )
            else:
                # Leaf node, return processed value
                return processed_data

        finally:
            self._depth -= 1

    def walk_with_filter(
        self,
        data: Any,
        filter_func: Callable[[Any, str, int], bool],
        processor: Callable[[Any, str, int], Any],
        path: str = "",
    ) -> Any:
        """
        Walk data structure, applying processor only to nodes that pass filter.

        Args:
            data: Root data structure to traverse
            filter_func: Function that returns True if node should be processed
            processor: Function to apply to filtered nodes
            path: Current path in the data structure

        Returns:
            Processed data structure
        """

        def conditional_processor(node: Any, node_path: str, depth: int) -> Any:
            if filter_func(node, node_path, depth):
                return processor(node, node_path, depth)
            return node

        return self.walk_and_process(data, conditional_processor, path)

    def find_nodes(
        self, data: Any, predicate: Callable[[Any, str, int], bool], path: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Find all nodes that match a predicate.

        Args:
            data: Root data structure to search
            predicate: Function that returns True for matching nodes
            path: Current path in the data structure

        Returns:
            List of dictionaries with 'value', 'path', and 'depth' keys
        """
        matches = []

        def collector(node: Any, node_path: str, depth: int) -> Any:
            if predicate(node, node_path, depth):
                matches.append({"value": node, "path": node_path, "depth": depth})
            return node

        self.walk_and_process(data, collector, path)
        return matches

    def transform_leaves(
        self, data: Any, leaf_transformer: Callable[[Any], Any], path: str = ""
    ) -> Any:
        """
        Transform only leaf nodes (non-container values).

        Args:
            data: Root data structure to transform
            leaf_transformer: Function to apply to leaf nodes
            path: Current path in the data structure

        Returns:
            Data structure with transformed leaves
        """

        def leaf_processor(node: Any, node_path: str, depth: int) -> Any:
            # Check if node is a leaf (not a container)
            if not isinstance(node, (dict, list, tuple, set)):
                return leaf_transformer(node)
            return node

        return self.walk_and_process(data, leaf_processor, path)


def walk_and_replace(
    data: Any, replacements: Dict[Any, Any], max_depth: int = 1000
) -> Any:
    """
    Walk data structure and replace values according to replacement map.

    Args:
        data: Data structure to process
        replacements: Mapping of old values to new values
        max_depth: Maximum traversal depth

    Returns:
        Data structure with replacements applied
    """
    walker = TreeWalker(max_depth=max_depth)

    def replacer(node: Any, path: str, depth: int) -> Any:
        return replacements.get(node, node)

    return walker.walk_and_process(data, replacer)


def resolve_proxies_in_dict(
    data: Any,
    resolving_paths: Set[str],
    visited_objects: Optional[Set[int]] = None,
    max_depth: int = 1000,
) -> Any:
    """
    Generic utility to resolve proxy objects in nested data structures.

    This function walks through nested data and resolves any proxy objects
    that have a 'resolve' method, with protection against circular references.

    Args:
        data: The data structure to process
        resolving_paths: Set of paths currently being resolved (for cycle detection)
        visited_objects: Set of object IDs already visited
        max_depth: Maximum recursion depth

    Returns:
        Data structure with proxies resolved
    """
    if visited_objects is None:
        visited_objects = set()

    walker = TreeWalker(max_depth=max_depth, visit_tracker=visited_objects)

    def proxy_resolver(node: Any, path: str, depth: int) -> Any:
        # Check if node is a proxy with resolve method
        if hasattr(node, "resolve") and callable(getattr(node, "resolve")):
            # Check for circular resolution
            if path in resolving_paths:
                logger.warning(f"Circular proxy resolution detected at path: {path}")
                return node  # Return unresolved to break cycle

            try:
                # Add path to resolution tracking
                resolving_paths.add(path)
                logger.debug(f"Resolving proxy at path: {path}")

                # Attempt to resolve the proxy
                resolved = node.resolve(resolving_paths)
                return resolved

            except Exception as e:
                logger.warning(f"Failed to resolve proxy at path {path}: {e}")
                return node  # Return unresolved on error
            finally:
                # Remove path from resolution tracking
                resolving_paths.discard(path)

        return node

    return walker.walk_and_process(data, proxy_resolver)


def apply_user_defined_links(
    data: Any,
    link_processor: Callable[[str, str], Any],
    link_key: str = "_link",
    max_depth: int = 1000,
) -> Any:
    """
    Apply user-defined link processing to data structure.

    Args:
        data: Data structure to process
        link_processor: Function that takes (link_value, path) and returns replacement
        link_key: Key that identifies links in dictionaries
        max_depth: Maximum traversal depth

    Returns:
        Data structure with links processed
    """
    walker = TreeWalker(max_depth=max_depth)

    def link_replacer(node: Any, path: str, depth: int) -> Any:
        if isinstance(node, dict) and link_key in node:
            link_value = node[link_key]
            if isinstance(link_value, str):
                # Replace the link with processed result
                processed_node = node.copy()
                processed_node[link_key] = link_processor(link_value, path)
                return processed_node
        return node

    return walker.walk_and_process(data, link_replacer)


def count_nodes_by_type(data: Any, max_depth: int = 1000) -> Dict[str, int]:
    """
    Count nodes in data structure by type.

    Args:
        data: Data structure to analyze
        max_depth: Maximum traversal depth

    Returns:
        Dictionary mapping type names to counts
    """
    walker = TreeWalker(max_depth=max_depth)
    type_counts = {}

    def type_counter(node: Any, path: str, depth: int) -> Any:
        node_type = type(node).__name__
        type_counts[node_type] = type_counts.get(node_type, 0) + 1
        return node

    walker.walk_and_process(data, type_counter)
    return type_counts


def find_deep_paths(data: Any, min_depth: int = 5, max_depth: int = 1000) -> List[str]:
    """
    Find paths that exceed a minimum depth threshold.

    Args:
        data: Data structure to analyze
        min_depth: Minimum depth to report
        max_depth: Maximum traversal depth

    Returns:
        List of paths that are deeper than min_depth
    """
    walker = TreeWalker(max_depth=max_depth)
    deep_paths = []

    def depth_tracker(node: Any, path: str, depth: int) -> Any:
        if depth >= min_depth and not isinstance(node, (dict, list)):
            # Only report leaf nodes at deep paths
            deep_paths.append(f"{path} (depth: {depth})")
        return node

    walker.walk_and_process(data, depth_tracker)
    return deep_paths
