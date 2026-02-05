"""Health check endpoints (Kubernetes-style probes)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.health.checks import check_blob_storage, check_database

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness() -> dict:
    """Liveness probe - is the process running?"""
    return {"status": "alive"}


@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)) -> dict:
    """Readiness probe - can we serve traffic?"""
    db_check = await check_database(db)
    blob_check = await check_blob_storage()

    checks = [db_check, blob_check]
    overall = "ready" if all(c["status"] == "healthy" for c in checks) else "not_ready"

    return {"status": overall, "checks": checks}


@router.get("/startup")
async def startup(db: AsyncSession = Depends(get_db)) -> dict:
    """Startup probe - has the app finished initializing?"""
    db_check = await check_database(db)
    return {"status": "started" if db_check["status"] == "healthy" else "starting"}
