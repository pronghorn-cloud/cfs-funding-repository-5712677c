"""Document API routes."""

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.database import get_db
from app.documents import service
from app.documents.schemas import DocumentResponse, DocumentUploadResponse
from app.exceptions import ValidationException

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    application_id: uuid.UUID = Form(...),
    category: str | None = Form(None),
    file: UploadFile = File(...),
    user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    if file.content_type not in service.ALLOWED_CONTENT_TYPES:
        raise ValidationException(f"File type '{file.content_type}' not allowed")

    data = await file.read()
    if len(data) > service.MAX_FILE_SIZE:
        raise ValidationException("File exceeds maximum size of 50 MB")

    doc = await service.upload_document(
        application_id=application_id,
        file_name=file.filename or "unnamed",
        file_data=data,
        content_type=file.content_type or "application/octet-stream",
        db=db,
        uploaded_by=user.sub,
        category=category,
    )
    return DocumentUploadResponse(id=doc.id, file_name=doc.file_name, file_size=doc.file_size)


@router.get("/{doc_id}")
async def download_document(
    doc_id: uuid.UUID,
    user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Response:
    doc, data = await service.download_document(doc_id, db)
    return Response(
        content=data,
        media_type=doc.content_type,
        headers={"Content-Disposition": f'attachment; filename="{doc.file_name}"'},
    )


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: uuid.UUID,
    user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
) -> None:
    await service.delete_document(doc_id, db)


@router.get("/application/{application_id}", response_model=list[DocumentResponse])
async def list_documents(
    application_id: uuid.UUID,
    user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentResponse]:
    docs = await service.list_documents(application_id, db)
    return [DocumentResponse.model_validate(d) for d in docs]
