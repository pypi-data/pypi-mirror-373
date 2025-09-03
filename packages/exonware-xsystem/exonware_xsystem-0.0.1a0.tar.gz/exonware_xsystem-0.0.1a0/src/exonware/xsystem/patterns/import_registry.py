"""
Import registration utilities for automatic __init__.py management.

This module provides functionality to automatically generate import statements
and __all__ lists for Python packages, supporting both flat and tree-based
import structures.
"""

import ast
import importlib
import logging
import os
import pkgutil
import re
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Default markers for auto-generated sections
DEFAULT_AUTO_MARKERS = ("#AUTO-START", "#AUTO-END")


@contextmanager
def _project_path_context(project_root: Optional[Path] = None):
    """
    Context manager for temporarily adding project root to sys.path.

    Args:
        project_root: Project root path to add to sys.path

    Yields:
        None
    """
    if project_root is None:
        project_root = Path.cwd().resolve()

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        try:
            yield
        finally:
            if str(project_root) in sys.path:
                sys.path.remove(str(project_root))
    else:
        yield


def _discover_classes_in_module(
    module, module_path: Path, init_folder_path: Path
) -> List[Tuple[str, str]]:
    """
    Discover all public classes in a module.

    Args:
        module: The imported module
        module_path: Path to the module file
        init_folder_path: Path to the __init__.py file being generated

    Returns:
        List of tuples (class_name, relative_import_path)
    """
    classes = []

    try:
        relative_mod_path = module_path.relative_to(init_folder_path.resolve())
        relative_mod_dotted = ".".join(relative_mod_path.with_suffix("").parts)

        for class_name in dir(module):
            obj = getattr(module, class_name)
            if isinstance(obj, type) and obj.__module__ == module.__name__:
                classes.append((class_name, relative_mod_dotted))
    except ValueError:
        # Module is not relative to init folder, skip
        logger.debug(f"Module {module_path} is not relative to {init_folder_path}")

    return classes


def _discover_classes_from_file(
    file_path: Path, init_folder_path: Path
) -> List[Tuple[str, str]]:
    """
    Discover classes in a Python file by parsing the AST (fallback when import fails).

    Args:
        file_path: Path to the Python file
        init_folder_path: Path to the __init__.py file being generated

    Returns:
        List of tuples (class_name, relative_import_path)
    """
    classes = []

    try:
        relative_mod_path = file_path.relative_to(init_folder_path.resolve())
        relative_mod_dotted = ".".join(relative_mod_path.with_suffix("").parts)

        # Read and parse the file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the AST
        tree = ast.parse(content)

        # Find class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                # Skip private classes (starting with _)
                if not class_name.startswith("_"):
                    classes.append((class_name, relative_mod_dotted))

    except Exception as e:
        logger.debug(f"Could not parse file {file_path}: {e}")

    return classes


