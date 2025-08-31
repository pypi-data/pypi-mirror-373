"""Token and scope definitions for pyinj dependency injection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Generic, Optional, Protocol, Type, TypeVar

__all__ = ["Token", "Scope"]

T = TypeVar("T")


class Scope(Enum):
    """Defines the lifecycle scope of a dependency."""

    SINGLETON = auto()
    """One instance per container, created once and reused."""

    TRANSIENT = auto()
    """New instance created for every resolution."""

    REQUEST = auto()
    """One instance per request context (web applications)."""

    SESSION = auto()
    """One instance per session context."""


@dataclass(frozen=True, slots=True)
class Token(Generic[T]):
    """Type-safe token for identifying dependencies.
    
    A token uniquely identifies a dependency in the container and carries
    type information to ensure type safety at runtime.
    """

    name: str
    """Unique name for this token."""

    expected_type: Optional[Type[T]] = None
    """The expected concrete type for this dependency."""

    protocol: Optional[Type[Protocol]] = None
    """The expected protocol this dependency should implement."""

    def __hash__(self) -> int:
        """Hash based on name for use in dictionaries."""
        return hash(self.name)

    def __str__(self) -> str:
        """String representation showing name and type info."""
        type_info = ""
        if self.expected_type:
            type_info = f"[{self.expected_type.__name__}]"
        elif self.protocol:
            type_info = f"[{self.protocol.__name__}]"
        return f"Token({self.name}{type_info})"

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (
            f"Token(name={self.name!r}, "
            f"expected_type={self.expected_type}, "
            f"protocol={self.protocol})"
        )

    def validate(self, instance: Any) -> bool:
        """Validate that an instance matches this token's type expectations.
        
        Args:
            instance: The instance to validate
            
        Returns:
            True if the instance is valid for this token
        """
        # Check protocol compliance first
        if self.protocol and hasattr(self.protocol, "__runtime_checkable__"):
            return isinstance(instance, self.protocol)

        # Check concrete type
        if self.expected_type:
            return isinstance(instance, self.expected_type)

        # No type constraints, any instance is valid
        return True