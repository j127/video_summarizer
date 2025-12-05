from src.core.llm import LLMClient
import math

class Translator:
    def __init__(self, client: LLMClient):
        self.client = client

    def translate_segments(self, segments: list, target_language: str, batch_size: int = 20) -> list:
        """
        Translates the text of each segment to the target language.
        Uses batching and JSON formatting to ensure strict 1-to-1 mapping.
        """
        import json
        translated_segments = []

        # Process in batches
        num_batches = math.ceil(len(segments) / batch_size)

        for i in range(num_batches):
            batch = segments[i * batch_size : (i + 1) * batch_size]

            # Prepare input as a list of strings
            texts_to_translate = [seg['text'].strip() for seg in batch]
            json_input = json.dumps(texts_to_translate, ensure_ascii=False, indent=2)

            prompt = (
                f"You are a precise translator. Translate the following JSON list of strings to {target_language}.\n"
                "Rules:\n"
                "1. Return a valid JSON list of strings.\n"
                "2. The output list MUST have exactly the same number of elements as the input list.\n"
                "3. Translate each string independently. DO NOT merge content from multiple strings into one.\n"
                "4. DO NOT split one string into multiple strings.\n"
                "5. Maintain the tone and context of the original text.\n\n"
                f"Input JSON:\n{json_input}\n\n"
                "Output JSON:"
            )

            response = self.client.generate(
                prompt,
                system_prompt=f"You are a professional translator. Translate to {target_language} preserving the exact structure."
            )

            # Parse response
            try:
                # Find the JSON list in the response (in case of extra text)
                start_idx = response.find('[')
                end_idx = response.rfind(']') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    translated_texts = json.loads(json_str)

                    if len(translated_texts) != len(batch):
                        print(f"Warning: Batch {i} size mismatch. Expected {len(batch)}, got {len(translated_texts)}. Fallback to original.")
                        translated_texts = texts_to_translate # Fallback
                else:
                    print(f"Warning: Could not find JSON in response for batch {i}. Fallback to original.")
                    print(f"DEBUG: Raw response:\n{response}")
                    translated_texts = texts_to_translate

            except json.JSONDecodeError as e:
                print(f"Warning: JSON decode error for batch {i}: {e}. Fallback to original.")
                print(f"DEBUG: Raw response:\n{response}")
                translated_texts = texts_to_translate

            # Update segments with translated text
            for j, segment in enumerate(batch):
                new_segment = segment.copy()
                if j < len(translated_texts):
                    new_segment['text'] = translated_texts[j]
                translated_segments.append(new_segment)

        return translated_segments
