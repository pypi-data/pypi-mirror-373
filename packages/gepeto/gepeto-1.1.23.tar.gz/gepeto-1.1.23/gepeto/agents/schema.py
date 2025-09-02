from datetime import datetime
from typing import Union, Literal, Dict, Any, Tuple, Optional, Type, List, Callable
from gepeto.prompts.schema import Prompt
from pydantic import BaseModel, computed_field
from gepeto.team.schemas.agent_schema import Agent
from gepeto.team.utils import debug_print
from gepeto.team.utils import func_to_json


## MAJOR TECH DEBT
class PromptAddSchema(BaseModel):
    name: str


class PromptSchema(PromptAddSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromptVersionSchema(BaseModel):
    id: int
    content: str
    description: str
    prompt_id: int
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]
    name: Union[str, None] = None
    prompt: Union[PromptSchema, None] = None


###


class AgentCreateSchema(BaseModel):
    name: str
    model: str
    prompt_version_id: int
    response_schema: Optional[dict] = None
    temperature: Union[float, None] = None
    max_tokens: Union[int, None] = None
    functions: Union[List[str], None] = None
    tool_choice: Union[str, None] = None
    parallel_tool_calls: Union[bool, None] = None


class AgentUpdateSchema(AgentCreateSchema):
    id: int


class AgentSchema(AgentUpdateSchema):
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    prompt_version: Union[PromptVersionSchema, None] = None

    @computed_field
    def functions_as_json(self) -> List[dict]:
        return [func_to_json(f) for f in self.functions]

    def to_agent(self) -> Agent:
        return Agent(
            id=self.id,
            name=self.name,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            instructions=self.map_prompt_version(self.prompt_version),
            functions=self.str_to_callable(self.functions),
            tool_choice=self.tool_choice if type(self.tool_choice) == str else "",
            parallel_tool_calls=self.parallel_tool_calls,
            response_schema=self.response_schema if self.response_schema else None,
        )

    def map_prompt_version(self, agent_prompt_version: dict) -> Prompt:
        mapped_prompt = Prompt(
            id=agent_prompt_version.id,
            created_at=datetime.fromisoformat(agent_prompt_version.created_at),
            updated_at=datetime.fromisoformat(agent_prompt_version.updated_at),
            name=agent_prompt_version.prompt.name,
            description=agent_prompt_version.description,
            content=agent_prompt_version.content,
            prompt_id=agent_prompt_version.prompt_id,
        )
        return mapped_prompt

    def str_to_callable(self, func_names):
        """
        Given a list of function names (strings), return a list of
        the corresponding callable objects. Raises ValueError if
        a name is not found or is not callable.
        """
        if func_names is None:
            return None

        # Skip empty or malformed function names
        if not func_names or func_names == "{}":
            return []

        callables_list = []
        debug_print(True, "func names ", func_names)
        for name in func_names:
            # Skip if name is empty or malformed
            if not name or name == "{}":
                continue

            candidate = globals().get(name)
            if candidate is None:
                raise ValueError(f"Function {name} not found in global scope.")
            if not callable(candidate):
                raise ValueError(f"'{name}' is not callable.")
            callables_list.append(candidate)
        return callables_list

    class Config:
        from_attributes = True


# New request models for agent CRUD requests:
class AgentSearchRequest(BaseModel):
    name: str


class AgentRequest(AgentSearchRequest):
    description: Optional[str] = None
    instructions: Union[str, Callable[[], str]] = "You are a helpful agent"
    # Add any other fields you want to allow when creating/updating an Agent
