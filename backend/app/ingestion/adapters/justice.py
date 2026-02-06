"""Justice data adapter."""

import structlog

from app.ingestion.adapters.base import AbstractDataSourceAdapter, IngestionRecord

logger = structlog.get_logger()


class JusticeAdapter(AbstractDataSourceAdapter):
    @property
    def source_name(self) -> str:
        return "Justice"

    async def fetch_data(self, year: int | None = None) -> list[IngestionRecord]:
        logger.info("justice_fetch_start", year=year)
        return []

    async def validate_connection(self) -> bool:
        return True
