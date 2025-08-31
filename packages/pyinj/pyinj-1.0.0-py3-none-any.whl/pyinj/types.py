"""Type definitions and aliases for pyinj."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, TypeAlias, Union

__all__ = ["Provider", "ProviderFactory", "SyncProvider", "AsyncProvider"]

# Type aliases for clarity
SyncProvider: TypeAlias = Callable[[], Any]
AsyncProvider: TypeAlias = Callable[[], Awaitable[Any]]
Provider: TypeAlias = Union[SyncProvider, AsyncProvider]
ProviderFactory: TypeAlias = Callable[..., Any]