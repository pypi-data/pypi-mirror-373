import argparse
import json
import os
import sys

from blackbear_media_scoring.downloader.downloader import Downloader
from blackbear_media_scoring.downloader.time_utils import parse_time


def main():
    parser = argparse.ArgumentParser(
        description="Download videos from YouTube with optional time ranges."
    )
    parser.add_argument("url", help="The URL of the YouTube video to download.")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="output",
        help="Directory to save the downloaded video. Defaults to 'output'.",
    )
    parser.add_argument(
        "-s",
        "--start-time",
        type=str,
        help="Start time of the video segment (e.g., '00:01:30' or '90').",
    )
    parser.add_argument(
        "-e",
        "--end-time",
        type=str,
        help="End time of the video segment (e.g., '00:02:00' or '120').",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output for yt-dlp.",
        default=False,
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Only print the absolute path of the downloaded file to stdout.",
    )

    args = parser.parse_args()

    start_time_seconds = None
    end_time_seconds = None

    if args.start_time:
        try:
            start_time_seconds = parse_time(args.start_time)
        except ValueError as e:
            # Output error as JSON
            result = {"status": "error", "message": f"Error parsing start time: {e}"}
            print(json.dumps(result))
            sys.exit(1)

    if args.end_time:
        try:
            end_time_seconds = parse_time(args.end_time)
        except ValueError as e:
            # Output error as JSON
            result = {"status": "error", "message": f"Error parsing end time: {e}"}
            print(json.dumps(result))
            sys.exit(1)

    if start_time_seconds is not None and end_time_seconds is not None:
        if start_time_seconds >= end_time_seconds:
            # Output error as JSON
            result = {
                "status": "error",
                "message": "Error: Start time must be before end time.",
            }
            print(json.dumps(result))
            sys.exit(1)

    downloader = Downloader(output_dir=args.output_dir, debug=args.debug)

    try:
        if args.verbose:
            print(f"Attempting to download: {args.url}", file=sys.stderr)
            if start_time_seconds is not None or end_time_seconds is not None:
                print(
                    f"Segment: {args.start_time or '0'} to {args.end_time or 'end'}",
                    file=sys.stderr,
                )

        filepath = downloader.download_youtube(
            args.url, start_time=start_time_seconds, end_time=end_time_seconds
        )
        # Output JSON instead of plain text
        result = {"status": "success", "filepath": os.path.abspath(filepath)}
        print(json.dumps(result))
    except Exception as e:
        # Output error as JSON
        result = {
            "status": "error",
            "message": f"An error occurred during download: {e}",
        }
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
