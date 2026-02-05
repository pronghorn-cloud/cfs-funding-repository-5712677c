"""Funding application API routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.applications import service
from app.applications.schemas import (
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationUpdate,
    CommentCreate,
    CommentResponse,
    DecisionCreate,
    SectionResponse,
    SectionSave,
    StatusTransition,
)
from app.auth.dependencies import AdminUser, CurrentUser, ReviewerUser
from app.common.pagination import PaginatedResponse, PaginationParams
from app.database import get_db

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationResponse, status_code=201)
async def create_application(
    data: ApplicationCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> ApplicationResponse:
    app = await service.create_application(data, db, created_by=user.sub)
    return ApplicationResponse.model_validate(app)


@router.get("", response_model=PaginatedResponse[ApplicationListResponse])
async def list_applications(
    user: CurrentUser,
    pagination: PaginationParams = Depends(),
    organization_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ApplicationListResponse]:
    return await service.list_applications(db, pagination, organization_id, status)


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> ApplicationResponse:
    app = await service.get_application(app_id, db)
    return ApplicationResponse.model_validate(app)


@router.patch("/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: uuid.UUID,
    data: ApplicationUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> ApplicationResponse:
    app = await service.update_application(app_id, data, db, updated_by=user.sub)
    return ApplicationResponse.model_validate(app)


@router.post("/{app_id}/sections", response_model=SectionResponse)
async def save_section(
    app_id: uuid.UUID,
    data: SectionSave,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> SectionResponse:
    section = await service.save_section(app_id, data, db)
    return SectionResponse.model_validate(section)


@router.post("/{app_id}/status", response_model=ApplicationResponse)
async def transition_status(
    app_id: uuid.UUID,
    data: StatusTransition,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> ApplicationResponse:
    app = await service.transition_status(app_id, data, db, changed_by=user.sub)
    return ApplicationResponse.model_validate(app)


@router.post("/{app_id}/decision", response_model=ApplicationResponse)
async def make_decision(
    app_id: uuid.UUID,
    data: DecisionCreate,
    user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> ApplicationResponse:
    app = await service.make_decision(app_id, data, db, decided_by=user.sub)
    return ApplicationResponse.model_validate(app)


@router.post("/{app_id}/comments", response_model=CommentResponse, status_code=201)
async def add_comment(
    app_id: uuid.UUID,
    data: CommentCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    comment = await service.add_comment(app_id, data, db, user_id=user.sub)
    return CommentResponse.model_validate(comment)


@router.get("/{app_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    app_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[CommentResponse]:
    include_internal = user.role in ("reviewer", "admin")
    comments = await service.list_comments(app_id, db, include_internal)
    return [CommentResponse.model_validate(c) for c in comments]
