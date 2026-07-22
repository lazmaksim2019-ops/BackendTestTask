from app.schemas.contact import ContactRequest
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

    async def save_contact(
        self,
        data: ContactRequest,
        correlation_id: str,
    ) -> dict:
        await self._contact_repo.save(data, correlation_id)
        return {
            "success": True,
            "message": "Спасибо! Ваше сообщение получено. Мы свяжемся с вами в ближайшее время.",
            "correlation_id": correlation_id,
            "ai_analysis": None,
        }

    async def process_async(
        self,
        data: ContactRequest,
        correlation_id: str,
    ) -> None:
        ai_result = await self._ai.analyze(data.name, data.comment)

        await self._email.send_owner_notification(
            {"name": data.name, "email": data.email, "phone": data.phone, "comment": data.comment},
            ai_result.model_dump(),
        )
        await self._email.send_user_copy(
            {"name": data.name, "email": data.email, "phone": data.phone, "comment": data.comment},
        )

        await self._stats_repo.increment("total_contacts")
        await self._stats_repo.increment(f"type_{ai_result.request_type}")
