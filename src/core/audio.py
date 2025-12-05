import os
from typing import Optional
import ffmpeg

class AudioProcessor:
    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extracts audio from a video file.
        Returns the path to the extracted audio file.
        """
        if output_path is None:
            base, _ = os.path.splitext(video_path)
            output_path = f"{base}.wav"

        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_path, acodec='pcm_s16le', ac=1, ar='16k')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            print(f"Error extracting audio: {e.stderr.decode()}")
            raise

        return output_path

    def embed_subtitles(self, video_path: str, subtitle_path: str, output_path: Optional[str] = None) -> str:
        """
        Embeds subtitles into a video file.
        Returns the path to the video file with embedded subtitles.
        """
        if output_path is None:
            base, ext = os.path.splitext(video_path)
            output_path = f"{base}_subbed{ext}"

        try:
            video = ffmpeg.input(video_path)
            # soft subtitles
            # (
            #     ffmpeg
            #     .output(video, output_path, vf=f"subtitles={subtitle_path}")
            #     .overwrite_output()
            #     .run(capture_stdout=True, capture_stderr=True)
            # )

            # For soft subs (mkv/mp4 container support varies), we usually map the subtitle stream.
            # But for "burning in" (hard subs), we use the subtitles filter.
            # Let's support hard subs for now as it's more universally compatible for viewing.
            # If soft subs are preferred, we can change this.

            (
                ffmpeg
                .input(video_path)
                .output(output_path, vf=f"subtitles='{subtitle_path}'")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

        except ffmpeg.Error as e:
            print(f"Error embedding subtitles: {e.stderr.decode()}")
            raise

        return output_path
