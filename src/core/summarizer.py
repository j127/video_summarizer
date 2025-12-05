from src.core.llm import LLMClient

class Summarizer:
    def __init__(self, client: LLMClient):
        self.client = client

    def summarize(self, text: str) -> str:
        prompt = f"""
        Please provide a concise summary of the following video transcript.
        Also provide a list of key points.

        Transcript:
        {text}
        """
        return self.client.generate(prompt, system_prompt="You are a helpful assistant that summarizes videos.")
