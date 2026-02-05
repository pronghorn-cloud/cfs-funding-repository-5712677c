"""Document Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    file_name: str
    file_type: str
    file_size: int
    content_type: str
    category: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    file_name: str
    file_size: int
    message: str = "File uploaded successfully"
