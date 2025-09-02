from blackbear_media_scoring.downloader.service.youtube import Youtube


class Downloader:
    def __init__(self, output_dir="output", debug=False):
        self.youtube = Youtube(output_dir, "video", "", debug)

    def download_youtube(self, url, start_time=None, end_time=None):
        return self.youtube.download(url, start_time, end_time)
