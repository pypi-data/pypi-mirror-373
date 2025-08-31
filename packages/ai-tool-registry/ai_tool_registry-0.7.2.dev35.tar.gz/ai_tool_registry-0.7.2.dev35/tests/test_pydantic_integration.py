"""
Tests for Pydantic model integration and validation.

This module focuses specifically on testing the integration between the tool registry
and Pydantic models, including complex nested structures and validation scenarios.
"""

from datetime import datetime
from enum import Enum
from typing import Any

import pytest
from pydantic import BaseModel, Field, ValidationError

from tool_registry_module import tool


class Priority(str, Enum):
    """Test enum for priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Address(BaseModel):
    """Nested Pydantic model for testing."""

    street: str
    city: str
    state: str
    zip_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")


class ContactInfo(BaseModel):
    """Contact information model."""

    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    phone: str | None = None
    address: Address | None = None


class Task(BaseModel):
    """Complex task model for testing."""

    id: int
    title: str
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    due_date: datetime | None = None
    assignee: ContactInfo | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TestPydanticIntegration:
    """Test Pydantic model integration with tools."""

    def test_simple_pydantic_model(self):
        """Test simple Pydantic model parameter."""

        @tool(description="Process contact information")
        def process_contact(contact: ContactInfo) -> str:
            return f"Contact: {contact.email}"

        # Test with dictionary
        result = process_contact(
            contact={"email": "test@example.com", "phone": "555-1234"}
        )
        assert result == "Contact: test@example.com"

        # Test with model instance
        contact = ContactInfo(email="user@domain.com")
        result = process_contact(contact=contact)
        assert result == "Contact: user@domain.com"

    def test_nested_pydantic_models(self):
        """Test nested Pydantic models."""

        @tool(description="Create user profile")
        def create_profile(contact: ContactInfo) -> dict[str, Any]:
            return {
                "email": contact.email,
                "has_phone": contact.phone is not None,
                "has_address": contact.address is not None,
                "city": contact.address.city if contact.address else None,
            }

        # Test with nested data
        result = create_profile(
            contact={
                "email": "john@example.com",
                "phone": "555-0123",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip_code": "12345",
                },
            }
        )

        assert result["email"] == "john@example.com"
        assert result["has_phone"] is True
        assert result["has_address"] is True
        assert result["city"] == "Anytown"

    def test_complex_pydantic_model(self):
        """Test complex Pydantic model with various field types."""

        @tool(description="Process task")
        def process_task(task: Task) -> dict[str, Any]:
            return {
                "task_id": task.id,
                "title": task.title,
                "priority": task.priority.value,
                "tag_count": len(task.tags),
                "has_assignee": task.assignee is not None,
                "metadata_keys": list(task.metadata.keys()),
            }

        # Test with complex nested data
        task_data = {
            "id": 123,
            "title": "Test Task",
            "description": "A test task for validation",
            "priority": "high",
            "assignee": {"email": "assignee@example.com", "phone": "555-9876"},
            "tags": ["urgent", "testing", "validation"],
            "metadata": {
                "created_by": "system",
                "project_id": 456,
                "estimated_hours": 8.5,
            },
        }

        result = process_task(task=task_data)

        assert result["task_id"] == 123
        assert result["title"] == "Test Task"
        assert result["priority"] == "high"
        assert result["tag_count"] == 3
        assert result["has_assignee"] is True
        assert "created_by" in result["metadata_keys"]

    def test_pydantic_validation_errors(self):
        """Test that Pydantic validation errors are properly handled."""

        @tool(description="Validate contact")
        def validate_contact(contact: ContactInfo) -> str:
            return f"Valid contact: {contact.email}"

        # Test with invalid email (should raise ValueError during conversion)
        with pytest.raises(ValueError):
            validate_contact(contact={"email": "invalid-email"})

    def test_optional_pydantic_fields(self):
        """Test handling of optional Pydantic fields."""

        @tool(description="Process optional task fields")
        def process_optional_task(task: Task) -> dict[str, Any]:
            return {
                "has_description": task.description is not None,
                "has_due_date": task.due_date is not None,
                "has_assignee": task.assignee is not None,
                "tag_count": len(task.tags),
            }

        # Test with minimal required fields
        minimal_task = {"id": 1, "title": "Minimal Task"}

        result = process_optional_task(task=minimal_task)
        assert result["has_description"] is False
        assert result["has_due_date"] is False
        assert result["has_assignee"] is False
        assert result["tag_count"] == 0

    def test_pydantic_field_validation(self):
        """Test Pydantic field validation with patterns."""

        @tool(description="Create address")
        def create_address(addr: Address) -> str:
            return f"{addr.street}, {addr.city}, {addr.state} {addr.zip_code}"

        # Test with valid zip code
        result = create_address(
            addr={
                "street": "123 Oak St",
                "city": "Springfield",
                "state": "IL",
                "zip_code": "62701",
            }
        )
        assert "62701" in result

        # Test with extended zip code
        result = create_address(
            addr={
                "street": "456 Pine Ave",
                "city": "Portland",
                "state": "OR",
                "zip_code": "97201-1234",
            }
        )
        assert "97201-1234" in result

        # Test with invalid zip code (should raise ValidationError)
        with pytest.raises(ValidationError):
            create_address(
                addr={
                    "street": "789 Elm St",
                    "city": "Boston",
                    "state": "MA",
                    "zip_code": "invalid",
                }
            )

    def test_list_of_pydantic_models(self):
        """Test handling of lists containing Pydantic models."""

        @tool(description="Process multiple contacts")
        def process_contacts(contacts: list[ContactInfo]) -> dict[str, Any]:
            emails = [contact.email for contact in contacts]
            phone_count = sum(1 for contact in contacts if contact.phone)
            return {
                "total_contacts": len(contacts),
                "emails": emails,
                "contacts_with_phone": phone_count,
            }

        contacts_data = [
            {"email": "alice@example.com", "phone": "555-1111"},
            {"email": "bob@example.com"},
            {"email": "charlie@example.com", "phone": "555-3333"},
        ]

        result = process_contacts(contacts=contacts_data)
        assert result["total_contacts"] == 3
        assert "alice@example.com" in result["emails"]
        assert result["contacts_with_phone"] == 2

    def test_enum_field_handling(self):
        """Test handling of enum fields in Pydantic models."""

        @tool(description="Filter tasks by priority")
        def filter_by_priority(priority: Priority) -> str:
            return f"Filtering tasks with priority: {priority.value}"

        # Test with enum value
        result = filter_by_priority(priority=Priority.HIGH)
        assert result == "Filtering tasks with priority: high"

        # Test with string value (should be converted to enum)
        result = filter_by_priority(priority="medium")
        assert result == "Filtering tasks with priority: medium"

    def test_mixed_pydantic_and_simple_types(self):
        """Test tools with both Pydantic models and simple types."""

        @tool(description="Update task with new data")
        def update_task(
            task: Task,
            new_title: str | None = None,
            add_tags: list[str] | None = None,
            increment_id: bool = False,
        ) -> dict[str, Any]:
            if add_tags is None:
                add_tags = []

            updated_task = task.model_copy()
            if new_title:
                updated_task.title = new_title
            updated_task.tags.extend(add_tags)
            if increment_id:
                updated_task.id += 1

            return {
                "id": updated_task.id,
                "title": updated_task.title,
                "tag_count": len(updated_task.tags),
            }

        initial_task = {"id": 100, "title": "Original Task", "tags": ["existing"]}

        result = update_task(
            task=initial_task,
            new_title="Updated Task",
            add_tags=["new", "updated"],
            increment_id=True,
        )

        assert result["id"] == 101
        assert result["title"] == "Updated Task"
        assert result["tag_count"] == 3  # existing + new + updated


class TestSchemaGenerationWithPydantic:
    """Test schema generation for Pydantic models."""

    def test_pydantic_model_schema_generation(self):
        """Test that Pydantic models generate proper schemas."""

        @tool(description="Process user task")
        def process_user_task(task: Task, user_id: int) -> str:
            return f"Task {task.id} for user {user_id}"

        schema = getattr(process_user_task, "_input_schema")
        properties = schema["properties"]

        # Check that both parameters are in schema
        assert "task" in properties
        assert "user_id" in properties

        # Check that task parameter has complex schema
        task_schema = properties["task"]
        # Should reference definitions or have nested properties
        assert (
            "$defs" in schema or "definitions" in schema or "properties" in task_schema
        )

    def test_nested_model_schema_references(self):
        """Test that nested models create proper schema references."""

        @tool(description="Create full contact")
        def create_full_contact(contact: ContactInfo) -> dict[str, Any]:
            return {"processed": True}

        schema = getattr(create_full_contact, "_input_schema")

        # Should have definitions/defs for nested models
        has_definitions = (
            "$defs" in schema
            or "definitions" in schema
            or any(
                "$ref" in str(prop) for prop in schema.get("properties", {}).values()
            )
        )
        assert has_definitions, "Schema should include definitions for nested models"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
