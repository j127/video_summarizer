from abc import ABC, abstractmethod
import ollama

class Summarizer(ABC):
    @abstractmethod
    def summarize(self, text: str) -> str:
        pass

class OllamaSummarizer(Summarizer):
    def __init__(self, model: str = "llama3"):
        self.model = model

    def summarize(self, text: str) -> str:
        """
        Summarizes text using Ollama.
        """
        prompt = f"""
        Please provide a concise summary of the following video transcript.
        Also provide a list of key points.

        Transcript:
        {text}
        """

        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error summarizing with Ollama: {str(e)}"

class OpenAISummarizer(Summarizer):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        # Import here to avoid hard dependency if not used
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            self.client = None

    def summarize(self, text: str) -> str:
        if not self.client:
            return "OpenAI client not initialized. Please install 'openai' package."

        prompt = f"""
        Please provide a concise summary of the following video transcript.
        Also provide a list of key points.

        Transcript:
        {text}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes videos."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error summarizing with OpenAI: {str(e)}"
