"""
Circular reference detection and management utilities.
"""

import logging
import weakref
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class CircularReferenceError(Exception):
    """Raised when circular references are detected."""

    pass


class CircularReferenceDetector:
    """
    Utility for detecting and managing circular references in data structures.

    This helps prevent infinite loops and memory leaks when traversing
    complex data structures that may contain circular references.
    """

    def __init__(self, max_depth: int = 100):
        """
        Initialize circular reference detector.

        Args:
            max_depth: Maximum traversal depth before considering it circular
        """
        self.max_depth = max_depth
        self._visiting: Set[int] = set()  # Currently being visited objects
        self._visited: Set[int] = set()  # All visited objects
        self._depth_map: Dict[int, int] = {}  # Object ID to depth mapping
        self._reference_graph: Dict[int, Set[int]] = defaultdict(set)
        self._current_depth = 0

    def is_circular(self, obj: Any, path: Optional[List[str]] = None) -> bool:
        """
        Check if an object contains circular references.

        Args:
            obj: Object to check
            path: Current path for debugging (optional)

        Returns:
            True if circular references are detected
        """
        try:
            self.traverse(obj, path or [])
            return False
        except CircularReferenceError:
            return True
        finally:
            self.reset()

    def traverse(self, obj: Any, path: List[str]) -> None:
        """
        Traverse an object checking for circular references.

        Args:
            obj: Object to traverse
            path: Current path in the object hierarchy

        Raises:
            CircularReferenceError: If circular reference is detected
        """
        # Skip basic types that can't contain references
        if obj is None or isinstance(obj, (str, int, float, bool, bytes)):
            return

        obj_id = id(obj)
        current_path = ".".join(path) if path else "root"

        # Check depth limit
        if self._current_depth > self.max_depth:
            raise CircularReferenceError(
                f"Maximum traversal depth ({self.max_depth}) exceeded at path: {current_path}"
            )

        # Check if we're currently visiting this object (immediate circular reference)
        if obj_id in self._visiting:
            raise CircularReferenceError(
                f"Circular reference detected at path: {current_path} "
                f"(object {obj_id} already being visited)"
            )

        # Check if we've seen this object before at a different depth
        if obj_id in self._depth_map:
            previous_depth = self._depth_map[obj_id]
            if previous_depth <= self._current_depth:
                raise CircularReferenceError(
                    f"Circular reference detected: object {obj_id} encountered again "
                    f"at path {current_path} (previously at depth {previous_depth}, "
                    f"now at depth {self._current_depth})"
                )

        # Mark as currently being visited
        self._visiting.add(obj_id)
        self._depth_map[obj_id] = self._current_depth

        try:
            self._current_depth += 1

            # Traverse based on object type
            if isinstance(obj, dict):
                self._traverse_dict(obj, path)
            elif isinstance(obj, (list, tuple, set)):
                self._traverse_sequence(obj, path)
            elif hasattr(obj, "__dict__"):
                self._traverse_object(obj, path)

            # Mark as completely visited
            self._visited.add(obj_id)

        finally:
            # Remove from currently visiting set
            self._visiting.discard(obj_id)
            self._current_depth -= 1

    def _traverse_dict(self, obj: dict, path: List[str]) -> None:
        """Traverse dictionary objects."""
        for key, value in obj.items():
            # Convert key to string for path tracking
            key_str = str(key) if not isinstance(key, str) else key
            new_path = path + [key_str]

            # Track reference relationship
            if hasattr(value, "__hash__"):
                try:
                    value_id = id(value)
                    obj_id = id(obj)
                    self._reference_graph[obj_id].add(value_id)
                except (TypeError, AttributeError):
                    pass

            self.traverse(value, new_path)

    def _traverse_sequence(self, obj: Union[list, tuple, set], path: List[str]) -> None:
        """Traverse sequence objects (list, tuple, set)."""
        for i, item in enumerate(obj):
            new_path = path + [f"[{i}]"]

            # Track reference relationship
            if hasattr(item, "__hash__"):
                try:
                    item_id = id(item)
                    obj_id = id(obj)
                    self._reference_graph[obj_id].add(item_id)
                except (TypeError, AttributeError):
                    pass

            self.traverse(item, new_path)

    def _traverse_object(self, obj: Any, path: List[str]) -> None:
        """Traverse custom objects via their __dict__."""
        # Skip certain types that are known to be safe
        if isinstance(obj, (type, weakref.ref, weakref.ProxyType)):
            return

        try:
            obj_dict = obj.__dict__
            for attr_name, attr_value in obj_dict.items():
                # Skip private attributes and known safe attributes
                if attr_name.startswith("_"):
                    continue

                new_path = path + [attr_name]

                # Track reference relationship
                if hasattr(attr_value, "__hash__"):
                    try:
                        attr_id = id(attr_value)
                        obj_id = id(obj)
                        self._reference_graph[obj_id].add(attr_id)
                    except (TypeError, AttributeError):
                        pass

                self.traverse(attr_value, new_path)

        except (AttributeError, TypeError):
            # Object doesn't have __dict__ or it's not accessible
            pass

    def reset(self) -> None:
        """Reset the detector state for reuse."""
        self._visiting.clear()
        self._visited.clear()
        self._depth_map.clear()
        self._reference_graph.clear()
        self._current_depth = 0

    def get_reference_graph(self) -> Dict[int, Set[int]]:
        """
        Get the reference graph discovered during traversal.

        Returns:
            Dictionary mapping object IDs to sets of referenced object IDs
        """
        return dict(self._reference_graph)

    def find_circular_paths(self, obj: Any) -> List[List[str]]:
        """
        Find all circular reference paths in an object.

        Args:
            obj: Object to analyze

        Returns:
            List of paths that form circular references
        """
        circular_paths = []

        def traverse_with_path_tracking(
            current_obj: Any,
            current_path: List[str],
            path_objects: Dict[int, List[str]],
        ) -> None:
            if current_obj is None or isinstance(
                current_obj, (str, int, float, bool, bytes)
            ):
                return

            obj_id = id(current_obj)

            if obj_id in path_objects:
                # Found circular reference
                circular_path = path_objects[obj_id] + current_path
                circular_paths.append(circular_path)
                return

            # Add current object to path
            path_objects[obj_id] = current_path.copy()

            try:
                if isinstance(current_obj, dict):
                    for key, value in current_obj.items():
                        key_str = str(key) if not isinstance(key, str) else key
                        traverse_with_path_tracking(
                            value, current_path + [key_str], path_objects.copy()
                        )
                elif isinstance(current_obj, (list, tuple)):
                    for i, item in enumerate(current_obj):
                        traverse_with_path_tracking(
                            item, current_path + [f"[{i}]"], path_objects.copy()
                        )
                elif hasattr(current_obj, "__dict__"):
                    obj_dict = current_obj.__dict__
                    for attr_name, attr_value in obj_dict.items():
                        if not attr_name.startswith("_"):
                            traverse_with_path_tracking(
                                attr_value,
                                current_path + [attr_name],
                                path_objects.copy(),
                            )
            except (AttributeError, TypeError, RuntimeError):
                pass

        try:
            traverse_with_path_tracking(obj, [], {})
        except RecursionError:
            logger.warning("RecursionError during circular path analysis")

        return circular_paths

    def get_stats(self) -> dict:
        """
        Get statistics about the last traversal.

        Returns:
            Dictionary with traversal statistics
        """
        return {
            "visited_objects": len(self._visited),
            "max_depth_reached": (
                max(self._depth_map.values()) if self._depth_map else 0
            ),
            "reference_count": sum(
                len(refs) for refs in self._reference_graph.values()
            ),
            "objects_with_references": len(self._reference_graph),
        }


def has_circular_references(obj: Any, max_depth: int = 100) -> bool:
    """
    Quick function to check if an object has circular references.

    Args:
        obj: Object to check
        max_depth: Maximum depth to traverse

    Returns:
        True if circular references are found
    """
    detector = CircularReferenceDetector(max_depth=max_depth)
    return detector.is_circular(obj)


def safe_traverse(obj: Any, visitor_func: callable, max_depth: int = 100) -> Any:
    """
    Safely traverse an object while avoiding circular references.

    Args:
        obj: Object to traverse
        visitor_func: Function to call for each visited object
        max_depth: Maximum depth to traverse

    Returns:
        Result of traversal or None if circular references detected
    """
    detector = CircularReferenceDetector(max_depth=max_depth)

    def safe_visit(current_obj: Any, path: List[str]) -> Any:
        try:
            detector.traverse(current_obj, path)
            return visitor_func(current_obj)
        except CircularReferenceError:
            logger.warning(
                f"Circular reference detected, skipping object at path: {'.'.join(path)}"
            )
            return None

    return safe_visit(obj, [])
