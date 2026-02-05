"""Reporting API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AdminUser
from app.database import get_db
from app.reporting import service
from app.reporting.schemas import BriefingRequest, ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", response_model=ReportResponse, status_code=201)
async def generate_report(
    request: BriefingRequest,
    user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> ReportResponse:
    result = await service.generate_briefing(request, db, generated_by=user.sub)
    return ReportResponse(**result)
