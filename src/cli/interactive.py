from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console
from rich.panel import Panel
import os

from src.core.downloader import VideoDownloader
from src.core.audio import AudioProcessor
from src.core.transcriber import Transcriber
from src.core.summarizer import Summarizer
from src.core.translator import Translator
from src.core.llm import OllamaClient, OpenAIClient

console = Console()

def interactive_mode():
    console.print(Panel.fit("Video Summarizer & Translator", style="bold blue"))

    # 1. Get Video URL
    url = inquirer.text(
        message="Enter the video URL:",
        validate=lambda result: len(result) > 0,
        invalid_message="URL cannot be empty",
    ).execute()

    # 2. Select Actions
    actions = inquirer.checkbox(
        message="Select actions to perform:",
        choices=[
            Choice("download", name="Download Video", enabled=True),
            Choice("extract_audio", name="Extract Audio", enabled=True),
            Choice("transcribe", name="Transcribe (Whisper)", enabled=True),
            Choice("summarize", name="Summarize (LLM)", enabled=True),
            Choice("translate", name="Translate (LLM)", enabled=False),
            Choice("embed_subs", name="Embed Subtitles", enabled=False),
        ],
        validate=lambda result: len(result) > 0,
        invalid_message="Please select at least one action",
    ).execute()

    # 3. Configure Options based on selection
    model_size = "base"
    if "transcribe" in actions:
        model_size = inquirer.select(
            message="Select Whisper model size:",
            choices=["tiny", "base", "small", "medium", "large"],
            default="base",
        ).execute()

    llm_provider = "ollama"
    llm_model = "llama3"
    if "summarize" in actions or "translate" in actions:
        llm_provider = inquirer.select(
            message="Select LLM Provider:",
            choices=["ollama", "openai"],
            default="ollama",
        ).execute()

        if llm_provider == "ollama":
            llm_model = inquirer.text(message="Enter Ollama model name:", default="llama3").execute()
        else:
            llm_model = inquirer.text(message="Enter OpenAI model name:", default="gpt-4o").execute()

    target_language = None
    if "translate" in actions:
        target_language = inquirer.text(
            message="Enter target language (e.g., Spanish, French):",
            validate=lambda result: len(result) > 0,
        ).execute()

    # 4. Execute
    console.print("\n[bold green]Starting processing...[/bold green]")

    try:
        # Download
        video_path = None
        if "download" in actions:
            with console.status("Downloading video..."):
                downloader = VideoDownloader("output")
                video_path = downloader.download(url)
            console.print(f"[green]Downloaded:[/green] {video_path}")

        # Audio
        audio_path = None
        if "extract_audio" in actions and video_path:
            with console.status("Extracting audio..."):
                audio_processor = AudioProcessor()
                audio_path = audio_processor.extract_audio(video_path)
            console.print(f"[green]Audio extracted:[/green] {audio_path}")

        # Transcribe
        transcript_result = None
        srt_path = None
        if "transcribe" in actions and audio_path:
            with console.status(f"Transcribing (Model: {model_size})..."):
                transcriber = Transcriber(model_size=model_size)
                transcript_result = transcriber.transcribe(audio_path)

                base, _ = os.path.splitext(video_path)
                srt_path = f"{base}.srt"
                transcriber.save_srt(transcript_result, srt_path)
            console.print(f"[green]Transcription saved:[/green] {srt_path}")

        # Initialize LLM
        client = None
        if ("summarize" in actions or "translate" in actions) and transcript_result:
            if llm_provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                client = OpenAIClient(api_key=api_key, model=llm_model)
            else:
                client = OllamaClient(model=llm_model)

        # Translate
        translated_srt_path = None
        if "translate" in actions and client and transcript_result:
            with console.status(f"Translating to {target_language}..."):
                # 1. Translate full text for summary/reference (optional but good to have)
                prompt = f"Translate the following text to {target_language}:\n\n{transcript_result['text']}"
                translated_text = client.generate(prompt, system_prompt=f"You are a professional translator. Translate the text to {target_language}.")

                base, _ = os.path.splitext(video_path)
                trans_path = f"{base}_{target_language}.txt"
                with open(trans_path, "w") as f:
                    f.write(translated_text)
                console.print(f"[green]Translation text saved:[/green] {trans_path}")

                # 2. Translate Segments for Subtitles
                if "embed_subs" in actions:
                    console.print("[dim]Translating subtitles segments...[/dim]")
                    translator = Translator(client)
                    translated_segments = translator.translate_segments(transcript_result["segments"], target_language)

                    # Create a new result dict with translated segments
                    translated_result = transcript_result.copy()
                    translated_result["segments"] = translated_segments

                    translated_srt_path = f"{base}_{target_language}.srt"
                    # Ensure transcriber is initialized if not already (e.g., if transcribe wasn't selected)
                    if 'transcriber' not in locals():
                        transcriber = Transcriber(model_size="base") # Default model size if not transcribed
                    transcriber.save_srt(translated_result, translated_srt_path)
                    console.print(f"[green]Translated SRT saved:[/green] {translated_srt_path}")

        # Summarize
        if "summarize" in actions and client and transcript_result:
            with console.status("Summarizing..."):
                summarizer = Summarizer(client)
                summary = summarizer.summarize(transcript_result["text"])

                base, _ = os.path.splitext(video_path)
                summary_path = f"{base}_summary.txt"
                with open(summary_path, "w") as f:
                    f.write(summary)

            console.print(f"[green]Summary saved:[/green] {summary_path}")
            console.print(Panel(summary, title="Summary"))

        # Embed Subs
        if "embed_subs" in actions and video_path:
            # Use translated SRT if available, otherwise original
            subs_to_embed = translated_srt_path if translated_srt_path else srt_path

            if subs_to_embed:
                with console.status(f"Embedding subtitles ({os.path.basename(subs_to_embed)})..."):
                    audio_processor = AudioProcessor() # Reusing for embed_subtitles method
                    output_video = audio_processor.embed_subtitles(video_path, subs_to_embed)
                console.print(f"[green]Video with subtitles:[/green] {output_video}")
            else:
                console.print("[yellow]No subtitles available to embed.[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()
