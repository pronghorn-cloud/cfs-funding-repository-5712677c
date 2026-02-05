"""Geography service."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException
from app.geography.models import Municipality, Region
from app.geography.schemas import MunicipalityResponse, RegionGeoJSON, RegionResponse


async def list_regions(
    db: AsyncSession,
    region_type: str | None = None,
) -> list[RegionResponse]:
    stmt = select(Region).order_by(Region.name)
    if region_type:
        stmt = stmt.where(Region.region_type == region_type)
    result = await db.execute(stmt)
    regions = result.scalars().all()
    return [
        RegionResponse(
            **{k: v for k, v in r.__dict__.items() if not k.startswith("_")},
            municipality_count=len(r.municipalities),
        )
        for r in regions
    ]


async def get_region(region_id: uuid.UUID, db: AsyncSession) -> Region:
    stmt = select(Region).where(Region.id == region_id)
    result = await db.execute(stmt)
    region = result.scalar_one_or_none()
    if region is None:
        raise NotFoundException("Region not found")
    return region


async def get_region_geojson(region_id: uuid.UUID, db: AsyncSession) -> RegionGeoJSON:
    region = await get_region(region_id, db)
    return RegionGeoJSON.model_validate(region)


async def get_all_geojson(db: AsyncSession) -> dict:
    """Return a GeoJSON FeatureCollection of all regions."""
    stmt = select(Region).where(Region.geojson.isnot(None))
    result = await db.execute(stmt)
    features = []
    for region in result.scalars().all():
        if region.geojson:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": str(region.id),
                    "name": region.name,
                    "code": region.code,
                    "region_type": region.region_type,
                },
                "geometry": region.geojson,
            })
    return {"type": "FeatureCollection", "features": features}


async def list_municipalities(
    db: AsyncSession,
    region_id: uuid.UUID | None = None,
) -> list[MunicipalityResponse]:
    stmt = select(Municipality).order_by(Municipality.name)
    if region_id:
        stmt = stmt.where(Municipality.region_id == region_id)
    result = await db.execute(stmt)
    return [MunicipalityResponse.model_validate(m) for m in result.scalars().all()]
