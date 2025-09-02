import requests
import os
from typing import Optional, List
from gepeto.agents.schema import (
    AgentSchema,
    AgentSearchRequest,
    AgentRequest,
    AgentCreateSchema,
)
from gepeto.prompts.schema import PromptRequest
from gepeto.prompts import Prompts
from gepeto.team.schema import Response
from gepeto.team.schemas.agent_schema import Agent
from gepeto.team.utils import debug_print


class Agents:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url="",
        prompts: Prompts = None,
        x_trace_id: Optional[str] = None,
    ):
        """Initialize Gepeto client with API key from env or passed directly"""
        self.api_key = api_key or os.environ.get("GEPETO_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEPETO_API_KEY must be set in environment or passed to constructor"
            )
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.prompts = prompts
        self.x_trace_id = x_trace_id

    def _make_request(self, method: str, endpoint: str, json_data: dict = None) -> dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "x-api-key": self.api_key,
        }
        if self.x_trace_id:
            headers["x-trace-id"] = self.x_trace_id
        response = requests.request(
            method=method, url=url, headers=headers, json=json_data
        )
        return response.json()

    def search(self, name: str) -> List[AgentSchema]:
        """Search for agents by name."""
        search_request = AgentSearchRequest(name=name)
        json_data = self._make_request(
            "POST", "/shared/agents/search", search_request.model_dump()
        )
        return [AgentSchema(**agent).name for agent in json_data]

    def get(self, name: str) -> AgentSchema:
        """Get a specific agent by name. Case-insensitive."""
        json_data = self._make_request("GET", f"/gepeto/agents/{name}")
        response = json_data["agent"]
        return AgentSchema(**response).to_agent()

    def list(self) -> List[AgentSchema]:
        """Get all agents."""
        json_data = self._make_request("GET", "/shared/organizations/agents")
        return [AgentSchema(**agent).name for agent in json_data]

    def create(self, agent: Agent) -> AgentSchema:
        """Create a new agent."""

        # convert instructions to Prompt if its a string
        if type(agent.instructions) == str:
            instructions = PromptRequest(
                name=agent.name + " prompt",
                content=agent.instructions,
                description="prompt for " + agent.name,
            )
        elif type(agent.instructions) == function:
            raise NotImplementedError(
                "functions are not currently implemented in the API"
            )
        elif type(agent.instructions) == PromptRequest:
            instructions = agent.instructions
        else:
            raise ValueError("Invalid instructions type")

        # create/update the prompt
        try:
            prompt = self.prompts.update(
                name=instructions.name,
                content=instructions.content,
                description=instructions.description,
            )
        except Exception as e:
            debug_print(
                f"tried to update but failed with error {e}, creating new prompt"
            )
            prompt = self.prompts.create(
                name=instructions.name,
                content=instructions.content,
                description=instructions.description,
            )
        # prompt type = prompt... need to convert it into PromptVersionSchema before sending to API

        json_str = (
            [func.__name__ for func in agent.functions] if agent.functions else []
        )

        agent_request = AgentCreateSchema(
            name=agent.name,
            model=agent.model,
            prompt_version_id=prompt.id,
            response_schema=(
                agent.response_format.model_json_schema()
                if agent.response_format
                else None
            ),
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
            functions=None,  # json_str,
            tool_choice=agent.tool_choice,
            parallel_tool_calls=agent.parallel_tool_calls,
        )
        # Endpoint for 'create' is left as a placeholder:
        debug_print("agent request ", agent_request.model_dump())
        json_data = self._make_request(
            "POST", "/shared/agents", agent_request.model_dump()
        )
        return AgentSchema(**json_data)

    def update(
        self,
        name: Optional[str] = None,
        instructions: Optional[str] = None,
        description: Optional[str] = None,
        model: Optional[str] = None,
        agent_id: Optional[int] = None,
    ) -> AgentSchema:
        """Update an existing agent."""
        agent_request = AgentRequest(
            name=name or "",
            instructions=instructions or "You are a helpful agent",
            description=description,
        )
        # Endpoint for 'update' is left as a placeholder:
        json_data = self._make_request("POST", "/version", agent_request.model_dump())
        return AgentSchema(**json_data)

    def delete(self, name: str) -> None:
        """Delete an agent by name."""
        request = self._make_request("DELETE", f"/shared/agents/{name}")
        return request

    def run(
        self,
        agent: Agent,
        message_history: List,
        context: dict = {},
        debug: bool = False,
        max_turns: int = 1000,
        execute_tools: bool = True,
        response_schema: dict = None,
        environment: str = "dev",
    ):
        res = None
        # Send function inputs
        try:
            response = self._make_request(
                "POST",
                f"/shared/agents/run/{agent.id}",
                {
                    "message_history": message_history,
                    "variable_inputs": context,
                    "debug": debug,
                    "max_turns": max_turns,
                    "prompt_version_id": agent.instructions.id,
                    # "execute_tools": execute_tools,
                    "response_schema": response_schema,
                    "environment": environment,
                },
            )
            if response.get("message"):
                raise Exception(response.get("message"))
            else:
                return Response(
                    messages=response.get("messages", []),
                    agent=response.get("agent"),
                    context=response.get("context", {}),
                    response_object=response.get("response_object"),
                    completion=response.get("completion"),
                )
        except Exception as e:
            raise e
        return res
