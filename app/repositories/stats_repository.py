import json
import aiofiles
from pathlib import Path


class StatsRepository:
    def __init__(self, data_dir: Path) -> None:
        self._file = data_dir / "stats.json"

    async def increment(self, key: str) -> dict:
        stats = await self._read_all()
        stats[key] = stats.get(key, 0) + 1
        async with aiofiles.open(self._file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(stats, ensure_ascii=False, indent=2))
        return stats

    async def get_all(self) -> dict:
        return await self._read_all()

    async def _read_all(self) -> dict:
        try:
            async with aiofiles.open(self._file, encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content) if content else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