def _generate_flat_imports(
    source_folders: List[str], init_folder_path: Path, project_root: Path
) -> Tuple[List[str], List[str]]:
    """
    Generate flat import statements for all classes.

    Args:
        source_folders: List of source directory paths
        init_folder_path: Path to the __init__.py file being generated
        project_root: Project root path

    Returns:
        Tuple of (import_lines, all_class_names)
    """
    import_lines = []
    all_class_names = []

    for source_dir_str in source_folders:
        source_dir = Path(source_dir_str).resolve()
        package_name = ".".join(source_dir.relative_to(project_root).parts)

        logger.debug(f"🔍 Scanning directory: {source_dir}")

        for _, modname, ispkg in pkgutil.iter_modules([str(source_dir)]):
            if ispkg or modname.startswith("_"):
                continue

            module_path = source_dir / f"{modname}.py"

            # Try to import the module first
            classes = []
            try:
                full_mod_name = f"{package_name}.{modname}"
                mod = importlib.import_module(full_mod_name)
                mod_path = Path(mod.__file__).resolve()

                classes = _discover_classes_in_module(mod, mod_path, init_folder_path)
                logger.debug(f"  ✅ Successfully imported {modname}")

            except ImportError as e:
                logger.warning(
                    f"⚠️  Could not import module '{modname}' from '{source_dir}'. Error: {e}"
                )
                logger.debug(f"  🔄 Trying to parse {modname} from file...")

                # Fallback: parse the file directly
                if module_path.exists():
                    classes = _discover_classes_from_file(module_path, init_folder_path)
                    if classes:
                        logger.debug(
                            f"  ✅ Found {len(classes)} classes in {modname} via file parsing"
                        )
                    else:
                        logger.debug(
                            f"  ⚠️  No classes found in {modname} via file parsing"
                        )
                else:
                    logger.debug(f"  ❌ File {module_path} does not exist")
                continue

            # Process discovered classes
            for class_name, relative_mod_dotted in classes:
                if class_name not in all_class_names:
                    import_lines.append(
                        f"from .{relative_mod_dotted} import {class_name}\n"
                    )
                    all_class_names.append(class_name)
                    logger.debug(
                        f"  ✅ Found class: {class_name} from {relative_mod_dotted}"
                    )

    return import_lines, all_class_names


def _generate_tree_imports(
    source_folders: List[str], init_folder_path: Path, project_root: Path
) -> Tuple[List[str], List[str]]:
    """
    Generate tree-structured import statements for all classes.

    Args:
        source_folders: List of source directory paths
        init_folder_path: Path to the __init__.py file being generated
        project_root: Project root path

    Returns:
        Tuple of (import_lines, all_class_names)
    """
    import_lines = []
    all_class_names = []

    for source_dir_str in source_folders:
        source_dir = Path(source_dir_str).resolve()
        package_name = ".".join(source_dir.relative_to(project_root).parts)

        logger.debug(f"🔍 Scanning directory: {source_dir}")

        for _, modname, ispkg in pkgutil.iter_modules([str(source_dir)]):
            if ispkg or modname.startswith("_"):
                continue

            module_path = source_dir / f"{modname}.py"

            # Try to import the module first
            classes = []
            try:
                full_mod_name = f"{package_name}.{modname}"
                mod = importlib.import_module(full_mod_name)
                mod_path = Path(mod.__file__).resolve()

                classes = _discover_classes_in_module(mod, mod_path, init_folder_path)
                logger.debug(f"  ✅ Successfully imported {modname}")

            except ImportError as e:
                logger.warning(
                    f"⚠️  Could not import module '{modname}' from '{source_dir}'. Error: {e}"
                )
                logger.debug(f"  🔄 Trying to parse {modname} from file...")

                # Fallback: parse the file directly
                if module_path.exists():
                    classes = _discover_classes_from_file(module_path, init_folder_path)
                    if classes:
                        logger.debug(
                            f"  ✅ Found {len(classes)} classes in {modname} via file parsing"
                        )
                    else:
                        logger.debug(
                            f"  ⚠️  No classes found in {modname} via file parsing"
                        )
                else:
                    logger.debug(f"  ❌ File {module_path} does not exist")
                continue

            # Process discovered classes
            for class_name, relative_mod_dotted in classes:
                if class_name not in all_class_names:
                    # For tree structure, we import the module and reference classes as module.Class
                    import_lines.append(f"from . import {relative_mod_dotted}\n")
                    all_class_names.append(f"{relative_mod_dotted}.{class_name}")
                    logger.debug(
                        f"  ✅ Found class: {class_name} from {relative_mod_dotted}"
                    )

    return import_lines, all_class_names


def _generate_code_block(
    import_lines: List[str], all_class_names: List[str]
) -> List[str]:
    """
    Generate the complete code block with imports and __all__.

    Args:
        import_lines: List of import statements
        all_class_names: List of class names for __all__

    Returns:
        List of code lines
    """
    if not import_lines:
        return []

    output_lines = sorted(set(import_lines))  # Remove duplicates
    all_class_names = sorted(set(all_class_names))  # Remove duplicates

    output_lines.append("\n__all__ = [\n")
    for name in all_class_names:
        output_lines.append(f"    '{name}',\n")
    output_lines.append("]\n")

    return output_lines


