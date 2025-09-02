"""Contextual abstractions for dependency injection using contextvars."""

from __future__ import annotations

import asyncio
from collections import ChainMap
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from contextvars import Token as ContextToken
from types import MappingProxyType
from typing import Any, TypeVar
from weakref import WeakValueDictionary

from .tokens import Scope, Token

__all__ = [
    "ContextualContainer",
    "RequestScope",
    "SessionScope",
    "get_current_context",
    "set_context",
]

T = TypeVar("T")

# Global context variable for DI scopes
_context_stack: ContextVar[ChainMap | None] = ContextVar(
    "pyinj_context_stack", default=None
)

# Session context for longer-lived dependencies
_session_context: ContextVar[dict[Token, Any] | None] = ContextVar(
    "pyinj_session_context", default=None
)


def get_current_context() -> MappingProxyType | None:
    """
    Get current dependency context as read-only view.

    Returns:
        Read-only mapping of current context or None
    """
    context = _context_stack.get()
    if context is not None:
        return MappingProxyType(context)
    return None


def set_context(context: ChainMap) -> ContextToken:
    """
    Set the current dependency context.

    Args:
        context: ChainMap of dependency caches

    Returns:
        Token for resetting context
    """
    return _context_stack.set(context)


class ContextualContainer:
    """
    Container with contextual scope support using contextvars.

    Provides Scala-inspired implicit context propagation that
    automatically flows through async calls.
    """

    def __init__(self) -> None:
        """Initialize contextual container."""
        # Singleton cache (process-wide)
        self._singletons: dict[Token, Any] = {}

        # Weak cache for transients (auto-cleanup)
        self._transients: WeakValueDictionary = WeakValueDictionary()

        # Providers registry
        self._providers: dict[Token, Any] = {}

        # Async locks for thread-safe singleton creation
        self._async_locks: dict[Token, asyncio.Lock] = {}

        # Track resources for cleanup
        self._resources: list[Any] = []

        # Scope manager (RAII contexts, precedence enforcement)
        self._scope_manager = ScopeManager(self)

    def _put_in_current_request_cache(self, token: Token[T], instance: T) -> None:
        """Insert a value into the current request cache unconditionally.

        This bypasses scope checks and is intended for temporary overrides
        that should only affect the current context.
        """
        context = _context_stack.get()
        if context and hasattr(context, "maps") and context.maps:
            context.maps[0][token] = instance

    @contextmanager
    def request_scope(self) -> Iterator[ContextualContainer]:
        """
        Create a new request scope (like FastAPI's request lifecycle).

        Example:
            with container.request_scope():
                # All dependencies resolved here are request-scoped
                service = container.get(ServiceToken)

        Yields:
            Self for chaining
        """
        with self._scope_manager.request_scope():
            yield self

    @asynccontextmanager
    async def async_request_scope(self) -> AsyncIterator[ContextualContainer]:
        """
        Async context manager for request scopes.

        Example:
            async with container.async_request_scope():
                service = await container.aget(ServiceToken)
        """
        async with self._scope_manager.async_request_scope():
            yield self

    @contextmanager
    def session_scope(self) -> Iterator[ContextualContainer]:
        """
        Create a session scope (longer-lived than request).

        Session scopes persist across multiple requests but are
        isolated between different sessions (e.g., users).
        """
        with self._scope_manager.session_scope():
            yield self

    def _cleanup_scope(self, cache: dict[Token, Any]) -> None:
        """
        Clean up resources in LIFO order.

        Args:
            cache: Cache of resources to clean up
        """
        for resource in reversed(list(cache.values())):
            try:
                if hasattr(resource, "close"):
                    resource.close()
                elif hasattr(resource, "__exit__"):
                    resource.__exit__(None, None, None)
            except Exception:
                # Log but don't fail cleanup
                pass

    async def _async_cleanup_scope(self, cache: dict[Token, Any]) -> None:
        """
        Async cleanup of resources.

        Args:
            cache: Cache of resources to clean up
        """
        tasks = []

        for resource in reversed(list(cache.values())):
            if hasattr(resource, "aclose"):
                tasks.append(resource.aclose())
            elif hasattr(resource, "__aexit__"):
                tasks.append(resource.__aexit__(None, None, None))
            elif hasattr(resource, "close"):
                # Sync cleanup in executor
                loop = asyncio.get_event_loop()
                tasks.append(loop.run_in_executor(None, resource.close))

        if tasks:
            # Gather with return_exceptions to prevent one failure from stopping others
            await asyncio.gather(*tasks, return_exceptions=True)

    def resolve_from_context(self, token: Token[T]) -> T | None:
        """
        Resolve dependency from current context.

        Args:
            token: Token to resolve

        Returns:
            Resolved instance or None if not in context
        """
        return self._scope_manager.resolve_from_context(token)

    def store_in_context(self, token: Token[T], instance: T) -> None:
        """
        Store instance in appropriate context.

        Args:
            token: Token for the instance
            instance: Instance to store
        """
        self._scope_manager.store_in_context(token, instance)

    def clear_request_context(self) -> None:
        """Clear current request context."""
        self._scope_manager.clear_request_context()

    def clear_session_context(self) -> None:
        """Clear current session context."""
        self._scope_manager.clear_session_context()

    def clear_all_contexts(self) -> None:
        """Clear all contexts including singletons."""
        self._scope_manager.clear_all_contexts()


