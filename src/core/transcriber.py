import whisper
import os
from typing import Optional, Tuple

class Transcriber:
    def __init__(self, model_size: str = "base"):
        print(f"Loading Whisper model: {model_size}...")
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path: str, task: str = "transcribe") -> dict:
        """
        Transcribes or translates audio file.
        task: "transcribe" or "translate"
        Returns the result dictionary from Whisper.
        """
        print(f"Starting {task} for {audio_path}...")
        result = self.model.transcribe(audio_path, task=task)
        return result

    def save_srt(self, result: dict, output_path: str):
        """
        Saves transcription result as SRT file.
        """
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], start=1):
                start = self._format_timestamp(segment["start"])
                end = self._format_timestamp(segment["end"])
                text = segment["text"].strip()

                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

    def _format_timestamp(self, seconds: float) -> str:
        """
        Formats seconds into SRT timestamp format (HH:MM:SS,mmm).
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
