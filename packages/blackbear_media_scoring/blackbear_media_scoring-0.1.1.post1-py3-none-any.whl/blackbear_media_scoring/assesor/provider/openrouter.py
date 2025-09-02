import json
import os

import requests

from ..prompts import AssessorPrompts
from .llm import LLM, ScoreResult


class OpenRouter(LLM):
    def __init__(self, model: str = "google/gemini-2.5-flash-lite"):
        """
        Initialize the OpenRouter client.

        Args:
            model (str): The OpenRouter model to use for requests
        """
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.model = os.environ.get("OPENROUTER_ASSESSOR_MODEL") or model
        self.base_url = "https://openrouter.ai/api/v1"
        self.prompt = AssessorPrompts()

    def score(self, text: str) -> ScoreResult:
        """
        Score the text using OpenRouter.

        Args:
            text (str): The text to score

        Returns:
            ScoreResult: The scoring result with categories and scores
        """
        # Format the prompt with the text
        prompt = self.prompt.base_template.format(text=text)

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }

        # Make API request
        response = requests.post(
            f"{self.base_url}/chat/completions", headers=headers, json=data
        )

        # Raise exception for bad status codes
        response.raise_for_status()

        # Parse response
        response_data = response.json()
        response_text = response_data["choices"][0]["message"]["content"]

        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if "usage" in response_data:
            usage = response_data["usage"]
            input_tokens = usage.get("prompt_tokens")
            output_tokens = usage.get("completion_tokens")

        # Parse the JSON response into ScoreResult
        try:
            response_json = json.loads(response_text)
            response_json["input_tokens"] = input_tokens
            response_json["output_tokens"] = output_tokens
            return ScoreResult.model_validate(response_json)
        except Exception as e:
            raise TypeError(f"Failed to parse response into ScoreResult: {e}")

