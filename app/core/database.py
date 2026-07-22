import aiosqlite
from pathlib import Path


DB_FILENAME = "app.db"
_connection: aiosqlite.Connection | None = None


def get_db_path(data_dir: Path) -> Path:
    return data_dir / DB_FILENAME


async def init_db(db_path: Path) -> None:
    global _connection
    db_path.parent.mkdir(parents=True, exist_ok=True)
    _connection = await aiosqlite.connect(db_path)
    _connection.row_factory = aiosqlite.Row
    await _connection.executescript("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            comment TEXT NOT NULL,
            correlation_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS stats (
            key TEXT PRIMARY KEY,
            value INTEGER NOT NULL DEFAULT 0
        );

        INSERT OR IGNORE INTO stats (key, value) VALUES ('total_contacts', 0);
    """)
    await _connection.commit()


def get_connection() -> aiosqlite.Connection:
    global _connection
    if _connection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _connection
