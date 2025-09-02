from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class SupportedModels(Enum):
    GEMINI = "gemini"
    OPENROUTER = "openrouter"


class ExtractionResult(BaseModel):
    description: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

    def to_dict(self):
        return {
            "description": self.description,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }


class LLMProvider(ABC):
    @abstractmethod
    def describe_video(
        self, video_path: str, prompt: str = "Describe this video"
    ) -> ExtractionResult:
        """
        Describe a video

        Args:
            video_path (str): Path to the video file
            prompt (str): Prompt to use for video description

        Returns:
            ExtractionResult: Description of the video with token counts
        """
        pass

    @abstractmethod
    def describe_images(
        self, image_paths: list[str], prompt: str = "Describe these images"
    ) -> ExtractionResult:
        """
        Describe multiple images in a single request.

        Args:
            image_paths (list[str]): List of paths to image files
            prompt (str): Prompt to use for image description

        Returns:
            ExtractionResult: Description of the images with token counts
        """
        pass

    @abstractmethod
    def describe_image(
        self, image_path: str, prompt: str = "Describe this image"
    ) -> ExtractionResult:
        """
        Describe an image.

        Args:
            image_path (str): Path to the image file

            prompt (str): Prompt to use for image description
        Returns:
            ExtractionResult: Description of the image with token counts
        """

        pass

    @abstractmethod
    def describe_audio(
        self, audio_path: str, prompt: str = "Describe this audio"
    ) -> ExtractionResult:
        """
        Describe an audio file using Gemini.

        Args:
            audio_path (str): Path to the audio file
            prompt (str): Prompt to use for audio description

        Returns:
            ExtractionResult: Description of the audio with token counts
        """

        pass

