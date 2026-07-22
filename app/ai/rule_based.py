from app.ai.base import AIStrategy
from app.schemas.ai import AIAnalysisResult


POSITIVE_KEYWORDS = [
    "спасибо", "благодарю", "отлично", "хороший", "great", "thanks",
    "amazing", "love", "wonderful", "awesome",
]
NEGATIVE_KEYWORDS = [
    "плохо", "ужасно", "не работает", "баг", "ошибка", "bug", "broken",
    "terrible", "awful", "not working", "broken", "error", "fail",
]

TYPE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("technical_question", ["как сделать", "how to", "помогите", "help", "question", "вопрос", "技术支持"]),
    ("collaboration", ["сотрудничество", "collaboration", "предложение", "offer", "合作", "work together"]),
    ("bug_report", ["баг", "bug", "ошибка", "error", "не работает", "broken", "crash"]),
    ("feature_request", ["хотелось бы", "feature", "улучшение", "improvement", "idea", "идея", "建议"]),
]


class RuleBasedAIStrategy(AIStrategy):
    async def analyze(self, name: str, comment: str) -> AIAnalysisResult:
        text_lower = comment.lower()

        sentiment = "neutral"
        score = 0.5

        pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
        neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)

        if pos_count > neg_count:
            sentiment = "positive"
            score = 0.5 + (pos_count * 0.1)
        elif neg_count > pos_count:
            sentiment = "negative"
            score = 0.5 - (neg_count * 0.1)

        score = max(0.0, min(1.0, score))

        request_type = "general"
        for rtype, keywords in TYPE_KEYWORDS:
            if any(kw in text_lower for kw in keywords):
                request_type = rtype
                break

        suggested_reply = self._generate_reply(name, sentiment, request_type, comment)

        return AIAnalysisResult(
            sentiment=sentiment,
            sentiment_score=round(score, 2),
            request_type=request_type,
            suggested_reply=suggested_reply,
        )

    def _generate_reply(self, name: str, sentiment: str, request_type: str, comment: str) -> str:
        greeting = f"Dear {name},"

        templates: dict[str, str] = {
            "technical_question": "Thank you for your technical inquiry. I will review your question and get back to you with a detailed answer shortly.",
            "collaboration": "Thank you for reaching out regarding collaboration. I am always open to interesting projects and would be happy to discuss this further.",
            "bug_report": "Thank you for reporting this issue. I take bugs seriously and will investigate it right away. I appreciate your help in improving the project.",
            "feature_request": "Thank you for your suggestion! I value user feedback and will consider adding this feature in future updates.",
            "general": "Thank you for your message. I have received your inquiry and will respond as soon as possible.",
        }

        body = templates.get(request_type, templates["general"])
        closing = "\n\nBest regards,\nThe Development Team"
        return f"{greeting}\n\n{body}{closing}"
