"""CFS Internal data adapter."""

import structlog

from app.ingestion.adapters.base import AbstractDataSourceAdapter, IngestionRecord

logger = structlog.get_logger()


class CFSInternalAdapter(AbstractDataSourceAdapter):
    @property
    def source_name(self) -> str:
        return "CFS Internal"

    async def fetch_data(self, year: int | None = None) -> list[IngestionRecord]:
        await logger.ainfo("cfs_internal_fetch_start", year=year)
        return []

    async def validate_connection(self) -> bool:
        return True
