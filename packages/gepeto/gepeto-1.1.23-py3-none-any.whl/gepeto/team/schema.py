from typing import List, Optional
from pydantic import BaseModel, Field
import logging
from gepeto.team.schemas.agent_schema import Agent

logger = logging.getLogger(__name__)


class Response(BaseModel):
    messages: List = Field(default_factory=list)
    agent: Optional[Agent] = None
    context: dict = Field(default_factory=dict)
    response_object: Optional[dict] = None
    completion: Optional[dict] = None

    @property
    def response_schema(self) -> Optional[BaseModel]:
        if self.agent and self.agent.response_schema and self.response_object:
            return self.agent.response_model(**self.response_object)
        return None

    def __str__(self) -> str:
        output = {
            "messages": self.messages,
            "agent": self.agent,
            "context": self.context,
            "response_object": self.response_object,
            "completion": self.completion,
            "response_schema": (
                self.response_schema.model_json_schema()
                if self.response_schema
                else None
            ),
        }
        return str(output)

    def get_response_schema_dump(self) -> Optional[dict]:
        """Get the JSON schema dump of the response schema model."""
        if self.response_schema:
            return self.response_schema.model_json_schema()
        return None


class Result(BaseModel):
    """possible return values of agent function"""

    value: str = ""
    agent: Optional[Agent] = None
    context: dict = {}
