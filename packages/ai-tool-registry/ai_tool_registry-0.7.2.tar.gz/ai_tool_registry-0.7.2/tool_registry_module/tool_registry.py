"""
Universal Tool Registry System for AI Provider Integration

This module provides a sophisticated tool registration system that automatically converts
Python functions into AI provider tools with proper schema generation, validation,
and error handling. Supports multiple AI providers including Anthropic Claude, OpenAI,
Mistral AI, AWS Bedrock, and Google Gemini.

Key Features:
- Automatic JSON schema generation from function signatures
- Pydantic model integration and validation
- Parameter filtering for internal/context parameters
- Multi-provider support with unified interface
- Comprehensive error handling and logging
- Type safety with full type hints
- Registry builders for all major AI providers

Usage Example:
    ```python
    from tool_registry_module import tool, build_registry_openai, build_registry_anthropic
    from pydantic import BaseModel


    class UserData(BaseModel):
        name: str
        age: int


    @tool(description="Process user information")
    def process_user(input: UserData, context: str = "default") -> UserData:
        return input


    # Use with different providers
    openai_registry = build_registry_openai([process_user])
    anthropic_registry = build_registry_anthropic([process_user])
    ```

Author: Claude Code Assistant
Version: 3.0
"""

import inspect
import logging
import types
from collections import OrderedDict
from collections.abc import Callable
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    TypedDict,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

from pydantic import ValidationError, create_model

from ._json_schema import InlineDefsJsonSchemaTransformer
from .tool_context_type import _is_tool_context_param

if TYPE_CHECKING:
    from anthropic.types import ToolParam


class ToolEntry(TypedDict):
    tool: Callable[..., Any]
    representation: dict[str, Any]


# Configure logger for this module
logger = logging.getLogger(__name__)


class ToolRegistryError(Exception):
    """Exception for tool registry validation errors."""

    pass


def create_schema_from_signature(
    func: Callable[..., Any], ignore_in_schema: list[str] | None = None
) -> dict[str, Any]:
    """
    Create a JSON schema from a function signature using Pydantic models.

    This function introspects a function's signature and creates a corresponding
    JSON schema that can be used by AI providers for tool calling. It handles
    both simple types and complex Pydantic models.

    Args:
        func: The function to generate schema for
        ignore_in_schema: List of parameter names to exclude from the schema

    Returns:
        A JSON schema dictionary compatible with AI provider tool formats

    Example:
        ```python
        def my_func(name: str, age: int = 25, context: str = "internal"):
            pass


        schema = create_schema_from_signature(my_func, ["context"])
        # Returns schema for 'name' and 'age' parameters only
        ```
    """
    if ignore_in_schema is None:
        ignore_in_schema = []

    sig = inspect.signature(func)
    hints = get_type_hints(func, include_extras=True)

    logger.debug(f"Generating schema for function: {func.__name__}")

    fields: dict[str, Any] = {}
    for param_name, param in sig.parameters.items():
        if param_name in ["args", "kwargs"] + ignore_in_schema:
            logger.debug(f"Skipping parameter: {param_name}")
            continue

        param_type = hints.get(param_name, Any)

        # Skip ToolContext parameters
        if _is_tool_context_param(param_type):
            logger.debug(f"Skipping ToolContext parameter: {param_name}")
            continue

        if param.default != inspect.Parameter.empty:
            fields[param_name] = (param_type, param.default)
            logger.debug(f"Added optional parameter: {param_name} = {param.default}")
        else:
            fields[param_name] = (param_type, ...)
            logger.debug(f"Added required parameter: {param_name}")

    if not fields:
        logger.warning(f"No fields found for function {func.__name__}")

    model_name = f"{func.__name__}InputModel"
    temp_model = create_model(model_name, **fields)

    schema = temp_model.model_json_schema()
    logger.debug(f"Generated schema for {func.__name__}: {len(fields)} fields")

    return schema


def _is_pydantic_model(param_type: type) -> bool:
    """
    Check if a type is a Pydantic model.

    Args:
        param_type: The type to check

    Returns:
        True if the type is a Pydantic model, False otherwise
    """
    return hasattr(param_type, "__bases__") and any(
        hasattr(base, "model_validate") for base in param_type.__mro__
    )


