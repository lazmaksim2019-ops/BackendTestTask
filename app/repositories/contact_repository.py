from app.core.database import get_connection
from app.schemas.contact import ContactRequest


class ContactRepository:
    async def save(self, contact: ContactRequest, correlation_id: str) -> dict:
        db = get_connection()
        await db.execute(
            "INSERT INTO contacts (name, email, phone, comment, correlation_id) VALUES (?, ?, ?, ?, ?)",
            (contact.name, contact.email, contact.phone, contact.comment, correlation_id),
        )
        await db.commit()
        return contact.model_dump() | {"correlation_id": correlation_id}

    async def count(self) -> int:
        db = get_connection()
        cursor = await db.execute_fetchall("SELECT COUNT(*) as cnt FROM contacts")
        return cursor[0]["cnt"] if cursor else 0
