"""Funding application database models."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_model import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.database import Base


class FundingApplication(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "funding_applications"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    funding_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    amount_requested: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    amount_approved: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    fiscal_year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    decision_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    organization: Mapped["app.organizations.models.Organization"] = relationship(
        back_populates="applications"
    )
    sections: Mapped[list["ApplicationSection"]] = relationship(
        back_populates="application", cascade="all, delete-orphan", lazy="selectin"
    )
    status_history: Mapped[list["ApplicationStatusHistory"]] = relationship(
        back_populates="application", cascade="all, delete-orphan", lazy="selectin"
    )
    comments: Mapped[list["ApplicationComment"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    documents: Mapped[list["app.documents.models.Document"]] = relationship(
        back_populates="application", lazy="selectin"
    )


class ApplicationSection(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "application_sections"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funding_applications.id"), nullable=False
    )
    section_type: Mapped[str] = mapped_column(String(100), nullable=False)
    section_order: Mapped[int] = mapped_column(nullable=False, default=0)
    data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    is_complete: Mapped[bool] = mapped_column(default=False, nullable=False)

    application: Mapped[FundingApplication] = relationship(back_populates="sections")


class ApplicationStatusHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "application_status_history"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funding_applications.id"), nullable=False
    )
    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    application: Mapped[FundingApplication] = relationship(back_populates="status_history")


class ApplicationComment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "application_comments"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funding_applications.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(default=False, nullable=False)

    application: Mapped[FundingApplication] = relationship(back_populates="comments")
