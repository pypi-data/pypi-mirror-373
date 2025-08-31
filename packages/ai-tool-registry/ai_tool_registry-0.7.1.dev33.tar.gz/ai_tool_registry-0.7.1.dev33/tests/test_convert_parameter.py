"""
Tests for _convert_parameter function with complex mixed types.

This module tests the _convert_parameter function's ability to handle complex
nested types including unions with BaseModel, str, None and dictionaries
with mixed value types.
"""

from enum import Enum
from typing import Union

import pytest
from pydantic import BaseModel, ValidationError

from tool_registry_module.tool_registry import _convert_parameter


class UserModel(BaseModel):
    name: str
    age: int


class AddressModel(BaseModel):
    street: str
    city: str
    zipcode: str


class StatusEnum(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class TestConvertParameter:
    """Test _convert_parameter function with complex mixed types."""

    def test_simple_types(self):
        """Test conversion of basic types."""
        assert _convert_parameter(int, "42") == 42
        assert _convert_parameter(float, "3.14") == 3.14
        assert _convert_parameter(str, 123) == "123"
        assert _convert_parameter(bool, "true") is True

    def test_none_values(self):
        """Test handling of None values."""
        assert _convert_parameter(str, None) is None
        assert _convert_parameter(int, None) is None
        assert _convert_parameter(UserModel, None) is None

    def test_pydantic_model_conversion(self):
        """Test conversion of dictionaries to Pydantic models."""
        user_dict = {"name": "John", "age": 30}
        result = _convert_parameter(UserModel, user_dict)

        assert isinstance(result, UserModel)
        assert result.name == "John"
        assert result.age == 30

    def test_pydantic_model_passthrough(self):
        """Test that existing Pydantic models are passed through unchanged."""
        user = UserModel(name="Alice", age=25)
        result = _convert_parameter(UserModel, user)

        assert result is user

    def test_enum_conversion_by_value(self):
        """Test enum conversion using string values."""
        result = _convert_parameter(StatusEnum, "active")
        assert result == StatusEnum.ACTIVE

    def test_enum_conversion_by_name(self):
        """Test enum conversion using enum names (case insensitive)."""
        result = _convert_parameter(StatusEnum, "PENDING")
        assert result == StatusEnum.PENDING

        result = _convert_parameter(StatusEnum, "inactive")
        assert result == StatusEnum.INACTIVE

    def test_enum_invalid_value(self):
        """Test enum conversion with invalid values."""
        with pytest.raises(ValueError, match="Invalid enum value 'invalid'"):
            _convert_parameter(StatusEnum, "invalid")

    def test_list_with_pydantic_models(self):
        """Test conversion of list containing dictionaries to Pydantic models."""
        users_data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = _convert_parameter(list[UserModel], users_data)

        assert len(result) == 2
        assert all(isinstance(user, UserModel) for user in result)
        assert result[0].name == "John"
        assert result[1].name == "Jane"

    def test_list_with_mixed_union_types(self):
        """Test list[BaseModel | str | None] - complex union in list."""
        mixed_data = [
            {"name": "John", "age": 30},  # Should become UserModel
            "just a string",  # Should stay string
            None,  # Should stay None
            {"name": "Jane", "age": 25},  # Should become UserModel
        ]

        result = _convert_parameter(list[UserModel | str | None], mixed_data)

        assert len(result) == 4
        assert isinstance(result[0], UserModel)
        assert result[0].name == "John"
        assert result[1] == "just a string"
        assert result[2] is None
        assert isinstance(result[3], UserModel)
        assert result[3].name == "Jane"

    def test_dict_with_pydantic_model_values(self):
        """Test dict[str, BaseModel] conversion."""
        users_dict = {
            "user1": {"name": "John", "age": 30},
            "user2": {"name": "Jane", "age": 25},
        }

        result = _convert_parameter(dict[str, UserModel], users_dict)

        assert len(result) == 2
        assert isinstance(result["user1"], UserModel)
        assert isinstance(result["user2"], UserModel)
        assert result["user1"].name == "John"
        assert result["user2"].name == "Jane"

    def test_dict_with_mixed_union_values(self):
        """Test dict[str, BaseModel | str | None] - complex union in dict values."""
        mixed_dict = {
            "user": {"name": "John", "age": 30},  # Should become UserModel
            "message": "hello world",  # Should stay string
            "empty": None,  # Should stay None
            "address": {
                "street": "123 Main",
                "city": "NYC",
                "zipcode": "10001",
            },  # Should become AddressModel if type allows
        }

        result = _convert_parameter(dict[str, UserModel | str | None], mixed_dict)

        assert len(result) == 4
        assert isinstance(result["user"], UserModel)
        assert result["user"].name == "John"
        assert result["message"] == "hello world"
        assert result["empty"] is None
        # Note: The address dict won't convert to UserModel due to different schema

    def test_nested_complex_types(self):
        """Test deeply nested complex types."""
        # Test list[dict[str, BaseModel | str]]
        complex_data = [
            {"user": {"name": "John", "age": 30}, "status": "active"},
            {"user": {"name": "Jane", "age": 25}, "status": "inactive"},
        ]

        result = _convert_parameter(list[dict[str, UserModel | str]], complex_data)

        assert len(result) == 2
        assert isinstance(result[0]["user"], UserModel)
        assert result[0]["user"].name == "John"
        assert result[0]["status"] == "active"
        assert isinstance(result[1]["user"], UserModel)
        assert result[1]["user"].name == "Jane"
        assert result[1]["status"] == "inactive"

    def test_union_type_fallback(self):
        """Test that union types fail strictly when no conversion is possible."""
        # Test Union[UserModel, int] with incompatible dict (no str in union)
        incompatible_dict = {"invalid": "data", "missing": "fields"}

        # Should attempt UserModel conversion first, fail, then try int, fail, then raise exception
        with pytest.raises((ValueError, ValidationError)):
            _convert_parameter(Union[UserModel, int], incompatible_dict)

    def test_union_with_none_handling(self):
        """Test Union types that include None."""
        # Test Union[UserModel, None]
        result1 = _convert_parameter(Union[UserModel, None], None)
        assert result1 is None

        result2 = _convert_parameter(
            Union[UserModel, None], {"name": "John", "age": 30}
        )
        assert isinstance(result2, UserModel)
        assert result2.name == "John"

    def test_passthrough_for_unsupported_types(self):
        """Test that unsupported types are passed through unchanged."""
        custom_object = object()
        result = _convert_parameter(object, custom_object)
        assert result is custom_object

    def test_list_without_type_args(self):
        """Test list without type arguments."""
        data = ["a", "b", "c"]
        result = _convert_parameter(list, data)
        assert result == data

    def test_dict_without_type_args(self):
        """Test dict without type arguments."""
        data = {"key": "value"}
        result = _convert_parameter(dict, data)
        assert result == data

    def test_list_with_enum_conversion(self):
        """Test list containing enums."""
        enum_data = ["active", "PENDING", "inactive"]
        result = _convert_parameter(list[StatusEnum], enum_data)

        assert len(result) == 3
        assert result[0] == StatusEnum.ACTIVE
        assert result[1] == StatusEnum.PENDING
        assert result[2] == StatusEnum.INACTIVE

    def test_dict_with_enum_keys_and_model_values(self):
        """Test dict[StatusEnum, UserModel] conversion."""
        mixed_dict = {
            "active": {"name": "John", "age": 30},
            "PENDING": {"name": "Jane", "age": 25},
        }

        result = _convert_parameter(dict[StatusEnum, UserModel], mixed_dict)

        assert len(result) == 2
        assert StatusEnum.ACTIVE in result
        assert StatusEnum.PENDING in result
        assert isinstance(result[StatusEnum.ACTIVE], UserModel)
        assert isinstance(result[StatusEnum.PENDING], UserModel)
        assert result[StatusEnum.ACTIVE].name == "John"
        assert result[StatusEnum.PENDING].name == "Jane"

    def test_triple_union_types(self):
        """Test Union[BaseModel, str, int] conversion."""
        # Test each type in the union
        result1 = _convert_parameter(
            Union[UserModel, str, int], {"name": "John", "age": 30}
        )
        assert isinstance(result1, UserModel)

        result2 = _convert_parameter(Union[UserModel, str, int], "hello")
        assert result2 == "hello"

        result3 = _convert_parameter(Union[UserModel, str, int], 42)
        assert result3 == 42  # int value stays int

    def test_error_propagation(self):
        """Test that conversion errors are properly propagated."""
        with pytest.raises(ValueError):
            _convert_parameter(int, "not_a_number")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
