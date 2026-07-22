import time
import json
import logging
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("app.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = time.time() - start

        log_entry = {
            "correlation_id": getattr(request.state, "correlation_id", None),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(elapsed * 1000, 2),
            "client_ip": request.client.host if request.client else None,
        }

        logger.info(json.dumps(log_entry, ensure_ascii=False))
        return response


def setup_file_logging(logs_dir: Path) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger("app")
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler = logging.FileHandler(
        logs_dir / "app.log", encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
