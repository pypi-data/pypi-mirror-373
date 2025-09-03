"""Main SDK class for Prompt Studio."""

from typing import Optional

import requests

from .exceptions import PromptNotFoundError


class PromptStudio:
    """
    SDK for interacting with prompts API.

    This class provides methods to fetch and render prompts using a given API.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api-studio.dev.trustsoft.ai",
    ):
        """
        Initialize the PromptStudio.

        Args:
            api_key: API key for authentication.
            base_url: Base URL for the API.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def get_prompt(
        self, project_name: str, prompt_name: str, alias: Optional[str] = None
    ) -> str:
        """
        Fetch a prompt from the API.

        Args:
            project_name: Name of the project.
            prompt_name: Name of the prompt.
            alias: Optional alias for the prompt, could be number or label of prompt version. If not provided, the latest active prompt is fetched..

        Returns:
            The prompt body as a string.

        Raises:
            ValueError: If the API request fails.
        """
        url = f"{self.base_url}/sdk-api/prompt"
        params = {
            "projectName": project_name,
            "promptName": prompt_name,
        }
        if alias:
            params["alias"] = alias
        response = self.session.get(url=url, params=params)
        if response.status_code == 404:
            raise PromptNotFoundError(
                f"Prompt '{prompt_name}' not found in project '{project_name}'"
            )
        if response.status_code != 200:
            raise PromptNotFoundError(f"Failed to fetch prompt: {response.text}")
        return response.json()["body"]
