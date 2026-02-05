"""Organization business logic."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginatedResponse, PaginationParams
from app.exceptions import NotFoundException
from app.organizations.models import Organization
from app.organizations.schemas import OrganizationCreate, OrganizationResponse, OrganizationUpdate


async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession,
    created_by: uuid.UUID | None = None,
) -> Organization:
    org = Organization(**data.model_dump(), created_by=created_by)
    db.add(org)
    await db.flush()
    return org


async def get_organization(org_id: uuid.UUID, db: AsyncSession) -> Organization:
    stmt = select(Organization).where(
        Organization.id == org_id,
        Organization.is_deleted.is_(False),
    )
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    if org is None:
        raise NotFoundException("Organization not found")
    return org


async def list_organizations(
    db: AsyncSession,
    pagination: PaginationParams,
    search: str | None = None,
) -> PaginatedResponse[OrganizationResponse]:
    base_query = select(Organization).where(Organization.is_deleted.is_(False))

    if search:
        base_query = base_query.where(Organization.name.ilike(f"%{search}%"))

    # Count
    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Paginate
    stmt = base_query.offset(pagination.offset).limit(pagination.page_size).order_by(Organization.name)
    result = await db.execute(stmt)
    items = [OrganizationResponse.model_validate(org) for org in result.scalars().all()]

    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


async def update_organization(
    org_id: uuid.UUID,
    data: OrganizationUpdate,
    db: AsyncSession,
    updated_by: uuid.UUID | None = None,
) -> Organization:
    org = await get_organization(org_id, db)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    if updated_by:
        org.updated_by = updated_by
    return org


async def delete_organization(org_id: uuid.UUID, db: AsyncSession) -> None:
    org = await get_organization(org_id, db)
    org.is_deleted = True
