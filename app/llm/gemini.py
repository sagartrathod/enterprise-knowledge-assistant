# app/llm/gemini.py
import os
from google import genai
from google.genai import types
from app.core.config import settings

class GeminiClient:
    def __init__(self, api_key: str | None = None):
        # Fall back to validated core settings configuration if not provided inline
        self.resolved_key = api_key or settings.GOOGLE_API_KEY
        
        if not self.resolved_key:
            raise ValueError("Google API Key has not been configured in your environment or .env file.")
            
        self.client = genai.Client(api_key=self.resolved_key)
        # Tie the architecture model name directly to text generation requirements
        self.model_name = "gemini-2.5-flash"

    async def generate_answer(self, formatted_prompt: str) -> str:
        """
        Asynchronously sends the formatted RAG prompt to Google Gemini using a low-creativity temperature config.
        """
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=formatted_prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,  # Strict grounding threshold (deterministic results)[cite: 1]
                max_output_tokens=1024,
            )
        )
        return response.text