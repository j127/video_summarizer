# Video Summarizer

A powerful CLI tool to download, transcribe, summarize, and translate videos. It leverages `yt-dlp` for downloading, `ffmpeg` for audio processing, `OpenAI Whisper` for transcription, and LLMs (Ollama or OpenAI) for summarization.

## Features

- **Video Downloading**: Supports YouTube and any other platform supported by `yt-dlp`.
- **Audio Extraction**: Extracts audio from video files automatically.
- **Transcription**: Uses OpenAI's Whisper model to transcribe audio to text with high accuracy.
- **Summarization**: Generates concise summaries and key points using local LLMs (Ollama) or OpenAI's API.
- **Subtitle Embedding**: Optionally embeds the generated subtitles (SRT) back into the video.
- **Cross-Platform**: Works on macOS, Linux, and Windows.

## Prerequisites

Before running the tool, ensure you have the following installed:

1.  **Python 3.9+**
2.  **uv** (Python package manager): [Installation Guide](https://github.com/astral-sh/uv)
3.  **ffmpeg**: Required for audio processing.
    - macOS: `brew install ffmpeg`
    - Linux: `sudo apt install ffmpeg`
    - Windows: `winget install ffmpeg`
4.  **Ollama** (Optional, for local summarization): [Download Ollama](https://ollama.com)
    - After installing, pull the default model: `ollama pull llama3`

## Installation

1.  Clone the repository:

    ```bash
    git clone <repository-url>
    cd video_summarizer
    ```

2.  Sync dependencies using `uv`:
    ```bash
    uv sync
    ```

## Usage

The tool is run via the CLI. You can execute it using `uv` or directly with the virtual environment's Python.

### Basic Usage

Process a video URL (Download -> Transcribe -> Summarize -> Embed Subs):

```bash
PYTHONPATH=. .venv/bin/python -m src.cli.main "https://www.youtube.com/watch?v=example"
```

### Options

| Option                             | Default  | Description                                                                                                  |
| :--------------------------------- | :------- | :----------------------------------------------------------------------------------------------------------- |
| `--output-dir`                     | `output` | Directory to save downloaded files and results.                                                              |
| `--model-size`                     | `base`   | Whisper model size (`tiny`, `base`, `small`, `medium`, `large`). Larger models are more accurate but slower. |
| `--llm-provider`                   | `ollama` | LLM provider to use: `ollama` (local) or `openai` (cloud).                                                   |
| `--llm-model`                      | `llama3` | Model name to use (e.g., `llama3` for Ollama, `gpt-4o` for OpenAI).                                          |
| `--translate`                      | `False`  | Translate audio to English (using Whisper).                                                                  |
| `--target-language`                | `None`   | Translate transcript to this language (using LLM). Overrides `--translate`.                                  |
| `--embed-subs` / `--no-embed-subs` | `True`   | Whether to embed the generated subtitles into the video.                                                     |

### Examples

**Use a larger Whisper model for better accuracy:**

```bash
PYTHONPATH=. .venv/bin/python -m src.cli.main "URL" --model-size medium
```

**Use OpenAI for summarization:**
_Requires `OPENAI_API_KEY` environment variable._

```bash
export OPENAI_API_KEY="sk-..."
PYTHONPATH=. .venv/bin/python -m src.cli.main "URL" --llm-provider openai --llm-model gpt-4o
```

**Disable subtitle embedding:**

```bash
PYTHONPATH=. .venv/bin/python -m src.cli.main "URL" --no-embed-subs
```

## Project Structure

- `src/core/`: Core logic modules.
  - `downloader.py`: Handles video downloading.
  - `audio.py`: Handles audio extraction and ffmpeg operations.
  - `transcriber.py`: Handles Whisper transcription.
  - `summarizer.py`: Handles LLM interactions.
- `src/cli/`: CLI entry point and commands.
- `output/`: Default directory for artifacts (ignored by git).
