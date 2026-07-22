from abc import ABC, abstractmethod
from app.schemas.ai import AIAnalysisResult


class AIStrategy(ABC):
    @abstractmethod
    async def analyze(self, name: str, comment: str) -> AIAnalysisResult:
        ...
