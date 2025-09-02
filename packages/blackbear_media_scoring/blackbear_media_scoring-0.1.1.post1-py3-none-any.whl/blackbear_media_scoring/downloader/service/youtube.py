import os

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, download_range_func

from ..time_utils import hhmmss

class FakeLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

class Youtube:
    def __init__(
        self, output_dir="output", media_type="video", fmt_override=None, debug=False
    ):
        self.output_dir = output_dir
        self.media_type = media_type
        self.fmt_override = fmt_override
        self.debug = debug

        os.makedirs(self.output_dir, exist_ok=True)

    def _check_file_exists(self, url, start_time=None, end_time=None):
        """Check if the file already exists in the output directory."""
        try:
            # Create a temporary YoutubeDL instance to extract info without downloading
            ydl_opts = {
                "quiet": True,
                "logger": FakeLogger(),
                "ignoreerrors": True,
                "no_warnings": True,
                "simulate": True,  # Don't download, just extract info
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            # Generate the expected filename based on the same logic as in download()
            if start_time is not None and end_time is not None:
                start_str = hhmmss(start_time).replace(":", "-")
                end_str = hhmmss(end_time).replace(":", "-")
                filename_template = f"%(id)s_{start_str}_to_{end_str}.%(ext)s"
            elif start_time is not None:
                start_str = hhmmss(start_time).replace(":", "-")
                filename_template = f"%(id)s_from_{start_str}.%(ext)s"
            elif end_time is not None:
                end_str = hhmmss(end_time).replace(":", "-")
                filename_template = f"%(id)s_to_{end_str}.%(ext)s"
            else:
                filename_template = "%%(id)s.%(ext)s"

            # Replace placeholders with actual values from info
            filename = filename_template % {
                "id": info.get("id", ""),
                "ext": info.get("ext", "mp4")  # Default to mp4 if not available
                .replace("/", "_")
                .replace("\\", "_"),  # Sanitize title
            }

            # Check if file exists in output directory
            full_path = os.path.join(self.output_dir, filename)
            if os.path.exists(full_path):
                return full_path

        except Exception as e:
            # If there's any error in checking, we'll proceed with download
            raise FileExistsError(f"Could not check if file exists: {e}")

        return None

    def download(self, url, start_time=None, end_time=None):
        # Check if file already exists before downloading
        existing_file = self._check_file_exists(url, start_time, end_time)
        if existing_file:
            return existing_file

        # This list will be populated by the progress hook to capture the final filename
        final_filepath_container = []

        def progress_hook(d):
            """Capture the final filename when the post-processing is complete."""
            if d["status"] == "finished":
                final_filepath_container.append(d.get("filename"))

        if start_time is not None and end_time is not None:
            start_str = hhmmss(start_time).replace(":", "-")
            end_str = hhmmss(end_time).replace(":", "-")
            outtmpl = os.path.join(
                self.output_dir, f"%(id)s_{start_str}_to_{end_str}.%(ext)s"
            )
        elif start_time is not None:
            start_str = hhmmss(start_time).replace(":", "-")
            outtmpl = os.path.join(self.output_dir, f"%(id)s_from_{start_str}.%(ext)s")
        elif end_time is not None:
            end_str = hhmmss(end_time).replace(":", "-")
            outtmpl = os.path.join(self.output_dir, f"%(id)s_to_{end_str}.%(ext)s")
        else:
            outtmpl = os.path.join(self.output_dir, "%%(id)s.%(ext)s")

        fmt_video = "bestvideo[height=720][vcodec^=avc1]+bestaudio/bestvideo[height<=720]+bestaudio/best"
        fmt_audio = "bestaudio[ext=m4a]/bestaudio"

        if self.media_type == "video":
            fmt = self.fmt_override or fmt_video
        else:
            fmt = self.fmt_override or fmt_audio

        ydl_opts = {
            "outtmpl": outtmpl,
            "format": fmt,
            "noplaylist": True,
            "download_ranges": download_range_func(None, [(start_time, end_time)]),
            "force_keyframes_at_cuts": True,
            "progress_hooks": [progress_hook],
            "logger": FakeLogger(),
            "ignoreerrors": True,
            "quiet": not self.debug,
            "no_warnings": not self.debug,
            "verbose": self.debug,
            "external_downloader_args": ["-loglevel", "panic"],
        }

        if start_time is not None:
            ranges = [(start_time, end_time)]
            ydl_opts["download_ranges"] = download_range_func(None, ranges)
            ydl_opts["force_keyframes_at_cuts"] = True

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except DownloadError as e:
            error_msg = str(e).lower()
            if "format" in error_msg and (
                "not available" in error_msg
                or "not found" in error_msg
                or "supported" in error_msg
            ):
                fallback_fmt = "best[acodec!=none][vcodec!=none]/best"
                ydl_opts["format"] = fallback_fmt
                try:
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                except DownloadError as fallback_error:
                    raise DownloadError(f"Failed to download even with fallback format. {fallback_error}")
            else:
                raise DownloadError(f"Failed to download or process video. {e}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")

        if not final_filepath_container:
            raise RuntimeError("Could not determine the output file path after download. The progress hook may have failed.")

        return final_filepath_container[0]
