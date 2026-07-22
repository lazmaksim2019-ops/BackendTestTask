from app.schemas.contact import ContactRequest
from app.schemas.ai import AIAnalysisResult
from app.services.ai_service import AIService
from app.services.email_service import EmailService
from app.repositories.contact_repository import ContactRepository
from app.repositories.stats_repository import StatsRepository


class ContactService:
    def __init__(
        self,
        ai_service: AIService,
        email_service: EmailService,
        contact_repo: ContactRepository,
        stats_repo: StatsRepository,
    ) -> None:
        self._ai = ai_service
        self._email = email_service
        self._contact_repo = contact_repo
        self._stats_repo = stats_repo

    async def process(
        self,
        data: ContactRequest,
        correlation_id: str,
    ) -> dict:
        ai_result = await self._ai.analyze(data.name, data.comment)

        contact_entry = await self._contact_repo.save(data, correlation_id)

        await self._email.send_owner_notification(contact_entry, ai_result.model_dump())
        await self._email.send_user_copy(contact_entry)

        await self._stats_repo.increment("total_contacts")
        await self._stats_repo.increment(f"type_{ai_result.request_type}")

        return {
            "success": True,
            "message": "Your message has been received. We will get back to you shortly.",
            "correlation_id": correlation_id,
            "ai_analysis": ai_result.model_dump(),
        }
