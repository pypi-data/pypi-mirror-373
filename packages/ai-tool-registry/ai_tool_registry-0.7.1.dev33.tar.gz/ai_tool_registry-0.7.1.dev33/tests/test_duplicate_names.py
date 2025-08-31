"""
Tests for duplicate function name detection in tool registry.

This module tests that the registry properly detects and prevents duplicate tool names.
"""

from unittest.mock import patch

import pytest

from tool_registry_module import ToolRegistryError, build_registry_openai, tool


def test_duplicate_function_names_raise_error():
    """Test that duplicate function names raise an error."""

    @tool(description="First function")
    def my_function(x: int) -> int:
        return x * 2

    @tool(description="Second function with same name")
    def my_function_2(y: int) -> int:  # Different actual name
        return y * 3

    # Manually set the same name to simulate the duplicate issue
    setattr(my_function_2, "__name__", "my_function")
    # Also need to update the _original_func name
    setattr(my_function_2, "_original_func", lambda: None)
    getattr(my_function_2, "_original_func").__name__ = "my_function"

    with patch("tool_registry_module.tool_registry.openai", create=True):
        with pytest.raises(
            ToolRegistryError, match="Duplicate tool name 'my_function' found"
        ):
            build_registry_openai([my_function, my_function_2])


def test_different_function_names_work():
    """Test that different function names work fine."""

    @tool(description="First function")
    def function_one(x: int) -> int:
        return x * 2

    @tool(description="Second function")
    def function_two(y: int) -> int:
        return y * 3

    with patch("tool_registry_module.tool_registry.openai", create=True):
        registry = build_registry_openai([function_one, function_two])

        assert len(registry) == 2
        assert "function_one" in registry
        assert "function_two" in registry


def test_performance_test_scenario_fails():
    """Test that the problematic performance test scenario fails as expected."""

    tools = []

    # This mimics what the performance test was doing wrong
    for i in range(5):  # Small number for test speed

        @tool(description=f"Tool number {i}")
        def dynamic_tool(x: int, y: int = i) -> int:  # noqa: B008
            return x + y

        # This is the problematic part - all functions get the same name
        setattr(dynamic_tool, "__name__", "dynamic_tool")  # Same name for all!
        tools.append(dynamic_tool)

    with patch("tool_registry_module.tool_registry.openai", create=True):
        with pytest.raises(
            ToolRegistryError, match="Duplicate tool name 'dynamic_tool' found"
        ):
            build_registry_openai(tools)


def test_correct_way_to_create_multiple_tools():
    """Test the correct way to create multiple similar tools."""

    def create_tool(i):
        @tool(description=f"Tool number {i}")
        def tool_func(x: int, y: int = i) -> int:  # noqa: B008
            return x + y

        # Give each tool a unique name
        setattr(tool_func, "__name__", f"tool_{i}")
        return tool_func

    tools = [create_tool(i) for i in range(5)]

    with patch("tool_registry_module.tool_registry.openai", create=True):
        registry = build_registry_openai(tools)

        assert len(registry) == 5
        for i in range(5):
            assert f"tool_{i}" in registry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
