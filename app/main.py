from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, get_db_path
from app.core.error_handler import global_error_handler
from app.middleware.correlation_id import CorrelationIDMiddleware
from app.middleware.logging_middleware import RequestLoggingMiddleware, setup_file_logging
from app.middleware.rate_limiter import RateLimitMiddleware
from app.api.v1.routes import contact, health, metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_file_logging(settings.logs_dir)
    await init_db(get_db_path(settings.data_dir))
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Requested-With"],
)
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, data_dir=settings.data_dir)

app.add_exception_handler(Exception, global_error_handler)

app.include_router(contact.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")

# Routes without version prefix for direct TZ compliance
app.include_router(contact.router, prefix="/api", include_in_schema=False)
app.include_router(health.router, prefix="/api", include_in_schema=False)
app.include_router(metrics.router, prefix="/api", include_in_schema=False)

app.mount("/", StaticFiles(directory=str(settings.base_dir / "static"), html=True), name="static")
