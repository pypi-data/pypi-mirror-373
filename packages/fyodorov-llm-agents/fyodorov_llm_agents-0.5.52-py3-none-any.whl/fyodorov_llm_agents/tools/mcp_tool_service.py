from datetime import datetime
import json
from typing import Any, Optional, Dict, List
import requests

from fyodorov_llm_agents.base_service import BaseService
from .mcp_tool_model import MCPTool as ToolModel


class MCPToolService(BaseService[ToolModel]):
    def __init__(self):
        super().__init__("mcp_tools")
        
    def _dict_to_model(self, data: Dict[str, Any]) -> ToolModel:
        """Convert dictionary from database to MCPTool"""
        # Handle ID conversion for string IDs
        if "id" in data:
            data["id"] = str(data["id"])
        if "user_id" in data:
            data["user_id"] = str(data["user_id"])
        return ToolModel.from_dict(data)
    
    def _model_to_dict(self, model: ToolModel) -> Dict[str, Any]:
        """Convert MCPTool to dictionary for database"""
        return model.to_dict()
        
    async def create_or_update_tool(
        self, access_token: str, tool: ToolModel, user_id: str
    ) -> ToolModel:
        """Create or update tool in database"""
        print(f"Creating or updating tool with handle {tool.handle} for user {user_id}")
        
        existing_tool = await self.get_by_handle_and_user(
            access_token, tool.handle, user_id
        )
        
        if existing_tool:
            print(f"Tool with handle {tool.handle} already exists, updating it.")
            update_data = tool.to_dict()
            return await self.update_in_db(existing_tool.id, update_data, access_token)
        else:
            print(f"Tool with handle {tool.handle} does not exist, creating it.")
            return await self.create_in_db(tool, access_token, user_id)

    async def get_by_handle_and_user(
        self, access_token: str, handle: str, user_id: str
    ) -> Optional[ToolModel]:
        """Get tool by handle and user_id, with fallback to public tools"""
        try:
            # First try to find user's private tool
            filters = {"user_id": user_id, "handle": handle}
            tools = await self.get_all_in_db(
                limit=1,
                user_id=None,  # Don't double-filter by user_id
                filters=filters,
                access_token=access_token
            )
            
            if tools:
                return tools[0]
            
            # Fallback to public tools with same handle
            filters = {"handle": handle, "public": True}
            tools = await self.get_all_in_db(
                limit=1,
                user_id=None,
                filters=filters,
                access_token=access_token
            )
            
            return tools[0] if tools else None
            
        except Exception as e:
            print(f"Error fetching tool by handle and user: {e}")
            raise e

    async def get_tools_by_user(
        self,
        user_id: str,
        limit: int = 10,
        created_at_lt: datetime = None,
        access_token: Optional[str] = None,
        include_public: bool = True
    ) -> List[ToolModel]:
        """Get tools for a specific user, optionally including public tools"""
        if created_at_lt is None:
            created_at_lt = datetime.now()
            
        tools = []
        
        # Get user's private tools
        user_tools = await self.get_all_in_db(
            limit=limit,
            created_at_lt=created_at_lt,
            user_id=user_id,
            access_token=access_token
        )
        tools.extend(user_tools)
        
        # Get public tools if requested
        if include_public:
            filters = {"public": True}
            public_tools = await self.get_all_in_db(
                limit=limit,
                created_at_lt=created_at_lt,
                user_id=None,
                filters=filters,
                access_token=access_token
            )
            
            # Avoid duplicates by handle
            existing_handles = {tool.handle for tool in tools if tool.handle}
            for public_tool in public_tools:
                if public_tool.handle and public_tool.handle not in existing_handles:
                    tools.append(public_tool)
        
        # Validate tools before returning
        validated_tools = []
        for tool in tools:
            try:
                if tool.validate():
                    validated_tools.append(tool)
                else:
                    print(f"Invalid tool data: {tool}")
            except Exception as e:
                print(f"Error validating tool {tool.id}: {e}")
        
        return validated_tools

    async def get_tool_agents(self, access_token: str, tool_id: str) -> List[str]:
        """Get agent IDs associated with a tool"""
        if not tool_id:
            raise ValueError("Tool ID is required")
            
        try:
            supabase = self.get_supabase_client(access_token)
            result = (
                supabase.table("agent_mcp_tools")
                .select("*")
                .eq("mcp_tool_id", tool_id)
                .execute()
            )
            
            agent_ids = [
                str(item["agent_id"]) for item in result.data if "agent_id" in item
            ]
            return agent_ids
            
        except Exception as e:
            print(f"Error fetching tool agents: {e}")
            raise e

    async def set_tool_agents(
        self, access_token: str, tool_id: str, agent_ids: List[str]
    ) -> List[str]:
        """Associate agents with a tool"""
        if not tool_id:
            raise ValueError("Tool ID is required")
            
        try:
            supabase = self.get_supabase_client(access_token)
            result_agent_ids = []
            
            for agent_id in agent_ids:
                # Verify agent exists
                agent_result = (
                    supabase.table("agents")
                    .select("*")
                    .eq("id", agent_id)
                    .limit(1)
                    .execute()
                )
                
                if not agent_result.data:
                    print(f"Agent with ID {agent_id} does not exist.")
                    continue
                
                # Create association
                supabase.table("agent_mcp_tools").insert(
                    {"mcp_tool_id": tool_id, "agent_id": agent_id}
                ).execute()
                result_agent_ids.append(agent_id)
            
            print("Associated tool with agents:", result_agent_ids)
            return result_agent_ids
            
        except Exception as e:
            print(f"Error setting tool agents: {e}")
            raise e

    async def call_mcp_server(
        self,
        tool_id: str,
        access_token: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Invoke an MCP tool via the tool's configured MCP server"""
        if not tool_id:
            raise ValueError("Tool ID is required")
            
        # Get tool from database
        tool = await self.get_in_db(tool_id, access_token)
        if not tool:
            raise ValueError("Tool not found")
        if not tool.handle:
            raise ValueError("Tool handle is required")
        if not tool.api_url:
            raise ValueError("Tool api_url is required")

        url = f"{tool.api_url}:call"
        headers = {"Content-Type": "application/json"}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        if args is None:
            args = {}

        try:
            print(f"Calling MCP server at {url} with args {args}")
            response = requests.post(url, headers=headers, json=args, timeout=30)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return json.dumps(response.json())
            return response.text
        except requests.RequestException as e:
            print(f"Error calling MCP server: {e}")
            raise e


class MCPTool:
    """Legacy wrapper class for backward compatibility"""
    
    @staticmethod
    async def create_or_update_in_db(
        access_token: str, tool: ToolModel, user_id: str
    ) -> ToolModel:
        """Legacy method for backward compatibility"""
        service = MCPToolService()
        return await service.create_or_update_tool(access_token, tool, user_id)

    @staticmethod
    async def create_in_db(
        access_token: str, tool: ToolModel, user_id: str
    ) -> ToolModel:
        """Legacy method for backward compatibility"""
        service = MCPToolService()
        return await service.create_in_db(tool, access_token, user_id)

    @staticmethod
    async def update_in_db(access_token: str, id: str, tool: ToolModel) -> ToolModel:
        """Legacy method for backward compatibility"""
        service = MCPToolService()
        update_data = tool.to_dict()
        return await service.update_in_db(id, update_data, access_token)

    @staticmethod
    async def delete_in_db(access_token: str, id: str) -> bool:
        """Legacy method for backward compatibility"""
        service = MCPToolService()
        return await service.delete_in_db(id, access_token)

    @staticmethod
    async def get_in_db(access_token: str, id: str) -> Optional[ToolModel]:
        """Legacy method for backward compatibility"""
        service = MCPToolService()
        return await service.get_in_db(id, access_token)

    @staticmethod
    async def get_by_name_and_user_id(
        access_token: str, handle: str, user_id: str
    ) -> Optional[ToolModel]:
        """Legacy method for backward compatibility"""
        service = MCPToolService()
        return await service.get_by_handle_and_user(access_token, handle, user_id)
    
    @staticmethod
    async def get_by_handle(handle: str, access_token: Optional[str] = None) -> Optional[ToolModel]:
        """Get tool by handle (public tools only)"""
        service = MCPToolService()
        filters = {"handle": handle, "public": True}
        tools = await service.get_all_in_db(
            limit=1,
            user_id=None,
            filters=filters,
            access_token=access_token
        )
        return tools[0] if tools else None

    @staticmethod
    async def get_all_in_db(
        limit: int = 10, 
        created_at_lt: datetime = None, 
        user_id: str = None,
        access_token: Optional[str] = None
    ) -> List[ToolModel]:
        """Legacy method for backward compatibility"""
        service = MCPToolService()
        if user_id:
            return await service.get_tools_by_user(user_id, limit, created_at_lt, access_token)
        else:
            return await service.get_all_in_db(limit, created_at_lt, user_id, None, access_token)

    @staticmethod
    async def get_tool_agents(access_token: str, id: str) -> List[str]:
        """Legacy method for backward compatibility"""
        service = MCPToolService()
        return await service.get_tool_agents(access_token, id)

    @staticmethod
    async def set_tool_agents(
        access_token: str, id: str, agent_ids: List[str]
    ) -> List[str]:
        """Legacy method for backward compatibility"""
        service = MCPToolService()
        return await service.set_tool_agents(access_token, id, agent_ids)

    @staticmethod
    async def call_mcp_server(
        id: str,
        access_token: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Legacy method for backward compatibility"""
        service = MCPToolService()
        return await service.call_mcp_server(id, access_token, args)