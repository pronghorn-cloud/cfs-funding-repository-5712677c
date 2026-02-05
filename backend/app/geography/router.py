"""Geography API routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.database import get_db
from app.geography import service
from app.geography.schemas import MunicipalityResponse, RegionGeoJSON, RegionResponse

router = APIRouter(prefix="/geography", tags=["geography"])


@router.get("/regions", response_model=list[RegionResponse])
async def list_regions(
    user: CurrentUser,
    region_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[RegionResponse]:
    return await service.list_regions(db, region_type)


@router.get("/regions/{region_id}", response_model=RegionResponse)
async def get_region(
    region_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> RegionResponse:
    region = await service.get_region(region_id, db)
    return RegionResponse.model_validate(region)


@router.get("/regions/{region_id}/geojson", response_model=RegionGeoJSON)
async def get_region_geojson(
    region_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> RegionGeoJSON:
    return await service.get_region_geojson(region_id, db)


@router.get("/geojson")
async def get_all_geojson(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await service.get_all_geojson(db)


@router.get("/municipalities", response_model=list[MunicipalityResponse])
async def list_municipalities(
    user: CurrentUser,
    region_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[MunicipalityResponse]:
    return await service.list_municipalities(db, region_id)
