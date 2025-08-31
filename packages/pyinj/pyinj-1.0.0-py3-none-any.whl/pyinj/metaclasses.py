"""Metaclass support for automatic dependency registration."""

from __future__ import annotations

from abc import ABCMeta
from typing import Any, ClassVar, Dict, Type

from pyinj.tokens import Scope, Token

__all__ = ["Injectable"]


class Injectable(ABCMeta):
    """Metaclass for automatic dependency registration.
    
    Classes using this metaclass can be automatically registered in
    the container by setting class attributes:
    
    Example:
        class DatabaseService(metaclass=Injectable):
            __injectable__ = True
            __token_name__ = "database" 
            __scope__ = Scope.SINGLETON
    """

    _registry: ClassVar[Dict[Type, Token]] = {}

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> Injectable:
        """Create a new class and optionally register it for injection.
        
        Args:
            name: The class name
            bases: Base classes
            namespace: Class namespace dictionary
            **kwargs: Additional keyword arguments
            
        Returns:
            The newly created class
        """
        cls = super().__new__(mcs, name, bases, namespace)

        # Only register if explicitly marked as injectable
        if namespace.get("__injectable__", False):
            token_name = namespace.get("__token_name__", name.lower())
            scope = namespace.get("__scope__", Scope.TRANSIENT)

            # Create type-safe token
            token = Token[cls](  # type: ignore[valid-type]
                name=token_name,
                expected_type=cls,
            )

            # Store in registry
            mcs._registry[cls] = token

            # Add metadata to class
            cls.__token__ = token  # type: ignore[attr-defined]
            cls.__scope__ = scope  # type: ignore[attr-defined]

        return cls

    @classmethod
    def get_registry(mcs) -> Dict[Type, Token]:
        """Get a copy of the injection registry.
        
        Returns:
            Dictionary mapping class types to their tokens
        """
        return mcs._registry.copy()