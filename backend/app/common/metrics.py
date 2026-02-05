"""Prometheus metrics for monitoring."""

from prometheus_client import Counter, Histogram, Gauge, Info

# Application info
app_info = Info("app", "Application information")

# HTTP metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Circuit breaker metrics
circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=half_open, 2=open)",
    ["name"],
)

# SVI metrics
svi_recalculation_duration_seconds = Histogram(
    "svi_recalculation_duration_seconds",
    "SVI score recalculation duration",
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0],
)

svi_active_indicators = Gauge(
    "svi_active_indicators",
    "Number of active SVI indicators",
)

# Ingestion metrics
ingestion_jobs_total = Counter(
    "ingestion_jobs_total",
    "Total ingestion jobs",
    ["source", "status"],
)

ingestion_job_duration_seconds = Histogram(
    "ingestion_job_duration_seconds",
    "Ingestion job duration in seconds",
    ["source"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0],
)

# Application metrics
funding_applications_total = Counter(
    "funding_applications_total",
    "Total funding applications",
    ["status"],
)

active_user_sessions = Gauge(
    "active_user_sessions",
    "Number of active user sessions",
)