def _convert_parameter(param_type: type, param_value: Any) -> Any:
    """
    Convert a parameter value to the expected type.

    Args:
        param_name: Name of the parameter (for error messages)
        param_type: Expected type of the parameter
        param_value: The value to convert

    Returns:
        The converted parameter value
    """
    from enum import Enum

    # Handle None values
    if param_value is None:
        return param_value
    origin = get_origin(param_type)
    if origin is Annotated:
        param_type = get_args(param_type)[0]
        origin = get_origin(param_type)

    if origin is None:
        origin = getattr(param_type, "__origin__", None)

    args = getattr(param_type, "__args__", ())
    last_exception = None
    if origin is Union or isinstance(param_type, types.UnionType):
        for union_type in args:
            if union_type is type(None) and param_value is None:
                return None
            # Skip isinstance check for parameterized generics (e.g., list[str])
            try:
                if isinstance(param_value, union_type):
                    return param_value
            except TypeError:
                # union_type is a parameterized generic, skip isinstance check
                pass

        last_exception = None
        for union_type in args:
            if union_type is type(None):
                continue
            try:
                return _convert_parameter(union_type, param_value)
            except (ValueError, ValidationError, TypeError) as e:
                last_exception = e
                continue

        if last_exception:
            raise last_exception

    elif origin is list:
        if args and isinstance(param_value, list):
            element_type = args[0]
            return [
                _convert_parameter(param_type=element_type, param_value=item)
                for item in param_value
            ]
        return param_value
    elif origin is dict:
        if len(args) == 2 and isinstance(param_value, dict):
            key_type, val_type = args
            return {
                _convert_parameter(
                    param_type=key_type, param_value=k
                ): _convert_parameter(param_type=val_type, param_value=v)
                for k, v in param_value.items()
            }

        # Only use isinstance for concrete types, not parameterized generics
    if get_origin(param_type) is None and not hasattr(param_type, "__args__"):
        if isinstance(param_value, param_type):
            return param_value

    if inspect.isclass(param_type) and issubclass(param_type, Enum):
        if isinstance(param_value, str):
            try:
                return param_type(param_value)
            except ValueError:
                # If direct value doesn't work, try by name
                for enum_member in param_type:
                    if enum_member.name.lower() == param_value.lower():
                        return enum_member
                raise ValueError(
                    f"Invalid enum value '{param_value}' for {param_type.__name__}"
                )
        return param_value

    basic_types = {int: int, float: float, str: str, bool: bool}

    if param_type in basic_types:
        try:
            return basic_types[param_type](param_value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert {param_value} to {param_type.__name__}: {e}"
            )

    if _is_pydantic_model(param_type):
        # Only use isinstance for concrete types, not parameterized generics
        if get_origin(param_type) is None and not hasattr(param_type, "__args__"):
            if isinstance(param_value, param_type):
                return param_value
        return param_type(**param_value)

    return param_value


@overload
def tool[T, **P](func: Callable[P, T]) -> Callable[P, T]: ...


