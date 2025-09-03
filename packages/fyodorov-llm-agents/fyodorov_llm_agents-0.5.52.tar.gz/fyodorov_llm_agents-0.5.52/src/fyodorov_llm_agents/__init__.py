"""
Fyodorov LLM Agents - A comprehensive library for managing LLM-based agents and tools.

This library provides base classes and models for building robust, scalable LLM agents
with standardized validation, serialization, and database operations.
"""

__version__ = "0.2.0"

# Import main base classes
from .base_model import FyodorovBaseModel
from .base_service import BaseService

# Import main models
from .agents.agent_model import Agent
from .instances.instance_model import InstanceModel
from .models.llm_model import LLMModel
from .providers.provider_model import ProviderModel
from .tools.mcp_tool_model import MCPTool

# Import main services
from .agents.agent_service import AgentService
from .instances.instance_service import InstanceService
from .models.llm_service import LLMService
from .providers.provider_service import Provider as ProviderService
from .tools.mcp_tool_service import MCPToolService

__all__ = [
    "FyodorovBaseModel",
    "BaseService",
    "Agent",
    "InstanceModel",
    "LLMModel",
    "ProviderModel",
    "MCPTool",
    "AgentService",
    "InstanceService",
    "LLMService",
    "ProviderService",
    "MCPToolService",
    "__version__",
]
