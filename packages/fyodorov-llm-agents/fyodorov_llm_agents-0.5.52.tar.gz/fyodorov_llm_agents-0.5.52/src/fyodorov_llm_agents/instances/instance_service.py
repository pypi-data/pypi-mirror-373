from datetime import datetime
from typing import Dict, Any, List, Optional

from fyodorov_llm_agents.base_service import BaseService
from fyodorov_llm_agents.providers.provider_service import Provider
from fyodorov_llm_agents.agents.agent_model import Agent as AgentModel
from fyodorov_llm_agents.agents.agent_service import AgentService
from fyodorov_llm_agents.agents.agent_executor import AgentExecutor
from fyodorov_llm_agents.tools.mcp_tool_service import MCPTool as ToolService
from .instance_model import InstanceModel


class InstanceService(BaseService[InstanceModel]):
    def __init__(self):
        super().__init__("instances")
        
    def _dict_to_model(self, data: Dict[str, Any]) -> InstanceModel:
        """Convert dictionary from database to InstanceModel"""
        return InstanceModel.from_dict(data)
    
    def _model_to_dict(self, model: InstanceModel) -> Dict[str, Any]:
        """Convert InstanceModel to dictionary for database"""
        return model.to_dict()
        
    async def create_instance_in_db(self, instance: InstanceModel, access_token: Optional[str] = None, user_id: Optional[str] = None) -> InstanceModel:
        """Create instance with smart upsert logic"""
        try:
            # Check if instance exists by title and agent_id
            existing_instance = await self.get_by_title_and_agent(
                instance.title, instance.agent_id, access_token
            )
            
            if existing_instance:
                # Update existing instance
                update_data = instance.to_dict()
                return await self.update_in_db(existing_instance.id, update_data, access_token)
            else:
                # Create new instance
                created = await self.create_in_db(instance, access_token, user_id)
                
                # Update title with ID for uniqueness
                if created and created.id:
                    update_data = {"title": f"{created.title} {created.id}"}
                    return await self.update_in_db(created.id, update_data, access_token)
                    
                return created
                
        except Exception as e:
            if hasattr(e, 'code') and e.code == "23505":
                print("Instance already exists")
                existing = await self.get_by_title_and_agent(
                    instance.title, instance.agent_id, access_token
                )
                return existing
            raise e
    
    async def get_by_title_and_agent(self, title: str, agent_id: str, access_token: Optional[str] = None) -> Optional[InstanceModel]:
        """Get instance by title and agent ID"""
        if not title:
            raise ValueError("Instance title is required")
        if not agent_id:
            raise ValueError("Agent ID is required")
            
        try:
            supabase = self.get_supabase_client(access_token)
            result = (
                supabase.table("instances")
                .select("*")
                .eq("title", title)
                .eq("agent_id", agent_id)
                .limit(1)
                .execute()
            )
            
            if not result or not result.data:
                return None
                
            instance_dict = result.data[0]
            return self._dict_to_model(instance_dict)
            
        except Exception as e:
            print(f"Error fetching instance by title and agent: {e}")
            raise e
    
    async def get_instances_by_user(
        self,
        user_id: str,
        limit: int = 10,
        created_at_lt: datetime = None,
        access_token: Optional[str] = None
    ) -> List[InstanceModel]:
        """Get instances for a specific user through their agents"""
        try:
            if created_at_lt is None:
                created_at_lt = datetime.now()
                
            # First get user's agents
            agent_service = AgentService()
            agents = await agent_service.get_all_in_db(
                limit=limit, 
                created_at_lt=created_at_lt, 
                user_id=user_id, 
                access_token=access_token
            )
            
            if not agents:
                return []
            
            # Get instances for each agent
            agent_ids = [agent.id for agent in agents]
            instances = []
            
            supabase = self.get_supabase_client(access_token)
            for agent_id in agent_ids:
                result = (
                    supabase.table("instances")
                    .select("*")
                    .eq("agent_id", agent_id)
                    .limit(limit)
                    .lt("created_at", created_at_lt)
                    .order("created_at", desc=True)
                    .execute()
                )
                
                if result.data:
                    for instance_data in result.data:
                        instances.append(self._dict_to_model(instance_data))
            
            return instances
            
        except Exception as e:
            print(f"Error fetching instances by user: {e}")
            raise e


