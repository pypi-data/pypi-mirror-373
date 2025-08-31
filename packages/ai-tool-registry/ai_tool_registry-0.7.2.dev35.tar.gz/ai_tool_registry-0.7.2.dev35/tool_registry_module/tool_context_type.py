import types
from typing import Annotated, Union, get_args, get_origin


class ToolContext[T]:
    """
    This is a generic type to mark a tool context variable in function inputs that will be ignored by the tool decorator
    """

    pass


def _is_tool_context_param(param: type) -> bool:
    if param is type(None):
        return False

    origin = get_origin(param)

    # Check if this is a direct ToolContext generic (e.g., ToolContext[str])
    if origin is ToolContext:
        return True

    # Check if this is an Annotated type with ToolContext
    if origin is Annotated:
        args = get_args(param)
        for arg in args[1:]:
            # Check for ToolContext class itself
            if arg is ToolContext:
                return True
            # Check for ToolContext generic instances (e.g., ToolContext[str])
            if hasattr(arg, "__origin__") and get_origin(arg) is ToolContext:
                return True
            # Check for subclasses of ToolContext
            if isinstance(arg, type) and issubclass(arg, ToolContext):
                return True

    # Check for Union types (both typing.Union and types.UnionType)
    if origin is Union or origin is types.UnionType:
        args = get_args(param)
        for arg in args:
            if arg is not type(None) and _is_tool_context_param(arg):
                raise TypeError(
                    "The ToolContext should not be used as a union type as the variable needs to fill a single function to pass context between the agent loop and the given tool."
                )

    return False
