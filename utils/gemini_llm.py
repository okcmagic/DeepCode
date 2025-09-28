import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from mcp_agent.workflows.llm.augmented_llm import AugmentedLLM
import logging

logger = logging.getLogger(__name__)

class GeminiAugmentedLLM(AugmentedLLM):
    def __init__(self, model: str = "gemini-1.5-flash", api_key: str = None, **kwargs):
        super().__init__(model=model, **kwargs)
        if api_key:
            genai.configure(api_key=api_key)

    async def completion(self, prompt, **kwargs):
        """
        Generates a completion using the Google Gemini API.
        It handles `max_tokens` and other generation parameters from kwargs.
        """
        generation_config = {}
        if 'max_tokens' in kwargs:
            generation_config['max_output_tokens'] = kwargs.pop('max_tokens')
        if 'temperature' in kwargs:
            generation_config['temperature'] = kwargs.pop('temperature')

        try:
            model = genai.GenerativeModel(self.model)
            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config if generation_config else None,
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            return f"An error occurred with the Gemini API: {e}"