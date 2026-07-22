from app.core.database import get_connection


class StatsRepository:
    async def increment(self, key: str) -> dict:
        db = get_connection()
        await db.execute(
            "INSERT INTO stats (key, value) VALUES (?, 1) ON CONFLICT(key) DO UPDATE SET value = value + 1",
            (key,),
        )
        await db.commit()

        cursor = await db.execute_fetchall("SELECT key, value FROM stats")
        return {row["key"]: row["value"] for row in cursor}

    async def get_all(self) -> dict:
        db = get_connection()
        cursor = await db.execute_fetchall("SELECT key, value FROM stats")
        return {row["key"]: row["value"] for row in cursor}
