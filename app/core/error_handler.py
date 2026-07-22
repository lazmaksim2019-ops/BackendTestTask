import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppError

logger = logging.getLogger("app")


async def global_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppError):
        logger.warning(
            "App error: %s - %s",
            exc.__class__.__name__,
            exc.detail,
            extra={"path": str(request.url)},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    logger.exception(
        "Unhandled error: %s",
        exc,
        extra={"path": str(request.url)},
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