@overload
def tool[T, **P](
    *,
    description: str | None = None,
    cache_control: Any | None = None,
    ignore_in_schema: list[str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


def tool[T, **P](
    func: Callable[P, T] | None = None,
    *,
    description: str | None = None,
    cache_control: Any | None = None,
    ignore_in_schema: list[str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]] | Callable[P, T]:
    """
    Decorator that converts a Python function into an AI provider tool.

    This decorator automatically generates JSON schemas from function signatures,
    handles Pydantic model validation, and provides parameter filtering capabilities.
    The resulting tool can be used with multiple AI providers including Anthropic Claude,
    OpenAI, Mistral AI, AWS Bedrock, and Google Gemini.

    Args:
        description: Human-readable description of what the tool does
        cache_control: Optional cache control settings (supported by some providers)
        ignore_in_schema: List of parameter names to exclude from the generated schema.
                         Useful for internal parameters like context or configuration.

    Returns:
        A decorator function that wraps the original function with tool capabilities

    Raises:
        SchemaGenerationError: If schema generation fails
        ToolValidationError: If parameter validation fails during execution

    Example:
        ```python
        @tool(
            description="Calculate the area of a rectangle",
            ignore_in_schema=["debug_mode"],
        )
        def calculate_area(
            length: float, width: float, debug_mode: bool = False
        ) -> float:
            if debug_mode:
                print(f"Calculating area for {length} x {width}")
            return length * width
        ```

    Note:
        The decorator preserves the original function's signature and behaviour while
        adding tool-specific metadata and automatic parameter conversion.
    """
    if ignore_in_schema is None:
        ignore_in_schema = []

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        logger.info(f"Registering tool: {func.__name__}")

        sig = inspect.signature(func)
        hints = get_type_hints(func, include_extras=True)

        # Generate schema for the function
        input_schema = create_schema_from_signature(func, ignore_in_schema or [])

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """
            Tool wrapper that handles parameter conversion and validation.

            Args:
                *args: Positional arguments from tool invocation
                **kwargs: Keyword arguments from tool invocation

            Returns:
                Result from the original function
            """

            # Filter kwargs to only include parameters that the function accepts
            valid_params = set(sig.parameters.keys())
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}

            # Bind arguments and apply defaults
            bound_args = sig.bind(*args, **filtered_kwargs)
            bound_args.apply_defaults()

            # Convert parameters to expected types
            converted_kwargs = {}
            for param_name, param_value in bound_args.arguments.items():
                if param_name in ["args", "kwargs"]:
                    continue
                param_type = hints.get(param_name, Any)

                # Skip conversion for parameters that should be ignored or are ToolContext
                if (
                    param_type is Any
                    or _is_tool_context_param(param=param_type)
                    or param_name in (ignore_in_schema or [])
                ):
                    converted_kwargs[param_name] = param_value
                else:
                    converted_kwargs[param_name] = _convert_parameter(
                        param_type=param_type, param_value=param_value
                    )

            return func(**converted_kwargs)

        func_description = description if description else inspect.getdoc(func)
        if not func_description:
            func_description = func.__name__
        setattr(wrapper, "_description", func_description)
        setattr(wrapper, "_cache_control", cache_control)
        setattr(wrapper, "_input_schema", input_schema)
        setattr(wrapper, "_original_func", func)
        setattr(wrapper, "_ignore_in_schema", ignore_in_schema)

        logger.info(f"Successfully registered tool: {func.__name__}")
        return wrapper

    if func is not None:
        return decorator(func)

    return decorator


def _build_registry_base[T](
    functions: list[Callable[..., T]],
    provider_name: str,
    build_representation_func: Callable[
        [Callable[..., Any], str], dict[str, Any] | Any
    ],
) -> dict[str, dict[str, Any]]:
    """
    Base function for building tool registries for any provider.

    Args:
        functions: List of functions decorated with @tool
        provider_name: Name of the provider (for logging)
        build_representation_func: Function to build provider-specific representation
        check_dependencies_func: Optional function to check provider dependencies

    Returns:
        Dictionary mapping tool names to their registry entries
    """
    logger.info(
        f"Building {provider_name} tool registry for {len(functions)} functions"
    )

    registry: OrderedDict[str, dict[str, Any]] = OrderedDict()
    processed_count = 0
    skipped_count = 0

    for func in functions:
        if not hasattr(func, "_input_schema"):
            logger.warning(
                f"Skipping function {func.__name__}: not decorated with @tool"
            )
            skipped_count += 1
            continue

        # Use the wrapper function's name (which can be modified) as the primary name
        func_name = func.__name__
        logger.debug(f"Processing tool: {func_name}")

        # Check for duplicate function names
        if func_name in registry:
            raise ToolRegistryError(
                f"Duplicate tool name '{func_name}' found. Each tool must have a unique name."
            )

        representation = build_representation_func(func, func_name)

        registry[func_name] = {
            "tool": func,
            "representation": representation,
        }

        processed_count += 1
        logger.debug(
            f"Successfully added {provider_name} tool to registry: {func_name}"
        )

    logger.info(
        f"{provider_name} registry building completed: {processed_count} tools processed, "
        f"{skipped_count} functions skipped"
    )

    return registry


def build_registry_anthropic[T](
    functions: list[Callable[..., T]],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with Anthropic Claude API.

    This function takes a list of tool-decorated functions and creates a registry
    that can be used directly with Anthropic's tool calling API. Each tool in the
    registry includes both the callable function and its API representation.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": ToolParam object for Anthropic API

    Raises:
        ToolRegistryError: If registry building fails

    Example:
        ```python
        @tool(description="Add two numbers")
        def add(a: int, b: int) -> int:
            return a + b

        @tool(description="Multiply two numbers")
        def multiply(a: int, b: int) -> int:
            return a * b

        registry = build_registry_anthropic([add, multiply])

        # Use with Anthropic API
        tools = [entry["representation"] for entry in registry.values()]
        ```

    Note:
        Only functions with the @tool decorator will be included in the registry.
        Functions without tool metadata will be silently skipped.
    """

    def build_anthropic_representation(
        func: Callable[..., Any], func_name: str
    ) -> "ToolParam":
        from anthropic.types import ToolParam

        tool_param = ToolParam(
            name=func_name,
            description=getattr(func, "_description"),
            input_schema=getattr(func, "_input_schema"),
        )

        if getattr(func, "_cache_control"):
            tool_param["cache_control"] = getattr(func, "_cache_control")
            logger.debug(f"Added cache control for tool: {func_name}")

        return tool_param

    return _build_registry_base(
        functions,
        "Anthropic",
        build_anthropic_representation,
    )


def build_registry_openai[T](
    functions: list[Callable[..., T]],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with OpenAI Function Calling API.

    This function takes a list of tool-decorated functions and creates a registry
    that can be used directly with OpenAI's function calling API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in OpenAI function format

    Example:
        ```python
        registry = build_registry_openai([add, multiply])

        # Use with OpenAI API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """

    def build_openai_representation(
        func: Callable[..., Any], func_name: str
    ) -> dict[str, Any]:
        try:
            import openai  # type: ignore # noqa: F401
        except ImportError:
            pass  # OpenAI not available, but we can still build the representation

        return {
            "type": "function",
            "name": func_name,
            "description": getattr(func, "_description"),
            "parameters": getattr(func, "_input_schema"),
            "strict": True,
        }

    return _build_registry_base(functions, "OpenAI", build_openai_representation)


def build_registry_mistral[T](
    functions: list[Callable[..., T]],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with Mistral AI Function Calling API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in Mistral function format

    Example:
        ```python
        registry = build_registry_mistral([add, multiply])

        # Use with Mistral AI API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """

    def build_mistral_representation(
        func: Callable[..., Any], func_name: str
    ) -> dict[str, Any]:
        try:
            import mistralai  # type: ignore # noqa: F401
        except ImportError:
            pass  # Mistral AI not available, but we can still build the representation

        return {
            "type": "function",
            "function": {
                "name": func_name,
                "description": getattr(func, "_description"),
                "parameters": getattr(func, "_input_schema"),
            },
        }

    return _build_registry_base(functions, "Mistral", build_mistral_representation)


def build_registry_bedrock[T](
    functions: list[Callable[..., T]],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with AWS Bedrock Converse API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in Bedrock tool format

    Example:
        ```python
        registry = build_registry_bedrock([add, multiply])

        # Use with AWS Bedrock API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """

    def build_bedrock_representation(
        func: Callable[..., Any], func_name: str
    ) -> dict[str, Any]:
        try:
            import boto3  # type: ignore  # noqa: F401, I001
        except ImportError:
            pass  # Boto3 not available, but we can still build the representation

        return {
            "toolSpec": {
                "name": func_name,
                "description": getattr(func, "_description"),
                "inputSchema": {
                    "json": InlineDefsJsonSchemaTransformer(
                        getattr(func, "_input_schema")
                    ).walk()
                },
            }
        }

    return _build_registry_base(functions, "Bedrock", build_bedrock_representation)


def build_registry_gemini[T](
    functions: list[Callable[..., T]],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with Google Gemini Function Calling API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in Gemini function format

    Example:
        ```python
        registry = build_registry_gemini([add, multiply])

        # Use with Google Gemini API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """

    def build_gemini_representation(
        func: Callable[..., Any], func_name: str
    ) -> dict[str, Any]:
        try:
            import google.generativeai as genai  # type: ignore  # noqa: F401, I001
        except ImportError:
            pass  # Google Generative AI not available, but we can still build the representation

        return {
            "name": func_name,
            "description": getattr(func, "_description"),
            "parameters": getattr(func, "_input_schema"),
        }

    return _build_registry_base(functions, "Gemini", build_gemini_representation)


def get_tool_info(
    registry: dict[str, dict[str, Any]], tool_name: str
) -> dict[str, Any]:
    """
    Get detailed information about a specific tool in the registry.

    Args:
        registry: Tool registry from build_registry_anthropic_tool_registry
        tool_name: Name of the tool to get information for

    Returns:
        Dictionary containing tool information

    Raises:
        KeyError: If tool is not found in registry
    """
    if tool_name not in registry:
        available_tools = list(registry.keys())
        raise KeyError(
            f"Tool '{tool_name}' not found. Available tools: {available_tools}"
        )

    tool_entry = registry[tool_name]
    wrapper_func = tool_entry["tool"]

    return {
        "name": tool_name,
        "description": wrapper_func._description,
        "schema": wrapper_func._input_schema,
        "cache_control": wrapper_func._cache_control,
        "ignored_parameters": wrapper_func._ignore_in_schema,
        "original_function": getattr(wrapper_func, "_original_func").__name__,
    }


def validate_registry(registry: dict[str, dict[str, Any]]) -> bool:
    """
    Validate that a tool registry has the correct structure.

    Args:
        registry: Tool registry to validate

    Returns:
        True if registry is valid

    Raises:
        ToolRegistryError: If registry is invalid
    """
    logger.info(f"Validating tool registry with {len(registry)} tools")

    for tool_name, tool_data in registry.items():
        # Check required keys
        if "tool" not in tool_data:
            raise ToolRegistryError(f"Tool '{tool_name}' missing 'tool' key")
        if "representation" not in tool_data:
            raise ToolRegistryError(f"Tool '{tool_name}' missing 'representation' key")

        # Check tool function has required metadata
        tool_func = tool_data["tool"]
        required_attrs = ["_description", "_input_schema", "_original_func"]
        for attr in required_attrs:
            if not hasattr(tool_func, attr):
                raise ToolRegistryError(f"Tool '{tool_name}' missing attribute: {attr}")

        # Check representation has required fields (varies by provider)
        representation = tool_data["representation"]

        # Basic validation - must have name and description somewhere
        has_name = (
            "name" in representation
            or (representation.get("function", {}).get("name"))
            or (representation.get("toolSpec", {}).get("name"))
        )

        has_description = (
            "description" in representation
            or (representation.get("function", {}).get("description"))
            or (representation.get("toolSpec", {}).get("description"))
        )

        has_schema = (
            "input_schema" in representation
            or "parameters" in representation
            or (representation.get("function", {}).get("parameters"))
            or (representation.get("toolSpec", {}).get("inputSchema"))
        )

        if not has_name:
            raise ToolRegistryError(
                f"Tool '{tool_name}' representation missing name field"
            )
        if not has_description:
            raise ToolRegistryError(
                f"Tool '{tool_name}' representation missing description field"
            )
        if not has_schema:
            raise ToolRegistryError(
                f"Tool '{tool_name}' representation missing schema field"
            )

    logger.info("Tool registry validation completed successfully")
    return True


# Export main functions and classes
__all__ = [
    "tool",
    "build_registry_anthropic",
    "build_registry_openai",
    "build_registry_mistral",
    "build_registry_bedrock",
    "build_registry_gemini",
    "get_tool_info",
    "validate_registry",
    "ToolRegistryError",
]
