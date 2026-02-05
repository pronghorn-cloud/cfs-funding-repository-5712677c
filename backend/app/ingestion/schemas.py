"""Ingestion Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class IngestionTrigger(BaseModel):
    data_source_id: uuid.UUID
    year: int | None = None


class IngestionJobResponse(BaseModel):
    id: uuid.UUID
    data_source_id: uuid.UUID
    source_name: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    records_processed: int = 0
    records_failed: int = 0
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
