"""Initial schema - all tables.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-02-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- regions (must come first, referenced by many tables) ---
    op.create_table(
        "regions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), unique=True, nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("region_type", sa.String(50), nullable=False),
        sa.Column("parent_id", UUID(as_uuid=True), sa.ForeignKey("regions.id"), nullable=True),
        sa.Column("population", sa.Integer, nullable=True),
        sa.Column("area_sq_km", sa.Float, nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("geojson", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- municipalities ---
    op.create_table(
        "municipalities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(50), nullable=True),
        sa.Column("municipality_type", sa.String(50), nullable=False),
        sa.Column("region_id", UUID(as_uuid=True), sa.ForeignKey("regions.id"), nullable=False),
        sa.Column("population", sa.Integer, nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("geojson", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- organizations ---
    op.create_table(
        "organizations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("legal_name", sa.String(255), nullable=True),
        sa.Column("organization_type", sa.String(100), nullable=False),
        sa.Column("registration_number", sa.String(100), nullable=True),
        sa.Column("address_line_1", sa.String(255), nullable=True),
        sa.Column("address_line_2", sa.String(255), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("province", sa.String(50), server_default="Alberta", nullable=False),
        sa.Column("postal_code", sa.String(10), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("region_id", UUID(as_uuid=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("azure_oid", sa.String(255), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), server_default="applicant", nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- user_sessions ---
    op.create_table(
        "user_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("refresh_token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_revoked", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- funding_applications ---
    op.create_table(
        "funding_applications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("funding_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), server_default="draft", nullable=False),
        sa.Column("amount_requested", sa.Numeric(12, 2), nullable=True),
        sa.Column("amount_approved", sa.Numeric(12, 2), nullable=True),
        sa.Column("fiscal_year", sa.String(20), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_by", UUID(as_uuid=True), nullable=True),
        sa.Column("decision_notes", sa.Text, nullable=True),
        sa.Column("is_deleted", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- application_sections ---
    op.create_table(
        "application_sections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("application_id", UUID(as_uuid=True), sa.ForeignKey("funding_applications.id"), nullable=False),
        sa.Column("section_type", sa.String(100), nullable=False),
        sa.Column("section_order", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("data", JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("is_complete", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- application_status_history ---
    op.create_table(
        "application_status_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("application_id", UUID(as_uuid=True), sa.ForeignKey("funding_applications.id"), nullable=False),
        sa.Column("from_status", sa.String(50), nullable=True),
        sa.Column("to_status", sa.String(50), nullable=False),
        sa.Column("changed_by", UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- application_comments ---
    op.create_table(
        "application_comments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("application_id", UUID(as_uuid=True), sa.ForeignKey("funding_applications.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("is_internal", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- documents ---
    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("application_id", UUID(as_uuid=True), sa.ForeignKey("funding_applications.id"), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.BigInteger, nullable=False),
        sa.Column("blob_path", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("is_deleted", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- reviews ---
    op.create_table(
        "reviews",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("application_id", UUID(as_uuid=True), sa.ForeignKey("funding_applications.id"), nullable=False),
        sa.Column("reviewer_id", UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(50), server_default="in_progress", nullable=False),
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("recommendation", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- review_scores ---
    op.create_table(
        "review_scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("review_id", UUID(as_uuid=True), sa.ForeignKey("reviews.id"), nullable=False),
        sa.Column("criteria", sa.String(100), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=False),
        sa.Column("weight", sa.Numeric(5, 4), server_default=sa.text("1.0"), nullable=False),
        sa.Column("comments", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- indicator_categories ---
    op.create_table(
        "indicator_categories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("weight", sa.Numeric(5, 4), server_default=sa.text("0.1667"), nullable=False),
        sa.Column("sort_order", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- indicators ---
    op.create_table(
        "indicators",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("category_id", UUID(as_uuid=True), sa.ForeignKey("indicator_categories.id"), nullable=False),
        sa.Column("name", sa.String(200), unique=True, nullable=False),
        sa.Column("display_name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("data_source", sa.String(200), nullable=True),
        sa.Column("weight", sa.Numeric(5, 4), server_default=sa.text("1.0"), nullable=False),
        sa.Column("is_inverse", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("sort_order", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- data_sources ---
    op.create_table(
        "data_sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), unique=True, nullable=False),
        sa.Column("source_type", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("config", JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- indicator_values ---
    op.create_table(
        "indicator_values",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("indicator_id", UUID(as_uuid=True), sa.ForeignKey("indicators.id"), nullable=False),
        sa.Column("region_id", UUID(as_uuid=True), sa.ForeignKey("regions.id"), nullable=False),
        sa.Column("data_source_id", UUID(as_uuid=True), sa.ForeignKey("data_sources.id"), nullable=True),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("normalized_value", sa.Float, nullable=True),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_indicator_values_indicator_year",
        "indicator_values",
        ["indicator_id", "year"],
    )
    op.create_index(
        "ix_indicator_values_region_year",
        "indicator_values",
        ["region_id", "year"],
    )

    # --- svi_scores ---
    op.create_table(
        "svi_scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("region_id", UUID(as_uuid=True), sa.ForeignKey("regions.id"), nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("composite_score", sa.Float, nullable=False),
        sa.Column("grade", sa.String(2), nullable=False),
        sa.Column("category_scores", JSONB, nullable=False),
        sa.Column("risk_index", sa.Float, nullable=True),
        sa.Column("normalization_method", sa.String(50), server_default="min_max", nullable=False),
        sa.Column("calculation_metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_svi_scores_region_year",
        "svi_scores",
        ["region_id", "year"],
        unique=True,
    )

    # --- ingestion_jobs ---
    op.create_table(
        "ingestion_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("data_source_id", UUID(as_uuid=True), nullable=False),
        sa.Column("source_name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_processed", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("records_failed", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("triggered_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- audit_log ---
    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("details", JSONB, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("ingestion_jobs")
    op.drop_index("ix_svi_scores_region_year", table_name="svi_scores")
    op.drop_table("svi_scores")
    op.drop_index("ix_indicator_values_region_year", table_name="indicator_values")
    op.drop_index("ix_indicator_values_indicator_year", table_name="indicator_values")
    op.drop_table("indicator_values")
    op.drop_table("data_sources")
    op.drop_table("indicators")
    op.drop_table("indicator_categories")
    op.drop_table("review_scores")
    op.drop_table("reviews")
    op.drop_table("documents")
    op.drop_table("application_comments")
    op.drop_table("application_status_history")
    op.drop_table("application_sections")
    op.drop_table("funding_applications")
    op.drop_table("user_sessions")
    op.drop_table("users")
    op.drop_table("organizations")
    op.drop_table("municipalities")
    op.drop_table("regions")
