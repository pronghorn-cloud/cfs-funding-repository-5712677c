"""FastAPI application factory with lifespan and middleware."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, RedirectResponse
from prometheus_client import make_asgi_app

from app.common.logging_config import setup_logging
from app.common.metrics import app_info
from app.config import get_settings
from app.database import close_db, init_db
from app.exceptions import register_exception_handlers
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.rate_limiting import RateLimitingMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown."""
    setup_logging()
    logger.info("app_starting", environment=settings.environment)

    # Initialize database (dev only - use alembic migrations in prod)
    if settings.environment == "development":
        try:
            await init_db()
        except Exception as exc:
            logger.warning("db_init_skipped", error=str(exc))

    app_info.info({
        "version": settings.app_version,
        "environment": settings.environment,
    })

    yield

    logger.info("app_shutting_down")
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware (order matters - outermost first)
    app.add_middleware(RateLimitingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    # Exception handlers
    register_exception_handlers(app)

    # Prometheus metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    # Root redirect to API docs
    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/api/docs")

    # Register routers
    _register_routers(app)

    return app


def _register_routers(app: FastAPI) -> None:
    """Register all API routers."""
    from app.health.router import router as health_router
    from app.auth.router import router as auth_router
    from app.organizations.router import router as organizations_router
    from app.applications.router import router as applications_router
    from app.documents.router import router as documents_router
    from app.reviews.router import router as reviews_router
    from app.reporting.router import router as reporting_router
    from app.vulnerability.router import router as vulnerability_router
    from app.ingestion.router import router as ingestion_router
    from app.geography.router import router as geography_router

    # Health checks (no prefix)
    app.include_router(health_router)

    # API v1 routes
    api_prefix = "/api/v1"
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(organizations_router, prefix=api_prefix)
    app.include_router(applications_router, prefix=api_prefix)
    app.include_router(documents_router, prefix=api_prefix)
    app.include_router(reviews_router, prefix=api_prefix)
    app.include_router(reporting_router, prefix=api_prefix)
    app.include_router(vulnerability_router, prefix=api_prefix)
    app.include_router(ingestion_router, prefix=api_prefix)
    app.include_router(geography_router, prefix=api_prefix)


app = create_app()
