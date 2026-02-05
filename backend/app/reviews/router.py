"""Review API routes."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, ReviewerUser
from app.database import get_db
from app.reviews import service
from app.reviews.schemas import ReviewCreate, ReviewResponse, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    data: ReviewCreate,
    user: ReviewerUser,
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    review = await service.create_review(data, db, reviewer_id=user.sub)
    return ReviewResponse.model_validate(review)


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: uuid.UUID,
    user: ReviewerUser,
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    review = await service.get_review(review_id, db)
    return ReviewResponse.model_validate(review)


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: uuid.UUID,
    data: ReviewUpdate,
    user: ReviewerUser,
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    review = await service.update_review(review_id, data, db)
    return ReviewResponse.model_validate(review)


@router.post("/{review_id}/complete", response_model=ReviewResponse)
async def complete_review(
    review_id: uuid.UUID,
    user: ReviewerUser,
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    review = await service.complete_review(review_id, db)
    return ReviewResponse.model_validate(review)


@router.get("/application/{application_id}", response_model=list[ReviewResponse])
async def list_reviews_for_application(
    application_id: uuid.UUID,
    user: ReviewerUser,
    db: AsyncSession = Depends(get_db),
) -> list[ReviewResponse]:
    reviews = await service.list_reviews_for_application(application_id, db)
    return [ReviewResponse.model_validate(r) for r in reviews]


@router.get("/reviewer/me", response_model=list[ReviewResponse])
async def list_my_reviews(
    user: ReviewerUser,
    db: AsyncSession = Depends(get_db),
) -> list[ReviewResponse]:
    reviews = await service.list_reviews_by_reviewer(user.sub, db)
    return [ReviewResponse.model_validate(r) for r in reviews]
