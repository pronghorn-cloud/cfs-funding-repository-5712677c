"""Geography database models."""

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_model import TimestampMixin, UUIDPrimaryKeyMixin
from app.database import Base


class Region(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "regions"

    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    region_type: Mapped[str] = mapped_column(String(50), nullable=False)  # health_zone, census_division, etc.
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("regions.id"), nullable=True
    )
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area_sq_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    geojson: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    municipalities: Mapped[list["Municipality"]] = relationship(
        back_populates="region", lazy="selectin"
    )


class Municipality(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "municipalities"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    municipality_type: Mapped[str] = mapped_column(String(50), nullable=False)  # city, town, village, etc.
    region_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False
    )
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    geojson: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    region: Mapped[Region] = relationship(back_populates="municipalities")
