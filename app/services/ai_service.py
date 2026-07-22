import logging
from app.ai.base import AIStrategy
from app.schemas.ai import AIAnalysisResult

logger = logging.getLogger("app.ai")


class AIService:
    def __init__(self, strategy: AIStrategy) -> None:
        self._strategy = strategy

    async def analyze(self, name: str, comment: str) -> AIAnalysisResult:
        try:
            result = await self._strategy.analyze(name, comment)
            logger.info("AI analysis successful: sentiment=%s type=%s", result.sentiment, result.request_type)
            return result
        except Exception as e:
            logger.warning("AI strategy failed (%s), falling back to rule-based: %s", type(self._strategy).__name__, e)
            from app.ai.rule_based import RuleBasedAIStrategy
            fallback = RuleBasedAIStrategy()
            result = await fallback.analyze(name, comment)
            logger.info("Rule-based fallback completed")
            return result
