"""Government of Alberta Health data adapter."""

import structlog

from app.ingestion.adapters.base import AbstractDataSourceAdapter, IngestionRecord

logger = structlog.get_logger()


class GoAHealthAdapter(AbstractDataSourceAdapter):
    @property
    def source_name(self) -> str:
        return "GoA Health"

    async def fetch_data(self, year: int | None = None) -> list[IngestionRecord]:
        # Placeholder for GoA Health data integration
        await logger.ainfo("goa_health_fetch_start", year=year)
        return []

    async def validate_connection(self) -> bool:
        return True
