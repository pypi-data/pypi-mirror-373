"""PyInj - Production-Ready Dependency Injection for Python 3.13+

A type-safe, production-ready dependency injection container that provides:
- Thread-safe and async-safe resolution
- O(1) performance for type lookups  
- Circular dependency detection
- Automatic resource cleanup
- Protocol-based type safety
- Metaclass auto-registration

Quick Start:
    from pyinj import Container, Token, Scope
    
    # Create container
    container = Container()
    
    # Define token
    DB_TOKEN = Token[Database]("database")
    
    # Register provider
    container.register(DB_TOKEN, create_database, Scope.SINGLETON)
    
    # Resolve dependency
    db = container.get(DB_TOKEN)
    
    # Cleanup
    await container.dispose()
"""

from pyinj.core import Container
from pyinj.exceptions import CircularDependencyError, PyInjError, ResolutionError
from pyinj.metaclasses import Injectable
from pyinj.protocols import SupportsAsyncClose, SupportsClose
from pyinj.tokens import Scope, Token
from pyinj.types import AsyncProvider, Provider, ProviderFactory, SyncProvider

__version__ = "1.0.0"
__author__ = "Qrius Global"

__all__ = [
    # Core classes
    "Container",
    "Token",
    "Scope",
    "Injectable",
    # Protocols
    "SupportsClose",
    "SupportsAsyncClose",
    # Type aliases
    "Provider",
    "SyncProvider", 
    "AsyncProvider",
    "ProviderFactory",
    # Exceptions
    "PyInjError",
    "ResolutionError", 
    "CircularDependencyError",
]