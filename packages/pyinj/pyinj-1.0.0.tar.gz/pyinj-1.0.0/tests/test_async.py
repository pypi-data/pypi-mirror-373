"""Async functionality and race condition tests."""

import asyncio
import pytest
from typing import Protocol, runtime_checkable

from pyinj import Container, Token, Scope, ResolutionError
from pyinj.protocols import SupportsAsyncClose


class MockAsyncResource:
    """Mock resource that supports async cleanup."""
    
    def __init__(self):
        self.value = "test"
        self.closed = False
    
    async def aclose(self) -> None:
        """Async cleanup."""
        self.closed = True


class TestAsyncResolution:
    """Test async dependency resolution."""

    @pytest.mark.asyncio
    async def test_async_provider_resolution(self):
        """Test resolving async providers."""
        container = Container()
        token = Token[str]("async_string")
        
        async def async_provider() -> str:
            await asyncio.sleep(0.001)  # Simulate async work
            return "async result"
        
        container.register(token, async_provider, Scope.TRANSIENT)
        
        result = await container.aget(token)
        assert result == "async result"

    @pytest.mark.asyncio
    async def test_sync_provider_in_async_context(self):
        """Test that sync providers work in async resolution."""
        container = Container()
        token = Token[str]("sync_string")
        
        def sync_provider() -> str:
            return "sync result"
        
        container.register(token, sync_provider, Scope.TRANSIENT)
        
        result = await container.aget(token)
        assert result == "sync result"

    def test_async_provider_in_sync_context_raises_error(self):
        """Test that async providers raise error in sync context."""
        container = Container()
        token = Token[str]("async_string")
        
        async def async_provider() -> str:
            return "async result"
        
        container.register(token, async_provider)
        
        with pytest.raises(ResolutionError) as exc_info:
            container.get(token)
        
        assert "Use aget() for async providers" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_async_singleton_creation(self):
        """Test that async singletons are created properly."""
        container = Container()
        token = Token[MockAsyncResource]("async_singleton")
        
        creation_count = 0
        
        async def create_resource() -> MockAsyncResource:
            nonlocal creation_count
            creation_count += 1
            await asyncio.sleep(0.001)  # Simulate async initialization
            return MockAsyncResource()
        
        container.register(token, create_resource, Scope.SINGLETON)
        
        # Resolve multiple times
        result1 = await container.aget(token)
        result2 = await container.aget(token)
        
        # Should be same instance
        assert result1 is result2
        # Should only be created once
        assert creation_count == 1

    @pytest.mark.asyncio
    async def test_async_singleton_race_condition(self):
        """Test that concurrent async singleton creation doesn't cause race conditions."""
        container = Container()
        token = Token[dict]("race_test")
        
        creation_count = 0
        
        async def create_resource() -> dict:
            nonlocal creation_count
            creation_count += 1
            # Simulate longer async work to increase chance of race
            await asyncio.sleep(0.01)
            return {"id": creation_count, "created_at": asyncio.get_running_loop().time()}
        
        container.register(token, create_resource, Scope.SINGLETON)
        
        # Launch many concurrent resolutions
        tasks = [container.aget(token) for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
        # All results should be the same instance
        first_result = results[0]
        for result in results:
            assert result is first_result
        
        # Factory should only be called once
        assert creation_count == 1
        assert first_result["id"] == 1

    @pytest.mark.asyncio
    async def test_mixed_async_sync_dependencies(self):
        """Test resolving mixed async and sync dependencies."""
        container = Container()
        
        sync_token = Token[str]("sync_dep")
        async_token = Token[str]("async_dep")
        combined_token = Token[dict]("combined")
        
        def sync_provider() -> str:
            return "sync_value"
        
        async def async_provider() -> str:
            await asyncio.sleep(0.001)
            return "async_value"
        
        async def combined_provider() -> dict:
            sync_val = container.get(sync_token)
            async_val = await container.aget(async_token)
            return {"sync": sync_val, "async": async_val}
        
        container.register(sync_token, sync_provider)
        container.register(async_token, async_provider)
        container.register(combined_token, combined_provider)
        
        result = await container.aget(combined_token)
        
        assert result == {"sync": "sync_value", "async": "async_value"}


class TestAsyncCleanup:
    """Test async resource cleanup."""

    @pytest.mark.asyncio
    async def test_async_resource_tracking(self):
        """Test that async resources are tracked for cleanup."""
        container = Container()
        token = Token[MockAsyncResource]("async_resource")
        
        def create_resource() -> MockAsyncResource:
            return MockAsyncResource()
        
        container.register(token, create_resource, Scope.SINGLETON)
        
        resource = container.get(token)
        assert not resource.closed
        
        # Dispose should close the resource
        await container.dispose()
        assert resource.closed

    @pytest.mark.asyncio
    async def test_dispose_multiple_async_resources(self):
        """Test disposing of multiple async resources."""
        container = Container()
        
        resources_created = []
        
        def create_resource() -> MockAsyncResource:
            resource = MockAsyncResource()
            resources_created.append(resource)
            return resource
        
        # Register multiple singleton resources
        for i in range(3):
            token = Token[MockAsyncResource](f"resource_{i}")
            container.register(token, create_resource, Scope.SINGLETON)
            container.get(token)  # Create the resources
        
        # All should be open
        assert len(resources_created) == 3
        for resource in resources_created:
            assert not resource.closed
        
        # Dispose should close all
        await container.dispose()
        
        for resource in resources_created:
            assert resource.closed

    @pytest.mark.asyncio
    async def test_dispose_with_cleanup_errors(self):
        """Test that dispose handles cleanup errors gracefully."""
        class ProblematicResource:
            def __init__(self):
                self.closed = False
            
            async def aclose(self) -> None:
                self.closed = True
                raise RuntimeError("Cleanup error!")
        
        container = Container()
        token = Token[ProblematicResource]("problematic")
        
        container.register(token, ProblematicResource, Scope.SINGLETON)
        resource = container.get(token)
        
        # Dispose should not raise even if cleanup fails
        await container.dispose()
        
        # Resource should still be marked as closed
        assert resource.closed

    @pytest.mark.asyncio
    async def test_dispose_clears_state(self):
        """Test that dispose clears container state."""
        container = Container()
        token = Token[str]("test")
        
        container.register(token, lambda: "test", Scope.SINGLETON)
        
        # Create singleton
        result1 = container.get(token)
        assert result1 == "test"
        
        # Dispose
        await container.dispose()
        
        # Singleton should be recreated
        result2 = container.get(token)
        assert result2 == "test"
        assert result1 is not result2  # Different instance after dispose


class TestAsyncInjection:
    """Test async dependency injection."""

    @pytest.mark.asyncio 
    async def test_inject_async_function(self):
        """Test injecting dependencies into async functions."""
        container = Container()
        
        class Service:
            def __init__(self, value: str):
                self.value = value
        
        service_token = Token[Service]("service", expected_type=Service)
        container.register(service_token, lambda: Service("injected"))
        
        @container.inject
        async def async_function(service: Service) -> str:
            await asyncio.sleep(0.001)
            return f"Result: {service.value}"
        
        result = await async_function()
        assert result == "Result: injected"

    @pytest.mark.asyncio
    async def test_async_circular_dependency_detection(self):
        """Test circular dependency detection in async context."""
        container = Container()
        token_a = Token[str]("async_A")
        token_b = Token[str]("async_B")
        
        async def provider_a() -> str:
            return await container.aget(token_b)
        
        async def provider_b() -> str:
            return await container.aget(token_a)
        
        container.register(token_a, provider_a)
        container.register(token_b, provider_b)
        
        with pytest.raises(ResolutionError):  # Should be CircularDependencyError
            await container.aget(token_a)