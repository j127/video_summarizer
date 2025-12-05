import typer
import os
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.core.downloader import VideoDownloader
from src.core.audio import AudioProcessor
from src.core.transcriber import Transcriber
from src.core.summarizer import Summarizer
from src.core.llm import OllamaClient, OpenAIClient

app = typer.Typer()
console = Console()

from src.cli.interactive import interactive_mode

@app.command()
def process(
    url: Optional[str] = typer.Argument(None, help="URL of the video to process"),
    output_dir: str = typer.Option("output", help="Directory to save outputs"),
    model_size: str = typer.Option("base", help="Whisper model size (tiny, base, small, medium, large)"),
    llm_provider: str = typer.Option("ollama", help="LLM provider (ollama or openai)"),
    llm_model: str = typer.Option("llama3", help="LLM model name"),
    translate: bool = typer.Option(False, help="Translate to English using Whisper"),
    target_language: Optional[str] = typer.Option(None, help="Target language for translation (using LLM)"),
    embed_subs: bool = typer.Option(False, help="Embed subtitles into the video"),
):
    """
    Process a video: Download -> Transcribe -> Summarize -> Translate (optional).
    If no URL is provided, enters interactive mode.
    """
    if url is None:
        interactive_mode()
        return

    console.print(f"[bold green]Processing video:[/bold green] {url}")

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

    # 3. Transcribe/Translate (Whisper)
    # If target_language is set, we just transcribe first (unless it's English, but let's keep it simple).
    # If translate flag is set (and no target_language), we use Whisper's translate (to English).
    whisper_task = "translate" if translate and not target_language else "transcribe"

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description=f"{whisper_task.capitalize().rstrip('e')}ing audio (Whisper)...", total=None)
        transcriber = Transcriber(model_size=model_size)
        result = transcriber.transcribe(audio_path, task=whisper_task)

        # Save SRT
        base, _ = os.path.splitext(video_path)
        srt_path = f"{base}.srt"
        transcriber.save_srt(result, srt_path)
    console.print(f"[green]Transcription saved:[/green] {srt_path}")

    # Initialize LLM Client
    if llm_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        llm_client = OpenAIClient(api_key=api_key, model=llm_model)
    else:
        llm_client = OllamaClient(model=llm_model)

    # 4. LLM Translation (if requested)
    transcript_text = result["text"]

    if target_language:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description=f"Translating to {target_language}...", total=None)
            # We need a Translator class or just do it inline for now.
            # Let's do it inline to fix the build first, then refactor.
            prompt = f"Translate the following text to {target_language}:\n\n{transcript_text}"
            translated_text = llm_client.generate(prompt, system_prompt=f"You are a professional translator. Translate the text to {target_language}.")

            # Update transcript text for summarization
            transcript_text = translated_text

            # Save translated text
            trans_path = f"{base}_{target_language}.txt"
            with open(trans_path, "w") as f:
                f.write(translated_text)
        console.print(f"[green]Translation saved:[/green] {trans_path}")

    # 5. Summarize
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Summarizing transcript...", total=None)
        summarizer = Summarizer(llm_client)
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
