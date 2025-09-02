import os

from google import genai

from ..prompts import AssessorPrompts
from .llm import LLM, ScoreResult


class Gemini(LLM):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=self.api_key)

        # NOTE: Sementara hardcode dulu
        self.model = "models/gemini-2.5-flash"
        self.prompt = AssessorPrompts()

    def score(self, text: str) -> ScoreResult:
        prompt = self.prompt.base_template.format(text=text)
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ScoreResult,
            },
        )

        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if hasattr(response, "usage_metadata") and response.usage_metadata is not None:
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = response.usage_metadata.candidates_token_count

        try:
            score_result = ScoreResult.model_validate(response.parsed)
            score_result.input_tokens = input_tokens
            score_result.output_tokens = output_tokens
            return score_result
        except Exception as e:
            raise TypeError(f"Failed to parse response into ScoreResult: {e}")
