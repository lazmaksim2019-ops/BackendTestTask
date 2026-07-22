import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        corr_id = request.headers.get(CORRELATION_ID_HEADER, str(uuid.uuid4()))
        request.state.correlation_id = corr_id
        response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER] = corr_id
        return response
