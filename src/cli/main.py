import typer
import os
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.core.downloader import VideoDownloader
from src.core.audio import AudioProcessor
from src.core.transcriber import Transcriber
from src.core.summarizer import OllamaSummarizer, OpenAISummarizer

app = typer.Typer()
console = Console()

@app.command()
def process(
    url: str = typer.Argument(..., help="URL of the video to process"),
    output_dir: str = typer.Option("output", help="Directory to save outputs"),
    model_size: str = typer.Option("base", help="Whisper model size"),
    llm_provider: str = typer.Option("ollama", help="LLM provider (ollama or openai)"),
    llm_model: str = typer.Option("llama3", help="LLM model name"),
    embed_subs: bool = typer.Option(True, help="Embed subtitles into video"),
):
    """
    Download, transcribe, summarize, and optionally embed subtitles for a video.
    """
    console.print(f"[bold green]Processing video from:[/bold green] {url}")

    # 1. Download
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Downloading video...", total=None)
        downloader = VideoDownloader(output_dir)
        video_path = downloader.download(url)
    console.print(f"[green]Downloaded:[/green] {video_path}")

    # 2. Extract Audio
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Extracting audio...", total=None)
        audio_processor = AudioProcessor()
        audio_path = audio_processor.extract_audio(video_path)
    console.print(f"[green]Audio extracted:[/green] {audio_path}")

    # 3. Transcribe
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Transcribing audio...", total=None)
        transcriber = Transcriber(model_size=model_size)
        result = transcriber.transcribe(audio_path)

        # Save SRT
        base, _ = os.path.splitext(video_path)
        srt_path = f"{base}.srt"
        transcriber.save_srt(result, srt_path)
    console.print(f"[green]Transcription saved:[/green] {srt_path}")

    # 4. Summarize
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Summarizing transcript...", total=None)
        transcript_text = result["text"]

        if llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            summarizer = OpenAISummarizer(api_key=api_key, model=llm_model)
        else:
            summarizer = OllamaSummarizer(model=llm_model)

        summary = summarizer.summarize(transcript_text)

        summary_path = f"{base}_summary.txt"
        with open(summary_path, "w") as f:
            f.write(summary)
    console.print(f"[green]Summary saved:[/green] {summary_path}")
    console.print(f"\n[bold]Summary:[/bold]\n{summary}\n")

    # 5. Embed Subtitles
    if embed_subs:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Embedding subtitles...", total=None)
            output_video_path = audio_processor.embed_subtitles(video_path, srt_path)
        console.print(f"[green]Video with subtitles saved:[/green] {output_video_path}")

if __name__ == "__main__":
    app()
