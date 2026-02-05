"""Geography Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class RegionResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    region_type: str
    parent_id: uuid.UUID | None = None
    population: int | None = None
    area_sq_km: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    municipality_count: int = 0

    model_config = {"from_attributes": True}


class RegionGeoJSON(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    geojson: dict | None = None

    model_config = {"from_attributes": True}


class MunicipalityResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str | None = None
    municipality_type: str
    region_id: uuid.UUID
    population: int | None = None
    latitude: float | None = None
    longitude: float | None = None

    model_config = {"from_attributes": True}