class ScopeManager:
    """Scope orchestration with RAII managers and explicit precedence.

    Precedence: REQUEST > SESSION > SINGLETON. Uses ContextVars for async safety.
    """

    def __init__(self, container: ContextualContainer) -> None:
        self._container = container

    @contextmanager
    def request_scope(self) -> Iterator[None]:
        request_cache: dict[Token, Any] = {}
        current = _context_stack.get()
        if current is None:
            new_context = ChainMap(request_cache, self._container._singletons)
        else:
            new_context = ChainMap(request_cache, current)
        token = _context_stack.set(new_context)
        try:
            yield
        finally:
            self._container._cleanup_scope(request_cache)
            _context_stack.reset(token)

    @asynccontextmanager
    async def async_request_scope(self) -> AsyncIterator[None]:
        request_cache: dict[Token, Any] = {}
        current = _context_stack.get()
        if current is None:
            new_context = ChainMap(request_cache, self._container._singletons)
        else:
            new_context = ChainMap(request_cache, current)
        token = _context_stack.set(new_context)
        try:
            yield
        finally:
            await self._container._async_cleanup_scope(request_cache)
            _context_stack.reset(token)

    @contextmanager
    def session_scope(self) -> Iterator[None]:
        session_cache = _session_context.get()
        if session_cache is None:
            session_cache = {}
            session_token = _session_context.set(session_cache)
        else:
            session_token = None
        current = _context_stack.get()
        if current is None:
            new_context = ChainMap(session_cache, self._container._singletons)
        else:
            new_context = ChainMap(current.maps[0], session_cache, self._container._singletons)
        context_token = _context_stack.set(new_context)
        try:
            yield
        finally:
            _context_stack.reset(context_token)
            if session_token:
                _session_context.reset(session_token)

    def resolve_from_context(self, token: Token[T]) -> T | None:
        context = _context_stack.get()
        if context and token in context:
            return context[token]
        if token.scope == Scope.SESSION:
            session = _session_context.get()
            if session and token in session:
                return session[token]
        if token.scope == Scope.SINGLETON and token in self._container._singletons:
            return self._container._singletons[token]
        if token.scope == Scope.TRANSIENT and token in self._container._transients:
            return self._container._transients[token]
        return None

    def store_in_context(self, token: Token[T], instance: T) -> None:
        if token.scope == Scope.SINGLETON:
            self._container._singletons[token] = instance
        elif token.scope == Scope.REQUEST:
            self._container._put_in_current_request_cache(token, instance)
        elif token.scope == Scope.SESSION:
            session = _session_context.get()
            if session is not None:
                session[token] = instance
        elif token.scope == Scope.TRANSIENT:
            try:
                self._container._transients[token] = instance
            except TypeError:
                pass

    def clear_request_context(self) -> None:
        context = _context_stack.get()
        if context and hasattr(context, "maps") and context.maps:
            context.maps[0].clear()

    def clear_session_context(self) -> None:
        session = _session_context.get()
        if session is not None:
            session.clear()

    def clear_all_contexts(self) -> None:
        self._container._singletons.clear()
        self._container._transients.clear()
        self.clear_request_context()
        self.clear_session_context()


class RequestScope:
    """
    Helper class for request-scoped dependencies.

    Example:
        async with RequestScope(container) as scope:
            service = scope.resolve(ServiceToken)
    """

    def __init__(self, container: ContextualContainer):
        """Initialize request scope."""
        self.container = container
        self._context_manager = None
        self._async_context_manager = None

    def __enter__(self) -> RequestScope:
        """Enter request scope."""
        self._context_manager = self.container.request_scope()
        self._context_manager.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit request scope."""
        if self._context_manager:
            self._context_manager.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self) -> RequestScope:
        """Async enter request scope."""
        self._async_context_manager = self.container.async_request_scope()
        await self._async_context_manager.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async exit request scope."""
        if self._async_context_manager:
            await self._async_context_manager.__aexit__(exc_type, exc_val, exc_tb)

    def resolve(self, token: Token[T]) -> T | None:
        """Resolve dependency in this scope."""
        return self.container.resolve_from_context(token)


class SessionScope:
    """
    Helper class for session-scoped dependencies.

    Example:
        with SessionScope(container) as scope:
            user = scope.resolve(UserToken)
    """

    def __init__(self, container: ContextualContainer):
        """Initialize session scope."""
        self.container = container
        self._context_manager = None

    def __enter__(self) -> SessionScope:
        """Enter session scope."""
        self._context_manager = self.container.session_scope()
        self._context_manager.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit session scope."""
        if self._context_manager:
            self._context_manager.__exit__(exc_type, exc_val, exc_tb)
