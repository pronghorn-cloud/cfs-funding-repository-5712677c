"""Review Pydantic schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ReviewScoreCreate(BaseModel):
    criteria: str
    score: Decimal
    weight: Decimal = Decimal("1.0")
    comments: str | None = None


class ReviewCreate(BaseModel):
    application_id: uuid.UUID
    scores: list[ReviewScoreCreate] = []
    recommendation: str | None = None
    notes: str | None = None


class ReviewUpdate(BaseModel):
    scores: list[ReviewScoreCreate] | None = None
    recommendation: str | None = None
    notes: str | None = None


class ReviewComplete(BaseModel):
    recommendation: str
    notes: str | None = None


class ReviewScoreResponse(BaseModel):
    id: uuid.UUID
    criteria: str
    score: Decimal
    weight: Decimal
    comments: str | None = None

    model_config = {"from_attributes": True}


class ReviewResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    reviewer_id: uuid.UUID
    status: str
    overall_score: Decimal | None = None
    recommendation: str | None = None
    notes: str | None = None
    scores: list[ReviewScoreResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationComparisonItem(BaseModel):
    application_id: uuid.UUID
    application_title: str
    organization_name: str
    amount_requested: Decimal | None = None
    average_score: Decimal | None = None
    review_count: int = 0
    recommendation_summary: dict[str, int] = {}
