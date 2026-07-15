# app/llm/openai.py
from openai import AsyncOpenAI
from app.core.config import settings

class OpenAIClient:
    def __init__(self, api_key: str | None = None):
        self.resolved_key = api_key or settings.OPENAI_API_KEY
        
        if not self.resolved_key:
            raise ValueError("OpenAI API Key has not been configured in your environment or .env file.")
            
        self.client = AsyncOpenAI(api_key=self.resolved_key)
        self.model_name = "gpt-4o-mini"

    async def generate_answer(self, formatted_prompt: str) -> str:
        """
        Asynchronously sends the formatted RAG prompt to the OpenAI chat completions endpoint.
        """
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.0, # Zero-out creativity to minimize RAG hallucinations
            max_tokens=1024
        )
        return response.choices[0].message.content or ""