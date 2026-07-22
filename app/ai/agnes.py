from openai import AsyncOpenAI
from app.ai.base import AIStrategy
from app.schemas.ai import AIAnalysisResult
from app.core.config import settings

SYSTEM_PROMPT = """You are a contact form analysis assistant. Analyze the user's message and return ONLY valid JSON with these fields:
- sentiment: one of "positive", "neutral", "negative"
- sentiment_score: float from 0.0 to 1.0
- request_type: one of "technical_question", "collaboration", "bug_report", "feature_request", "general"
- suggested_reply: a brief professional reply addressing the query

Return ONLY the JSON object, no markdown, no code blocks."""


class AgnesAIStrategy(AIStrategy):
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.ai_api_key,
            base_url=settings.ai_api_base_url,
            timeout=8.0,
        )

    async def analyze(self, name: str, comment: str) -> AIAnalysisResult:
        response = await self._client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Name: {name}\nMessage: {comment}",
                },
            ],
            temperature=0.3,
            max_tokens=512,
        )

        raw = response.choices[0].message.content or ""
        import json
        data = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
        return AIAnalysisResult(**data)
