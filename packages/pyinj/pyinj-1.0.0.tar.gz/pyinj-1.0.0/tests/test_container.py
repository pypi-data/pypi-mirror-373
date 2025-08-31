"""Core container functionality tests."""

import pytest
from typing import Protocol, runtime_checkable

from pyinj import Container, Token, Scope, ResolutionError, CircularDependencyError


class TestBasicRegistration:
    """Test basic dependency registration and resolution."""

    def test_register_and_get_transient(self):
        """Test registering and resolving transient dependencies."""
        container = Container()
        token = Token[str]("test_string")
        
        container.register(token, lambda: "hello world", Scope.TRANSIENT)
        
        result1 = container.get(token)
        result2 = container.get(token)
        
        assert result1 == "hello world"
        assert result2 == "hello world"
        # Transient scope should create new instances
        assert result1 is not result2

    def test_register_and_get_singleton(self):
        """Test registering and resolving singleton dependencies."""
        container = Container()
        token = Token[list]("test_list")
        
        container.register(token, lambda: [], Scope.SINGLETON)
        
        result1 = container.get(token)
        result2 = container.get(token)
        
        assert result1 == []
        assert result2 == []
        # Singleton scope should return same instance
        assert result1 is result2

    def test_unregistered_token_raises_error(self):
        """Test that resolving unregistered token raises ResolutionError."""
        container = Container()
        token = Token[str]("nonexistent")
        
        with pytest.raises(ResolutionError) as exc_info:
            container.get(token)
        
        assert "No provider registered" in str(exc_info.value)
        assert "nonexistent" in str(exc_info.value)

    def test_token_validation(self):
        """Test that token validates returned instances."""
        container = Container()
        token = Token[str]("string_token", expected_type=str)
        
        # This should work
        container.register(token, lambda: "valid string")
        result = container.get(token)
        assert result == "valid string"
        
        # This should fail validation
        bad_token = Token[int]("int_token", expected_type=int)
        container.register(bad_token, lambda: "not an int")
        
        with pytest.raises(TypeError) as exc_info:
            container.get(bad_token)
        
        assert "Invalid type" in str(exc_info.value)

    def test_is_registered(self):
        """Test checking if tokens are registered."""
        container = Container()
        token1 = Token[str]("registered")
        token2 = Token[str]("not_registered")
        
        container.register(token1, lambda: "test")
        
        assert container.is_registered(token1) is True
        assert container.is_registered(token2) is False

    def test_get_scope(self):
        """Test retrieving scope of registered tokens."""
        container = Container()
        singleton_token = Token[str]("singleton")
        transient_token = Token[str]("transient")
        nonexistent_token = Token[str]("nonexistent")
        
        container.register(singleton_token, lambda: "test", Scope.SINGLETON)
        container.register(transient_token, lambda: "test", Scope.TRANSIENT)
        
        assert container.get_scope(singleton_token) == Scope.SINGLETON
        assert container.get_scope(transient_token) == Scope.TRANSIENT
        assert container.get_scope(nonexistent_token) is None


class TestCircularDependencies:
    """Test circular dependency detection."""

    def test_simple_circular_dependency(self):
        """Test detection of simple A -> B -> A circular dependency."""
        container = Container()
        token_a = Token[str]("A")
        token_b = Token[str]("B")
        
        container.register(token_a, lambda: container.get(token_b))
        container.register(token_b, lambda: container.get(token_a))
        
        with pytest.raises(CircularDependencyError) as exc_info:
            container.get(token_a)
        
        error_msg = str(exc_info.value)
        assert "Circular dependency" in error_msg
        assert "A" in error_msg and "B" in error_msg

    def test_complex_circular_dependency(self):
        """Test detection of A -> B -> C -> A circular dependency."""
        container = Container()
        token_a = Token[str]("A")
        token_b = Token[str]("B") 
        token_c = Token[str]("C")
        
        container.register(token_a, lambda: container.get(token_b))
        container.register(token_b, lambda: container.get(token_c))
        container.register(token_c, lambda: container.get(token_a))
        
        with pytest.raises(CircularDependencyError):
            container.get(token_a)

    def test_self_circular_dependency(self):
        """Test detection of self-referencing circular dependency."""
        container = Container()
        token = Token[str]("self_ref")
        
        container.register(token, lambda: container.get(token))
        
        with pytest.raises(CircularDependencyError):
            container.get(token)


