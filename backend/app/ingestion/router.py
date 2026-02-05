"""Ingestion API routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AdminUser
from app.database import get_db
from app.ingestion import service
from app.ingestion.schemas import IngestionJobResponse, IngestionTrigger

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/trigger", response_model=IngestionJobResponse, status_code=201)
async def trigger_ingestion(
    data: IngestionTrigger,
    user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> IngestionJobResponse:
    job = await service.trigger_ingestion(
        data.data_source_id, db, triggered_by=user.sub, year=data.year
    )
    return IngestionJobResponse.model_validate(job)


@router.get("/jobs/{job_id}", response_model=IngestionJobResponse)
async def get_job_status(
    job_id: uuid.UUID,
    user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> IngestionJobResponse:
    job = await service.get_job_status(job_id, db)
    return IngestionJobResponse.model_validate(job)


@router.get("/jobs", response_model=list[IngestionJobResponse])
async def list_jobs(
    user: AdminUser,
    data_source_id: uuid.UUID | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[IngestionJobResponse]:
    jobs = await service.list_jobs(db, data_source_id, limit)
    return [IngestionJobResponse.model_validate(j) for j in jobs]
