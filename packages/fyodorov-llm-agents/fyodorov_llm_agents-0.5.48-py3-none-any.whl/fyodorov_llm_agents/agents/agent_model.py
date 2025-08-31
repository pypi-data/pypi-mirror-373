import re
import requests
import yaml
from pydantic import HttpUrl
from typing import Optional, Dict, Any, ClassVar
from fyodorov_llm_agents.base_model import FyodorovBaseModel
from fyodorov_llm_agents.models.llm_model import LLMModel
from fyodorov_llm_agents.providers.provider_model import ProviderModel


class Agent(FyodorovBaseModel):
    # Override class constants for validation
    MAX_DESCRIPTION_LENGTH: ClassVar[int] = 280
    MAX_NAME_LENGTH: ClassVar[int] = 80
    VALID_CHARACTERS_REGEX: ClassVar[str] = r'^[a-zA-Z0-9\s.,!?:;\'"-_]+$'

    user_id: Optional[str] = None
    api_key: str | None = None
    api_url: HttpUrl | None = None
    tools: list[str] = []
    rag: list[dict] = []
    model_id: int | None = None
    name: str = "My Agent"
    description: str = "My Agent Description"
    prompt: str = "My Prompt"
    prompt_size: int = 10000
    public: bool | None = False

    def validate(self) -> bool:
        """Validate agent fields"""
        try:
            self.validate_name(self.name)
            self.validate_description(self.description)
            self.validate_prompt(self.prompt, self.prompt_size)
            return super().validate()
        except ValueError:
            raise

    def resource_dict(self) -> Dict[str, Any]:
        """Generate resource dictionary for API responses"""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "name": self.name,
            "description": self.description,
        }

    @classmethod
    def validate_name(cls, name: str) -> str:
        if not name:
            raise ValueError("Name is required")
        if len(name) > cls.MAX_NAME_LENGTH:
            raise ValueError("Name exceeds maximum length")
        if not re.match(cls.VALID_CHARACTERS_REGEX, name):
            raise ValueError("Name contains invalid characters")
        return name

    @classmethod
    def validate_description(cls, description: str) -> str:
        if not description:
            raise ValueError("Description is required")
        if len(description) > cls.MAX_DESCRIPTION_LENGTH:
            raise ValueError("Description exceeds maximum length")
        if not re.match(cls.VALID_CHARACTERS_REGEX, description):
            raise ValueError("Description contains invalid characters")
        return description

    @classmethod
    def validate_prompt(cls, prompt: str, prompt_size: int) -> str:
        """Validate agent prompt"""
        if not prompt:
            raise ValueError("Prompt is required")
        if len(prompt) > prompt_size:
            raise ValueError("Prompt exceeds maximum length")
        return prompt

    def to_dict(
        self, exclude_none: bool = True, exclude_fields: list = None
    ) -> Dict[str, Any]:
        """Convert agent to dictionary, handling model reference"""
        if exclude_fields is None:
            exclude_fields = []

        # Always exclude the model object to avoid serialization issues
        exclude_fields = exclude_fields + ["model", "provider"]

        data = super().to_dict(exclude_none=exclude_none, exclude_fields=exclude_fields)

        # Add model_id if model is present
        if self.model_id:
            data["model_id"] = self.model_id

        # Convert HttpUrl to string
        if "api_url" in data and data["api_url"] is not None:
            data["api_url"] = str(data["api_url"])

        return data

    @staticmethod
    def call_api(url: str = "", method: str = "GET", body: dict = {}) -> dict:
        """Make API call - utility method"""
        if not url:
            raise ValueError("API URL is required")
        try:
            res = requests.request(
                method=method,
                url=url,
                json=body,
            )
            if res.status_code != 200:
                raise ValueError(
                    f"Error fetching API json from {url}: {res.status_code}"
                )
            json = res.json()
            return json
        except Exception as e:
            print(f"Error calling API: {e}")
            raise

    @classmethod
    def from_yaml(cls, yaml_str: str):
        """Instantiate Agent from YAML."""
        if not yaml_str:
            raise ValueError("YAML string is required")
        agent_dict = yaml.safe_load(yaml_str)
        agent = Agent(**agent_dict)
        agent.validate()
        return agent

    @classmethod
    async def from_dict(cls, agent_dict: Dict[str, Any], user_id: str = None, **kwargs):
        """Create Agent from dictionary with model resolution"""
        if not agent_dict:
            raise ValueError("Agent dict is required")

        # Import here to avoid circular imports
        from fyodorov_llm_agents.models.llm_service import LLMService

        processed_data = agent_dict.copy()

        # Handle model reference
        if "model" in processed_data and isinstance(processed_data["model"], str):
            llm_service = LLMService()
            model = await llm_service.get_model(user_id=user_id, id=processed_data["model"]) 
            if model is None:
                name = processed_data["name"].lower().replace(" ", "_")+"_model"
                model = await llm_service.save_model_in_db(
                    access_token=None,
                    user_id=user_id,
                    model=LLMModel.from_dict(
                        {
                            "name": name, 
                            "provider": "openai"
                        }
                    ),
                )
            processed_data["model"] = model
            processed_data["model_id"] = model.id

        # Set user_id if provided
        if user_id:
            processed_data["user_id"] = user_id

        # Remove debug print for production
        # print(f"Agent dict: {processed_data}")

        # Create and validate agent
        agent = cls(**processed_data)
        agent.validate()
        return agent
