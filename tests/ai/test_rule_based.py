import pytest
from app.ai.rule_based import RuleBasedAIStrategy


@pytest.mark.asyncio
class TestRuleBasedAI:
    async def test_positive_sentiment(self):
        strategy = RuleBasedAIStrategy()
        result = await strategy.analyze("Alice", "Great work! Thanks a lot!")
        assert result.sentiment == "positive"
        assert result.sentiment_score > 0.5

    async def test_negative_sentiment(self):
        strategy = RuleBasedAIStrategy()
        result = await strategy.analyze("Bob", "This is broken. Terrible bug.")
        assert result.sentiment == "negative"
        assert result.sentiment_score < 0.5

    async def test_neutral_sentiment(self):
        strategy = RuleBasedAIStrategy()
        result = await strategy.analyze("Charlie", "I have a question about the API.")
        assert result.sentiment == "neutral"

    async def test_request_type_classification(self):
        strategy = RuleBasedAIStrategy()
        result = await strategy.analyze("Dave", "How to integrate your API?")
        assert result.request_type == "technical_question"

    async def test_collaboration_detection(self):
        strategy = RuleBasedAIStrategy()
        result = await strategy.analyze("Eve", "I want to collaborate on a project.")
        assert result.request_type == "collaboration"

    async def test_suggested_reply_not_empty(self):
        strategy = RuleBasedAIStrategy()
        result = await strategy.analyze("Frank", "Just saying hello.")
        assert result.suggested_reply
        assert "Frank" in result.suggested_reply
