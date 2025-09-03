import importlib.metadata
import inspect
import threading
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, cast
from functools import lru_cache

T = TypeVar("T")


_EXT_GROUP_PREFIX = "naylence."

_EXT_MANAGER_CACHE: Dict[tuple[str, Type[Any]], "ExtensionManager[Any]"] = {}
_EXT_MANAGER_LOCK = (
    threading.RLock()
)  # RLock allows same thread to acquire multiple times


class ExtensionManager(Generic[T]):
    """
    Generic helper to load classes (or callables) from entry-points,
    enforce that they subclass/implement a given base_type, and expose a
    simple registry API for lookup by name.
    """

    def __init__(self, *, group: str, base_type: Type[T]):
        """
        :param group: the entry-point group name (e.g. "naylence.fabric.backends")
        :param base_type: the abstract/interface class that every plugin must subclass
        """
        self._group = group
        self._base_type = base_type
        self._registry: Dict[str, Type[T]] = {}
        self._instance_cache: Dict[str, T] = {}  # Cache for factory instances
        self._load_all()

    def _load_all(self) -> None:
        """
        Discover all installed entry-points under self._group, attempt to load(),
        and ensure each one is a subclass (or at least an instance of) self._base_type.
        """
        # Python 3.10+ API
        eps = importlib.metadata.entry_points(group=self._group)

        for ep in eps:
            name = ep.name
            try:
                cls = ep.load()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load entry-point '{name}' from group '{self._group}': {e!r}"
                )

            # If the loaded object is a module-level function or something else,
            # you may want to allow it as long as it returns a correct type. But
            # most often you expect a class. Let's check subclass or issubclass:
            if not inspect.isclass(cls):
                raise TypeError(
                    f"Entry-point '{name}' in group '{self._group}' did not yield a class, "
                    f"but returned {type(cls).__name__}"
                )

            # Ensure it inherits from base_type:
            if not issubclass(cls, self._base_type):
                raise TypeError(
                    f"Entry-point '{name}' in group '{self._group}' must be a subclass of "
                    f"{self._base_type.__name__}, but got {cls!r}"
                )

            # Register it:
            self._registry[name] = cast(Type[T], cls)

    def available_names(self) -> List[str]:
        """
        :returns: list of all registered entry-point names in this group
        """
        return list(self._registry.keys())

    def get(self, name: Optional[str] = None) -> Type[T]:
        """
        Retrieve the plugin class registered under the given name.
        If name is None, raises an error (caller should pick a default).
        """
        if name is None:
            raise ValueError(
                f"No name provided; available options: {self.available_names()!r}"
            )
        try:
            return self._registry[name]
        except KeyError:
            raise KeyError(
                f"Unknown plugin '{name}' in group '{self._group}'. "
                f"Available: {self.available_names()!r}"
            )

    def get_instance(self, name: Optional[str] = None, *args: Any, **kwargs: Any) -> T:
        """
        Retrieve a cached factory instance for the given name.

        :param name: the plugin name to get an instance for
        :param args: positional arguments to pass to the factory constructor (only used on first creation)
        :param kwargs: keyword arguments to pass to the factory constructor (only used on first creation)
        :returns: cached or newly created factory instance
        """
        if name is None:
            raise ValueError(
                f"No name provided; available options: {self.available_names()!r}"
            )
        return self._get_or_create_extension_instance(name, *args, **kwargs)

    def clear_instance_cache(self, name: Optional[str] = None) -> None:
        """
        Clear cached factory instances.

        :param name: specific plugin name to clear from cache, or None to clear all
        """
        if name is None:
            self._instance_cache.clear()
        else:
            self._instance_cache.pop(name, None)

    def get_cached_instance_names(self) -> List[str]:
        """
        Get the names of all currently cached factory instances.

        :returns: list of plugin names that have cached instances
        """
        return list(self._instance_cache.keys())

    def get_default_extensions(self) -> List[str]:
        """
        Get all extension names that are marked as default.

        :returns: list of extension names marked with is_default=True
        """
        defaults = []
        for name in self._registry.keys():
            instance = self._get_or_create_extension_instance(name)
            if getattr(instance, "is_default", False):
                defaults.append(name)
        return defaults

    def get_default_instance(
        self, *args: Any, **kwargs: Any
    ) -> Optional[Tuple[T, str]]:
        """
        Get the default extension instance. Warns if multiple defaults exist.

        :param args: positional arguments to pass to the factory constructor
        :param kwargs: keyword arguments to pass to the factory constructor
        :returns: default extension instance or None if no default found
        """
        defaults = self.get_default_extensions()

        if not defaults:
            return None

        if len(defaults) > 1:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Multiple default implementations found for {self._base_type.__name__}: {defaults}. "
                f"Using '{defaults[0]}'. Consider configuring explicit type."
            )

        instance = self._get_or_create_extension_instance(defaults[0], *args, **kwargs)
        return (instance, defaults[0]) if instance else None

    def get_best_default_instance(
        self, *args: Any, **kwargs: Any
    ) -> Optional[Tuple[T, str]]:
        """
        Get the best default extension instance by priority.
        Selects the highest priority among all default-eligible extensions.

        :param args: positional arguments to pass to the factory constructor
        :param kwargs: keyword arguments to pass to the factory constructor
        :returns: best default extension instance or None if no default found
        """
        # Get all extensions and their priorities
        candidates = []
        for name in self._registry.keys():
            instance = self._get_or_create_extension_instance(name)
            is_default = getattr(instance, "is_default", False)
            priority = getattr(instance, "priority", 0)

            # Only consider factories marked as defaults
            if is_default:
                candidates.append((name, instance, priority))

        if not candidates:
            return None

        # Sort by priority (highest first) and pick the best
        candidates.sort(key=lambda x: x[2], reverse=True)
        best_name, best_instance, best_priority = candidates[0]

        # Log selection if multiple candidates exist
        if len(candidates) > 1:
            import logging

            logger = logging.getLogger(__name__)
            logger.debug(
                f"Selected best default for {self._base_type.__name__}: '{best_name}' "
                f"(priority={best_priority}) among {[f'{c[0]}(p={c[2]})' for c in candidates]}"
            )

        return (best_instance, best_name)

    def _get_or_create_extension_instance(
        self, name: str, *args: Any, **kwargs: Any
    ) -> T:
        """
        Get or create a cached factory instance for the given plugin name.
        Factory instances are cached since they're typically stateless.

        :param name: the plugin name to get an instance for
        :param args: positional arguments to pass to the factory constructor (only used on first creation)
        :param kwargs: keyword arguments to pass to the factory constructor (only used on first creation)
        :returns: cached or newly created factory instance
        """
        if name not in self._instance_cache:
            cls = self.get(name)
            self._instance_cache[name] = cls(*args, **kwargs)
        return self._instance_cache[name]

    def __repr__(self) -> str:
        cached_instances = len(self._instance_cache)
        return (
            f"<ExtensionManager group={self._group!r} base={self._base_type.__name__!r} "
            f"plugins={self.available_names()!r} cached_instances={cached_instances}>"
        )

    @staticmethod
    def lazy_init(*, group: str, base_type: Type[T]) -> "ExtensionManager[T]":
        """
        Lazily create (or retrieve) a singleton ExtensionManager for the
        given (group, base_type) pair.

        :param group:     entry-point group name, e.g. "naylence.fabric.backends"
        :param base_type: abstract/interface class every plugin must subclass
        :returns:         the cached ExtensionManager instance
        """
        key = (group, base_type)  # composite key keeps different base_types distinct

        with _EXT_MANAGER_LOCK:
            mgr = _EXT_MANAGER_CACHE.get(key)
            if mgr is None:
                mgr = ExtensionManager(group=group, base_type=base_type)
                _EXT_MANAGER_CACHE[key] = mgr

        # cast narrows the generic type for the caller
        return cast("ExtensionManager[T]", mgr)

    @classmethod
    def get_extensions_by_type(cls, base_type: Type[Any]) -> Dict[str, Type[T]]:
        """
        Return all registered extensions for the base_type as {name: factory}.
        Returns a readonly copy to prevent mutation of the internal registry.

        :param base_type: the base type/interface to get extensions for
        :returns: dictionary mapping extension names to their factory classes (readonly copy)
        """
        mgr = ExtensionManager.lazy_init(
            group=_EXT_GROUP_PREFIX + base_type.__name__, base_type=base_type
        )
        # Return a copy to prevent mutation of the internal registry
        return mgr._registry.copy()

        # Alternative implementation for truly immutable result:
        # return types.MappingProxyType(mgr._registry)
        # Note: MappingProxyType creates a read-only view, but some IDEs/tools
        # might not recognize it as Dict[str, Type[T]] for type checking

    @staticmethod
    def get_extension_by_name_and_type(
        name: str, base_type: Type[T], *args: Any, **kwargs: Any
    ) -> T:
        """
        Create a resource instance by getting the appropriate ExtensionManager for the base_type
        and retrieving the named plugin from it.

        :param name: the plugin/extension name to look for
        :param base_type: the base type/interface that the plugin should implement
        :param args: positional arguments to pass to the plugin constructor
        :param kwargs: keyword arguments to pass to the plugin constructor
        :returns: an instance of the plugin
        :raises ValueError: if no suitable ExtensionManager or plugin is found
        """
        mgr = ExtensionManager.lazy_init(
            group=_EXT_GROUP_PREFIX + base_type.__name__, base_type=base_type
        )

        # Check if this manager has the requested plugin name
        if name in mgr._registry:
            return mgr._get_or_create_extension_instance(name, *args, **kwargs)

        # If plugin not found, provide helpful error message
        raise ValueError(
            f"Plugin '{name}' not found in ExtensionManager for base_type '{base_type.__name__}'. "
            f"Available plugins: {mgr.available_names()}"
        )

    @staticmethod
    def get_default_extension_by_type(
        base_type: Type[T], *args: Any, **kwargs: Any
    ) -> Optional[Tuple[T, str]]:
        """
        Get the default extension instance for a given base type.

        :param base_type: the base type/interface to get default for
        :param args: positional arguments to pass to the factory constructor
        :param kwargs: keyword arguments to pass to the factory constructor
        :returns: default extension instance or None if no default found
        """
        mgr = ExtensionManager.lazy_init(
            group=_EXT_GROUP_PREFIX + base_type.__name__, base_type=base_type
        )
        return mgr.get_default_instance(*args, **kwargs)

    @staticmethod
    def get_best_default_extension_by_type(
        base_type: Type[T], *args: Any, **kwargs: Any
    ) -> Optional[Tuple[T, str]]:
        """
        Get the best default extension instance for a given base type by priority.

        :param base_type: the base type/interface to get best default for
        :param args: positional arguments to pass to the factory constructor
        :param kwargs: keyword arguments to pass to the factory constructor
        :returns: best default extension instance or None if no default found
        """
        mgr = ExtensionManager.lazy_init(
            group=_EXT_GROUP_PREFIX + base_type.__name__, base_type=base_type
        )
        return mgr.get_best_default_instance(*args, **kwargs)

    @staticmethod
    def find_all_extensions_by_base_type(base_type: Type[T]) -> Dict[str, Type[T]]:
        """
        Find all plugin classes across all cached ExtensionManager instances that are
        compatible with the given base_type.

        :param base_type: the base type/interface to search for
        :returns: dictionary mapping plugin names to their classes
        """
        result: Dict[str, Type[T]] = {}

        # Create a snapshot of the cache to avoid iteration during modification
        with _EXT_MANAGER_LOCK:
            cache_snapshot = dict(_EXT_MANAGER_CACHE)

        for (cached_group, cached_base_type), mgr in cache_snapshot.items():
            # Check if this manager handles compatible types
            if cached_base_type == base_type or issubclass(cached_base_type, base_type):
                # Add all plugins from this manager
                for plugin_name, plugin_class in mgr._registry.items():
                    # Handle potential name conflicts by prefixing with group
                    if plugin_name in result:
                        # Use group-prefixed name to avoid conflicts
                        prefixed_name = f"{cached_group}:{plugin_name}"
                        result[prefixed_name] = cast(Type[T], plugin_class)
                    else:
                        result[plugin_name] = cast(Type[T], plugin_class)

        return result

    @staticmethod
    def find_all_extension_instances_by_base_type(
        base_type: Type[T], *args: Any, **kwargs: Any
    ) -> Dict[str, T]:
        """
        Find all plugin instances across all cached ExtensionManager instances that are
        compatible with the given base_type. Instances are cached within their respective managers.

        :param base_type: the base type/interface to search for
        :param args: positional arguments to pass to factory constructors (only used on first creation)
        :param kwargs: keyword arguments to pass to factory constructors (only used on first creation)
        :returns: dictionary mapping plugin names to their cached instances
        """
        result: Dict[str, T] = {}

        # Create a snapshot of the cache to avoid iteration during modification
        with _EXT_MANAGER_LOCK:
            cache_snapshot = dict(_EXT_MANAGER_CACHE)

        for (cached_group, cached_base_type), mgr in cache_snapshot.items():
            # Check if this manager handles compatible types
            if cached_base_type == base_type or issubclass(cached_base_type, base_type):
                # Add all plugin instances from this manager
                for plugin_name in mgr._registry.keys():
                    # Handle potential name conflicts by prefixing with group
                    if plugin_name in result:
                        # Use group-prefixed name to avoid conflicts
                        prefixed_name = f"{cached_group}:{plugin_name}"
                        result[prefixed_name] = mgr._get_or_create_extension_instance(
                            plugin_name, *args, **kwargs
                        )
                    else:
                        result[plugin_name] = mgr._get_or_create_extension_instance(
                            plugin_name, *args, **kwargs
                        )

        return result

    @staticmethod
    def get_all_extension_managers() -> Dict[
        tuple[str, Type[Any]], "ExtensionManager[Any]"
    ]:
        """
        Get a copy of all cached ExtensionManager instances.

        :returns: dictionary mapping (group, base_type) tuples to ExtensionManager instances
        """
        with _EXT_MANAGER_LOCK:
            return _EXT_MANAGER_CACHE.copy()

    @staticmethod
    @lru_cache(maxsize=None)
    def lazy_load_plugin_for_type(type_name: str) -> bool:
        """
        Import the entry-point whose name equals `type_name` in any
        'naylence.*' group. This triggers registration of plugin classes
        via their respective registration mechanisms.

        :param type_name: the plugin/extension name to search for and load
        :returns: True if a matching entry-point was found and loaded, False otherwise
        """
        try:
            eps = importlib.metadata.entry_points()
        except Exception:
            return False  # safe fallback – do nothing

        # Python 3.10+: EntryPoints supports `.select`; <3.10 returns list
        if hasattr(eps, "select"):
            candidates = eps
        else:
            candidates = eps  # type: ignore[assignment]

        for ep in candidates:
            if ep.group.startswith(_EXT_GROUP_PREFIX) and ep.name == type_name:
                try:
                    ep.load()  # side-effects register the plugin class
                    return True
                except Exception:
                    pass
                # Note: we continue searching in case there are multiple matches
                # across different groups, but return True after first successful load

        return False
