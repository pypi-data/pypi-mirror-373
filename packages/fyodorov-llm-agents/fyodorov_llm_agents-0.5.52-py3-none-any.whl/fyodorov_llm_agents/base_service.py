from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import TypeVar, Generic, Optional, List, Dict, Any, TYPE_CHECKING
from supabase import Client
from fyodorov_utils.config.supabase import get_supabase
import logging
import os

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper()
)
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from fyodorov_llm_agents.base_model import FyodorovBaseModel

T = TypeVar("T", bound="FyodorovBaseModel")  # Generic type bound to FyodorovBaseModel


class BaseService(Generic[T], ABC):
    """
    Base service class that provides common database operations and utilities
    for all fyodorov-llm-agents services.
    """

    def __init__(self, table_name: str, access_token: Optional[str] = None, **model_kwargs) -> None:
        self.table_name = table_name
        self.access_token = access_token
        self._supabase_client: Optional[Client] = None
        self._supabase_client = self.get_supabase_client()
        self.model_kwargs = model_kwargs

    def get_supabase_client(self, access_token: Optional[str] = None) -> Client:
        """Get Supabase client, optionally with access token"""
        current_client = getattr(self, "_supabase_client", None)
        if current_client is None:
            access_token = access_token or self.access_token
            current_client = get_supabase(access_token)
            self._supabase_client = current_client
        return current_client


    def _dict_to_model(self, data: Dict[str, Any]) -> T:
        """Convert dictionary from database to model instance"""
        print("[_dict_to_model] Converting dict to model:", data)
        model = T(**data, **self.model_kwargs)
        print("[_dict_to_model] Converted model:", model)
        return model

    @abstractmethod
    def _model_to_dict(self, model: T) -> Dict[str, Any]:
        """Convert model instance to dictionary for database"""
        return T(**self.model_kwargs)

    def _prepare_for_db(
        self, data: Dict[str, Any], exclude_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Prepare data dictionary for database insertion/update

        Args:
            data: Raw data dictionary from model
            exclude_fields: Fields to exclude from database operation

        Returns:
            Cleaned data dictionary ready for database
        """
        print("Preparing data for DB with exclude fields:", exclude_fields)
        if exclude_fields is None:
            exclude_fields = ["id", "created_at", "updated_at"]
            print("Setting default exclude fields:", exclude_fields)

        print("Cleaning data")
        cleaned_data = {
            k: v for k, v in data.items() if k not in exclude_fields and v is not None
        }
        print("Cleaned data:", cleaned_data)
        return cleaned_data

    async def create_in_db(
        self,
        model: T,
        access_token: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> T:
        """Create a new record in the database"""
        print(f"Creating record in {self.table_name} table")
        try:
            supabase = self.get_supabase_client(access_token)
            print("Got supabase client")
            data_dict = self._model_to_dict(model)
            print("Converted model to dict")
            if user_id:
                data_dict["user_id"] = user_id
                print("Added user_id to dict")
            # Remove fields that should not be inserted
            print("Preparing data for DB")
            data_dict = self._prepare_for_db(data_dict)

            logger.debug(f"Creating {self.table_name} with data: {data_dict}")
            result = supabase.table(self.table_name).insert(data_dict).execute()

            if not result.data:
                raise ValueError(f"Error creating {self.table_name} in database")

            created_dict = result.data[0]
            model = await self._dict_to_model(created_dict)
            return model
        except Exception as e:
            logger.error(f"Error creating {self.table_name}: {str(e)}")
            raise self.handle_database_error(e, "creating")

    async def update_in_db(
        self, id: str, update_data: Dict[str, Any], access_token: Optional[str] = None
    ) -> T:
        """Update a record in the database"""
        if not id:
            raise ValueError(f"{self.table_name.capitalize()} ID is required")
        try:
            supabase = self.get_supabase_client(access_token)

            # Remove fields that should not be updated
            update_data = self._prepare_for_db(
                update_data, exclude_fields=["id", "created_at", "updated_at"]
            )

            logger.debug(f"Updating {self.table_name} {id} with data: {update_data}")
            result = (
                supabase.table(self.table_name)
                .update(update_data)
                .eq("id", id)
                .execute()
            )

            if not result.data:
                raise ValueError(
                    f"{self.table_name.capitalize()} with ID {id} not found"
                )

            updated_dict = result.data[0]
            return await self._dict_to_model(updated_dict)
        except Exception as e:
            logger.error(f"Error updating {self.table_name} {id}: {str(e)}")
            raise self.handle_database_error(e, "updating")

    async def delete_in_db(self, id: str, access_token: Optional[str] = None) -> bool:
        """Delete a record from the database"""
        if not id:
            raise ValueError(f"{self.table_name.capitalize()} ID is required")
        try:
            supabase = self.get_supabase_client(access_token)

            logger.debug(f"Deleting {self.table_name} {id}")
            result = supabase.table(self.table_name).delete().eq("id", id).execute()
            print(f"Result of delete operation: {result}")
            if hasattr(result, "error") and result.error:
                raise ValueError(f"Error deleting {self.table_name} {id}: {result.error.message}")
            return result.data[0]["id"] == id
        except Exception as e:
            logger.error(f"Error deleting {self.table_name} {id}: {str(e)}")
            raise self.handle_database_error(e, "deleting")

    async def get_in_db(
        self, id: str, access_token: Optional[str] = None
    ) -> Optional[T]:
        """Get a single record by ID"""
        if not id:
            raise ValueError(f"{self.table_name.capitalize()} ID is required")
        try:
            supabase = self.get_supabase_client(access_token)

            result = (
                supabase.table(self.table_name)
                .select("*")
                .eq("id", id)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            record_dict = result.data[0]
            logger.debug(f"Fetched {self.table_name}: {record_dict}")
            model = await self._dict_to_model(record_dict)
            return model
        except Exception as e:
            logger.error(f"Error fetching {self.table_name} {id}: {str(e)}")
            raise self.handle_database_error(e, "fetching")

    async def get_all_in_db(
        self,
        limit: int = 10,
        created_at_lt: datetime = None,
        user_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        access_token: Optional[str] = None,
    ) -> List[T]:
        """Get multiple records with optional filters"""
        print(f"get_all_in_db called with user_id: {user_id}, filters: {filters}, limit: {limit}, created_at_lt: {created_at_lt}")
        try:
            supabase = self.get_supabase_client(access_token)

            print(f"Building query for {self.table_name}")
            query = supabase.table(self.table_name).select("*")

            # Apply user filter if provided
            if user_id:
                print(f"[get_all_in_db] Applying user filter for {self.table_name}")
                query = query.eq("user_id", user_id)

            # Apply additional filters
            if filters:
                print(f"[get_all_in_db] Applying additional filters: {filters}")
                for key, value in filters.items():
                    query = query.eq(key, value)

            # Apply date filter
            if created_at_lt is None:
                print(f"[get_all_in_db] No created_at_lt provided, using current datetime")
                created_at_lt = datetime.now() + timedelta(days=1)  # Add one day to ensure inclusion of today's records
            print(f"[get_all_in_db] Applying created_at_lt filter: {created_at_lt}")
            query = query.lt("created_at", created_at_lt)

            # Apply ordering and limit
            print(f"[get_all_in_db] Applying ordering and limit")
            query = query.order("created_at", desc=True).limit(limit)

            print(f"Executing query for {self.table_name}")
            result = query.execute()

            if not result.data:
                print(f"No records found in {self.table_name}")
                return []

            print(f"Fetched {len(result.data)} records from {self.table_name}")
            # records = [self._dict_to_model(record) for record in result.data]
            records = []
            for record in result.data:
                try:
                    print(f"Converting record to model: {record}")
                    model_instance = self._dict_to_model(record)
                    print(f"Converted model instance: {model_instance}")
                    records.append(model_instance)
                except Exception as e:
                    logger.error(f"Error converting record to model: {str(e)}")
                    print(f"Error converting record to model: {str(e)}")
                    continue
            print(f"Converted {len(records)} records to models")
            # logger.debug(f"Fetched {len(records)} {self.table_name} records")
            return records
        except Exception as e:
            logger.error(f"Error fetching {self.table_name} records: {str(e)}")
            raise self.handle_database_error(e, "fetching")

    async def upsert_in_db(
        self,
        model: T,
        access_token: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> T:
        """Create or update a record in the database"""
        try:
            supabase = self.get_supabase_client(access_token)
            data_dict = self._model_to_dict(model)

            if user_id:
                data_dict["user_id"] = user_id

            logger.debug(f"Upserting {self.table_name} with data: {data_dict}")
            result = supabase.table(self.table_name).upsert(data_dict).execute()

            if not result.data:
                raise ValueError(f"Error upserting {self.table_name} in database")

            upserted_dict = result.data[0]
            return self._dict_to_model(upserted_dict)
        except Exception as e:
            logger.error(f"Error upserting {self.table_name}: {str(e)}")
            raise self.handle_database_error(e, "upserting")

    def handle_database_error(self, e: Exception, operation: str) -> Exception:
        """Handle common database errors with consistent messaging

        Args:
            e: The original exception
            operation: Description of the database operation that failed

        Returns:
            A more specific exception with better error messaging
        """
        error_msg = f"Error {operation} {self.table_name}: {str(e)}"
        logger.error(error_msg)

        # Handle specific database error codes
        if hasattr(e, "code"):
            if e.code == "23505":  # Unique constraint violation
                return ValueError(f"{self.table_name} row already exists")
            elif e.code == "23503":  # Foreign key violation
                return ValueError("Referenced record does not exist")
            elif e.code == "42P01":  # Table does not exist
                return ValueError(f"{self.table_name} table not found")

        return e
