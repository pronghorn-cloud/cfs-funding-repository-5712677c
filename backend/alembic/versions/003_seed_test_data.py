"""Seed test data - synthetic indicator values and pre-computed SVI scores.

Revision ID: 003_seed_test_data
Revises: 002_seed_svi_catalog
Create Date: 2026-02-05
"""

import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from scripts.generate_test_data import compute_svi_scores, generate_all_values

# revision identifiers
revision = "003_seed_test_data"
down_revision = "002_seed_svi_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Generate synthetic data
    values = generate_all_values()
    scores = compute_svi_scores(values)

    # Insert indicator values
    values_table = sa.table(
        "indicator_values",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("indicator_id", UUID(as_uuid=True)),
        sa.column("region_id", UUID(as_uuid=True)),
        sa.column("data_source_id", UUID(as_uuid=True)),
        sa.column("value", sa.Float),
        sa.column("year", sa.Integer),
        sa.column("metadata_json", JSONB),
    )

    # Batch insert for performance
    batch_size = 100
    for i in range(0, len(values), batch_size):
        batch = values[i : i + batch_size]
        op.bulk_insert(
            values_table,
            [
                {
                    "id": v["id"],
                    "indicator_id": v["indicator_id"],
                    "region_id": v["region_id"],
                    "data_source_id": v["data_source_id"],
                    "value": v["value"],
                    "year": v["year"],
                    "metadata_json": v["metadata_json"],
                }
                for v in batch
            ],
        )

    # Insert SVI scores
    scores_table = sa.table(
        "svi_scores",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("region_id", UUID(as_uuid=True)),
        sa.column("year", sa.Integer),
        sa.column("composite_score", sa.Float),
        sa.column("grade", sa.String),
        sa.column("category_scores", JSONB),
        sa.column("normalization_method", sa.String),
        sa.column("calculation_metadata", JSONB),
    )

    op.bulk_insert(
        scores_table,
        [
            {
                "id": s["id"],
                "region_id": s["region_id"],
                "year": s["year"],
                "composite_score": s["composite_score"],
                "grade": s["grade"],
                "category_scores": s["category_scores"],
                "normalization_method": s["normalization_method"],
                "calculation_metadata": s["calculation_metadata"],
            }
            for s in scores
        ],
    )


def downgrade() -> None:
    # Delete synthetic data by checking metadata
    op.execute(
        sa.text("DELETE FROM svi_scores WHERE calculation_metadata->>'synthetic' = 'true'")
    )
    op.execute(
        sa.text("DELETE FROM indicator_values WHERE metadata_json->>'synthetic' = 'true'")
    )
