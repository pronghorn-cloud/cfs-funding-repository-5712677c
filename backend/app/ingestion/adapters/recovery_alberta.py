"""Recovery Alberta data adapter."""

import structlog

from app.ingestion.adapters.base import AbstractDataSourceAdapter, IngestionRecord

logger = structlog.get_logger()


class RecoveryAlbertaAdapter(AbstractDataSourceAdapter):
    @property
    def source_name(self) -> str:
        return "Recovery Alberta"

    async def fetch_data(self, year: int | None = None) -> list[IngestionRecord]:
        await logger.ainfo("recovery_alberta_fetch_start", year=year)
        return []

    async def validate_connection(self) -> bool:
        return True
