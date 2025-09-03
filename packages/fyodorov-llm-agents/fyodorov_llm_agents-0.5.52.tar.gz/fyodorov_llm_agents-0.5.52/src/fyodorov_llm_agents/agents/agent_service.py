from datetime import datetime
from typing import Dict, Any, List, Optional
from fyodorov_llm_agents.base_service import BaseService
from fyodorov_llm_agents.agents.agent_model import Agent as AgentModel
from fyodorov_llm_agents.models.llm_service import LLMService


class AgentService(BaseService[AgentModel]):
    def __init__(self, **kwargs):
        super().__init__("agents", **kwargs)
        
    def _dict_to_model(self, data: Dict[str, Any]) -> AgentModel:
        """Convert dictionary from database to AgentModel"""
        return AgentModel.from_dict(data)
    
    def _model_to_dict(self, model: AgentModel) -> Dict[str, Any]:
        """Convert AgentModel to dictionary for database"""
        return model.to_dict()
        
    async def get_agent_in_db(self, id: str, access_token: Optional[str] = None) -> Optional[AgentModel]:
        """Get agent by ID with model loading"""
        agent = await self.get_in_db(id, access_token)
        if agent and hasattr(agent, 'model_id') and agent.model_id:
            # Load the associated model
            try:
                llm_service = LLMService()
                agent.model_id = await llm_service.get_model(id=agent.model_id)
            except Exception as e:
                print(f"Error loading model for agent {id}: {e}")
        return agent

    async def get_all_in_db(
        self,
        limit: int = 10,
        created_at_lt: datetime = None,
        user_id: str = None,
        access_token: Optional[str] = None
    ) -> List[AgentModel]:
        """Get agents with optional filtering"""            
        # Use custom filters for public agents if no user_id is provided
        filters = None
        if user_id is None:
            filters = {"public": True}
            
        return await super().get_all_in_db(limit, created_at_lt, user_id, filters, access_token)

    async def save_from_dict(self, access_token: str, user_id: str, agent_dict: Dict[str, Any]) -> AgentModel:
        """Create agent from dictionary data"""
        agent = await AgentModel.from_dict(agent_dict, user_id)
        return await self.create_in_db(agent, access_token,user_id)

    async def get_agent_tools(self, access_token: str, agent_id: str) -> List[Dict[str, Any]]:
        """Get tools assigned to an agent"""
        if not agent_id:
            raise ValueError("Agent ID is required")
        
        supabase = self.get_supabase_client(access_token)
        result = (
            supabase.table("agent_mcp_tools")
            .select("*")
            .eq("agent_id", agent_id)
            .execute()
        )
        tool_ids = [
            item["mcp_tool_id"] for item in result.data if "mcp_tool_id" in item
        ]
        
        result = []
        for tool_id in tool_ids:
            tool = (
                supabase.table("mcp_tools")
                .select("*")
                .eq("id", tool_id)
                .limit(1)
                .execute()
            )
            if tool and tool.data:
                tool_dict = tool.data[0]
                tool_dict["id"] = str(tool_dict["id"])
                result.append(tool_dict)
        return result

    async def assign_agent_tools(
        self, access_token: str, agent_id: str, tool_ids: List[str]
    ) -> List[str]:
        """Assign tools to an agent"""
        if not tool_ids:
            raise ValueError("Tool IDs are required")
            
        supabase = self.get_supabase_client(access_token)
        result = []
        
        for tool_id in tool_ids:
            # Check if tool is valid and exists in the database
            tool_result = (
                supabase.table("mcp_tools")
                .select("*")
                .eq("id", tool_id)
                .limit(1)
                .execute()
            )
            if not tool_result.data:
                print(f"Tool with ID {tool_id} does not exist.")
                continue
                
            supabase.table("agent_mcp_tools").insert(
                {"mcp_tool_id": tool_id, "agent_id": agent_id}
            ).execute()
            print("Inserted tool", tool_id, "for agent", agent_id)
            result.append(tool_id)
        return result

    async def delete_agent_tool_connection(
        self, access_token: str, agent_id: str, tool_id: str
    ) -> bool:
        """Remove tool connection from an agent"""
        if not agent_id:
            raise ValueError("Agent ID is required")
        if not tool_id:
            raise ValueError("Tool ID is required")
            
        try:
            supabase = self.get_supabase_client(access_token)
            supabase.table("agent_mcp_tools").delete().eq("agent_id", agent_id).eq(
                "mcp_tool_id", tool_id
            ).execute()
            return True
        except Exception as e:
            print("Error deleting agent tool", str(e))
            raise e
