import json
import aiofiles
from pathlib import Path
from app.schemas.contact import ContactRequest


class ContactRepository:
    def __init__(self, data_dir: Path) -> None:
        self._file = data_dir / "contacts.json"

    async def save(self, contact: ContactRequest, correlation_id: str) -> dict:
        entry = contact.model_dump() | {
            "correlation_id": correlation_id,
        }
        records = await self._read_all()
        records.append(entry)
        async with aiofiles.open(self._file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(records, ensure_ascii=False, indent=2))
        return entry

    async def _read_all(self) -> list:
        try:
            async with aiofiles.open(self._file, encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    async def count(self) -> int:
        records = await self._read_all()
        return len(records)
