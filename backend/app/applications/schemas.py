"""Application Pydantic schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    organization_id: uuid.UUID
    title: str
    funding_type: str
    amount_requested: Decimal | None = None
    fiscal_year: str | None = None
    description: str | None = None


class ApplicationUpdate(BaseModel):
    title: str | None = None
    funding_type: str | None = None
    amount_requested: Decimal | None = None
    fiscal_year: str | None = None
    description: str | None = None


class SectionSave(BaseModel):
    section_type: str
    data: dict
    is_complete: bool = False


class StatusTransition(BaseModel):
    new_status: str
    notes: str | None = None


class DecisionCreate(BaseModel):
    status: str  # approved or denied
    amount_approved: Decimal | None = None
    notes: str | None = None


class CommentCreate(BaseModel):
    content: str
    is_internal: bool = False


class SectionResponse(BaseModel):
    id: uuid.UUID
    section_type: str
    section_order: int
    data: dict
    is_complete: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class StatusHistoryResponse(BaseModel):
    id: uuid.UUID
    from_status: str | None
    to_status: str
    changed_by: uuid.UUID | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    content: str
    is_internal: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    funding_type: str
    status: str
    amount_requested: Decimal | None = None
    amount_approved: Decimal | None = None
    fiscal_year: str | None = None
    description: str | None = None
    submitted_at: datetime | None = None
    decision_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    sections: list[SectionResponse] = []

    model_config = {"from_attributes": True}


class ApplicationListResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    funding_type: str
    status: str
    amount_requested: Decimal | None = None
    fiscal_year: str | None = None
    submitted_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
