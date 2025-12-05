# Video Summarizer

I'm building a video summarizer tool. It should be an interactive CLI or TUI in Python that can run on Mac, Linux, and Windows.

Main features:

## Video Translation

The tool should be able to translate a video into a target language.

We'll use [whisper](https://github.com/openai/whisper) for the first version. A future verison might use a different tool (or have the option to use one of several translation tools), so the code should be flexible enough to support that.

## Video Summarization

After yt-dlp fetches a video (or the tool is pointed at a local video), the tool should create a text transcription of the video using whisper.

The tool should then have a way to output the transcription to a file and/or send it into an LLM for summarization. There should be a way to connect to different LLMs (e.g., local tools, ChatGPT, Gemini). I'm not sure if it's possible to send it into Apple Intelligence's "writing tools", but if the text transcription is opened in TextEdit, it should be possible to use the "writing tools" to generate a summary.

Summaries should summarize the video into a single text file and provide a list of key points in the video. The tool should also have a way to output the summary to a file.

## Technology

- yt-dlp to fetch videos. The tool will support any video platform that yt-dlp supports.
- it should also be possible to point the tool to any local video file that ffmepeg supports
- ffmpeg to process video files and to add translated subtitles to videos
- whisper to translate video files
