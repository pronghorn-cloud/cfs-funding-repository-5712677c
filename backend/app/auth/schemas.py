"""Auth Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class UserClaims(BaseModel):
    sub: uuid.UUID
    email: str
    display_name: str
    role: str
    organization_id: uuid.UUID | None = None


class UserProfile(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    first_name: str | None = None
    last_name: str | None = None
    role: str
    organization_id: uuid.UUID | None = None
    is_active: bool
    last_login: datetime | None = None

    model_config = {"from_attributes": True}
