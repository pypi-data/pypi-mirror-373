from blackbear_media_scoring.assesor.provider.gemini import Gemini
from blackbear_media_scoring.assesor.provider.llm import LLM, ScoreResult
from blackbear_media_scoring.assesor.provider.openrouter import OpenRouter


class Assessor:
    def __init__(self, model: str = "gemini"):
        model_lower = model.lower()
        if model_lower == "gemini":
            self.llm: LLM = Gemini()
        elif model_lower == "openrouter":
            self.llm: LLM = OpenRouter()
        else:
            raise ValueError(
                f"Unsupported model: '{model}'. Supported models are 'gemini' and 'openrouter'."
            )

    def score_text(self, text: str) -> ScoreResult:
        """
        Scores the given text for sensitive content using the initialized LLM.

        Args:
            text (str): The text content to be scored.

        Returns:
            ScoreResult: An object containing the scores for different categories.
        """
        return self.llm.score(text)