class TestProtocolResolution:
    """Test protocol-based dependency resolution."""

    def test_protocol_resolution(self):
        """Test resolving dependencies by protocol."""
        @runtime_checkable
        class Greeter(Protocol):
            def greet(self) -> str: ...

        class FriendlyGreeter:
            def greet(self) -> str:
                return "Hello!"

        container = Container()
        token = Token[FriendlyGreeter](
            "friendly_greeter", 
            expected_type=FriendlyGreeter,
            protocol=Greeter
        )
        
        container.register(token, FriendlyGreeter)
        
        greeter = container.resolve_protocol(Greeter)
        assert greeter.greet() == "Hello!"
        assert isinstance(greeter, Greeter)

    def test_unresolved_protocol_raises_error(self):
        """Test that unresolved protocols raise ResolutionError."""
        @runtime_checkable
        class NonexistentProtocol(Protocol):
            def method(self) -> None: ...

        container = Container()
        
        with pytest.raises(ResolutionError) as exc_info:
            container.resolve_protocol(NonexistentProtocol)
        
        assert "No implementation" in str(exc_info.value)
        assert "NonexistentProtocol" in str(exc_info.value)


class TestOverrides:
    """Test dependency overrides for testing."""

    def test_override_dependency(self):
        """Test overriding a dependency with a specific value."""
        container = Container()
        token = Token[str]("test")
        
        container.register(token, lambda: "original")
        assert container.get(token) == "original"
        
        container.override(token, "overridden")
        assert container.get(token) == "overridden"

    def test_clear_overrides(self):
        """Test clearing all overrides."""
        container = Container()
        token1 = Token[str]("test1")
        token2 = Token[str]("test2")
        
        container.register(token1, lambda: "original1")
        container.register(token2, lambda: "original2")
        
        container.override(token1, "override1")
        container.override(token2, "override2")
        
        assert container.get(token1) == "override1"
        assert container.get(token2) == "override2"
        
        container.clear_overrides()
        
        assert container.get(token1) == "original1"
        assert container.get(token2) == "original2"


class TestTypeResolution:
    """Test type-based resolution."""

    def test_resolve_by_concrete_type(self):
        """Test resolving dependencies by concrete type."""
        container = Container()
        
        class Service:
            def __init__(self):
                self.value = 42
        
        token = Token[Service]("service", expected_type=Service)
        container.register(token, Service)
        
        resolved = container._resolve_type(Service)
        assert isinstance(resolved, Service)
        assert resolved.value == 42

    def test_resolve_token_type_hint(self):
        """Test resolving Token[T] type hints."""
        container = Container()
        
        class Database:
            def __init__(self):
                self.connected = True
        
        db_token = Token[Database]("database", expected_type=Database)
        container.register(db_token, Database)
        
        # This simulates what happens in auto-injection
        from typing import get_origin, get_args
        token_type = Token[Database]
        
        if get_origin(token_type) is Token:
            inner_type = get_args(token_type)[0]
            resolved = container._resolve_type(inner_type)
            assert isinstance(resolved, Database)
            assert resolved.connected is True

    def test_unresolved_type_raises_error(self):
        """Test that unresolved types raise ResolutionError."""
        container = Container()
        
        class UnregisteredService:
            pass
        
        with pytest.raises(ResolutionError) as exc_info:
            container._resolve_type(UnregisteredService)
        
        assert "Cannot resolve type" in str(exc_info.value)