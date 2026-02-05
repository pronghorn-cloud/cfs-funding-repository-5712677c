"""Authentication service: MSAL integration and JWT management."""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import msal
import structlog
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User, UserSession
from app.auth.schemas import TokenResponse, UserClaims
from app.config import get_settings
from app.exceptions import ForbiddenException, NotFoundException

logger = structlog.get_logger()
settings = get_settings()


def get_msal_app() -> msal.ConfidentialClientApplication:
    return msal.ConfidentialClientApplication(
        client_id=settings.azure_client_id,
        client_credential=settings.azure_client_secret,
        authority=settings.azure_authority_url,
    )


def get_auth_url(state: str | None = None) -> str:
    app = get_msal_app()
    flow = app.initiate_auth_code_flow(
        scopes=["User.Read"],
        redirect_uri=settings.azure_redirect_uri,
        state=state,
    )
    return flow.get("auth_uri", "")


async def handle_callback(
    code: str,
    db: AsyncSession,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> TokenResponse:
    app = get_msal_app()
    result = app.acquire_token_by_authorization_code(
        code,
        scopes=["User.Read"],
        redirect_uri=settings.azure_redirect_uri,
    )

    if "error" in result:
        raise ForbiddenException(f"Authentication failed: {result.get('error_description', '')}")

    id_token_claims = result.get("id_token_claims", {})
    azure_oid = id_token_claims.get("oid", "")
    email = id_token_claims.get("preferred_username", "")
    display_name = id_token_claims.get("name", email)

    # Upsert user
    stmt = select(User).where(User.azure_oid == azure_oid)
    result_db = await db.execute(stmt)
    user = result_db.scalar_one_or_none()

    if user is None:
        user = User(
            azure_oid=azure_oid,
            email=email,
            display_name=display_name,
            first_name=id_token_claims.get("given_name"),
            last_name=id_token_claims.get("family_name"),
        )
        db.add(user)
        await db.flush()
    else:
        user.last_login = datetime.now(UTC)

    # Generate tokens
    return await _create_tokens(user, db, ip_address, user_agent)


async def refresh_tokens(
    refresh_token: str,
    db: AsyncSession,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> TokenResponse:
    token_hash = _hash_token(refresh_token)
    stmt = (
        select(UserSession)
        .where(UserSession.refresh_token_hash == token_hash)
        .where(UserSession.is_revoked.is_(False))
        .where(UserSession.expires_at > datetime.now(UTC))
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if session is None:
        raise ForbiddenException("Invalid or expired refresh token")

    # Revoke old session
    session.is_revoked = True

    # Get user
    stmt = select(User).where(User.id == session.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise ForbiddenException("User account is disabled")

    return await _create_tokens(user, db, ip_address, user_agent)


async def logout(refresh_token: str, db: AsyncSession) -> None:
    token_hash = _hash_token(refresh_token)
    stmt = select(UserSession).where(UserSession.refresh_token_hash == token_hash)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if session:
        session.is_revoked = True


def validate_access_token(token: str) -> UserClaims:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return UserClaims(**payload)
    except JWTError as exc:
        raise ForbiddenException("Invalid access token") from exc


async def get_user_by_id(user_id: uuid.UUID, db: AsyncSession) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("User not found")
    return user


async def _create_tokens(
    user: User,
    db: AsyncSession,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> TokenResponse:
    now = datetime.now(UTC)
    access_expires = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    refresh_expires = now + timedelta(minutes=settings.jwt_refresh_token_expire_minutes)

    access_payload = {
        "sub": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "organization_id": str(user.organization_id) if user.organization_id else None,
        "exp": access_expires,
        "iat": now,
    }

    access_token = jwt.encode(access_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    refresh_token = str(uuid.uuid4())

    # Store session
    session = UserSession(
        user_id=user.id,
        refresh_token_hash=_hash_token(refresh_token),
        expires_at=refresh_expires,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(session)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
