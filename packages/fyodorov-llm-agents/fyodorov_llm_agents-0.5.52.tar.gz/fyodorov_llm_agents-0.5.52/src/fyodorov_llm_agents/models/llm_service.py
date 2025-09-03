from datetime import datetime
from typing import Dict, Any, List, Optional

from fyodorov_llm_agents.base_service import BaseService
from fyodorov_llm_agents.providers.provider_service import Provider
from fyodorov_llm_agents.models.llm_model import LLMModel


class LLMService(BaseService[LLMModel]):
    def __init__(self, access_token: Optional[str] = None, **kwargs) -> None:
        super().__init__("models", access_token, **kwargs)

    def _dict_to_model(self, data: Dict[str, Any]) -> LLMModel:
        return LLMModel.from_dict(data)

    def _model_to_dict(self, model: LLMModel) -> Dict[str, Any]:
        return model.to_dict()

    async def save_model_in_db(
        self, user_id: str, model: LLMModel
    ) -> LLMModel:
        """Save model in database with provider resolution"""
        # Get or create provider
        provider_service = Provider()
        provider = await provider_service.get_provider(
            self.access_token, user_id, model.provider
        )

        # Update model with provider ID
        model.provider = provider.id

        # Use base service upsert method
        return await self.upsert_in_db(model, access_token, user_id)

    async def update_model_in_db(
        self, access_token: str, user_id: str, name: str, update_data: Dict[str, Any]
    ) -> LLMModel:
        """Update model by name and user_id"""
        if not user_id or not name:
            raise ValueError("Model name and User ID are required")

        # Find existing model first
        existing_model = await self.get_model_by_name_and_user(access_token, user_id, name)
        if not existing_model:
            raise ValueError(f"Model '{name}' not found for user {user_id}")

        # Update the model
        return await self.update_in_db(existing_model.id, update_data, access_token)

    async def update_model_by_id_in_db(
        self, access_token: str, id: str, update_data: Dict[str, Any]
    ) -> LLMModel:
        """Update model by ID"""
        if not id:
            raise ValueError("Model ID is required")
        return await self.update_in_db(id, update_data, access_token)

    async def get_model_by_name_and_user(
        self, access_token: str, user_id: str, name: str
    ) -> Optional[LLMModel]:
        """Get model by name and user_id"""
        if not user_id or not name:
            raise ValueError("Model name and User ID are required")

        filters = {"user_id": user_id, "name": name}
        models = await self.get_all_in_db(
            limit=1,
            user_id=None,
            filters=filters,
            access_token=access_token,
        )
        return models[0] if models else None

    async def get_models_by_user(
        self,
        access_token: str,
        user_id: str,
        limit: int = 10,
        created_at_lt: datetime | None = None,
    ) -> List[LLMModel]:
        """Get all models for a user"""
        if created_at_lt is None:
            created_at_lt = datetime.now()
        return await self.get_all_in_db(
            limit=limit,
            created_at_lt=created_at_lt,
            user_id=user_id,
            access_token=access_token,
        )

    # Convenience methods migrated from legacy LLM wrapper
    async def get_model(
        self,
        access_token: str | None = None,
        user_id: str | None = None,
        name: str | None = None,
        id: str | None = None,
    ) -> Optional[LLMModel]:
        if id:
            return await self.get_in_db(id, access_token)
        if name and user_id:
            return await self.get_model_by_name_and_user(access_token, user_id, name)
        raise ValueError("Either 'id' or both 'name' and 'user_id' must be provided")

    async def get_models(
        self,
        access_token: str,
        user_id: str,
        limit: int = 10,
        created_at_lt: datetime | None = None,
    ) -> List[LLMModel]:
        return await self.get_models_by_user(access_token, user_id, limit, created_at_lt)

    async def delete_model_in_db(self, access_token: str, id: str) -> bool:
        return await self.delete_in_db(id, access_token)
