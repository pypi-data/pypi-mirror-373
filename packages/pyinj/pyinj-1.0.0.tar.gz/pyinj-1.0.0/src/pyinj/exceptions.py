"""Exception classes for pyinj dependency injection container."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from pyinj.tokens import Token

__all__ = ["PyInjError", "ResolutionError", "CircularDependencyError"]


class PyInjError(Exception):
    """Base exception for all pyinj errors."""


class ResolutionError(PyInjError):
    """Raised when a dependency cannot be resolved."""

    def __init__(self, token: Token, chain: List[Token], cause: str) -> None:
        """Initialize resolution error with context.
        
        Args:
            token: The token that couldn't be resolved
            chain: The current resolution chain  
            cause: Human-readable cause description
        """
        self.token = token
        self.chain = chain
        self.cause = cause
        
        chain_str = " -> ".join(t.name for t in chain) if chain else "root"
        super().__init__(
            f"Cannot resolve token '{token.name}':\n"
            f"  Resolution chain: {chain_str}\n"
            f"  Cause: {cause}"
        )


class CircularDependencyError(ResolutionError):
    """Raised when a circular dependency is detected during resolution."""

    def __init__(self, token: Token, chain: List[Token]) -> None:
        """Initialize circular dependency error.
        
        Args:
            token: The token that created the cycle
            chain: The resolution chain showing the cycle
        """
        super().__init__(
            token,
            chain,
            f"Circular dependency detected: {' -> '.join(t.name for t in chain)} -> {token.name}"
        )