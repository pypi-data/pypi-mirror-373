import os
import base64
import json
import requests
from typing import Optional

from .provider import LLMProvider, ExtractionResult
from ..video_utils import extract_frames_and_audio, cleanup_temp_files


class OpenRouter(LLMProvider):
    def __init__(self, api_key: str, model: str = "google/gemini-2.5-flash-lite"):
        """
        Initialize the OpenRouter client with the provided API key.

        Args:
            api_key (str): Your OpenRouter API key
            model (str): The OpenRouter model to use for requests
        """
        self.api_key = os.environ.get("OPENROUTER_API_KEY") or api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Check for environment variables to override default models
        image_model = os.environ.get("OPENROUTER_IMAGE_EXTRACTOR_MODEL")
        if image_model:
            self.image_model = image_model
        else:
            self.image_model = model
            
        audio_model = os.environ.get("OPENROUTER_AUDIO_EXTRACTOR_MODEL")
        if audio_model:
            self.audio_model = audio_model
        else:
            self.audio_model = model
        
    def _encode_file_to_base64(self, file_path: str) -> str:
        """Encode a file to base64 string."""
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode('utf-8')
            
    def _prepare_multimodal_content(self, video_path: str, prompt: str) -> dict:
        """
        Prepare multimodal content for OpenRouter API request.
        
        Args:
            video_path (str): Path to the video file
            prompt (str): Prompt to use for video description
            
        Returns:
            dict: Prepared content for API request
        """
        # Extract frames and audio
        frame_files, audio_path = extract_frames_and_audio(video_path)
        
        try:
            # Prepare content parts
            content_parts = []
            
            # Add prompt as text
            content_parts.append({
                "type": "text",
                "text": prompt
            })
            
            # Add frames as base64 images (limit to first 10 frames to avoid too large requests)
            for frame_path in frame_files[:10]:
                frame_base64 = self._encode_file_to_base64(frame_path)
                content_parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{frame_base64}"
                    }
                })
                
            # Add audio if available
            if audio_path:
                audio_base64 = self._encode_file_to_base64(audio_path)
                content_parts.append({
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_base64,
                        "format": "mp3"
                    }
                })
                
            return {
                "role": "user",
                "content": content_parts
            }
            
        finally:
            # Clean up temporary files
            cleanup_temp_files(frame_files, audio_path)
        
    def describe_video(
        self, video_path: str, prompt: str = "Describe this video"
    ) -> ExtractionResult:
        """
        Describe a video using OpenRouter.
        
        Args:
            video_path (str): Path to the video file
            prompt (str): Prompt to use for video description
            
        Returns:
            ExtractionResult: Description of the video from OpenRouter with token counts
        """
        # Prepare content for API request
        content = self._prepare_multimodal_content(video_path, prompt)
        
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [content]
        }
        
        # Make API request
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        # Raise exception for bad status codes
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        description = response_data["choices"][0]["message"]["content"]
        
        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if "usage" in response_data:
            usage = response_data["usage"]
            input_tokens = usage.get("prompt_tokens")
            output_tokens = usage.get("completion_tokens")
        
        return ExtractionResult(
            description=description,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
    def describe_image(
        self, image_path: str, prompt: str = "Describe this image"
    ) -> ExtractionResult:
        """
        Describe an image using OpenRouter.
        
        Args:
            image_path (str): Path to the image file
            prompt (str): Prompt to use for image description
            
        Returns:
            ExtractionResult: Description of the image from OpenRouter with token counts
        """
        # Encode image to base64
        image_base64 = self._encode_file_to_base64(image_path)
        
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        content = [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            }
        ]
        
        data = {
            "model": self.image_model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }
        
        # Make API request
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        # Raise exception for bad status codes
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        description = response_data["choices"][0]["message"]["content"]
        
        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if "usage" in response_data:
            usage = response_data["usage"]
            input_tokens = usage.get("prompt_tokens")
            output_tokens = usage.get("completion_tokens")
        
        return ExtractionResult(
            description=description,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

    def describe_images(
        self, image_paths: list[str], prompt: str = "Describe these images"
    ) -> ExtractionResult:
        """
        Describe multiple images in a single request.

        Args:
            image_paths (list[str]): List of paths to image files
            prompt (str): Prompt to use for image description

        Returns:
            ExtractionResult: Description of the images from OpenRouter with token counts
        """
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare content parts
        content_parts = []
        
        # Add prompt as text
        content_parts.append({
            "type": "text",
            "text": prompt
        })
        
        # Add each image as base64
        for image_path in image_paths:
            image_base64 = self._encode_file_to_base64(image_path)
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            })
        
        data = {
            "model": self.image_model,
            "messages": [
                {
                    "role": "user",
                    "content": content_parts
                }
            ]
        }
        
        # Make API request
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        # Raise exception for bad status codes
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        description = response_data["choices"][0]["message"]["content"]
        
        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if "usage" in response_data:
            usage = response_data["usage"]
            input_tokens = usage.get("prompt_tokens")
            output_tokens = usage.get("completion_tokens")
        
        return ExtractionResult(
            description=description,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
    def describe_audio(
        self, audio_path: str, prompt: str = "Describe this audio"
    ) -> ExtractionResult:
        """
        Describe an audio file using OpenRouter.
        
        Args:
            audio_path (str): Path to the audio file
            prompt (str): Prompt to use for audio description
            
        Returns:
            ExtractionResult: Description of the audio from OpenRouter with token counts
        """
        # Encode audio to base64
        audio_base64 = self._encode_file_to_base64(audio_path)
        
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        content = [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "input_audio",
                "input_audio": {
                    "data": audio_base64,
                    "format": "mp3"
                }
            }
        ]
        
        data = {
            "model": self.audio_model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }
        
        # Make API request
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        # Raise exception for bad status codes
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        description = response_data["choices"][0]["message"]["content"]
        
        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if "usage" in response_data:
            usage = response_data["usage"]
            input_tokens = usage.get("prompt_tokens")
            output_tokens = usage.get("completion_tokens")
        
        return ExtractionResult(
            description=description,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )