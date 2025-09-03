from __future__ import annotations

from collections import defaultdict
import importlib.metadata as metadata
from typing import (
    Any,
    Dict,
    Generic,
    Optional,
    Type,
    TypeVar,
    overload,
)

from pydantic import BaseModel

from .extension_manager import ExtensionManager
from .resource_config import ResourceConfig

from .resource_factory import ResourceFactory

# Type variables for resource and config types
T_co = TypeVar("T_co", covariant=True)
C_contra = TypeVar("C_contra")

# F is a factory producing T_co from config C_contra
F = TypeVar("F", bound=ResourceFactory[Any, Any])

# ─── Global registry: iface → (type_name → factory instance) ──────────────────
_factory_registry: Dict[
    Type[ResourceFactory[Any, Any]], Dict[str, ResourceFactory[Any, Any]]
] = {}

# ─── Config model registry keyed by interface name ────────────────────────────
_config_models: Dict[str, Dict[str, Type[BaseModel]]] = {}

_model_to_type: Dict[str, Dict[Type[BaseModel], str]] = defaultdict(dict)

M = TypeVar("M", bound=BaseModel)


def register_factory(
    iface: Type[ResourceFactory[T_co, C_contra]],
    factory: ResourceFactory[T_co, C_contra],
    resource_type: Optional[str] = None,
) -> None:
    """
    Register a factory under its interface.
    iface = ConnectorFactory or AuthorizerFactory, etc.
    factory.type is its discriminator string.
    """
    type_name = resource_type or getattr(factory, "type", None)
    if not type_name:
        raise ValueError(
            "Either 'resource_type' must be provided or factory must have a 'type' attribute"
        )
    _factory_registry.setdefault(iface, {})[type_name] = factory


def get_composite_factory(
    iface: Type[ResourceFactory[T_co, C_contra]],
) -> ResourceFactory[T_co, C_contra]:
    """
    Returns a composite ResourceFactory which dispatches to the
    registered implementations based on config.type.
    """
    return CompositeFactory(iface)


def load_entrypoint_factories(
    iface: Type[ResourceFactory[Any, Any]], group: str
) -> None:
    """
    Discovers all entry-points under `group`, loads them, instantiates
    and registers each under the given iface.
    """
    eps = metadata.entry_points().select(group=group)
    for ep in eps:
        try:
            factory_cls = ep.load()
            factory = factory_cls()
            register_factory(iface, factory)
        except Exception as e:
            import logging

            logging.getLogger(__name__).warning(
                f"Could not load factory {ep.name!r}: {e}"
            )


T1 = TypeVar("T1")  # the resource we're building
C1 = TypeVar("C1")  # any config class


@overload
async def create_resource(  # type: ignore
    iface: Type[ResourceFactory[T1, C1]], config: C1, **kwargs: Any
) -> T1: ...


# @overload
# async def create_resource(
#     iface: Type[ResourceFactory[T1, C1]], config: None, **kwargs: Any
# ) -> Optional[T1]: ...


async def create_resource(  # type: ignore
    iface: Type[ResourceFactory[T1, Any]],
    config: Optional[ResourceConfig | dict[str, Any]],
    **kwargs: Any,
) -> Optional[T1]:
    if config is None:
        return None

    type = None
    if isinstance(config, dict):
        type = config.get("type")
    elif isinstance(config, ResourceConfig):
        type = getattr(config, "type", None)

    if not type:
        raise ValueError(f"Config {config!r} does not have a 'type' attribute")

    extension: ResourceFactory = ExtensionManager.get_extension_by_name_and_type(
        name=type, base_type=iface
    )

    typed_config = ResourceConfig.model_validate(config, by_alias=True)
    return await extension.create(typed_config, **kwargs)


async def create_default_resource(
    iface: Type[ResourceFactory[T1, Any]],
    config: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> Optional[T1]:
    """
    Create a resource using the best available default implementation for the given interface.
    Uses priority-based selection if available, falling back to legacy single-default behavior.

    :param iface: the resource factory interface
    :param config: optional configuration (without 'type' field)
    :param kwargs: additional keyword arguments
    :returns: resource instance using best default implementation, or None if no default
    """
    # Try priority-based selection first
    try:
        ext = ExtensionManager.get_best_default_extension_by_type(iface, **kwargs)
    except AttributeError:
        # Fall back to legacy single-default behavior if new method not available
        ext = ExtensionManager.get_default_extension_by_type(iface, **kwargs)

    if ext is None:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"default_resource_factory_not_found_for_type_{iface.__name__}")
        return None

    default_factory = ext[0]
    instance_type = ext[1]
    # Merge config with default type
    final_config = config or {}
    if isinstance(final_config, dict):
        final_config = final_config.copy()
        final_config.setdefault("type", instance_type)

    return await default_factory.create(final_config, **kwargs)


class CompositeFactory(Generic[T_co, C_contra], ResourceFactory[T_co, C_contra]):
    """
    Composite ResourceFactory which dispatches to the
    registered implementations based on config.type,
    and validates config.params against any registered BaseModel.
    """

    def __init__(self, iface: Type[ResourceFactory[T_co, Any]]) -> None:
        self.iface = iface
        self.iface_name = iface.__name__
        self.type = f"composite-{self.iface_name}"

    async def create(
        self, config: Optional[C_contra | dict[str, Any]] = None, **kwargs: Any
    ) -> T_co:
        if not config:
            raise ValueError(f"Missing config {self.iface_name}")

        type = None
        if isinstance(config, dict):
            type = config.get("type")
        elif isinstance(config, ResourceConfig):
            type = getattr(config, "type", None)

        if not type:
            raise ValueError(f"Config {config!r} does not have a 'type' attribute")

        extension: ResourceFactory = ExtensionManager.get_extension_by_name_and_type(
            name=type, base_type=self.iface
        )

        typed_config = ResourceConfig.model_validate(config, by_alias=True)
        return await extension.create(typed_config, **kwargs)


def get_factory(
    iface: Type[ResourceFactory[T_co, C_contra]], name: str
) -> ResourceFactory[T_co, C_contra]:
    """
    Look up the factory of interface `iface` with discriminator `name`.
    """
    return ExtensionManager.get_extension_by_name_and_type(name=name, base_type=iface)
