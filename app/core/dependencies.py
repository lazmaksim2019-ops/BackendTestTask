from app.ai.factory import create_ai_strategy
from app.services.ai_service import AIService
from app.services.email_service import EmailService
from app.services.contact_service import ContactService
from app.repositories.contact_repository import ContactRepository
from app.repositories.stats_repository import StatsRepository

_contact_service: ContactService | None = None


def _build_contact_service() -> ContactService:
    ai_strategy = create_ai_strategy()
    ai_service = AIService(ai_strategy)
    email_service = EmailService()
    contact_repo = ContactRepository()
    stats_repo = StatsRepository()
    return ContactService(ai_service, email_service, contact_repo, stats_repo)


def get_contact_service() -> ContactService:
    global _contact_service
    if _contact_service is None:
        _contact_service = _build_contact_service()
    return _contact_service


def get_stats_repo() -> StatsRepository:
    return StatsRepository()
