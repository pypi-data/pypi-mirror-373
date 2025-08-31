import os
import asyncio
from typing import Any, Dict, List

import litellm
import requests

from fyodorov_utils.config.service_discovery import get_service_url
from fyodorov_llm_agents.agents.agent_model import Agent as AgentModel
from fyodorov_llm_agents.models.llm_service import LLMService
from fyodorov_llm_agents.providers.provider_service import Provider
from fyodorov_llm_agents.tools.mcp_tool_service import MCPTool as ToolService


class AgentExecutor:
    """Runtime executor for AgentModel: handles LLM calls and tool routing."""

    async def run(
        self,
        agent: AgentModel,
        input: str = "",
        history: List[dict] | None = None,
        user_id: str = "",
    ) -> Dict[str, Any]:
        if history is None:
            history = []

        print("call_with_fn_calling (AgentExecutor.run)")
        litellm.set_verbose = True
        print(f"[AgentExecutor.run] agent.model: {agent.model_id}")

        # Resolve provider/api configuration without mutating the model
        api_key = agent.api_key
        api_url = agent.api_url
        llm_service = LLMService()
        model = llm_service.get_model(id=agent.model_id)
        model_name = model.base_model if model.base_model else ""
        provider_service = Provider()
        provider = await provider_service.get_provider(
            access_token=None, user_id=user_id, id=model.provider
        )
        if provider:
            api_key = provider.api_key
            api_url = provider.api_url
            if provider.name == "gemini":
                model = "gemini/" + model.base_model
                os.environ["GEMINI_API_KEY"] = api_key or ""
            else:
                # Fallback to using the provider's base with given model
                model = model_name
        elif api_key and api_key.startswith("sk-"):
            model = "openai/" + model_name
            os.environ["OPENAI_API_KEY"] = api_key
            api_url = "https://api.openai.com/v1"
        elif api_key:
            model = "mistral/" + model_name
            os.environ["MISTRAL_API_KEY"] = api_key
            api_url = "https://api.mistral.ai/v1"
        else:
            print("Provider Ollama")
            model = "ollama/" + model_name
            if api_url is None:
                api_url = "https://api.ollama.ai/v1"

        base_url = str(api_url).rstrip("/") if api_url else None
        messages: list[dict] = [
            {"content": agent.prompt, "role": "system"},
            *(history or []),
            {"content": input, "role": "user"},
        ]

        # Load tools (support both string handles and tool objects)
        print(f"Tools on agent: {agent.tools}")
        mcp_tools = []
        for tool in agent.tools:
            try:
                if hasattr(tool, "get_function"):
                    mcp_tools.append(tool)
                else:
                    tool_instance = await ToolService.get_by_handle(tool)
                    if tool_instance:
                        mcp_tools.append(tool_instance)
            except Exception as e:
                print(f"Error fetching tool {tool}: {e}")

        tool_schemas = [tool.get_function() for tool in mcp_tools if tool]
        print(f"Tool schemas: {tool_schemas}")

        if tool_schemas:
            print(
                f"calling litellm with model {model}, messages: {messages}, max_retries: 0, history: {history}, base_url: {base_url}, tools: {tool_schemas}"
            )
            response = litellm.completion(
                model=model, messages=messages, max_retries=0, base_url=base_url
            )
        else:
            print(
                f"calling litellm with model {model}, messages: {messages}, max_retries: 0, history: {history}, base_url: {base_url}"
            )
            response = litellm.completion(
                model=model, messages=messages, max_retries=0, base_url=base_url
            )
        print(f"Response: {response}")

        message = response.choices[0].message
        if getattr(message, "tool_calls", None):
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            args = tool_call.function.arguments

            # Find the corresponding tool
            mcp_tool = None
            for tool in mcp_tools:
                function_def = tool.get_function()
                if function_def["name"] == function_name:
                    mcp_tool = tool
                    break

            # Forward tool call to Tsiolkovsky instead of calling locally
            tool_output = await self._forward_tool_call_to_tsiolkovsky(
                mcp_tool.id, args, user_id
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call],
                }
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_output,
                }
            )

            followup = litellm.completion(
                model=model,
                messages=messages,
                max_retries=0,
                base_url=base_url,
            )
            return {"answer": followup.choices[0].message.content}

        answer = message.content
        print(f"Answer: {answer}")
        return {"answer": answer}

    async def _forward_tool_call_to_tsiolkovsky(
        self, tool_id: str, args: str, user_session: str
    ) -> str:
        """Forward function call to Tsiolkovsky for execution"""
        try:
            tsiolkovsky_url = get_service_url("Tsiolkovsky")

            response = await asyncio.to_thread(
                requests.post,
                f"{tsiolkovsky_url}/tools/{tool_id}/call",
                json={"args": args},
                headers={"Authorization": f"Bearer {user_session}"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("result", "")
            else:
                return f"Error calling tool: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Error forwarding tool call: {str(e)}"
