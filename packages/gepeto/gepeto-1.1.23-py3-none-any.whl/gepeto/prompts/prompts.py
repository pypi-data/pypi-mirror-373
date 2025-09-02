import requests
from gepeto.prompts.schema import Prompt, PromptSearchRequest, PromptRequest
import os
from typing import Optional, List


class Prompts:
    def __init__(self, api_key: Optional[str] = None, base_url=""):
        """Initialize Gepeto client with API key from env or passed directly"""
        self.api_key = api_key or os.environ.get("GEPETO_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEPETO_API_KEY must be set in environment or passed to constructor"
            )
        self.base_url = base_url
        self.headers = {"x-api-key": self.api_key}

    def _make_request(self, method: str, endpoint: str, json_data: dict = None) -> dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}/prompts{endpoint}"
        response = requests.request(
            method=method, url=url, headers=self.headers, json=json_data
        )
        response.raise_for_status()
        return response.json()

    def search(self, name: str) -> List[Prompt]:
        """Search for prompts by name"""
        search_request = PromptSearchRequest(name=name)
        json_data = self._make_request("POST", "/search", search_request.model_dump())
        return [Prompt(**prompt) for prompt in json_data]

    def get(self, name: str) -> Prompt:
        """Get a specific prompt by name. case-insensitive"""
        json_data = self._make_request("GET", f"/{name}")
        prompt_fields = {
            "id": json_data["id"],
            "created_at": json_data["created_at"],
            "updated_at": json_data["updated_at"],
            "name": json_data["prompt"]["name"],
            "description": json_data.get("description"),
            "content": json_data.get("content"),
            "prompt_id": json_data["prompt_id"],
            "organization_id": json_data["prompt"].get("organisation_id"),
        }
        return Prompt(**prompt_fields)

    def list(self) -> List[Prompt]:
        """Get all prompts"""
        json_data = self._make_request("GET", "")
        return [Prompt(**prompt).name for prompt in json_data]

    def create(self, name: str, content: str, description: str = None) -> Prompt:
        """Create a new prompt"""
        prompt = PromptRequest(name=name, content=content, description=description)
        json_data = self._make_request("POST", "", prompt.model_dump())
        return Prompt(
            created_at=json_data["created_at"],
            updated_at=json_data["updated_at"],
            id=json_data["id"],
            prompt_id=json_data["prompt_id"],
            name=json_data["prompt"]["name"],
        )

    def update(self, name: str, content: str = None, description: str = None) -> Prompt:
        prompt = PromptRequest(name=name, content=content, description=description)
        json_data = self._make_request("POST", "/version", prompt.model_dump())
        prompt_fields = {
            "id": json_data["id"],
            "created_at": json_data["created_at"],
            "updated_at": json_data["updated_at"],
            "name": json_data["prompt"]["name"],
            "description": json_data.get("description"),
            "content": json_data.get("content"),
            "prompt_id": json_data["prompt_id"],
            "organization_id": json_data["prompt"].get("organisation_id"),
        }
        return Prompt(**prompt_fields)

    def delete(self, name: str) -> None:
        raise NotImplementedError("delete is not currently implemented in the API")
