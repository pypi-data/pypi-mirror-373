from abc import ABC
from typing import Dict, Any, Optional, ClassVar, List
from datetime import datetime
from pydantic import BaseModel
import re
import yaml
import json


class FyodorovBaseModel(BaseModel, ABC):
    """
    Base model class that provides common functionality for all fyodorov-llm-agents models.

    Provides:
    - Standardized to_dict() method
    - Common validation patterns
    - YAML serialization/deserialization
    - Resource dictionary generation
    - Field validation utilities
    """

    # Common fields that most models have
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    # Validation constants (can be overridden by subclasses)
    VALID_CHARACTERS_REGEX: ClassVar[str] = r'^[a-zA-Z0-9\s.,!?:;\'"-_]+$'
    MAX_NAME_LENGTH: ClassVar[int] = 80
    MAX_DESCRIPTION_LENGTH: ClassVar[int] = 280

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

    def to_dict(
        self, exclude_none: bool = True, exclude_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Convert model to dictionary representation for database operations.

        Args:
            exclude_none: Whether to exclude None values
            exclude_fields: List of field names to exclude

        Returns:
            Dictionary representation of the model
        """
        if exclude_fields is None:
            exclude_fields = []

        data = self.dict(exclude_none=exclude_none)

        # Remove excluded fields
        for field in exclude_fields:
            data.pop(field, None)

        # Convert datetime objects and other complex types for database compatibility
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif hasattr(value, "to_dict"):
                # Handle nested models that have to_dict method
                data[key] = value.to_dict()
            elif isinstance(value, list) and value and hasattr(value[0], "to_dict"):
                # Handle lists of models
                data[key] = [
                    item.to_dict() if hasattr(item, "to_dict") else item
                    for item in value
                ]

        return data

    def resource_dict(self) -> Dict[str, Any]:
        """
        Generate a simplified dictionary for API responses.
        Typically includes id, name, description, and other key fields.

        Should be overridden by subclasses to include relevant fields.
        """
        base_resource = {}

        if hasattr(self, "id") and self.id is not None:
            base_resource["id"] = self.id
        if hasattr(self, "name") and self.name is not None:
            base_resource["name"] = self.name
        if hasattr(self, "description") and self.description is not None:
            base_resource["description"] = self.description
        if hasattr(self, "created_at") and self.created_at is not None:
            base_resource["created_at"] = self.created_at

        return base_resource

    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs):
        """
        Create model instance from dictionary.

        Args:
            data: Dictionary with model data
            **kwargs: Additional arguments passed to constructor

        Returns:
            Model instance
        """
        # Convert string dates back to datetime objects if needed
        processed_data = data.copy()

        for key, value in processed_data.items():
            if isinstance(value, str) and key.endswith("_at"):
                try:
                    processed_data[key] = datetime.fromisoformat(
                        value.replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    pass  # Keep original value if conversion fails

        # Merge any additional kwargs
        processed_data.update(kwargs)

        return cls(**processed_data)

    @classmethod
    def from_yaml(cls, yaml_str: str):
        """
        Create model instance from YAML string.

        Args:
            yaml_str: YAML string representation

        Returns:
            Model instance
        """
        if not yaml_str:
            raise ValueError("YAML string is required")

        try:
            data = yaml.safe_load(yaml_str)
            if not isinstance(data, dict):
                raise ValueError("YAML string must represent a dictionary")

            instance = cls.from_dict(data)
            if hasattr(instance, "validate"):
                instance.validate()

            return instance
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")

    def to_yaml(self) -> str:
        """
        Convert model to YAML string representation.

        Returns:
            YAML string
        """
        data = self.to_dict(exclude_none=True)
        return yaml.dump(
            data, default_flow_style=False, sort_keys=False, allow_unicode=True
        )

    def to_json(self, **kwargs) -> str:
        """
        Convert model to JSON string representation.

        Returns:
            JSON string
        """
        data = self.to_dict(exclude_none=True)
        return json.dumps(data, default=str, ensure_ascii=False, **kwargs)

    def validate(self) -> bool:
        """
        Perform model-specific validation.
        Should be overridden by subclasses to implement specific validation logic.

        Returns:
            True if validation passes

        Raises:
            ValueError: If validation fails
        """
        return True

    # Common validation methods
    @classmethod
    def validate_text_field(
        cls, value: str, field_name: str, max_length: int = None, required: bool = True
    ) -> str:
        """
        Validate a text field with common rules.

        Args:
            value: The value to validate
            field_name: Name of the field for error messages
            max_length: Maximum allowed length
            required: Whether the field is required

        Returns:
            The validated value

        Raises:
            ValueError: If validation fails
        """
        if not value and required:
            raise ValueError(f"{field_name} is required")

        if value and max_length and len(value) > max_length:
            raise ValueError(f"{field_name} exceeds maximum length of {max_length}")

        if value and not re.match(cls.VALID_CHARACTERS_REGEX, value):
            raise ValueError(f"{field_name} contains invalid characters")

        return value

    @classmethod
    def validate_name(cls, name: str) -> str:
        """Validate a name field"""
        return cls.validate_text_field(name, "Name", cls.MAX_NAME_LENGTH, required=True)

    @classmethod
    def validate_description(cls, description: str, required: bool = True) -> str:
        """Validate a description field"""
        return cls.validate_text_field(
            description, "Description", cls.MAX_DESCRIPTION_LENGTH, required=required
        )

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update model fields from dictionary data.

        Args:
            data: Dictionary with updated field values
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def copy_with_updates(self, **updates) -> "FyodorovBaseModel":
        """
        Create a copy of the model with updated fields.

        Args:
            **updates: Field updates to apply

        Returns:
            New model instance with updates applied
        """
        current_data = self.to_dict(exclude_none=False)
        current_data.update(updates)
        return self.__class__.from_dict(current_data)

    def merge_from(self, other: "FyodorovBaseModel") -> None:
        """
        Merge fields from another model instance.

        Args:
            other: Model instance to merge from
        """
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot merge from {type(other).__name__} to {type(self).__name__}"
            )

        other_data = other.to_dict(
            exclude_none=True, exclude_fields=["id", "created_at"]
        )
        self.update_from_dict(other_data)

    def __str__(self) -> str:
        """String representation of the model"""
        class_name = self.__class__.__name__
        if hasattr(self, "name"):
            return f"{class_name}(id={self.id}, name='{self.name}')"
        elif hasattr(self, "id"):
            return f"{class_name}(id={self.id})"
        else:
            return f"{class_name}()"

    def __repr__(self) -> str:
        """Detailed string representation of the model"""
        try:
            data = self.to_dict(exclude_none=True)
            # Limit data size for readability
            if len(str(data)) > 200:
                key_fields = {
                    k: v for k, v in data.items() if k in ["id", "name", "created_at"]
                }
                return f"{self.__class__.__name__}({key_fields}...)"
            return f"{self.__class__.__name__}({data})"
        except Exception:
            return f"{self.__class__.__name__}(<serialization_error>)"
