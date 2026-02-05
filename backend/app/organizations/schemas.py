"""Organization Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class OrganizationCreate(BaseModel):
    name: str
    legal_name: str | None = None
    organization_type: str
    registration_number: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province: str = "Alberta"
    postal_code: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    description: str | None = None
    region_id: uuid.UUID | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    organization_type: str | None = None
    registration_number: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    description: str | None = None
    region_id: uuid.UUID | None = None


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    legal_name: str | None = None
    organization_type: str
    registration_number: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province: str
    postal_code: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    description: str | None = None
    region_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
