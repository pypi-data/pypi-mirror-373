from __future__ import annotations

from typing import Any, Generic, Optional, Protocol, TypeVar

T = TypeVar("T", covariant=True)
C = TypeVar("C", contravariant=True)


class ResourceFactory(Protocol, Generic[T, C]):
    """
    A generic factory interface.
    T = the thing you're building (connector, store, client, etc.)
    C = config type (often a pydantic model)
    """

    # type: str
    is_default: bool = False  # Mark factory as default implementation
    priority: int = 0  # Priority for default selection (higher values win)

    async def create(
        self, config: Optional[C | dict[str, Any]] = None, **kwargs: Any
    ) -> T:
        """
        Given a config of type C, produce or raise for resource of type T.
        """
        ...
