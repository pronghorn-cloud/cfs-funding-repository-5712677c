"""Review business logic."""

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, NotFoundException
from app.reviews.models import Review, ReviewScore
from app.reviews.schemas import ReviewCreate, ReviewScoreCreate, ReviewUpdate


async def create_review(
    data: ReviewCreate,
    db: AsyncSession,
    reviewer_id: uuid.UUID,
) -> Review:
    # Check if reviewer already has a review for this application
    stmt = select(Review).where(
        Review.application_id == data.application_id,
        Review.reviewer_id == reviewer_id,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise ConflictException("You already have a review for this application")

    review = Review(
        application_id=data.application_id,
        reviewer_id=reviewer_id,
        notes=data.notes,
        recommendation=data.recommendation,
    )
    db.add(review)
    await db.flush()

    for score_data in data.scores:
        score = ReviewScore(
            review_id=review.id,
            criteria=score_data.criteria,
            score=score_data.score,
            weight=score_data.weight,
            comments=score_data.comments,
        )
        db.add(score)

    if data.scores:
        review.overall_score = _calculate_weighted_score(data.scores)

    await db.flush()
    return review


async def get_review(review_id: uuid.UUID, db: AsyncSession) -> Review:
    stmt = select(Review).where(Review.id == review_id)
    result = await db.execute(stmt)
    review = result.scalar_one_or_none()
    if review is None:
        raise NotFoundException("Review not found")
    return review


async def update_review(
    review_id: uuid.UUID,
    data: ReviewUpdate,
    db: AsyncSession,
) -> Review:
    review = await get_review(review_id, db)
    if review.status == "completed":
        raise ConflictException("Cannot edit a completed review")

    if data.scores is not None:
        # Delete existing scores and replace
        stmt = select(ReviewScore).where(ReviewScore.review_id == review_id)
        result = await db.execute(stmt)
        for existing in result.scalars().all():
            await db.delete(existing)

        for score_data in data.scores:
            score = ReviewScore(
                review_id=review.id,
                criteria=score_data.criteria,
                score=score_data.score,
                weight=score_data.weight,
                comments=score_data.comments,
            )
            db.add(score)

        review.overall_score = _calculate_weighted_score(data.scores)

    if data.recommendation is not None:
        review.recommendation = data.recommendation
    if data.notes is not None:
        review.notes = data.notes

    await db.flush()
    return review


async def complete_review(review_id: uuid.UUID, db: AsyncSession) -> Review:
    review = await get_review(review_id, db)
    if review.status == "completed":
        raise ConflictException("Review is already completed")
    review.status = "completed"
    return review


async def list_reviews_for_application(
    application_id: uuid.UUID,
    db: AsyncSession,
) -> list[Review]:
    stmt = (
        select(Review)
        .where(Review.application_id == application_id)
        .order_by(Review.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_reviews_by_reviewer(
    reviewer_id: uuid.UUID,
    db: AsyncSession,
) -> list[Review]:
    stmt = (
        select(Review)
        .where(Review.reviewer_id == reviewer_id)
        .order_by(Review.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


def _calculate_weighted_score(scores: list[ReviewScoreCreate]) -> Decimal:
    total_weight = sum(s.weight for s in scores)
    if total_weight == 0:
        return Decimal("0")
    weighted_sum = sum(s.score * s.weight for s in scores)
    return (weighted_sum / total_weight).quantize(Decimal("0.01"))
