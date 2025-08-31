"""
Integration tests for union type conversion in tool wrapper functions.

This module tests that union type conversion works correctly when tools are called
with real data, ensuring the _convert_parameter function works properly within
the tool decorator wrapper.
"""

from enum import Enum
from unittest.mock import patch

import pytest
from pydantic import BaseModel

from tool_registry_module import build_registry_openai, tool


class UserModel(BaseModel):
    name: str
    age: int


class AddressModel(BaseModel):
    street: str
    city: str
    zipcode: str


class ContactModel(BaseModel):
    email: str
    phone: str | None = None


class StatusEnum(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class TestToolUnionIntegration:
    """Test union type conversion through actual tool function calls."""

    def test_simple_union_basemodel_or_string(self):
        """Test Union[BaseModel, str] parameter conversion."""

        @tool(description="Process user data or message")
        def process_data(data: UserModel | str) -> dict:
            if isinstance(data, UserModel):
                return {"type": "user", "name": data.name, "age": data.age}
            else:
                return {"type": "string", "message": data}

        # Test with dict that should convert to UserModel
        result1 = process_data({"name": "John", "age": 30})
        assert result1 == {"type": "user", "name": "John", "age": 30}

        # Test with string that should stay string
        result2 = process_data("Hello World")
        assert result2 == {"type": "string", "message": "Hello World"}

    def test_union_with_none(self):
        """Test Union[BaseModel, None] parameter conversion."""

        @tool(description="Process optional user data")
        def process_optional_user(user: UserModel | None) -> dict:
            if user is None:
                return {"status": "no_user"}
            return {"status": "has_user", "name": user.name}

        # Test with None
        result1 = process_optional_user(None)
        assert result1 == {"status": "no_user"}

        # Test with dict that should convert to UserModel
        result2 = process_optional_user({"name": "Alice", "age": 25})
        assert result2 == {"status": "has_user", "name": "Alice"}

    def test_list_with_union_elements(self):
        """Test list[Union[BaseModel, str, None]] parameter conversion."""

        @tool(description="Process mixed list of users and messages")
        def process_mixed_list(items: list[UserModel | str | None]) -> dict:
            result = {"users": [], "messages": [], "nulls": 0}

            for item in items:
                if isinstance(item, UserModel):
                    result["users"].append({"name": item.name, "age": item.age})
                elif isinstance(item, str):
                    result["messages"].append(item)
                elif item is None:
                    result["nulls"] += 1

            return result

        mixed_data = [
            {"name": "John", "age": 30},  # Should become UserModel
            "Hello",  # Should stay string
            None,  # Should stay None
            {"name": "Jane", "age": 25},  # Should become UserModel
            "World",  # Should stay string
        ]

        result = process_mixed_list(mixed_data)

        assert len(result["users"]) == 2
        assert result["users"][0] == {"name": "John", "age": 30}
        assert result["users"][1] == {"name": "Jane", "age": 25}
        assert result["messages"] == ["Hello", "World"]
        assert result["nulls"] == 1

    def test_dict_with_union_values(self):
        """Test dict[str, Union[BaseModel, str, None]] parameter conversion."""

        @tool(description="Process dictionary with mixed value types")
        def process_mixed_dict(data: dict[str, UserModel | str | None]) -> dict:
            result = {"users": {}, "messages": {}, "nulls": []}

            for key, value in data.items():
                if isinstance(value, UserModel):
                    result["users"][key] = {"name": value.name, "age": value.age}
                elif isinstance(value, str):
                    result["messages"][key] = value
                elif value is None:
                    result["nulls"].append(key)

            return result

        mixed_dict = {
            "user1": {"name": "Alice", "age": 30},
            "msg1": "Hello",
            "empty": None,
            "user2": {"name": "Bob", "age": 25},
            "msg2": "World",
        }

        result = process_mixed_dict(mixed_dict)

        assert len(result["users"]) == 2
        assert result["users"]["user1"] == {"name": "Alice", "age": 30}
        assert result["users"]["user2"] == {"name": "Bob", "age": 25}
        assert result["messages"] == {"msg1": "Hello", "msg2": "World"}
        assert result["nulls"] == ["empty"]

    def test_complex_nested_union_types(self):
        """Test deeply nested union types: list[dict[str, Union[BaseModel, str]]]."""

        @tool(description="Process complex nested structure")
        def process_complex_data(
            items: list[dict[str, UserModel | ContactModel | str]],
        ) -> dict:
            result = {"entries": []}

            for item_dict in items:
                entry = {}
                for key, value in item_dict.items():
                    if isinstance(value, UserModel):
                        entry[key] = {"type": "user", "name": value.name}
                    elif isinstance(value, ContactModel):
                        entry[key] = {"type": "contact", "email": value.email}
                    elif isinstance(value, str):
                        entry[key] = {"type": "string", "value": value}
                result["entries"].append(entry)

            return result

        complex_data = [
            {
                "user": {"name": "John", "age": 30},
                "contact": {"email": "john@example.com", "phone": "123-456-7890"},
                "note": "Important client",
            },
            {
                "user": {"name": "Jane", "age": 25},
                "status": "Active",
                "contact": {"email": "jane@example.com"},
            },
        ]

        result = process_complex_data(complex_data)

        assert len(result["entries"]) == 2

        # First entry
        entry1 = result["entries"][0]
        assert entry1["user"]["type"] == "user"
        assert entry1["user"]["name"] == "John"
        assert entry1["contact"]["type"] == "contact"
        assert entry1["contact"]["email"] == "john@example.com"
        assert entry1["note"]["type"] == "string"
        assert entry1["note"]["value"] == "Important client"

        # Second entry
        entry2 = result["entries"][1]
        assert entry2["user"]["type"] == "user"
        assert entry2["user"]["name"] == "Jane"
        assert entry2["status"]["type"] == "string"
        assert entry2["status"]["value"] == "Active"
        assert entry2["contact"]["type"] == "contact"
        assert entry2["contact"]["email"] == "jane@example.com"

    def test_union_with_enum_conversion(self):
        """Test Union[Enum, str] parameter conversion."""

        @tool(description="Process status that can be enum or string")
        def process_status(status: StatusEnum | str) -> dict:
            if isinstance(status, StatusEnum):
                return {"type": "enum", "value": status.value, "name": status.name}
            else:
                return {"type": "string", "value": status}

        # Test with string that matches str type in union
        result1 = process_status("active")
        assert result1 == {"type": "string", "value": "active"}

        # Test with actual enum instance
        result2 = process_status(StatusEnum.PENDING)
        assert result2 == {"type": "enum", "value": "pending", "name": "PENDING"}

        # Test with string that doesn't match enum (should stay string)
        result3 = process_status("unknown_status")
        assert result3 == {"type": "string", "value": "unknown_status"}

    def test_dict_with_enum_keys_and_union_values(self):
        """Test dict[Enum, Union[BaseModel, str]] parameter conversion."""

        @tool(description="Process status mapping with mixed values")
        def process_status_mapping(
            mapping: dict[StatusEnum, UserModel | str],
        ) -> dict:
            result = {}
            for status, value in mapping.items():
                if isinstance(value, UserModel):
                    result[status.value] = {"type": "user", "name": value.name}
                else:
                    result[status.value] = {"type": "string", "value": value}
            return result

        status_data = {
            "active": {"name": "John", "age": 30},
            "PENDING": "Waiting for approval",
            "inactive": {"name": "Jane", "age": 25},
        }

        result = process_status_mapping(status_data)

        assert result["active"]["type"] == "user"
        assert result["active"]["name"] == "John"
        assert result["pending"]["type"] == "string"
        assert result["pending"]["value"] == "Waiting for approval"
        assert result["inactive"]["type"] == "user"
        assert result["inactive"]["name"] == "Jane"

    def test_union_fallback_behavior(self):
        """Test that union types fall back gracefully when conversion fails."""

        @tool(description="Process data with fallback behavior")
        def process_with_fallback(data: UserModel | str) -> dict:
            if isinstance(data, UserModel):
                return {"type": "user", "name": data.name}
            else:
                return {"type": "other", "value": str(data)}

        # Test with dict that can't convert to UserModel (missing required fields)
        invalid_user_dict = {"invalid": "data", "missing": "required_fields"}
        result = process_with_fallback(invalid_user_dict)

        # Should fall back to treating it as "other" since conversion failed
        assert result["type"] == "other"
        assert "invalid" in result["value"]

    def test_multiple_union_parameters(self):
        """Test function with multiple union type parameters."""

        @tool(description="Process multiple union parameters")
        def process_multiple_unions(
            user_or_name: UserModel | str,
            contact_or_email: ContactModel | str | None,
            status: StatusEnum | str = "pending",
        ) -> dict:
            result = {}

            # Process user_or_name
            if isinstance(user_or_name, UserModel):
                result["user"] = {"name": user_or_name.name, "age": user_or_name.age}
            else:
                result["user"] = {"name": user_or_name, "age": None}

            # Process contact_or_email
            if isinstance(contact_or_email, ContactModel):
                result["contact"] = contact_or_email.email
            elif contact_or_email is None:
                result["contact"] = None
            else:
                result["contact"] = contact_or_email

            # Process status
            if isinstance(status, StatusEnum):
                result["status"] = status.value
            else:
                result["status"] = status

            return result

        # Test with mixed parameter types
        result = process_multiple_unions(
            user_or_name={"name": "Alice", "age": 30},
            contact_or_email={"email": "alice@example.com", "phone": "123-456-7890"},
            status="active",
        )

        assert result["user"]["name"] == "Alice"
        assert result["user"]["age"] == 30
        assert result["contact"] == "alice@example.com"
        assert result["status"] == "active"

    def test_tool_registry_with_union_functions(self):
        """Test that tools with union types can be registered and work in registry."""

        @tool(description="Handle mixed user data")
        def handle_user_data(data: UserModel | str) -> str:
            if isinstance(data, UserModel):
                return f"User: {data.name}"
            return f"Message: {data}"

        @tool(description="Process optional contact")
        def process_contact(contact: ContactModel | None = None) -> dict:
            if contact is None:
                return {"has_contact": False}
            return {"has_contact": True, "email": contact.email}

        with patch("tool_registry_module.tool_registry.openai", create=True):
            registry = build_registry_openai([handle_user_data, process_contact])

            assert len(registry) == 2
            assert "handle_user_data" in registry
            assert "process_contact" in registry

            # Test that the tools work correctly from the registry
            user_tool = registry["handle_user_data"]["tool"]
            contact_tool = registry["process_contact"]["tool"]

            # Test user tool with dict input
            result1 = user_tool({"name": "Bob", "age": 35})
            assert result1 == "User: Bob"

            # Test user tool with string input
            result2 = user_tool("Hello World")
            assert result2 == "Message: Hello World"

            # Test contact tool with dict input
            result3 = contact_tool({"email": "test@example.com"})
            assert result3 == {"has_contact": True, "email": "test@example.com"}

            # Test contact tool with None input
            result4 = contact_tool(None)
            assert result4 == {"has_contact": False}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
