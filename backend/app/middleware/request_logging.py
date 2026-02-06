"""Structured request/response logging middleware."""

import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.common.metrics import http_request_duration_seconds, http_requests_total

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path

        response = await call_next(request)

        duration = time.perf_counter() - start_time
        status_code = response.status_code

        # Prometheus metrics
        http_requests_total.labels(
            method=method, endpoint=path, status_code=status_code
        ).inc()
        http_request_duration_seconds.labels(method=method, endpoint=path).observe(duration)

        # Skip health check logging to reduce noise
        if not path.startswith("/health"):
            logger.info(
                "request_completed",
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=round(duration * 1000, 2),
                client_ip=request.client.host if request.client else None,
            )

        return response
