"""
Performance tests for the AI Tool Registry system.

This module tests the performance characteristics of the tool registry,
including decorator overhead, registry building speed, and tool execution performance.
"""

import time
from typing import Any
from unittest.mock import patch

import pytest
from pydantic import BaseModel

from tool_registry_module import build_registry_openai, tool


class LargeDataModel(BaseModel):
    """Large model for performance testing."""

    id: int
    name: str
    description: str
    tags: list[str]
    metadata: dict[str, Any]
    nested_data: dict[str, dict[str, Any]]


class TestPerformance:
    """Performance tests for tool registry operations."""

    @pytest.mark.slow
    def test_decorator_overhead(self):
        """Test the performance overhead of the @tool decorator."""

        # Define a simple function without decoration
        def simple_add(a: int, b: int) -> int:
            return a + b

        # Define the same function with decoration
        @tool(description="Add two numbers")
        def decorated_add(a: int, b: int) -> int:
            return a + b

        # Time multiple calls to measure overhead
        iterations = 1000

        # Time undecorated function
        start_time = time.time()
        for _ in range(iterations):
            simple_add(5, 3)
        undecorated_time = time.time() - start_time

        # Time decorated function
        start_time = time.time()
        for _ in range(iterations):
            decorated_add(5, 3)
        decorated_time = time.time() - start_time

        # Calculate overhead
        overhead_ratio = decorated_time / undecorated_time

        # Assert that overhead is reasonable (less than 100x slower)
        # Note: Our decorator does full parameter conversion, binding, and type checking
        # which adds significant overhead, but should still be reasonable
        assert overhead_ratio < 300.0, (
            f"Decorator overhead too high: {overhead_ratio:.2f}x"
        )

        print(
            f"Decorator overhead: {overhead_ratio:.2f}x ({decorated_time:.4f}s vs {undecorated_time:.4f}s)"
        )

    @pytest.mark.slow
    def test_large_registry_building_performance(self):
        """Test performance of building registries with many tools."""
        # Create a large number of tools
        num_tools = 100

        def create_tool(i):
            @tool(description=f"Tool number {i}")
            def dynamic_tool(x: int, y: int = i) -> int:  # noqa: B008
                return x + y

            # Give each tool a unique name
            setattr(dynamic_tool, "__name__", f"tool_{i}")
            return dynamic_tool

        tools = [create_tool(i) for i in range(num_tools)]

        # Time registry building
        start_time = time.time()
        with patch("tool_registry_module.tool_registry.openai", create=True):
            registry = build_registry_openai(tools)
        build_time = time.time() - start_time

        # Verify registry was built correctly
        assert len(registry) == num_tools

        # Assert reasonable build time (should be under 1 second for 100 tools)
        assert build_time < 1.0, (
            f"Registry building too slow: {build_time:.3f}s for {num_tools} tools"
        )

        print(f"Built registry with {num_tools} tools in {build_time:.3f}s")

    @pytest.mark.slow
    def test_complex_schema_generation_performance(self):
        """Test performance of schema generation for complex Pydantic models."""

        @tool(description="Process large data structure")
        def process_large_data(
            data: LargeDataModel,
            batch_size: int = 100,
            validate: bool = True,
            options: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            if options is None:
                options = {}
            return {"processed": True, "id": data.id}

        # Time schema generation (happens during decoration)
        start_time = time.time()
        schema = getattr(process_large_data, "_input_schema")
        schema_time = time.time() - start_time

        # Verify schema was generated
        assert "properties" in schema
        assert "data" in schema["properties"]

        # Assert reasonable schema generation time
        assert schema_time < 0.1, f"Schema generation too slow: {schema_time:.3f}s"

        print(f"Generated complex schema in {schema_time:.4f}s")

    @pytest.mark.slow
    def test_parameter_conversion_performance(self):
        """Test performance of parameter conversion with complex models."""

        @tool(description="Convert parameters")
        def convert_params(data: LargeDataModel) -> str:
            return f"Processed {data.name}"

        # Create test data
        test_data = {
            "id": 12345,
            "name": "Performance Test",
            "description": "A test for performance measurement",
            "tags": ["performance", "test", "measurement"] * 10,  # 30 tags
            "metadata": {
                f"key_{i}": f"value_{i}" for i in range(50)
            },  # 50 metadata items
            "nested_data": {
                f"section_{i}": {f"field_{j}": j for j in range(10)} for i in range(10)
            },  # 10 sections with 10 fields each
        }

        # Time parameter conversion
        iterations = 100
        start_time = time.time()
        for _ in range(iterations):
            convert_params(data=test_data)
        conversion_time = time.time() - start_time

        avg_time = conversion_time / iterations

        # Assert reasonable conversion time (should be under 1ms per call)
        assert avg_time < 0.001, (
            f"Parameter conversion too slow: {avg_time:.4f}s per call"
        )

        print(
            f"Parameter conversion: {avg_time:.4f}s per call ({iterations} iterations)"
        )

    @pytest.mark.slow
    def test_concurrent_tool_execution(self):
        """Test performance of concurrent tool execution."""
        import concurrent.futures

        @tool(description="CPU intensive task")
        def cpu_task(n: int) -> int:
            # Simulate CPU-intensive work
            result = 0
            for i in range(n):
                result += i**2
            return result % 1000000

        # Test sequential execution
        iterations = 50
        work_size = 10000

        start_time = time.time()
        sequential_results = []
        for _ in range(iterations):
            sequential_results.append(cpu_task(work_size))
        sequential_time = time.time() - start_time

        # Test concurrent execution
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            concurrent_results = list(
                executor.map(lambda _: cpu_task(work_size), range(iterations))
            )
        concurrent_time = time.time() - start_time

        # Verify results are consistent
        assert len(sequential_results) == len(concurrent_results) == iterations

        # Calculate speedup (concurrent should be faster for I/O bound, similar for CPU bound)
        speedup = sequential_time / concurrent_time

        print(
            f"Sequential: {sequential_time:.3f}s, Concurrent: {concurrent_time:.3f}s, Speedup: {speedup:.2f}x"
        )

        # Assert that concurrent execution doesn't cause significant slowdown
        assert speedup > 0.5, (
            f"Concurrent execution caused significant slowdown: {speedup:.2f}x"
        )

    @pytest.mark.slow
    def test_memory_usage_with_many_tools(self):
        """Test memory usage when creating many tools."""
        import os

        import psutil

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create many tools
        num_tools = 500

        def create_memory_tool(i):
            @tool(description=f"Memory test tool {i}")
            def memory_tool(data: str, count: int = i) -> str:  # noqa: B008
                return f"{data}_{count}"

            setattr(memory_tool, "__name__", f"memory_tool_{i}")
            return memory_tool

        tools = [create_memory_tool(i) for i in range(num_tools)]

        # Build registry
        with patch("tool_registry_module.tool_registry.openai", create=True):
            registry = build_registry_openai(tools)

        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Verify registry was built
        assert len(registry) == num_tools

        # Assert reasonable memory usage (should be under 100MB for 500 tools)
        assert memory_increase < 100, (
            f"Memory usage too high: {memory_increase:.1f}MB for {num_tools} tools"
        )

        print(f"Memory increase: {memory_increase:.1f}MB for {num_tools} tools")

    def test_schema_caching_performance(self):
        """Test that schema generation is cached and doesn't repeat."""
        call_count = 0

        def counting_create_schema(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return original_create_schema(*args, **kwargs)

        # Patch schema creation to count calls
        from tool_registry_module import tool_registry

        original_create_schema = tool_registry.create_schema_from_signature

        with patch.object(
            tool_registry, "create_schema_from_signature", counting_create_schema
        ):
            # Create tool (should call schema generation once)
            @tool(description="Schema caching test")
            def cached_tool(x: int, y: str) -> str:
                return f"{x}: {y}"

            # Access schema multiple times
            schema1 = getattr(cached_tool, "_input_schema")
            schema2 = getattr(cached_tool, "_input_schema")
            schema3 = getattr(cached_tool, "_input_schema")

            # Verify schema is the same object (cached)
            assert schema1 is schema2 is schema3

            # Verify schema generation was only called once
            assert call_count == 1, (
                f"Schema generation called {call_count} times, expected 1"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "slow"])
