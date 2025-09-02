import os

from google import genai
from google.genai import types

from .provider import LLMProvider, ExtractionResult


class Gemini(LLMProvider):
    def __init__(self, api_key: str):
        """
        Initialize the Gemini client with the provided API key.

        Args:
            api_key (str): Your Gemini API key
        """
        self.client = genai.Client(api_key=api_key)

    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        return os.path.getsize(file_path)

    def _upload_file(self, file_path: str):
        """Upload file using Gemini Files API."""

        return self.client.files.upload(file=file_path)

    def describe_video(
        self, video_path: str, prompt: str = "Describe this video"
    ) -> ExtractionResult:
        """
        Describe a video using Gemini.

        Args:
            video_path (str): Path to the video file
            prompt (str): Prompt to use for video description

        Returns:
            ExtractionResult: Description of the video from Gemini with token counts
        """
        # Check file size to determine upload method
        file_size = self._get_file_size(video_path)

        if file_size > 20 * 1024 * 1024:  # 20MB
            # Upload file first for large files
            uploaded_file = self._upload_file(video_path)
            content = [prompt, uploaded_file]
        else:
            # Embed directly for small files
            with open(video_path, "rb") as f:
                video_bytes = f.read()

            # Determine MIME type based on file extension
            mime_type = self._get_video_mime_type(video_path)

            content = types.Content(
                parts=[
                    types.Part(
                        inline_data=types.Blob(data=video_bytes, mime_type=mime_type)
                    ),
                    types.Part(text=prompt),
                ]
            )

        response = self.client.models.generate_content(
            model="models/gemini-2.5-flash", contents=content
        )

        description = response.text or ""
        
        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if hasattr(response, 'usage_metadata') and response.usage_metadata is not None:
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = (
                response.usage_metadata.candidates_token_count
            )
        
        return ExtractionResult(
            description=description,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

    def describe_image(
        self, image_path: str, prompt: str = "Describe this image"
    ) -> ExtractionResult:
        """
        Describe an image using Gemini.

        Args:
            image_path (str): Path to the image file

            prompt (str): Prompt to use for image description
        Returns:
            ExtractionResult: Description of the image from Gemini with token counts
        """
        # Check file size to determine upload method
        file_size = self._get_file_size(image_path)

        if file_size > 20 * 1024 * 1024:  # 20MB
            # Upload file first for large files
            uploaded_file = self._upload_file(image_path)
            content = [prompt, uploaded_file]
        else:
            # Embed directly for small files
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            # Determine MIME type based on file extension
            mime_type = self._get_image_mime_type(image_path)

            content = types.Content(
                parts=[
                    types.Part(
                        inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
                    ),
                    types.Part(text=prompt),
                ]
            )

        response = self.client.models.generate_content(
            model="models/gemini-2.5-flash", contents=content
        )

        description = response.text or ""
        
        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if hasattr(response, 'usage_metadata') and response.usage_metadata is not None:
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = (
                response.usage_metadata.candidates_token_count
            )
        
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
            ExtractionResult: Description of the images from Gemini with token counts
        """
        content_parts = []
        
        # Add the prompt as the first part
        content_parts.append(types.Part(text=prompt))
        
        # Add each image as a separate part
        for image_path in image_paths:
            # Check file size to determine upload method
            file_size = self._get_file_size(image_path)

            if file_size > 20 * 1024 * 1024:  # 20MB
                # Upload file first for large files
                uploaded_file = self._upload_file(image_path)
                content_parts.append(uploaded_file)
            else:
                # Embed directly for small files
                with open(image_path, "rb") as f:
                    image_bytes = f.read()

                # Determine MIME type based on file extension
                mime_type = self._get_image_mime_type(image_path)

                content_parts.append(
                    types.Part(
                        inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
                    )
                )

        content = types.Content(parts=content_parts)

        response = self.client.models.generate_content(
            model="models/gemini-2.5-flash", contents=content
        )

        description = response.text or ""
        
        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if hasattr(response, 'usage_metadata') and response.usage_metadata is not None:
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = (
                response.usage_metadata.candidates_token_count
            )
        
        return ExtractionResult(
            description=description,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

    def describe_audio(
        self, audio_path: str, prompt: str = "Describe this audio"
    ) -> ExtractionResult:
        """
        Describe an audio file using Gemini.

        Args:
            audio_path (str): Path to the audio file
            prompt (str): Prompt to use for audio description

        Returns:
            ExtractionResult: Description of the audio from Gemini with token counts
        """
        # Check file size to determine upload method
        file_size = self._get_file_size(audio_path)

        if file_size > 20 * 1024 * 1024:  # 20MB
            # Upload file first for large files
            uploaded_file = self._upload_file(audio_path)
            content = [prompt, uploaded_file]
        else:
            # Embed directly for small files
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            # Determine MIME type based on file extension
            mime_type = self._get_audio_mime_type(audio_path)

            content = types.Content(
                parts=[
                    types.Part(
                        inline_data=types.Blob(data=audio_bytes, mime_type=mime_type)
                    ),
                    types.Part(text=prompt),
                ]
            )

        response = self.client.models.generate_content(
            model="models/gemini-2.5-flash", contents=content
        )

        description = response.text or ""
        
        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if hasattr(response, 'usage_metadata') and response.usage_metadata is not None:
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = (
                response.usage_metadata.candidates_token_count
            )
        
        return ExtractionResult(
            description=description,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

    def _get_video_mime_type(self, file_path: str) -> str:
        """Determine MIME type for video files."""
        extension = file_path.lower().split(".")[-1]
        mime_types = {
            "mp4": "video/mp4",
            "mpeg": "video/mpeg",
            "mov": "video/mov",
            "avi": "video/avi",
            "flv": "video/x-flv",
            "mpg": "video/mpg",
            "webm": "video/webm",
            "wmv": "video/wmv",
            "3gpp": "video/3gpp",
        }
        return mime_types.get(extension, "video/mp4")

    def _get_image_mime_type(self, file_path: str) -> str:
        """Determine MIME type for image files."""
        extension = file_path.lower().split(".")[-1]
        mime_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
            "heic": "image/heic",
            "heif": "image/heif",
        }
        return mime_types.get(extension, "image/jpeg")

    def _get_audio_mime_type(self, file_path: str) -> str:
        """Determine MIME type for audio files."""
        extension = file_path.lower().split(".")[-1]
        mime_types = {
            "wav": "audio/wav",
            "mp3": "audio/mp3",
            "aiff": "audio/aiff",
            "aac": "audio/aac",
            "ogg": "audio/ogg",
            "flac": "audio/flac",
        }
        return mime_types.get(extension, "audio/mp3")
