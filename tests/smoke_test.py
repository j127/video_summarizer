from src.core.downloader import VideoDownloader
from src.core.audio import AudioProcessor
from src.core.transcriber import Transcriber
from src.core.summarizer import OllamaSummarizer

print("Imports successful")
try:
    d = VideoDownloader()
    a = AudioProcessor()
    # t = Transcriber() # Might load model, skip for smoke test
    s = OllamaSummarizer()
    print("Instantiation successful")
except Exception as e:
    print(f"Error: {e}")
