import os
from typing import Optional

from .prompts import ExtractorPrompts
from .provider.gemini import Gemini
from .provider.openrouter import OpenRouter
from .provider.provider import SupportedModels


class Extractor:
    def __init__(
        self, model: str, image_model: Optional[str], audio_model: Optional[str]
    ):
        self.prompt = ExtractorPrompts()

        # If image_model or audio_model are not specified, use the main model
        if image_model is None:
            image_model = model
        if audio_model is None:
            audio_model = model

        # Validate models
        try:
            selected_model = SupportedModels(model)
            selected_image_model = SupportedModels(image_model)
            selected_audio_model = SupportedModels(audio_model)
        except ValueError:
            supported_models = ", ".join([m.value for m in SupportedModels])
            raise ValueError(
                f"Unsupported model. Supported models are: {supported_models}"
            )

        provider_map = {
            SupportedModels.GEMINI: Gemini,
            SupportedModels.OPENROUTER: OpenRouter,
        }

        # Create providers for each model type
        self.provider = self._create_provider(provider_map, selected_model)
        self.image_provider = self._create_provider(provider_map, selected_image_model)
        self.audio_provider = self._create_provider(provider_map, selected_audio_model)

    def _create_provider(self, provider_map, selected_model):
        """Create a provider instance for the given model."""
        provider_class = provider_map[selected_model]

        api_key = None
        if selected_model == SupportedModels.GEMINI:
            api_key = os.environ.get("GEMINI_API_KEY")
        elif selected_model == SupportedModels.OPENROUTER:
            api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                f"API key for model '{selected_model.value}' not found in environment variables."
            )

        return provider_class(api_key)

    def describe_video(self, video_path: str):
        response = self.provider.describe_video(
            video_path, self.prompt.video_descriptor
        )

        return response

    def describe_images(self, image_paths: list[str]):
        response = self.image_provider.describe_images(
            image_paths, self.prompt.image_descriptor
        )

        return response

    def describe_image(self, image_path: str):
        response = self.image_provider.describe_image(
            image_path, self.prompt.image_descriptor
        )

        return response

    def describe_audio(self, audio_path: str):
        response = self.audio_provider.describe_audio(
            audio_path, self.prompt.audio_descriptor
        )

        return response
