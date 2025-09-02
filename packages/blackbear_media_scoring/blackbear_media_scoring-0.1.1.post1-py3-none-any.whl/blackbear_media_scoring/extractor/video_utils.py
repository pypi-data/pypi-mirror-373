import os
import shutil
import tempfile
from typing import List, Optional

import ffmpeg


def extract_frames_and_audio(
    video_path: str, frames_per_second: int = 1
) -> tuple[List[str], Optional[str]]:
    """
    Extract frames and audio from a video file.

    Args:
        video_path (str): Path to the video file
        frames_per_second (int): Number of frames to extract per second

    Returns:
        tuple: List of frame paths and audio file path (if exists)
    """
    # Create temporary directory for extracted frames and audio
    temp_dir = tempfile.mkdtemp()

    try:
        # Extract frames
        frame_pattern = os.path.join(temp_dir, "frame_%04d.jpg")
        (
            ffmpeg.input(video_path)
            .output(frame_pattern, vf=f"fps={frames_per_second}", vcodec="mjpeg")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        # Get list of frame files
        frame_files = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if f.startswith("frame_") and f.endswith(".jpg")
        ]
        frame_files.sort()

        # Extract audio
        audio_path = os.path.join(temp_dir, "audio.mp3")
        try:
            (
                ffmpeg.input(video_path)
                .output(audio_path, acodec="mp3")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error:
            # If audio extraction fails, set audio_path to None
            audio_path = None

        return frame_files, audio_path

    except Exception as e:
        # Clean up temp directory if something goes wrong
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise e


def cleanup_temp_files(frame_files: List[str], audio_path: Optional[str] = None):
    """
    Clean up temporary files created during video processing.

    Args:
        frame_files (List[str]): List of frame file paths
        audio_path (Optional[str]): Audio file path if exists
    """
    # Clean up frame files
    for frame_file in frame_files:
        try:
            os.remove(frame_file)
        except OSError:
            pass

    # Clean up audio file if exists
    if audio_path and os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except OSError:
            pass

    # Clean up parent directory if empty
    if frame_files:
        temp_dir = os.path.dirname(frame_files[0])
        try:
            os.rmdir(temp_dir)
        except OSError:
            pass
    elif audio_path:
        temp_dir = os.path.dirname(audio_path)
        try:
            os.rmdir(temp_dir)
        except OSError:
            pass

