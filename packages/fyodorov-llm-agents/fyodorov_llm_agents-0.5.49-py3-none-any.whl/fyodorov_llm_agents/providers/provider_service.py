from datetime import datetime
from typing import Dict, Any, Optional, List
from fyodorov_llm_agents.base_service import BaseService
from fyodorov_llm_agents.providers.provider_model import ProviderModel


class Provider(BaseService[ProviderModel]):
    def __init__(self, **kwargs):
        super().__init__("providers", access_token=None, **kwargs)

    def _dict_to_model(self, data: Dict[str, Any]) -> ProviderModel:
        """Convert dictionary from database to ProviderModel"""
        # Ensure id is properly converted
        if "id" in data:
            data["id"] = str(data["id"])
        return ProviderModel.from_dict(data)

    def _model_to_dict(self, model: ProviderModel) -> Dict[str, Any]:
        """Convert ProviderModel to dictionary for database"""
        return model.to_dict()

    async def update_provider_in_db(
        self, id: str, update: Dict[str, Any], access_token: Optional[str] = None
    ) -> ProviderModel:
        """Update provider in database"""
        return await self.update_in_db(id, update, access_token)

    async def save_provider_in_db(
        self, access_token: str, provider: ProviderModel, user_id: str
    ) -> ProviderModel:
        """Save provider in database with automatic URL setting"""
        try:
            print("Access token for saving provider:", access_token)

            # Set default API URLs based on provider name
            if not provider.api_url or provider.api_url == "":
                provider = self._set_default_api_url(provider)

            print("Setting provider api_url to", provider.api_url)

            # Check if provider already exists and merge if needed
            existing_provider = await self.get_provider(
                access_token, user_id, provider.name
            )
            if existing_provider:
                print("Provider already exists, merging with existing data")
                # Merge existing data with new data (new data takes precedence)
                existing_dict = existing_provider.to_dict()
                new_dict = provider.to_dict()
                merged_dict = {**existing_dict, **new_dict}
                provider = ProviderModel.from_dict(merged_dict)

            # Use upsert method from base class
            result = await self.upsert_in_db(provider, access_token, user_id)
            print("Saved provider", result)
            return result

        except Exception as e:
            # Handle duplicate key error
            if hasattr(e, "code") and e.code == "23505":
                print("Provider already exists")
                return provider
            raise e

    def _set_default_api_url(self, provider: ProviderModel) -> ProviderModel:
        """Set default API URL based on provider name"""
        name = provider.name.lower()
        url_map = {
            "openai": "https://api.openai.com/v1",
            "mistral": "https://api.mistral.ai/v1",
            "ollama": "http://localhost:11434/v1",
            "openrouter": "https://openrouter.ai/api/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models/",
            "google": "https://generativelanguage.googleapis.com/v1beta/models/",
        }

        if name in url_map:
            provider.api_url = url_map[name]
        else:
            raise ValueError("No URL provided when creating a provider")

        return provider

    async def delete_provider_in_db(
        self, id: str, access_token: Optional[str] = None
    ) -> bool:
        """Delete provider from database"""
        return await self.delete_in_db(id, access_token)

    async def get_provider_by_id(
        self, id: str
    ) -> Optional[ProviderModel]:
        """Get provider by ID"""
        print("[get_provider_by_id] Fetching provider by ID:", id)
        provider = await self.get_in_db(id, self.access_token)
        if provider:
            print("[get_provider_by_id] Fetched provider", provider)
        return provider

    async def get_provider(
        self, access_token: str, user_id: str, id: str
    ) -> Optional[ProviderModel]:
        """Get provider by name and user_id"""
        print(f"Getting provider with ID: {id} and user_id: {user_id}")
        if not id:
            raise ValueError("Provider name is required")
        if not user_id:
            raise ValueError("User ID is required")

        try:
            # Use the base class method with filters
            filters = {"user_id": user_id, "id": id}

            providers = await self.get_all_in_db(
                limit=1,
                user_id=None,  # Don't double-filter by user_id
                filters=filters,
                access_token=access_token,
            )

            if not providers:
                print("Provider not found")
                return None

            provider = providers[0]
            print("[get_provider] Fetched provider", provider)
            return provider

        except Exception as e:
            print("Error fetching provider", str(e))
            raise e

    async def get_or_create_provider(
        self, access_token: str, user_id: str, name: str
    ) -> ProviderModel:
        """Get existing provider or create new one"""
        try:
            provider = await self.get_provider(access_token, user_id, name)
            if provider:
                return provider
        except Exception as e:
            print(f"Error getting provider {name}: {e}")

        # Create new provider if not found
        provider = ProviderModel(name=name.lower())
        return await self.save_provider_in_db(access_token, provider, user_id)

    async def get_providers(
        self,
        limit: int = 10,
        created_at_lt: datetime = datetime.now(),
        user_id: str = None,
        access_token: Optional[str] = None,
    ) -> List[ProviderModel]:
        """Get providers with optional filtering"""
        print(
            f"Fetching providers for user_id: {user_id} with limit: {limit} and created_at_lt: {created_at_lt}"
        )

        providers = await self.get_all_in_db(
            limit=limit,
            created_at_lt=created_at_lt,
            user_id=user_id,
            access_token=access_token,
        )

        print("Fetched providers", providers)
        return providers
