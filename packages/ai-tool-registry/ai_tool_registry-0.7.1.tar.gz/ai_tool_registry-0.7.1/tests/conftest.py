"""
Pytest configuration and fixtures for tool registry tests.

This module provides common fixtures and configuration for all test modules.
"""

from typing import Any

import pytest
from pydantic import BaseModel


# Test fixtures
class SimpleUser(BaseModel):
    """Simple test user model."""

    name: str
    age: int
    email: str = "test@example.com"


@pytest.fixture
def sample_user():
    """Provide a sample user for testing."""
    return SimpleUser(name="Test User", age=30)


@pytest.fixture
def sample_user_dict():
    """Provide a sample user dictionary for testing."""
    return {"name": "Dict User", "age": 25, "email": "dict@example.com"}


@pytest.fixture
def simple_tools():
    """Create a set of simple test tools."""
    from tool_registry_module import tool

    @tool(description="Add two numbers")
    def add(a: int, b: int) -> int:
        """Add two integers."""
        return a + b

    @tool(description="Concatenate strings")
    def concat(x: str, y: str, separator: str = " ") -> str:
        """Concatenate two strings with optional separator."""
        return f"{x}{separator}{y}"

    @tool(description="Calculate square")
    def square(number: float) -> float:
        """Calculate the square of a number."""
        return number**2

    return [add, concat, square]


@pytest.fixture
def complex_tools():
    """Create a set of complex test tools with Pydantic models."""
    from tool_registry_module import tool

    @tool(description="Process user data")
    def process_user(user: SimpleUser, active: bool = True) -> dict[str, Any]:
        """Process user data and return summary."""
        return {
            "name": user.name,
            "age": user.age,
            "email": user.email,
            "is_active": active,
            "can_vote": user.age >= 18,
        }

    @tool(description="Batch process users", ignore_in_schema=["debug"])
    def batch_process(
        users: list[SimpleUser], batch_size: int = 10, debug: bool = False
    ) -> dict[str, Any]:
        """Process multiple users in batches."""
        if debug:
            print(f"Processing {len(users)} users in batches of {batch_size}")

        return {
            "total_users": len(users),
            "batch_size": batch_size,
            "batches_needed": (len(users) + batch_size - 1) // batch_size,
        }

    return [process_user, batch_process]


@pytest.fixture
def invalid_functions():
    """Create functions that are not decorated with @tool."""

    def not_a_tool(data: str) -> str:
        """This function is not decorated."""
        return f"Not a tool: {data}"

    def another_regular_function(x: int, y: int) -> int:
        """Another regular function."""
        return x * y

    return [not_a_tool, another_regular_function]


# Test markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests that test individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that test component interaction"
    )
    config.addinivalue_line("markers", "slow: Tests that may take longer to run")
    config.addinivalue_line(
        "markers", "provider: Tests for specific AI provider integrations"
    )


# Custom assertions
def assert_valid_registry_structure(registry: dict[str, dict[str, Any]]):
    """Assert that a registry has the correct structure."""
    assert isinstance(registry, dict), "Registry should be a dictionary"

    for tool_name, entry in registry.items():
        assert isinstance(tool_name, str), (
            f"Tool name should be string, got {type(tool_name)}"
        )
        assert isinstance(entry, dict), (
            f"Registry entry should be dict, got {type(entry)}"
        )
        assert "tool" in entry, f"Entry for {tool_name} missing 'tool' key"
        assert "representation" in entry, (
            f"Entry for {tool_name} missing 'representation' key"
        )
        assert callable(entry["tool"]), f"Tool {tool_name} should be callable"
        assert isinstance(entry["representation"], dict), (
            f"Representation for {tool_name} should be dict"
        )


def assert_valid_tool_metadata(tool_func):
    """Assert that a decorated tool has all required metadata."""
    required_attrs = [
        "_description",
        "_input_schema",
        "_original_func",
        "_cache_control",
        "_ignore_in_schema",
    ]

    for attr in required_attrs:
        assert hasattr(tool_func, attr), f"Tool missing required attribute: {attr}"

    # Check types
    assert isinstance(getattr(tool_func, "_description"), str), (
        "_description should be string"
    )
    assert isinstance(getattr(tool_func, "_input_schema"), dict), (
        "_input_schema should be dict"
    )
    assert callable(getattr(tool_func, "_original_func")), (
        "_original_func should be callable"
    )
    assert isinstance(getattr(tool_func, "_ignore_in_schema"), list), (
        "_ignore_in_schema should be list"
    )


# Make assertions available to all test modules
pytest.assert_valid_registry_structure = assert_valid_registry_structure
pytest.assert_valid_tool_metadata = assert_valid_tool_metadata
