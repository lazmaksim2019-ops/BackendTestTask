import asyncio
import logging
from app.ai.base import AIStrategy
from app.schemas.ai import AIAnalysisResult

logger = logging.getLogger("app.ai")

_AI_TIMEOUT = 5.0

_DEFAULT_FALLBACK = AIAnalysisResult(
    sentiment="neutral",
    sentiment_score=0.0,
    request_type="general",
    suggested_reply="Спасибо за ваше сообщение. Мы свяжемся с вами в ближайшее время.",
)


class AIService:
    def __init__(self, strategy: AIStrategy) -> None:
        self._strategy = strategy

    async def analyze(self, name: str, comment: str) -> AIAnalysisResult:
        try:
            result = await asyncio.wait_for(
                self._strategy.analyze(name, comment),
                timeout=_AI_TIMEOUT,
            )
            logger.info("AI analysis successful: sentiment=%s type=%s", result.sentiment, result.request_type)
            return result
        except Exception as e:
            logger.warning("AI strategy failed (%s): %s", type(self._strategy).__name__, e)

        try:
            from app.ai.rule_based import RuleBasedAIStrategy
            fallback = RuleBasedAIStrategy()
            result = await fallback.analyze(name, comment)
            logger.info("Rule-based fallback completed")
            return result
        except Exception as e:
            logger.error("Rule-based fallback also failed: %s", e)
            return _DEFAULT_FALLBACK
