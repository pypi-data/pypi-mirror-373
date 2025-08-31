"""
Tests for ToolContext type handling and parameter skipping.

This module tests the _is_tool_context_param function and ensures that
ToolContext parameters are properly identified and skipped in both
direct type annotations and Annotated type hints.
"""

from typing import Annotated, Union

import pytest

from tool_registry_module.tool_context_type import ToolContext, _is_tool_context_param


class TestToolContextTypeDetection:
    """Test the _is_tool_context_param function for various type scenarios."""

    def test_direct_tool_context_type(self):
        """Test that direct ToolContext[T] types are detected."""
        # Direct ToolContext generic
        assert _is_tool_context_param(ToolContext[str]) is True
        assert _is_tool_context_param(ToolContext[int]) is True
        assert _is_tool_context_param(ToolContext[dict]) is True

    def test_annotated_tool_context_type(self):
        """Test that Annotated ToolContext types are detected."""
        # Annotated with ToolContext class
        assert _is_tool_context_param(Annotated[str, ToolContext]) is True
        assert _is_tool_context_param(Annotated[int, ToolContext]) is True

        # Annotated with ToolContext generic instances
        assert _is_tool_context_param(Annotated[str, ToolContext[str]]) is True
        assert _is_tool_context_param(Annotated[int, ToolContext[int]]) is True

        # Multiple annotations with ToolContext
        assert (
            _is_tool_context_param(Annotated[str, "description", ToolContext]) is True
        )
        assert (
            _is_tool_context_param(Annotated[int, ToolContext, "other_annotation"])
            is True
        )

    def test_non_tool_context_types(self):
        """Test that non-ToolContext types are not detected as tool context."""
        # Basic types
        assert _is_tool_context_param(str) is False
        assert _is_tool_context_param(int) is False
        assert _is_tool_context_param(float) is False
        assert _is_tool_context_param(bool) is False
        assert _is_tool_context_param(list) is False
        assert _is_tool_context_param(dict) is False

        # Complex types
        assert _is_tool_context_param(list[str]) is False
        assert _is_tool_context_param(dict[str, int]) is False

        # Annotated types without ToolContext
        assert _is_tool_context_param(Annotated[str, "description"]) is False
        assert _is_tool_context_param(Annotated[int, "other_annotation"]) is False

    def test_none_type_handling(self):
        """Test that None type is properly handled."""
        assert _is_tool_context_param(type(None)) is False
        assert _is_tool_context_param(None.__class__) is False

    def test_union_type_with_tool_context_raises_error(self):
        """Test that union types with ToolContext raise TypeError."""
        # Union with ToolContext should raise error
        with pytest.raises(
            TypeError, match="The ToolContext should not be used as a union type"
        ):
            _is_tool_context_param(Union[str, ToolContext[str]])

        with pytest.raises(
            TypeError, match="The ToolContext should not be used as a union type"
        ):
            _is_tool_context_param(Union[ToolContext[int], str])

        # Modern union syntax with ToolContext should raise error
        with pytest.raises(
            TypeError, match="The ToolContext should not be used as a union type"
        ):
            _is_tool_context_param(str | ToolContext[str])

        with pytest.raises(
            TypeError, match="The ToolContext should not be used as a union type"
        ):
            _is_tool_context_param(ToolContext[int] | str)

    def test_union_type_with_none_and_tool_context_raises_error(self):
        """Test that union types with None and ToolContext raise TypeError."""
        with pytest.raises(
            TypeError, match="The ToolContext should not be used as a union type"
        ):
            _is_tool_context_param(Union[ToolContext[str], None])

        with pytest.raises(
            TypeError, match="The ToolContext should not be used as a union type"
        ):
            _is_tool_context_param(ToolContext[int] | None)

    def test_union_type_without_tool_context(self):
        """Test that union types without ToolContext are handled correctly."""
        # Union without ToolContext should return False
        assert _is_tool_context_param(Union[str, int]) is False
        assert _is_tool_context_param(str | int) is False
        assert _is_tool_context_param(Union[str, None]) is False
        assert _is_tool_context_param(str | None) is False

    def test_complex_annotated_scenarios(self):
        """Test complex annotation scenarios."""

        # Custom class that's not ToolContext
        class CustomContext:
            pass

        # Should not detect non-ToolContext classes
        assert _is_tool_context_param(Annotated[str, CustomContext]) is False

        # Mixed annotations - only ToolContext should trigger detection
        assert (
            _is_tool_context_param(Annotated[str, CustomContext, ToolContext]) is True
        )
        assert (
            _is_tool_context_param(
                Annotated[int, "desc", CustomContext, ToolContext[str]]
            )
            is True
        )

    def test_edge_cases(self):
        """Test edge cases and unusual type scenarios."""
        # Note: Annotated[str] with no annotations is not valid, so we skip this test

        # Generic types that are not ToolContext
        from typing import Generic, TypeVar

        T = TypeVar("T")

        class OtherGeneric(Generic[T]):
            pass

        assert _is_tool_context_param(OtherGeneric[str]) is False


