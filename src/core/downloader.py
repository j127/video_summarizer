import os
from typing import Optional
import yt_dlp

class VideoDownloader:
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def download(self, url: str) -> str:
        """
        Downloads a video from a URL using yt-dlp.
        Returns the absolute path to the downloaded file.
        """
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            # Allow downloading remote components to solve challenges (e.g. 'n' parameter)
            'remote_components': ['ejs:github'],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return os.path.abspath(filename)
