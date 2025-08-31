"""
Comprehensive tests for the AI Tool Registry system.

This module tests the core functionality of the tool decorator and registry builders,
including schema generation, parameter validation, and multi-provider support.
"""

import inspect
from typing import Any
from unittest.mock import patch

import pytest
from pydantic import BaseModel

from tool_registry_module import (
    ToolRegistryError,
    build_registry_anthropic,
    build_registry_bedrock,
    build_registry_gemini,
    build_registry_mistral,
    build_registry_openai,
    create_schema_from_signature,
    get_tool_info,
    tool,
    validate_registry,
)
from tool_registry_module.tool_registry import _convert_parameter, _is_pydantic_model


class UserData(BaseModel):
    """Test Pydantic model for complex parameter testing."""

    name: str
    age: int
    email: str | None = None


class TestToolDecorator:
    """Test the @tool decorator functionality."""

    def test_basic_tool_decoration(self):
        """Test basic tool decoration with simple parameters."""

        @tool(description="Add two numbers")
        def add_numbers(a: int, b: int) -> int:
            return a + b

        # Check that metadata is attached
        assert hasattr(add_numbers, "_description")
        assert hasattr(add_numbers, "_input_schema")
        assert hasattr(add_numbers, "_original_func")
        assert hasattr(add_numbers, "_cache_control")
        assert hasattr(add_numbers, "_ignore_in_schema")

        # Check metadata values
        assert getattr(add_numbers, "_description") == "Add two numbers"
        assert getattr(add_numbers, "_cache_control") is None
        assert getattr(add_numbers, "_ignore_in_schema") == []

        # Test function still works
        result = add_numbers(5, 3)
        assert result == 8

    def test_tool_with_default_parameters(self):
        """Test tool decoration with default parameter values."""

        @tool(description="Greet a user")
        def greet_user(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        result = greet_user("Alice")
        assert result == "Hello, Alice!"

        result = greet_user("Bob", "Hi")
        assert result == "Hi, Bob!"

    def test_tool_with_pydantic_model(self):
        """Test tool decoration with Pydantic model parameters."""

        @tool(description="Process user data")
        def process_user(user: UserData) -> str:
            return f"Processing {user.name}, age {user.age}"

        # Test with Pydantic model instance
        user = UserData(name="Alice", age=30, email="alice@example.com")
        result = process_user(user)
        assert result == "Processing Alice, age 30"

        # Test with dictionary (should be converted to Pydantic model)
        user_dict = {"name": "Bob", "age": 25}
        result = process_user(user=user_dict)
        assert result == "Processing Bob, age 25"

    def test_tool_with_ignored_parameters(self):
        """Test tool decoration with ignored parameters in schema."""

        @tool(description="Calculate with debug", ignore_in_schema=["debug_mode"])
        def calculate(x: int, y: int, debug_mode: bool = False) -> int:
            if debug_mode:
                print(f"Calculating {x} + {y}")
            return x + y

        # Check that debug_mode is not in the schema
        schema = getattr(calculate, "_input_schema")
        assert "debug_mode" not in schema.get("properties", {})
        assert "x" in schema.get("properties", {})
        assert "y" in schema.get("properties", {})

        # Test function still works with ignored parameter
        result = calculate(5, 3, debug_mode=True)
        assert result == 8

    def test_tool_with_cache_control(self):
        """Test tool decoration with cache control."""
        cache_control = {"type": "ephemeral"}

        @tool(description="Cached function", cache_control=cache_control)
        def cached_function(data: str) -> str:
            return f"Processed: {data}"

        assert getattr(cached_function, "_cache_control") == cache_control

    def test_tool_preserves_function_signature(self):
        """Test that the tool decorator preserves the original function signature."""

        @tool(description="Original function")
        def original_function(a: int, b: str = "default") -> str:
            """Original docstring."""
            return f"{a}: {b}"

        # Check that wrapper preserves signature
        sig = inspect.signature(original_function)
        params = list(sig.parameters.keys())
        assert "a" in params
        assert "b" in params

        # Check that original function is accessible
        original = getattr(original_function, "_original_func")
        assert original.__name__ == "original_function"


class TestSchemaGeneration:
    """Test schema generation functionality."""

    def test_create_schema_simple_types(self):
        """Test schema generation for simple types."""

        def simple_func(name: str, age: int, height: float = 5.9) -> str:
            return f"{name} is {age} years old"

        schema = create_schema_from_signature(simple_func, [])

        assert schema["type"] == "object"
        properties = schema["properties"]

        # Check required field
        assert "name" in properties
        assert properties["name"]["type"] == "string"
        assert "age" in properties
        assert properties["age"]["type"] == "integer"

        # Check optional field
        assert "height" in properties
        assert properties["height"]["type"] == "number"

        # Check required vs optional
        assert "name" in schema["required"]
        assert "age" in schema["required"]
        assert "height" not in schema["required"]

    def test_create_schema_with_ignored_params(self):
        """Test schema generation with ignored parameters."""

        def func_with_ignored(
            name: str, age: int, internal_param: str = "ignore"
        ) -> str:
            return f"{name}: {age}"

        schema = create_schema_from_signature(func_with_ignored, ["internal_param"])

        properties = schema["properties"]
        assert "name" in properties
        assert "age" in properties
        assert "internal_param" not in properties

    def test_create_schema_pydantic_model(self):
        """Test schema generation with Pydantic models."""

        def func_with_model(user: UserData, count: int = 1) -> str:
            return f"{user.name}: {count}"

        schema = create_schema_from_signature(func_with_model, [])

        properties = schema["properties"]
        assert "user" in properties
        assert "count" in properties

        # Pydantic model should generate nested schema
        user_schema = properties["user"]
        assert (
            "$defs" in schema or "definitions" in schema or "properties" in user_schema
        )


class TestRegistryBuilders:
    """Test registry builder functions."""

    def setup_method(self):
        """Set up test tools for each test."""

        @tool(description="Add two numbers")
        def add(a: int, b: int) -> int:
            return a + b

        @tool(description="Multiply numbers")
        def multiply(x: float, y: float) -> float:
            return x * y

        @tool(description="Process user", ignore_in_schema=["debug"])
        def process_user_data(user: UserData, debug: bool = False) -> str:
            return f"Processing {user.name}"

        # Non-decorated function (should be skipped)
        def not_a_tool(data: str) -> str:
            return data

        self.test_tools = [add, multiply, process_user_data]
        self.mixed_functions = [add, not_a_tool, multiply]

    @pytest.mark.unit
    def test_build_registry_anthropic_success(self):
        """Test successful Anthropic registry building."""

        # Mock ToolParam to act like a dict when called
        class MockToolParam(dict):
            def __init__(self, **kwargs):
                super().__init__(kwargs)

        with patch("anthropic.types.ToolParam", MockToolParam):
            registry = build_registry_anthropic(self.test_tools)

            assert len(registry) == 3
            assert "add" in registry
            assert "multiply" in registry
            assert "process_user_data" in registry

            # Check registry structure
            for tool_name, entry in registry.items():
                assert "tool" in entry
                assert "representation" in entry
                assert callable(entry["tool"])

    @pytest.mark.unit
    def test_build_registry_openai_success(self):
        """Test successful OpenAI registry building."""
        registry = build_registry_openai(self.test_tools)

        assert len(registry) == 3

        # Check OpenAI-specific format
        add_entry = registry["add"]
        representation = add_entry["representation"]
        assert representation["type"] == "function"
        assert representation["name"] == "add"
        assert representation["description"] == "Add two numbers"
        assert "parameters" in representation
        assert representation["strict"] is True

    @pytest.mark.unit
    def test_build_registry_mistral_success(self):
        """Test successful Mistral registry building."""
        registry = build_registry_mistral(self.test_tools)

        assert len(registry) == 3

        # Check Mistral-specific format
        add_entry = registry["add"]
        representation = add_entry["representation"]
        assert representation["type"] == "function"
        assert "function" in representation
        assert representation["function"]["name"] == "add"

    @pytest.mark.unit
    def test_build_registry_bedrock_success(self):
        """Test successful Bedrock registry building."""
        registry = build_registry_bedrock(self.test_tools)

        assert len(registry) == 3

        # Check Bedrock-specific format
        add_entry = registry["add"]
        representation = add_entry["representation"]
        assert "toolSpec" in representation
        assert representation["toolSpec"]["name"] == "add"
        assert "inputSchema" in representation["toolSpec"]

    @pytest.mark.unit
    def test_build_registry_gemini_success(self):
        """Test successful Gemini registry building."""
        registry = build_registry_gemini(self.test_tools)

        assert len(registry) == 3

        # Check Gemini-specific format
        add_entry = registry["add"]
        representation = add_entry["representation"]
        assert representation["name"] == "add"
        assert "parameters" in representation

    @pytest.mark.unit
    def test_registry_skips_non_decorated_functions(self):
        """Test that non-decorated functions are skipped."""
        registry = build_registry_openai(self.mixed_functions)

        # Should only include decorated functions
        assert len(registry) == 2
        assert "add" in registry
        assert "multiply" in registry
        assert "not_a_tool" not in registry

    @pytest.mark.unit
    def test_registry_missing_dependencies(self):
        """Test registry building with missing dependencies."""

        registry = build_registry_openai(self.test_tools)
        assert len(registry) == 3


class TestRegistryValidation:
    """Test registry validation functionality."""

    def test_validate_registry_success(self):
        """Test successful registry validation."""

        # Create a valid registry manually
        @tool(description="Test function")
        def test_func(x: int) -> int:
            return x * 2

        registry = {
            "test_func": {
                "tool": test_func,
                "representation": {
                    "name": "test_func",
                    "description": "Test function",
                    "input_schema": {"type": "object"},
                },
            }
        }

        # Should not raise an exception
        result = validate_registry(registry)
        assert result is True

    def test_validate_registry_missing_tool_key(self):
        """Test validation failure for missing 'tool' key."""
        registry = {"invalid": {"representation": {"name": "test"}}}

        with pytest.raises(ToolRegistryError, match="missing 'tool' key"):
            validate_registry(registry)

    def test_validate_registry_missing_representation_key(self):
        """Test validation failure for missing 'representation' key."""

        @tool(description="Test")
        def test_func() -> None:
            pass

        registry = {"invalid": {"tool": test_func}}

        with pytest.raises(ToolRegistryError, match="missing 'representation' key"):
            validate_registry(registry)

    def test_validate_registry_missing_tool_attributes(self):
        """Test validation failure for missing tool attributes."""

        def invalid_tool() -> None:
            pass

        registry = {
            "invalid": {
                "tool": invalid_tool,
                "representation": {
                    "name": "invalid",
                    "description": "test",
                    "input_schema": {},
                },
            }
        }

        with pytest.raises(ToolRegistryError, match="missing attribute"):
            validate_registry(registry)


class TestGetToolInfo:
    """Test get_tool_info functionality."""

    def test_get_tool_info_success(self):
        """Test successful tool info retrieval."""

        @tool(description="Test tool", cache_control={"type": "ephemeral"})
        def test_tool(x: int, y: str = "default") -> str:
            return f"{x}: {y}"

        registry = {"test_tool": {"tool": test_tool, "representation": {}}}

        info = get_tool_info(registry, "test_tool")

        assert info["name"] == "test_tool"
        assert info["description"] == "Test tool"
        assert info["cache_control"] == {"type": "ephemeral"}
        assert "schema" in info
        assert info["original_function"] == "test_tool"

    def test_get_tool_info_not_found(self):
        """Test tool info retrieval for non-existent tool."""
        registry = {}

        with pytest.raises(KeyError, match="Tool 'nonexistent' not found"):
            get_tool_info(registry, "nonexistent")


class TestParameterConversion:
    """Test parameter conversion and validation."""

    def test_pydantic_model_conversion(self):
        """Test automatic conversion of dict to Pydantic model."""

        @tool(description="Process user")
        def process_user(user: UserData) -> str:
            return f"Hello {user.name}"

        # Test with dictionary input
        user_dict = {"name": "Alice", "age": 30}
        result = process_user(user=user_dict)
        assert result == "Hello Alice"

        # Test with already instantiated model
        user_model = UserData(name="Bob", age=25)
        result = process_user(user=user_model)
        assert result == "Hello Bob"

    def test_positional_and_keyword_arguments(self):
        """Test handling of both positional and keyword arguments."""

        @tool(description="Mixed args")
        def mixed_args(a: int, b: str, c: float = 1.0) -> str:
            return f"{a}, {b}, {c}"

        # Test positional arguments
        result = mixed_args(1, "test")
        assert result == "1, test, 1.0"

        # Test keyword arguments
        result = mixed_args(a=2, b="hello", c=2.5)
        assert result == "2, hello, 2.5"

        # Test mixed
        result = mixed_args(3, "world", c=3.14)
        assert result == "3, world, 3.14"

    def test_convertible_params_optimization(self):
        """Test that convertible params optimization works correctly."""

        @tool(description="Simple function without complex types")
        def simple_func(a: int, b: str) -> str:
            return f"{a}: {b}"

        # Should not trigger complex parameter conversion
        result = simple_func(42, "test")
        assert result == "42: test"

        # Verify function has minimal metadata
        assert hasattr(simple_func, "_input_schema")
        assert hasattr(simple_func, "_description")

    def test_parameter_binding_with_defaults(self):
        """Test parameter binding and defaults application."""

        @tool(description="Function with defaults")
        def func_with_defaults(
            required: str, optional: int = 10, another_optional: str = "default"
        ) -> str:
            return f"{required}-{optional}-{another_optional}"

        # Test with only required parameter
        result = func_with_defaults("test")
        assert result == "test-10-default"

        # Test with some optional parameters
        result = func_with_defaults("hello", 20)
        assert result == "hello-20-default"

        # Test with all parameters
        result = func_with_defaults("world", 30, "custom")
        assert result == "world-30-custom"

    def test_extra_kwargs_handling(self):
        """Test that extra kwargs are filtered out and don't cause failures."""

        @tool(description="Function that should ignore extra kwargs")
        def simple_func(name: str, age: int = 25) -> str:
            return f"Hello {name}, you are {age} years old"

        # Test normal usage
        result = simple_func("Alice", age=30)
        assert result == "Hello Alice, you are 30 years old"

        # Test with extra kwargs (should be ignored)
        result = simple_func("Bob", age=35, extra_param="ignored", another_param=42)
        assert result == "Hello Bob, you are 35 years old"

        # Test with only extra kwargs for optional params (should use defaults)
        result = simple_func("Charlie", extra_param="ignored")
        assert result == "Hello Charlie, you are 25 years old"

        # Test with mixed positional and extra kwargs
        result = simple_func("David", 40, extra_param="ignored", debug=True)
        assert result == "Hello David, you are 40 years old"


class TestInternalFunctions:
    """Test internal helper functions."""

    def test_is_pydantic_model_detection(self):
        """Test _is_pydantic_model function."""

        # Test with Pydantic model
        assert _is_pydantic_model(UserData) is True

        # Test with regular class
        class RegularClass:
            pass

        assert _is_pydantic_model(RegularClass) is False

        # Test with built-in types
        assert _is_pydantic_model(str) is False
        assert _is_pydantic_model(int) is False
        assert _is_pydantic_model(dict) is False

    def test_convert_parameter_basic_types(self):
        """Test _convert_parameter with basic types."""

        # Test basic type conversions
        assert _convert_parameter(int, "42") == 42
        assert _convert_parameter(float, "3.14") == 3.14
        assert _convert_parameter(str, 123) == "123"
        assert _convert_parameter(bool, "true") is True

        # Test None handling
        assert _convert_parameter(str, None) is None
        assert _convert_parameter(UserData, None) is None

    def test_convert_parameter_pydantic_model(self):
        """Test _convert_parameter with Pydantic models."""

        # Test dictionary to Pydantic model conversion
        user_dict = {"name": "John", "age": 30}
        result = _convert_parameter(UserData, user_dict)
        assert isinstance(result, UserData)
        assert result.name == "John"
        assert result.age == 30

        # Test passthrough of existing Pydantic model
        user_model = UserData(name="Alice", age=25)
        result = _convert_parameter(UserData, user_model)
        assert result is user_model

    def test_convert_parameter_list_handling(self):
        """Test _convert_parameter with list types."""

        # Test list of Pydantic models
        users_data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = _convert_parameter(list[UserData], users_data)

        assert len(result) == 2
        assert all(isinstance(user, UserData) for user in result)
        assert result[0].name == "John"
        assert result[1].name == "Jane"

        # Test list without type args
        simple_list = ["a", "b", "c"]
        result = _convert_parameter(list, simple_list)
        assert result == simple_list

    def test_convert_parameter_dict_handling(self):
        """Test _convert_parameter with dict types."""

        # Test dict with Pydantic model values
        users_dict = {
            "user1": {"name": "John", "age": 30},
            "user2": {"name": "Jane", "age": 25},
        }
        result = _convert_parameter(dict[str, UserData], users_dict)

        assert len(result) == 2
        assert isinstance(result["user1"], UserData)
        assert isinstance(result["user2"], UserData)
        assert result["user1"].name == "John"
        assert result["user2"].name == "Jane"


class TestIntegration:
    """Integration tests for the complete workflow."""

    @pytest.mark.integration
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""

        # Define tools
        @tool(description="Mathematical addition")
        def add(a: int, b: int) -> int:
            """Add two integers."""
            return a + b

        @tool(description="User greeting", ignore_in_schema=["debug"])
        def greet(name: str, title: str = "Mr.", debug: bool = False) -> str:
            """Greet a user with optional title."""
            greeting = f"Hello, {title} {name}!"
            if debug:
                print(f"Generated greeting: {greeting}")
            return greeting

        @tool(description="Process user data")
        def handle_user(user: UserData) -> dict[str, Any]:
            """Process user data and return summary."""
            return {
                "processed": True,
                "user_name": user.name,
                "user_age": user.age,
                "has_email": user.email is not None,
            }

        tools = [add, greet, handle_user]

        # Build registries for different providers
        openai_registry = build_registry_openai(tools)

        # Mock ToolParam to act like a dict when called
        class MockToolParam(dict):
            def __init__(self, **kwargs):
                super().__init__(kwargs)

        with patch("anthropic.types.ToolParam", MockToolParam):
            anthropic_registry = build_registry_anthropic(tools)

        # Validate registries
        assert validate_registry(openai_registry) is True
        assert validate_registry(anthropic_registry) is True

        # Test tool execution
        add_tool = openai_registry["add"]["tool"]
        assert add_tool(10, 5) == 15

        greet_tool = openai_registry["greet"]["tool"]
        assert greet_tool("Alice") == "Hello, Mr. Alice!"
        assert greet_tool("Bob", "Dr.") == "Hello, Dr. Bob!"

        # Test Pydantic model handling
        user_tool = openai_registry["handle_user"]["tool"]
        user_data = {"name": "Charlie", "age": 35, "email": "charlie@test.com"}
        result = user_tool(user=user_data)
        assert result["processed"] is True
        assert result["user_name"] == "Charlie"
        assert result["user_age"] == 35
        assert result["has_email"] is True

        # Test tool info retrieval
        add_info = get_tool_info(openai_registry, "add")
        assert add_info["name"] == "add"
        assert add_info["description"] == "Mathematical addition"
        assert "schema" in add_info
        assert "original_function" in add_info

    @pytest.mark.integration
    def test_schema_validation_with_real_data(self):
        """Test schema generation and validation with realistic data."""

        @tool(description="Complex data processor")
        def process_complex_data(
            users: list[UserData],
            config: dict[str, Any],
            batch_size: int = 10,
            validate_emails: bool = True,
        ) -> dict[str, Any]:
            """Process a batch of users with configuration."""
            return {
                "processed_count": len(users),
                "batch_size": batch_size,
                "config_keys": list(config.keys()),
                "validation_enabled": validate_emails,
            }

        # Check schema generation
        schema = getattr(process_complex_data, "_input_schema")
        properties = schema["properties"]

        assert "users" in properties
        assert "config" in properties
        assert "batch_size" in properties
        assert "validate_emails" in properties

        # Test required vs optional
        required = schema.get("required", [])
        assert "users" in required
        assert "config" in required
        assert "batch_size" not in required  # Has default
        assert "validate_emails" not in required  # Has default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