def _update_init_file_content(
    existing_lines: List[str], generated_block: List[str], auto_markers: Tuple[str, str]
) -> List[str]:
    """
    Update the content of an __init__.py file with generated imports.

    Args:
        existing_lines: Existing lines in the __init__.py file
        generated_block: Generated import block
        auto_markers: Start and end markers for auto-generated section

    Returns:
        Updated content lines
    """
    start_marker, end_marker = auto_markers
    new_content_lines = []
    in_auto_gen_section = False
    start_marker_found = False

    for line in existing_lines:
        if line.strip() == start_marker:
            new_content_lines.append(line)
            new_content_lines.extend(generated_block)
            in_auto_gen_section = True
            start_marker_found = True
        elif line.strip() == end_marker:
            new_content_lines.append(line)
            in_auto_gen_section = False
        elif not in_auto_gen_section:
            new_content_lines.append(line)

    if not start_marker_found:
        if new_content_lines and new_content_lines[-1].strip() != "":
            new_content_lines.append("\n")
        new_content_lines.append(f"{start_marker}\n")
        new_content_lines.extend(generated_block)
        new_content_lines.append(f"{end_marker}\n")

    return new_content_lines


def register_imports_flat(
    target_package: str,
    source_folders: List[str],
    project_root: Optional[Path] = None,
    auto_markers: Tuple[str, str] = DEFAULT_AUTO_MARKERS,
    logger_instance: Optional[logging.Logger] = None,
) -> bool:
    """
    Register all public classes under a package in a flat structure.

    This function scans source folders for classes and generates import statements
    that make all classes directly accessible from the package level.

    Args:
        target_package: Target package path (e.g., "src.exonware.xcombot")
        source_folders: List of source directory paths to scan
        project_root: Project root path (defaults to current working directory)
        auto_markers: Tuple of (start_marker, end_marker) for auto-generated sections
        logger_instance: Optional logger instance (uses module logger if None)

    Returns:
        True if successful, False otherwise

    Example:
        register_imports_flat(
            target_package="src.exonware.xcombot",
            source_folders=["src/exonware/xcombot/core", "src/exonware/xcombot/platforms"]
        )
    """
    if logger_instance:
        global logger
        logger = logger_instance

    try:
        logger.info(
            f"🚀 Starting flat import registration for package: {target_package}"
        )

        if project_root is None:
            project_root = Path.cwd().resolve()

        init_file_path = Path(target_package.replace(".", "/")) / "__init__.py"
        init_file_path.parent.mkdir(parents=True, exist_ok=True)
        init_file_path.touch(exist_ok=True)

        logger.debug(f"📁 Target __init__.py: {init_file_path}")

        with _project_path_context(project_root):
            import_lines, all_class_names = _generate_flat_imports(
                source_folders, init_file_path.parent, project_root
            )

        generated_block = _generate_code_block(import_lines, all_class_names)

        if not generated_block:
            logger.info(f"ℹ️  No classes found for {init_file_path}. Skipping update.")
            return True

        # Read existing content
        with open(init_file_path, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()

        # Update content
        new_content_lines = _update_init_file_content(
            existing_lines, generated_block, auto_markers
        )

        # Write updated content
        with open(init_file_path, "w", encoding="utf-8") as f:
            f.writelines(new_content_lines)

        logger.info(
            f"✅ Successfully updated {init_file_path} with {len(all_class_names)} classes"
        )
        return True

    except Exception as e:
        logger.error(f"❌ Error during flat import registration: {e}")
        return False


def register_imports_tree(
    target_package: str,
    source_folders: List[str],
    project_root: Optional[Path] = None,
    auto_markers: Tuple[str, str] = DEFAULT_AUTO_MARKERS,
    logger_instance: Optional[logging.Logger] = None,
) -> bool:
    """
    Register all public classes following tree structure.

    This function scans source folders for classes and generates import statements
    that maintain the module hierarchy, making classes accessible through their
    submodule paths.

    Args:
        target_package: Target package path (e.g., "src.exonware.xcombot")
        source_folders: List of source directory paths to scan
        project_root: Project root path (defaults to current working directory)
        auto_markers: Tuple of (start_marker, end_marker) for auto-generated sections
        logger_instance: Optional logger instance (uses module logger if None)

    Returns:
        True if successful, False otherwise

    Example:
        register_imports_tree(
            target_package="src.exonware.xcombot",
            source_folders=["src/exonware/xcombot/core", "src/exonware/xcombot/platforms"]
        )
    """
    if logger_instance:
        global logger
        logger = logger_instance

    try:
        logger.info(
            f"🌳 Starting tree import registration for package: {target_package}"
        )

        if project_root is None:
            project_root = Path.cwd().resolve()

        init_file_path = Path(target_package.replace(".", "/")) / "__init__.py"
        init_file_path.parent.mkdir(parents=True, exist_ok=True)
        init_file_path.touch(exist_ok=True)

        logger.debug(f"📁 Target __init__.py: {init_file_path}")

        with _project_path_context(project_root):
            import_lines, all_class_names = _generate_tree_imports(
                source_folders, init_file_path.parent, project_root
            )

        generated_block = _generate_code_block(import_lines, all_class_names)

        if not generated_block:
            logger.info(f"ℹ️  No classes found for {init_file_path}. Skipping update.")
            return True

        # Read existing content
        with open(init_file_path, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()

        # Update content
        new_content_lines = _update_init_file_content(
            existing_lines, generated_block, auto_markers
        )

        # Write updated content
        with open(init_file_path, "w", encoding="utf-8") as f:
            f.writelines(new_content_lines)

        logger.info(
            f"✅ Successfully updated {init_file_path} with {len(all_class_names)} classes"
        )
        return True

    except Exception as e:
        logger.error(f"❌ Error during tree import registration: {e}")
        return False


def register_imports_batch(
    tasks: List[Dict[str, Any]],
    registration_type: str = "flat",
    project_root: Optional[Path] = None,
    auto_markers: Tuple[str, str] = DEFAULT_AUTO_MARKERS,
    logger_instance: Optional[logging.Logger] = None,
) -> Dict[str, bool]:
    """
    Register imports for multiple packages in batch.

    Args:
        tasks: List of task dictionaries with 'target_package' and 'source_folders' keys
        registration_type: Either "flat" or "tree"
        project_root: Project root path
        auto_markers: Tuple of (start_marker, end_marker) for auto-generated sections
        logger_instance: Optional logger instance

    Returns:
        Dictionary mapping task target_package to success status

    Example:
        tasks = [
            {
                "target_package": "src.exonware.xcombot.core",
                "source_folders": ["src/exonware/xcombot/core"]
            },
            {
                "target_package": "src.exonware.xcombot.platforms",
                "source_folders": ["src/exonware/xcombot/platforms"]
            }
        ]
        results = register_imports_batch(tasks, registration_type="flat")
    """
    if logger_instance:
        global logger
        logger = logger_instance

    logger.info(
        f"🔄 Starting batch import registration ({registration_type}) for {len(tasks)} tasks"
    )

    results = {}
    registration_func = (
        register_imports_flat if registration_type == "flat" else register_imports_tree
    )

    for task in tasks:
        target_package = task["target_package"]
        source_folders = task["source_folders"]

        logger.debug(f"🔍 Processing task: {target_package}")
        success = registration_func(
            target_package=target_package,
            source_folders=source_folders,
            project_root=project_root,
            auto_markers=auto_markers,
            logger_instance=logger_instance,
        )
        results[target_package] = success

    success_count = sum(1 for success in results.values() if success)
    logger.info(
        f"✅ Batch registration completed: {success_count}/{len(tasks)} successful"
    )

    return results
