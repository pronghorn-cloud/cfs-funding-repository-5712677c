"""Simple in-memory rate limiting middleware."""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings


class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int | None = None):  # type: ignore[no-untyped-def]
        super().__init__(app)
        settings = get_settings()
        self.calls_per_minute = calls_per_minute or settings.rate_limit_per_minute
        self.window = 60.0
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()

        # Clean old entries
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if now - t < self.window
        ]

        if len(self._requests[client_ip]) >= self.calls_per_minute:
            return JSONResponse(
                status_code=429,
                content={"error": "RATE_LIMITED", "detail": "Too many requests"},
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
