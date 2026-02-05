"""Environics Analytics data adapter."""

import structlog

from app.ingestion.adapters.base import AbstractDataSourceAdapter, IngestionRecord

logger = structlog.get_logger()


class EnvironicsAdapter(AbstractDataSourceAdapter):
    @property
    def source_name(self) -> str:
        return "Environics Analytics"

    async def fetch_data(self, year: int | None = None) -> list[IngestionRecord]:
        await logger.ainfo("environics_fetch_start", year=year)
        return []

    async def validate_connection(self) -> bool:
        return True
