"""Health check implementations for external dependencies."""

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


async def check_database(db: AsyncSession) -> dict:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "component": "database"}
    except Exception as exc:
        logger.warning("health_check_failed", component="database", error=str(exc))
        return {"status": "unhealthy", "component": "database", "error": str(exc)}


async def check_blob_storage() -> dict:
    """Check Azure Blob Storage connectivity."""
    try:
        from azure.storage.blob.aio import BlobServiceClient
        from app.config import get_settings

        settings = get_settings()
        async with BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        ) as client:
            async for _ in client.list_containers(max_results=1):
                break
        return {"status": "healthy", "component": "blob_storage"}
    except Exception as exc:
        logger.warning("health_check_failed", component="blob_storage", error=str(exc))
        return {"status": "unhealthy", "component": "blob_storage", "error": str(exc)}
