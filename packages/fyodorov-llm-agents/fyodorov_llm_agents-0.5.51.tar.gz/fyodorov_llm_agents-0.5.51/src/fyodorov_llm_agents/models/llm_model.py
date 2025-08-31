from typing import Dict, Any, List, Optional
from fyodorov_llm_agents.base_model import FyodorovBaseModel


class LLMModel(FyodorovBaseModel):
    name: str
    provider: int | None = None
    params: dict | None = None
    mode: str = "chat"
    base_model: str
    input_cost_per_token: float | None = None
    output_cost_per_token: float | None = None
    max_tokens: int | None = None

    def to_dict(
        self, exclude_none: bool = True, exclude_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Convert LLM model to dictionary"""
        data = super().to_dict(exclude_none=exclude_none, exclude_fields=exclude_fields)
        # Remove debug print for production
        # print(f"LLMModel to_dict: {data}")
        return data

    def resource_dict(self) -> Dict[str, Any]:
        """Generate resource dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs) -> "LLMModel":
        """Create LLMModel from dictionary with special handling for nested data"""
        processed_data = data.copy()

        # Handle model_info nested structure
        if "model_info" in data and isinstance(data["model_info"], dict):
            if "base_model" in data["model_info"]:
                processed_data["base_model"] = data["model_info"]["base_model"]

        # Ensure required fields are present
        if "name" not in processed_data:
            raise ValueError("LLMModel requires a name")
        if "provider" not in processed_data:
            raise ValueError("LLMModel requires a provider")

        # Remove debug print for production
        # print('Input dict for LLMModel:', processed_data)
        return super().from_dict(processed_data, **kwargs)

    def validate(self) -> bool:
        """Validate LLM model fields"""
        if not self.name:
            raise ValueError("LLM model name is required")
        if not self.base_model:
            raise ValueError("LLM base_model is required")
        return super().validate()
