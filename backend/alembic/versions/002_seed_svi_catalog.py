"""Seed SVI catalog - regions, categories, indicators, data sources.

Revision ID: 002_seed_svi_catalog
Revises: 001_initial_schema
Create Date: 2026-02-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from app.vulnerability.catalog import (
    ALL_REGIONS,
    CATEGORIES,
    DATA_SOURCES,
    INDICATORS,
)

# revision identifiers
revision = "002_seed_svi_catalog"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Insert Health Zones first (parent_id=NULL), then Census Divisions
    regions_table = sa.table(
        "regions",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("code", sa.String),
        sa.column("region_type", sa.String),
        sa.column("parent_id", UUID(as_uuid=True)),
        sa.column("population", sa.Integer),
        sa.column("area_sq_km", sa.Float),
        sa.column("latitude", sa.Float),
        sa.column("longitude", sa.Float),
    )

    for region in ALL_REGIONS:
        op.execute(
            regions_table.insert().values(
                id=region["id"],
                name=region["name"],
                code=region["code"],
                region_type=region["region_type"],
                parent_id=region.get("parent_id"),
                population=region.get("population"),
                area_sq_km=region.get("area_sq_km"),
                latitude=region.get("latitude"),
                longitude=region.get("longitude"),
            )
        )

    # Insert indicator categories
    categories_table = sa.table(
        "indicator_categories",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("display_name", sa.String),
        sa.column("description", sa.String),
        sa.column("weight", sa.Numeric),
        sa.column("sort_order", sa.Integer),
    )

    for cat in CATEGORIES:
        op.execute(
            categories_table.insert().values(
                id=cat["id"],
                name=cat["name"],
                display_name=cat["display_name"],
                description=cat["description"],
                weight=cat["weight"],
                sort_order=cat["sort_order"],
            )
        )

    # Insert data sources
    sources_table = sa.table(
        "data_sources",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("source_type", sa.String),
        sa.column("description", sa.String),
        sa.column("url", sa.String),
    )

    for src in DATA_SOURCES:
        op.execute(
            sources_table.insert().values(
                id=src["id"],
                name=src["name"],
                source_type=src["source_type"],
                description=src["description"],
                url=src.get("url"),
            )
        )

    # Insert indicators
    indicators_table = sa.table(
        "indicators",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("category_id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("display_name", sa.String),
        sa.column("description", sa.String),
        sa.column("unit", sa.String),
        sa.column("data_source", sa.String),
        sa.column("is_inverse", sa.Boolean),
        sa.column("sort_order", sa.Integer),
    )

    # Build a lookup from data source id -> name for the indicator's data_source text field
    source_id_to_name = {s["id"]: s["name"] for s in DATA_SOURCES}

    for ind in INDICATORS:
        # The indicator model stores source as a string name, but catalog has the source ID.
        # Resolve back to source name for the text field.
        source_name = source_id_to_name.get(ind["data_source"], ind["data_source"])

        op.execute(
            indicators_table.insert().values(
                id=ind["id"],
                category_id=ind["category_id"],
                name=ind["name"],
                display_name=ind["display_name"],
                description=ind["description"],
                unit=ind.get("unit"),
                data_source=source_name,
                is_inverse=ind.get("is_inverse", False),
                sort_order=ind.get("sort_order", 0),
            )
        )


def downgrade() -> None:
    # Delete in reverse order to respect FK constraints
    op.execute(sa.text("DELETE FROM indicators"))
    op.execute(sa.text("DELETE FROM data_sources"))
    op.execute(sa.text("DELETE FROM indicator_categories"))
    op.execute(sa.text("DELETE FROM regions WHERE region_type = 'census_division'"))
    op.execute(sa.text("DELETE FROM regions WHERE region_type = 'health_zone'"))
