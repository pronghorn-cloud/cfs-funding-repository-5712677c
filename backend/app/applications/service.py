"""Funding application business logic and workflow."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.applications.enums import ApplicationStatus
from app.applications.models import (
    ApplicationComment,
    ApplicationSection,
    ApplicationStatusHistory,
    FundingApplication,
)
from app.applications.schemas import (
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationUpdate,
    CommentCreate,
    DecisionCreate,
    SectionSave,
    StatusTransition,
)
from app.common.pagination import PaginatedResponse, PaginationParams
from app.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException


async def create_application(
    data: ApplicationCreate,
    db: AsyncSession,
    created_by: uuid.UUID,
) -> FundingApplication:
    app = FundingApplication(
        **data.model_dump(),
        status=ApplicationStatus.DRAFT,
        created_by=created_by,
    )
    db.add(app)
    await db.flush()

    # Create initial status history
    history = ApplicationStatusHistory(
        application_id=app.id,
        to_status=ApplicationStatus.DRAFT,
        changed_by=created_by,
        notes="Application created",
    )
    db.add(history)
    return app


async def get_application(app_id: uuid.UUID, db: AsyncSession) -> FundingApplication:
    stmt = (
        select(FundingApplication)
        .where(FundingApplication.id == app_id, FundingApplication.is_deleted.is_(False))
        .options(selectinload(FundingApplication.sections))
    )
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()
    if application is None:
        raise NotFoundException("Application not found")
    return application


async def list_applications(
    db: AsyncSession,
    pagination: PaginationParams,
    organization_id: uuid.UUID | None = None,
    status: str | None = None,
) -> PaginatedResponse[ApplicationListResponse]:
    base_query = select(FundingApplication).where(FundingApplication.is_deleted.is_(False))

    if organization_id:
        base_query = base_query.where(FundingApplication.organization_id == organization_id)
    if status:
        base_query = base_query.where(FundingApplication.status == status)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    stmt = (
        base_query
        .offset(pagination.offset)
        .limit(pagination.page_size)
        .order_by(FundingApplication.created_at.desc())
    )
    result = await db.execute(stmt)
    items = [ApplicationListResponse.model_validate(a) for a in result.scalars().all()]

    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


async def update_application(
    app_id: uuid.UUID,
    data: ApplicationUpdate,
    db: AsyncSession,
    updated_by: uuid.UUID,
) -> FundingApplication:
    application = await get_application(app_id, db)
    if application.status != ApplicationStatus.DRAFT:
        raise ConflictException("Can only edit applications in draft status")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    application.updated_by = updated_by
    return application


async def save_section(
    app_id: uuid.UUID,
    data: SectionSave,
    db: AsyncSession,
) -> ApplicationSection:
    application = await get_application(app_id, db)
    if application.status not in (ApplicationStatus.DRAFT, ApplicationStatus.ADDITIONAL_INFO_REQUESTED):
        raise ConflictException("Cannot edit sections in current status")

    # Upsert section
    stmt = select(ApplicationSection).where(
        ApplicationSection.application_id == app_id,
        ApplicationSection.section_type == data.section_type,
    )
    result = await db.execute(stmt)
    section = result.scalar_one_or_none()

    if section is None:
        section = ApplicationSection(
            application_id=app_id,
            section_type=data.section_type,
            data=data.data,
            is_complete=data.is_complete,
        )
        db.add(section)
    else:
        section.data = data.data
        section.is_complete = data.is_complete

    await db.flush()
    return section


async def transition_status(
    app_id: uuid.UUID,
    transition: StatusTransition,
    db: AsyncSession,
    changed_by: uuid.UUID,
) -> FundingApplication:
    application = await get_application(app_id, db)
    current_status = ApplicationStatus(application.status)
    new_status = ApplicationStatus(transition.new_status)

    valid_transitions = ApplicationStatus.valid_transitions()
    if new_status not in valid_transitions.get(current_status, []):
        raise ValidationException(
            f"Cannot transition from '{current_status}' to '{new_status}'"
        )

    old_status = application.status
    application.status = new_status

    if new_status == ApplicationStatus.SUBMITTED:
        application.submitted_at = datetime.now(UTC)

    history = ApplicationStatusHistory(
        application_id=app_id,
        from_status=old_status,
        to_status=new_status,
        changed_by=changed_by,
        notes=transition.notes,
    )
    db.add(history)
    return application


async def make_decision(
    app_id: uuid.UUID,
    decision: DecisionCreate,
    db: AsyncSession,
    decided_by: uuid.UUID,
) -> FundingApplication:
    application = await get_application(app_id, db)
    if application.status not in (ApplicationStatus.REVIEWED, ApplicationStatus.RECOMMENDED):
        raise ConflictException("Application is not ready for a decision")

    new_status = ApplicationStatus(decision.status)
    if new_status not in (ApplicationStatus.APPROVED, ApplicationStatus.DENIED):
        raise ValidationException("Decision must be 'approved' or 'denied'")

    old_status = application.status
    application.status = new_status
    application.decision_at = datetime.now(UTC)
    application.decision_by = decided_by
    application.decision_notes = decision.notes
    if decision.amount_approved is not None:
        application.amount_approved = decision.amount_approved

    history = ApplicationStatusHistory(
        application_id=app_id,
        from_status=old_status,
        to_status=new_status,
        changed_by=decided_by,
        notes=decision.notes,
    )
    db.add(history)
    return application


async def add_comment(
    app_id: uuid.UUID,
    data: CommentCreate,
    db: AsyncSession,
    user_id: uuid.UUID,
) -> ApplicationComment:
    await get_application(app_id, db)  # Verify exists
    comment = ApplicationComment(
        application_id=app_id,
        user_id=user_id,
        content=data.content,
        is_internal=data.is_internal,
    )
    db.add(comment)
    await db.flush()
    return comment


async def list_comments(
    app_id: uuid.UUID,
    db: AsyncSession,
    include_internal: bool = False,
) -> list[ApplicationComment]:
    stmt = select(ApplicationComment).where(ApplicationComment.application_id == app_id)
    if not include_internal:
        stmt = stmt.where(ApplicationComment.is_internal.is_(False))
    stmt = stmt.order_by(ApplicationComment.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())
