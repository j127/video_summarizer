from abc import ABC, abstractmethod
import ollama

class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        pass

class OllamaClient(LLMClient):
    def __init__(self, model: str = "llama3"):
        self.model = model

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error with Ollama: {str(e)}"

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            self.client = None

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        if not self.client:
            return "OpenAI client not initialized. Please install 'openai' package."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error with OpenAI: {str(e)}"