class Instance(InstanceModel):
    """Legacy wrapper class for backward compatibility - extends InstanceModel with runtime functionality"""
    
    async def chat_w_fn_calls(
        self, input: str = "", access_token: str = None, user_id: str = ""
    ) -> dict:
        """Execute chat with function calling"""
        # Get the agent service and load the agent
        agent_service = AgentService()
        agent: AgentModel = await agent_service.get_agent_in_db(self.agent_id, access_token)
        
        if not agent:
            raise ValueError(f"Agent with ID {self.agent_id} not found")
        
        print(f"Model fetched via AgentService.get_agent_in_db: {agent.model_id}")
        
        # Add timestamp to prompt
        agent.prompt = (
            f"{agent.prompt}\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )
        
        # Process tools
        print(f"Processing agent tools: {agent.tools}")
        for index, tool in enumerate(agent.tools):
            if isinstance(tool, str):
                agent.tools[index] = await ToolService.get_by_name_and_user_id(
                    access_token, tool, user_id
                )
                if agent.tools[index]:
                    print(f"Tool fetched: {agent.tools[index]}")
                    agent.prompt += f"\n\n{agent.tools[index].handle}: {agent.tools[index].description}\n\n"
        
        # Create runtime agent and execute
        executor = AgentExecutor()
        res = await executor.run(
            agent=agent, input=input, history=self.chat_history, user_id=user_id
        )
        
        # Update chat history
        self.chat_history.append({"role": "user", "content": input})
        self.chat_history.append({"role": "assistant", "content": res["answer"]})
        
        # Update instance in database
        instance_service = InstanceService()
        await instance_service.create_instance_in_db(self, access_token, user_id)
        
        return res

    @staticmethod
    async def create_in_db(instance: InstanceModel, access_token: Optional[str] = None, user_id: Optional[str] = None) -> InstanceModel:
        """Legacy method for backward compatibility"""
        instance_service = InstanceService()
        return await instance_service.create_instance_in_db(instance, access_token, user_id)

    @staticmethod
    async def update_in_db(id: str, instance: dict, access_token: Optional[str] = None) -> InstanceModel:
        """Legacy method for backward compatibility"""
        instance_service = InstanceService()
        return await instance_service.update_in_db(id, instance, access_token)

    @staticmethod
    async def delete_in_db(id: str, access_token: Optional[str] = None) -> bool:
        """Legacy method for backward compatibility"""
        instance_service = InstanceService()
        return await instance_service.delete_in_db(id, access_token)

    @staticmethod
    async def get_by_title_and_agent(title: str, agent_id: str, access_token: Optional[str] = None) -> Optional[InstanceModel]:
        """Legacy method for backward compatibility"""
        instance_service = InstanceService()
        return await instance_service.get_by_title_and_agent(title, agent_id, access_token)

    @staticmethod
    async def get_in_db(id: str, access_token: Optional[str] = None) -> Optional[InstanceModel]:
        """Legacy method for backward compatibility"""
        instance_service = InstanceService()
        return await instance_service.get_in_db(id, access_token)

    @staticmethod
    async def get_all_in_db(
        limit: int = 10, 
        created_at_lt: datetime = None, 
        user_id: str = None,
        access_token: Optional[str] = None
    ) -> List[InstanceModel]:
        """Legacy method for backward compatibility"""
        instance_service = InstanceService()
        if user_id:
            return await instance_service.get_instances_by_user(user_id, limit, created_at_lt, access_token)
        else:
            return await instance_service.get_all_in_db(limit, created_at_lt, user_id, None, access_token)