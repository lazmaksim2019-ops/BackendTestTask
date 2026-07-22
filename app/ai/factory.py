import logging
from app.ai.base import AIStrategy
from app.ai.agnes import AgnesAIStrategy
from app.ai.rule_based import RuleBasedAIStrategy
from app.core.config import settings

logger = logging.getLogger("app.ai")


def create_ai_strategy() -> AIStrategy:
    if settings.ai_api_key:
        logger.info("Using Agnes AI strategy")
        return AgnesAIStrategy()

    logger.warning("No AI API key configured, using rule-based fallback")
    return RuleBasedAIStrategy()
