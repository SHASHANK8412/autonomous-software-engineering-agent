import os
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_random_exponential
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GeminiService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set.")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.initialized = True

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def generate_content(self, prompt: str):
        """Generate content using the Gemini API with retry logic."""
        try:
            response = self.model.generate_content(prompt)
            self._log_token_usage(prompt, response)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content from Gemini: {e}")
            raise

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def stream_content(self, prompt: str):
        """Stream content from the Gemini API."""
        try:
            response = self.model.generate_content(prompt, stream=True)
            for chunk in response:
                yield chunk.text
        except Exception as e:
            logger.error(f"Error streaming content from Gemini: {e}")
            raise

    def _log_token_usage(self, prompt, response):
        """Log the token usage for a given prompt and response."""
        # This is a placeholder for token logging.
        # The actual token count is not directly available in the V1 API.
        # A more sophisticated approach would be to use a tokenizer to estimate usage.
        prompt_tokens = len(prompt.split())
        completion_tokens = len(response.text.split())
        total_tokens = prompt_tokens + completion_tokens
        logger.info(f"Gemini API call token usage: ~{total_tokens} tokens.")

def get_gemini_service():
    return GeminiService()
