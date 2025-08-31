from pydantic import Field
from typing import Optional, Dict, Any, Literal, ClassVar
import requests
import json
import logging
import os
from fyodorov_llm_agents.base_model import FyodorovBaseModel

# Configure logging for MCP tool operations
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper()
)
logger = logging.getLogger(__name__)

APIUrlTypes = Literal["openapi"]


class MCPTool(FyodorovBaseModel):
    """
    Pydantic model corresponding to the 'mcp_tools' table.
    """

    # Override class constants for validation
    MAX_NAME_LENGTH: ClassVar[int] = 80
    MAX_DESCRIPTION_LENGTH: ClassVar[int] = 1000

    name: str = Field(..., max_length=MAX_NAME_LENGTH)
    handle: Optional[str] = None
    description: Optional[str] = Field(None, max_length=MAX_DESCRIPTION_LENGTH)
    logo_url: Optional[str] = None
    user_id: Optional[str] = None

    public: Optional[bool] = False
    api_type: Optional[str] = None
    api_url: Optional[str] = None
    auth_method: Optional[str] = None
    auth_info: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None
    health_status: Optional[str] = None
    usage_notes: Optional[str] = None

    # Fields for launching local tools
    launch_command: Optional[str] = None
    launch_args: Optional[list[str]] = None
    launch_working_directory: Optional[str] = None

    def validate(self) -> bool:
        """
        Run custom validations on the model fields.
        Returns True if all validations pass, otherwise raises ValueError.
        """
        if not self.name:
            raise ValueError("MCP tool name is required")

        self.validate_text_field(self.name, "Name", self.MAX_NAME_LENGTH)

        if self.description:
            self.validate_text_field(
                self.description, "Description", self.MAX_DESCRIPTION_LENGTH
            )

        # Validate auth configuration if auth_method is specified
        if self.auth_method:
            if self.auth_method == "bearer" and (
                not self.auth_info or not self.auth_info.get("token")
            ):
                raise ValueError("Bearer auth method requires token in auth_info")
            elif self.auth_method == "basic" and (
                not self.auth_info
                or not self.auth_info.get("username")
                or not self.auth_info.get("password")
            ):
                raise ValueError(
                    "Basic auth method requires username and password in auth_info"
                )

        return super().validate()

    def resource_dict(self) -> Dict[str, Any]:
        """Generate resource dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

    def get_function(self) -> Dict[str, Any]:
        """
        Convert this MCP tool into a function definition usable by LLMs (OpenAI-style).
        """
        if not self.capabilities or "functions" not in self.capabilities:
            raise ValueError(f"Tool '{self.name}' is missing `capabilities.functions`")

        # For now: return the first declared capability
        func = self.capabilities["functions"][0]
        return {
            "name": func["name"],
            "description": func.get("description", "No description provided."),
            "parameters": func.get("parameters", {}),
        }

    def call(self, args: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Call the MCP tool with given arguments

        Args:
            args: Arguments to pass to the tool
            timeout: Request timeout in seconds

        Returns:
            Dictionary containing response data and metadata

        Raises:
            ValueError: If tool configuration is invalid
            requests.RequestException: If the API call fails
        """
        if not self.api_url:
            raise ValueError("MCP tool is missing an `api_url`")

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Fyodorov-Agent/1.0",
        }

        # Handle authentication
        auth = None
        if self.auth_method == "bearer":
            if not self.auth_info or not self.auth_info.get("token"):
                raise ValueError(
                    "Bearer token required but not provided in `auth_info`"
                )
            headers["Authorization"] = f"Bearer {self.auth_info['token']}"
        elif self.auth_method == "basic":
            if (
                not self.auth_info
                or not self.auth_info.get("username")
                or not self.auth_info.get("password")
            ):
                raise ValueError(
                    "Basic auth requires `username` and `password` in `auth_info`"
                )
            auth = (self.auth_info["username"], self.auth_info["password"])

        try:
            logger.info(
                f"Calling MCP tool '{self.name}' at {self.api_url} with args: {args}"
            )
            response = requests.post(
                self.api_url, json=args, headers=headers, auth=auth, timeout=timeout
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            result = {
                "success": True,
                "status_code": response.status_code,
                "content_type": content_type,
                "tool_name": self.name,
            }

            if "application/json" in content_type:
                result["data"] = response.json()
                result["text"] = json.dumps(response.json(), indent=2)
            else:
                result["data"] = response.text
                result["text"] = response.text

            return result

        except requests.Timeout:
            logger.error(f"Timeout calling MCP tool '{self.name}'")
            return {
                "success": False,
                "error": f"Tool '{self.name}' timed out after {timeout} seconds",
                "tool_name": self.name,
            }
        except requests.RequestException as e:
            logger.error(f"Error calling MCP tool '{self.name}': {e}")
            return {"success": False, "error": str(e), "tool_name": self.name}
