"""Organization API routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AdminUser, CurrentUser
from app.common.pagination import PaginatedResponse, PaginationParams
from app.database import get_db
from app.organizations import service
from app.organizations.schemas import OrganizationCreate, OrganizationResponse, OrganizationUpdate

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    data: OrganizationCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    org = await service.create_organization(data, db, created_by=user.sub)
    return OrganizationResponse.model_validate(org)


@router.get("", response_model=PaginatedResponse[OrganizationResponse])
async def list_organizations(
    user: CurrentUser,
    pagination: PaginationParams = Depends(),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[OrganizationResponse]:
    return await service.list_organizations(db, pagination, search)


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    org = await service.get_organization(org_id, db)
    return OrganizationResponse.model_validate(org)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: uuid.UUID,
    data: OrganizationUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    org = await service.update_organization(org_id, data, db, updated_by=user.sub)
    return OrganizationResponse.model_validate(org)


@router.delete("/{org_id}", status_code=204)
async def delete_organization(
    org_id: uuid.UUID,
    user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    await service.delete_organization(org_id, db)
