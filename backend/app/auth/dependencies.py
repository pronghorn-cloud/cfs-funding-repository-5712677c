"""Auth dependencies for FastAPI route injection."""

import uuid
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import UserClaims
from app.auth.service import validate_access_token
from app.database import get_db
from app.exceptions import ForbiddenException


async def get_current_user(
    authorization: Annotated[str, Header()],
) -> UserClaims:
    if not authorization.startswith("Bearer "):
        raise ForbiddenException("Invalid authorization header")
    token = authorization.removeprefix("Bearer ")
    return validate_access_token(token)


def require_role(*roles: str):
    """Dependency factory that checks user role."""

    async def _check_role(
        user: Annotated[UserClaims, Depends(get_current_user)],
    ) -> UserClaims:
        if user.role not in roles:
            raise ForbiddenException(f"Role '{user.role}' does not have access")
        return user

    return _check_role


CurrentUser = Annotated[UserClaims, Depends(get_current_user)]
AdminUser = Annotated[UserClaims, Depends(require_role("admin"))]
ReviewerUser = Annotated[UserClaims, Depends(require_role("reviewer", "admin"))]
