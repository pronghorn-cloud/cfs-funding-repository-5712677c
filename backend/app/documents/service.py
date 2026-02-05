"""Document service with Azure Blob Storage integration."""

import uuid
from pathlib import PurePosixPath

import structlog
from azure.storage.blob.aio import BlobServiceClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.circuit_breaker import CircuitBreaker
from app.config import get_settings
from app.documents.models import Document
from app.exceptions import ExternalServiceException, NotFoundException

logger = structlog.get_logger()
settings = get_settings()

blob_circuit_breaker = CircuitBreaker(name="azure_blob_storage", failure_threshold=3)

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "image/jpeg",
    "image/png",
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


async def upload_document(
    application_id: uuid.UUID,
    file_name: str,
    file_data: bytes,
    content_type: str,
    db: AsyncSession,
    uploaded_by: uuid.UUID,
    category: str | None = None,
) -> Document:
    file_size = len(file_data)
    file_ext = PurePosixPath(file_name).suffix.lower()
    blob_path = f"applications/{application_id}/{uuid.uuid4()}{file_ext}"

    try:
        await blob_circuit_breaker.call(_upload_to_blob, blob_path, file_data, content_type)
    except Exception as exc:
        raise ExternalServiceException(f"Failed to upload file: {exc}") from exc

    doc = Document(
        application_id=application_id,
        file_name=file_name,
        file_type=file_ext.lstrip("."),
        file_size=file_size,
        blob_path=blob_path,
        content_type=content_type,
        category=category,
        created_by=uploaded_by,
    )
    db.add(doc)
    await db.flush()
    return doc


async def download_document(doc_id: uuid.UUID, db: AsyncSession) -> tuple[Document, bytes]:
    stmt = select(Document).where(Document.id == doc_id, Document.is_deleted.is_(False))
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if doc is None:
        raise NotFoundException("Document not found")

    try:
        data = await blob_circuit_breaker.call(_download_from_blob, doc.blob_path)
    except Exception as exc:
        raise ExternalServiceException(f"Failed to download file: {exc}") from exc

    return doc, data


async def delete_document(doc_id: uuid.UUID, db: AsyncSession) -> None:
    stmt = select(Document).where(Document.id == doc_id, Document.is_deleted.is_(False))
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if doc is None:
        raise NotFoundException("Document not found")

    doc.is_deleted = True
    # Optionally delete from blob storage
    try:
        await blob_circuit_breaker.call(_delete_from_blob, doc.blob_path)
    except Exception:
        await logger.awarning("blob_delete_failed", blob_path=doc.blob_path)


async def list_documents(application_id: uuid.UUID, db: AsyncSession) -> list[Document]:
    stmt = (
        select(Document)
        .where(Document.application_id == application_id, Document.is_deleted.is_(False))
        .order_by(Document.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def _upload_to_blob(blob_path: str, data: bytes, content_type: str) -> None:
    async with BlobServiceClient.from_connection_string(
        settings.azure_storage_connection_string
    ) as client:
        container_client = client.get_container_client(settings.azure_storage_container)
        await container_client.upload_blob(
            name=blob_path,
            data=data,
            content_settings={"content_type": content_type},
            overwrite=True,
        )


async def _download_from_blob(blob_path: str) -> bytes:
    async with BlobServiceClient.from_connection_string(
        settings.azure_storage_connection_string
    ) as client:
        container_client = client.get_container_client(settings.azure_storage_container)
        blob_client = container_client.get_blob_client(blob_path)
        download = await blob_client.download_blob()
        return await download.readall()


async def _delete_from_blob(blob_path: str) -> None:
    async with BlobServiceClient.from_connection_string(
        settings.azure_storage_connection_string
    ) as client:
        container_client = client.get_container_client(settings.azure_storage_container)
        blob_client = container_client.get_blob_client(blob_path)
        await blob_client.delete_blob()
