import re
from typing import Any, Callable, Dict, List, Type


class _FormatProxy:
    """
    A descriptor that acts as a proxy for a specific format handler.

    This class is intended for internal use by DynamicFacade. It allows for
    the creation of a fluent API like `xData.json.load(...)`.
    """

    def __init__(self, handler_class: Type, parent_facade_instance: "DynamicFacade"):
        self._handler_class = handler_class
        self._parent = parent_facade_instance

    def load(self, source: Any, **kwargs: Any) -> Any:
        """
        Loads data using the associated handler.

        This method delegates the loading operation to the parent facade's
        `_load_with_handler` method, passing the specific handler class
        it is proxying for.

        Args:
            source: The data source to load (e.g., file path, string, dict).
            **kwargs: Additional keyword arguments for the handler.

        Returns:
            An instance of the parent facade's data container.
        """
        return self._parent._load_with_handler(
            source=source, handler_class=self._handler_class, **kwargs
        )

    def save(self, data_container: Any, file_path: str, **kwargs: Any) -> None:
        """
        Saves data using the associated handler.

        This method delegates the saving operation to the parent facade's
        `_save_with_handler` method.

        Args:
            data_container: The data object to save.
            file_path: The path to save the file to.
            **kwargs: Additional keyword arguments for the handler.
        """
        self._parent._save_with_handler(
            data_container=data_container,
            file_path=file_path,
            handler_class=self._handler_class,
            **kwargs,
        )


class DynamicFacade:
    """
    A base class for creating facades with format-specific methods.

    This class dynamically discovers handler classes and attaches proxy objects
    (like `json`, `xml`) to itself at runtime. This allows for an intuitive,

    discoverable API for loading data in different formats.
    """

    def __init__(
        self, handler_base_class: Type, handler_discovery_func: Callable[[], List[Type]]
    ):
        """
        Initializes the DynamicFacade.

        Args:
            handler_base_class: The base class that all format handlers inherit from.
            handler_discovery_func: A function that returns a list of all handler classes.
        """
        self._handler_base_class = handler_base_class
        self._handler_map = self._discover_handlers(handler_discovery_func)
        self._attach_proxies()

    def _discover_handlers(
        self, discovery_func: Callable[[], List[Type]]
    ) -> Dict[str, Type]:
        """
        Discovers handler classes and maps them to format names.
        """
        handler_map = {}
        handlers = discovery_func()
        for handler in handlers:
            if issubclass(handler, self._handler_base_class):
                format_name = self._get_format_name(handler)
                if format_name:
                    handler_map[format_name] = handler
        return handler_map

    def _get_format_name(self, handler_class: Type) -> str:
        """
        Derives a format name (e.g., 'json') from a handler class name
        (e.g., 'JSONDataHandler').
        """
        name = handler_class.__name__
        # Assumes format like 'JSONDataHandler', 'XMLDataHandler'
        match = re.match(r"([A-Z0-9]+)DataHandler", name)
        if match:
            return match.group(1).lower()
        return ""

    def _attach_proxies(self) -> None:
        """
        Creates and attaches a `_FormatProxy` for each discovered handler.
        """
        for format_name, handler_class in self._handler_map.items():
            proxy_instance = _FormatProxy(handler_class, self)
            setattr(self, format_name, proxy_instance)

    def _load_with_handler(
        self, source: Any, handler_class: Type, **kwargs: Any
    ) -> Any:
        """
        Placeholder for the actual data loading logic.

        Subclasses must override this method to define how to create a data
        container instance using the provided source and handler.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError(
            "Subclasses of DynamicFacade must implement `_load_with_handler`."
        )

    def _save_with_handler(
        self, data_container: Any, file_path: str, handler_class: Type, **kwargs: Any
    ) -> None:
        """
        Placeholder for the actual data saving logic.

        Subclasses must override this method to define how to save a data
        container instance using the provided handler and file path.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError(
            "Subclasses of DynamicFacade must implement `_save_with_handler`."
        )

    def available_formats(self) -> List[str]:
        """
        Returns a list of available format names.
        """
        return sorted(self._handler_map.keys())
