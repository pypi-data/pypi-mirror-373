"""Protocol definitions for resource management and type checking."""

from typing import Protocol, runtime_checkable

__all__ = ["SupportsClose", "SupportsAsyncClose"]


@runtime_checkable
class SupportsClose(Protocol):
    """Protocol for resources that can be synchronously closed."""

    def close(self) -> None:
        """Close the resource synchronously."""
        ...


@runtime_checkable
class SupportsAsyncClose(Protocol):
    """Protocol for resources that can be asynchronously closed."""

    async def aclose(self) -> None:
        """Close the resource asynchronously."""
        ...