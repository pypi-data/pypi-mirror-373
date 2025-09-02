import argparse
import os
import sys

from dotenv import load_dotenv


def main():
    """
    Main entry point for the blackbear-score command.
    Supports three subcommands: extract, assess, download
    """
    # Load environment variables
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, ".env")
    load_dotenv(env_path)

    parser = argparse.ArgumentParser(
        description="Blackbear Media Scoring - Unified CLI",
        prog="blackbear-score"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available services",
        required=True
    )

    # Extractor subcommand
    extractor_parser = subparsers.add_parser(
        "extract",
        help="Extract descriptions from media files"
    )
    extractor_parser.add_argument(
        "video_path",
        help="Path to the video file to describe"
    )
    extractor_parser.add_argument(
        "--model",
        default="gemini",
        help="The AI model to use for extraction (default: gemini)"
    )
    extractor_parser.add_argument(
        "--image-model",
        help="The AI model to use for image extraction"
    )
    extractor_parser.add_argument(
        "--audio-model",
        help="The AI model to use for audio extraction"
    )
    extractor_parser.add_argument(
        "--media-type",
        choices=["video", "image", "audio"],
        default="video",
        help="Type of media to process (default: video)"
    )

    # Assessor subcommand
    assessor_parser = subparsers.add_parser(
        "assess",
        help="Assess text for sensitive content"
    )
    assessor_parser.add_argument(
        "text",
        help="The text content to be scored"
    )
    assessor_parser.add_argument(
        "--model",
        default="gemini",
        help="The LLM model to use for assessment (default: gemini)"
    )

    # Downloader subcommand
    downloader_parser = subparsers.add_parser(
        "download",
        help="Download videos from YouTube with optional time ranges"
    )
    downloader_parser.add_argument(
        "url",
        help="The URL of the YouTube video to download"
    )
    downloader_parser.add_argument(
        "-o",
        "--output-dir",
        default="output",
        help="Directory to save the downloaded video (default: output)"
    )
    downloader_parser.add_argument(
        "-s",
        "--start-time",
        type=str,
        help="Start time of the video segment (e.g., '00:01:30' or '90')"
    )
    downloader_parser.add_argument(
        "-e",
        "--end-time",
        type=str,
        help="End time of the video segment (e.g., '00:02:00' or '120')"
    )
    downloader_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output for yt-dlp",
        default=False
    )
    downloader_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Only print the absolute path of the downloaded file to stdout"
    )

    # Parse arguments
    args = parser.parse_args()

    # Delegate to the appropriate service based on the subcommand
    if args.command == "extract":
        # Import and run extractor main function
        from blackbear_media_scoring.extractor.__main__ import main as extractor_main
        # We need to modify sys.argv to match what the extractor expects
        original_argv = sys.argv[:]
        try:
            sys.argv = [original_argv[0] + " extract"] + original_argv[2:]
            extractor_main()
        finally:
            sys.argv = original_argv
    elif args.command == "assess":
        # Import and run assessor main function
        from blackbear_media_scoring.assesor.__main__ import main as assessor_main
        # We need to modify sys.argv to match what the assessor expects
        original_argv = sys.argv[:]
        try:
            sys.argv = [original_argv[0] + " assess"] + original_argv[2:]
            assessor_main()
        finally:
            sys.argv = original_argv
    elif args.command == "download":
        # Import and run downloader main function
        from blackbear_media_scoring.downloader.__main__ import main as downloader_main
        # We need to modify sys.argv to match what the downloader expects
        original_argv = sys.argv[:]
        try:
            sys.argv = [original_argv[0] + " download"] + original_argv[2:]
            downloader_main()
        finally:
            sys.argv = original_argv


if __name__ == "__main__":
    main()
