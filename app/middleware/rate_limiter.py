import time
import json
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import RateLimitError


class SlidingWindowRateLimiter:
    def __init__(self, data_dir: Path) -> None:
        self._file = data_dir / "rate_limit_log.json"
        self._file.parent.mkdir(parents=True, exist_ok=True)
        if not self._file.exists():
            self._file.write_text("[]", encoding="utf-8")

    def _read_log(self) -> list[dict]:
        try:
            data = self._file.read_text(encoding="utf-8")
            return json.loads(data) if data else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_log(self, entries: list[dict]) -> None:
        self._file.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")

    def check(self, key: str) -> None:
        now = time.time()
        window = settings.rate_limit_window_seconds
        max_reqs = settings.rate_limit_requests

        entries = self._read_log()
        cutoff = now - window
        entries = [e for e in entries if e["timestamp"] > cutoff]
        client_entries = [e for e in entries if e["key"] == key]

        if len(client_entries) >= max_reqs:
            raise RateLimitError(
                f"Rate limit exceeded: {max_reqs} requests per {window}s"
            )

        entries.append({"key": key, "timestamp": now})
        self._write_log(entries)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, data_dir: Path) -> None:
        super().__init__(app)
        self._limiter = SlidingWindowRateLimiter(data_dir)

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST":
            client_ip = request.client.host if request.client else "unknown"
            try:
                self._limiter.check(client_ip)
            except RateLimitError as e:
                return JSONResponse(
                    status_code=429,
                    content={"detail": e.detail},
                )
        return await call_next(request)
