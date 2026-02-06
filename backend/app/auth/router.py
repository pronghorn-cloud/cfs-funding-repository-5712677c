"""Auth API routes."""

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service as auth_service
from app.auth.dependencies import CurrentUser
from app.auth.schemas import RefreshRequest, TokenResponse, UserProfile
from app.config import get_settings
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.get("/login")
async def login(request: Request) -> RedirectResponse:
    """Initiate Azure AD login flow."""
    if settings.debug:
        return RedirectResponse(url="/api/v1/auth/dev-login")
    auth_url = auth_service.get_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/dev-login")
async def dev_login(
    role: str = Query("admin"),
) -> TokenResponse:
    """Dev-only: issue JWTs for a mock user without Azure AD. Only available when DEBUG=true."""
    if not settings.debug:
        from app.exceptions import ForbiddenException
        raise ForbiddenException("Dev login is only available in debug mode")
    return auth_service.create_dev_token(role=role)


@router.get("/callback")
async def callback(
    code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Handle Azure AD callback and issue JWTs."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await auth_service.handle_callback(code, db, ip_address, user_agent)


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token using refresh token."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await auth_service.refresh_tokens(body.refresh_token, db, ip_address, user_agent)


@router.post("/logout")
async def logout(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Revoke refresh token."""
    await auth_service.logout(body.refresh_token, db)
    return {"status": "logged_out"}


@router.get("/me")
async def me(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """Get current user profile."""
    try:
        db_user = await auth_service.get_user_by_id(user.sub, db)
        return UserProfile.model_validate(db_user)
    except Exception:
        if settings.debug:
            return UserProfile(
                id=user.sub,
                email=user.email,
                display_name=user.display_name,
                role=user.role,
                organization_id=user.organization_id,
                is_active=True,
            )
        raise
