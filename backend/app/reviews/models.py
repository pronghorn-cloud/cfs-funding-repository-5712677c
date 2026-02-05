"""Review database models."""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_model import TimestampMixin, UUIDPrimaryKeyMixin
from app.database import Base


class Review(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "reviews"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funding_applications.id"), nullable=False
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="in_progress", nullable=False)
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    scores: Mapped[list["ReviewScore"]] = relationship(
        back_populates="review", cascade="all, delete-orphan", lazy="selectin"
    )


class ReviewScore(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "review_scores"

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reviews.id"), nullable=False
    )
    criteria: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("1.0"), nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    review: Mapped[Review] = relationship(back_populates="scores")
