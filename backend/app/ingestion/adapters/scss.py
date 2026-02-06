"""SCSS (Shelter Capacity & Statistics System) data adapter."""

import structlog

from app.ingestion.adapters.base import AbstractDataSourceAdapter, IngestionRecord

logger = structlog.get_logger()


class SCSSAdapter(AbstractDataSourceAdapter):
    @property
    def source_name(self) -> str:
        return "SCSS"

    async def fetch_data(self, year: int | None = None) -> list[IngestionRecord]:
        logger.info("scss_fetch_start", year=year)
        return []

    async def validate_connection(self) -> bool:
        return True
