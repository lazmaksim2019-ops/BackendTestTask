from fastapi import status


class AppError(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        if detail:
            self.detail = detail


class ValidationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = "Validation failed"


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"


class RateLimitError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Too many requests"


class AIError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "AI service unavailable"


class EmailError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "Email service unavailable"