class TestToolContextIntegration:
    """Test ToolContext integration with the tool decorator."""

    def test_tool_context_parameter_skipping(self):
        """Test that ToolContext parameters are skipped in tool registration."""
        from tool_registry_module import tool

        @tool(description="Test function with tool context")
        def test_function_with_context(
            regular_param: str,
            context: ToolContext[dict],
            another_param: int,
            annotated_context: Annotated[str, ToolContext],
        ) -> str:
            return f"regular: {regular_param}, another: {another_param}"

        # Get tool schema directly
        schema = getattr(test_function_with_context, "_input_schema")
        properties = schema["properties"]

        # Should have regular parameters
        assert "regular_param" in properties
        assert "another_param" in properties

        # Should NOT have ToolContext parameters
        assert "context" not in properties
        assert "annotated_context" not in properties

        # Verify parameter count
        assert len(properties) == 2

    def test_function_with_only_tool_context_parameters(self):
        """Test function that has only ToolContext parameters."""
        from tool_registry_module import tool

        @tool(description="Function with only tool context params")
        def context_only_function(
            ctx1: ToolContext[dict], ctx2: Annotated[str, ToolContext]
        ) -> str:
            return "test"

        # Get tool schema directly
        schema = getattr(context_only_function, "_input_schema")

        # Schema should have no properties
        properties = schema["properties"]
        assert len(properties) == 0

    def test_mixed_parameter_types(self):
        """Test function with mix of regular, optional, and ToolContext parameters."""
        from typing import Optional

        from tool_registry_module import tool

        @tool(description="Mixed parameter types")
        def mixed_function(
            required: str,
            context: ToolContext[dict],
            annotated_context: Annotated[int, ToolContext, "context param"],
            optional: Optional[int] = None,
            annotated_optional: Annotated[Optional[str], "description"] = None,
        ) -> str:
            return "test"

        # Get tool schema directly
        schema = getattr(mixed_function, "_input_schema")
        properties = schema["properties"]

        # Should have regular and optional parameters
        assert "required" in properties
        assert "optional" in properties
        assert "annotated_optional" in properties

        # Should NOT have ToolContext parameters
        assert "context" not in properties
        assert "annotated_context" not in properties

        # Verify parameter count
        assert len(properties) == 3

    def test_tool_context_object_reference_preservation(self):
        """Test that ToolContext parameters maintain object references for mutation."""
        from tool_registry_module import tool

        # Create a context object that can be mutated
        class Context:
            def __init__(self):
                self.call_count = 0
                self.last_input = None
                self.metadata = {}

        @tool(description="Function that modifies context")
        def modify_context_function(
            user_input: str, context: ToolContext[Context]
        ) -> str:
            # Modify the context object
            context.call_count += 1
            context.last_input = user_input
            context.metadata[f"call_{context.call_count}"] = user_input
            return f"Processed: {user_input}"

        # Create context instance
        ctx = Context()
        original_id = id(ctx)

        # Verify initial state
        assert ctx.call_count == 0
        assert ctx.last_input is None
        assert ctx.metadata == {}

        # Call function with context
        result1 = modify_context_function(user_input="first call", context=ctx)

        # Verify the same object was modified (reference preserved)
        assert id(ctx) == original_id
        assert ctx.call_count == 1
        assert ctx.last_input == "first call"
        assert ctx.metadata == {"call_1": "first call"}
        assert result1 == "Processed: first call"

        # Call again with same context
        result2 = modify_context_function(user_input="second call", context=ctx)

        # Verify continued mutation of same object
        assert id(ctx) == original_id
        assert ctx.call_count == 2
        assert ctx.last_input == "second call"
        assert ctx.metadata == {"call_1": "first call", "call_2": "second call"}
        assert result2 == "Processed: second call"

    def test_tool_context_dict_reference_preservation(self):
        """Test that ToolContext dict parameters maintain references for mutation."""
        from tool_registry_module import tool

        @tool(description="Function that modifies dict context")
        def modify_dict_context(action: str, context: ToolContext[dict]) -> str:
            # Modify the context dict
            context["actions"] = context.get("actions", [])
            context["actions"].append(action)
            context["last_action"] = action
            return f"Action recorded: {action}"

        # Create context dict
        ctx = {"initial": "value"}
        original_id = id(ctx)

        # Call function
        result1 = modify_dict_context(action="login", context=ctx)

        # Verify same dict object was modified
        assert id(ctx) == original_id
        assert ctx["initial"] == "value"  # Original data preserved
        assert ctx["actions"] == ["login"]
        assert ctx["last_action"] == "login"
        assert result1 == "Action recorded: login"

        # Call again
        result2 = modify_dict_context(action="logout", context=ctx)

        # Verify continued mutation
        assert id(ctx) == original_id
        assert ctx["actions"] == ["login", "logout"]
        assert ctx["last_action"] == "logout"
        assert result2 == "Action recorded: logout"

    def test_tool_context_list_reference_preservation(self):
        """Test that ToolContext list parameters maintain references for mutation."""
        from tool_registry_module import tool

        @tool(description="Function that modifies list context")
        def modify_list_context(item: str, context: ToolContext[list]) -> str:
            # Modify the context list
            context.append(item)
            return f"Added: {item}"

        # Create context list
        ctx = ["initial_item"]
        original_id = id(ctx)

        # Call function
        result1 = modify_list_context(item="new_item", context=ctx)

        # Verify same list object was modified
        assert id(ctx) == original_id
        assert ctx == ["initial_item", "new_item"]
        assert result1 == "Added: new_item"

        # Call again
        result2 = modify_list_context(item="another_item", context=ctx)

        # Verify continued mutation
        assert id(ctx) == original_id
        assert ctx == ["initial_item", "new_item", "another_item"]
        assert result2 == "Added: another_item"

    def test_tool_context_annotated_reference_preservation(self):
        """Test that Annotated ToolContext parameters maintain references."""
        from tool_registry_module import tool

        @tool(description="Function with annotated context")
        def modify_annotated_context(
            message: str, session: Annotated[dict, ToolContext, "session context"]
        ) -> str:
            # Modify the session context
            session["messages"] = session.get("messages", [])
            session["messages"].append(message)
            session["message_count"] = len(session["messages"])
            return f"Message added: {message}"

        # Create session context
        session_ctx = {"user_id": "123", "start_time": "2023-01-01"}
        original_id = id(session_ctx)

        # Call function
        result = modify_annotated_context(message="Hello", session=session_ctx)

        # Verify same object was modified
        assert id(session_ctx) == original_id
        assert session_ctx["user_id"] == "123"  # Original data preserved
        assert session_ctx["start_time"] == "2023-01-01"
        assert session_ctx["messages"] == ["Hello"]
        assert session_ctx["message_count"] == 1
        assert result == "Message added: Hello"

    def test_tool_context_mixed_parameters_reference_preservation(self):
        """Test reference preservation with mixed parameter types."""
        from typing import Optional

        from tool_registry_module import tool

        @tool(description="Function with mixed parameters including context")
        def complex_function_with_context(
            required_param: str,
            context: ToolContext[dict],
            optional_param: Optional[int] = None,
            annotated_context: Annotated[list, ToolContext] = None,
        ) -> dict:
            # Modify both context objects
            context["calls"] = context.get("calls", 0) + 1
            context["last_required"] = required_param
            context["last_optional"] = optional_param

            if annotated_context is not None:
                annotated_context.append(f"call_{context['calls']}")

            return {
                "required": required_param,
                "optional": optional_param,
                "context_calls": context["calls"],
                "annotated_length": len(annotated_context) if annotated_context else 0,
            }

        # Create context objects
        main_ctx = {"initial": True}
        list_ctx = ["start"]
        main_id = id(main_ctx)
        list_id = id(list_ctx)

        # Call function
        result = complex_function_with_context(
            required_param="test",
            context=main_ctx,
            optional_param=42,
            annotated_context=list_ctx,
        )

        # Verify both context objects maintain references and were modified
        assert id(main_ctx) == main_id
        assert id(list_ctx) == list_id

        assert main_ctx["initial"] is True  # Original data preserved
        assert main_ctx["calls"] == 1
        assert main_ctx["last_required"] == "test"
        assert main_ctx["last_optional"] == 42

        assert list_ctx == ["start", "call_1"]

        assert result == {
            "required": "test",
            "optional": 42,
            "context_calls": 1,
            "annotated_length": 2,
        }
