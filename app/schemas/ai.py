from pydantic import BaseModel


class AIAnalysisResult(BaseModel):
    sentiment: str
    sentiment_score: float
    request_type: str
    suggested_reply: str
