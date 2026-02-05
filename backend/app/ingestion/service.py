"""Ingestion pipeline orchestration service."""

import uuid
from datetime import UTC, datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.metrics import ingestion_job_duration_seconds, ingestion_jobs_total
from app.ingestion.adapters.base import AbstractDataSourceAdapter
from app.ingestion.adapters.cfs_internal import CFSInternalAdapter
from app.ingestion.adapters.environics import EnvironicsAdapter
from app.ingestion.adapters.goa_health import GoAHealthAdapter
from app.ingestion.adapters.justice import JusticeAdapter
from app.ingestion.adapters.recovery_alberta import RecoveryAlbertaAdapter
from app.ingestion.adapters.scss import SCSSAdapter
from app.ingestion.adapters.statscan import StatsCanAdapter
from app.ingestion.models import IngestionJob
from app.ingestion.schemas import IngestionJobResponse
from app.vulnerability.models import DataSource, Indicator, IndicatorValue
from app.geography.models import Region
from app.exceptions import NotFoundException

logger = structlog.get_logger()

ADAPTER_REGISTRY: dict[str, type[AbstractDataSourceAdapter]] = {
    "statscan": StatsCanAdapter,
    "goa_health": GoAHealthAdapter,
    "environics": EnvironicsAdapter,
    "cfs_internal": CFSInternalAdapter,
    "scss": SCSSAdapter,
    "recovery_alberta": RecoveryAlbertaAdapter,
    "justice": JusticeAdapter,
}


async def trigger_ingestion(
    data_source_id: uuid.UUID,
    db: AsyncSession,
    triggered_by: uuid.UUID | None = None,
    year: int | None = None,
) -> IngestionJob:
    # Get data source config
    stmt = select(DataSource).where(DataSource.id == data_source_id)
    result = await db.execute(stmt)
    data_source = result.scalar_one_or_none()
    if data_source is None:
        raise NotFoundException("Data source not found")

    # Create job
    job = IngestionJob(
        data_source_id=data_source_id,
        source_name=data_source.name,
        status="running",
        started_at=datetime.now(UTC),
        triggered_by=triggered_by,
    )
    db.add(job)
    await db.flush()

    # Get adapter
    adapter_class = ADAPTER_REGISTRY.get(data_source.source_type)
    if adapter_class is None:
        job.status = "failed"
        job.error_message = f"No adapter for source type: {data_source.source_type}"
        return job

    adapter = adapter_class()

    try:
        records = await adapter.fetch_data(year)

        # Resolve indicator and region references
        indicators_cache: dict[str, uuid.UUID] = {}
        regions_cache: dict[str, uuid.UUID] = {}
        processed = 0
        failed = 0

        for record in records:
            try:
                # Resolve indicator
                if record.indicator_name not in indicators_cache:
                    ind_stmt = select(Indicator.id).where(
                        Indicator.name == record.indicator_name
                    )
                    ind_result = await db.execute(ind_stmt)
                    ind_id = ind_result.scalar_one_or_none()
                    if ind_id:
                        indicators_cache[record.indicator_name] = ind_id

                # Resolve region
                if record.region_code not in regions_cache:
                    reg_stmt = select(Region.id).where(Region.code == record.region_code)
                    reg_result = await db.execute(reg_stmt)
                    reg_id = reg_result.scalar_one_or_none()
                    if reg_id:
                        regions_cache[record.region_code] = reg_id

                ind_id = indicators_cache.get(record.indicator_name)
                reg_id = regions_cache.get(record.region_code)

                if ind_id and reg_id:
                    # Upsert indicator value
                    existing_stmt = select(IndicatorValue).where(
                        IndicatorValue.indicator_id == ind_id,
                        IndicatorValue.region_id == reg_id,
                        IndicatorValue.year == record.year,
                    )
                    existing = (await db.execute(existing_stmt)).scalar_one_or_none()

                    if existing:
                        existing.value = record.value
                        existing.data_source_id = data_source_id
                    else:
                        val = IndicatorValue(
                            indicator_id=ind_id,
                            region_id=reg_id,
                            data_source_id=data_source_id,
                            value=record.value,
                            year=record.year,
                            metadata_json=record.metadata,
                        )
                        db.add(val)
                    processed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

        job.status = "completed"
        job.completed_at = datetime.now(UTC)
        job.records_processed = processed
        job.records_failed = failed
        data_source.last_fetched_at = datetime.now(UTC)

        ingestion_jobs_total.labels(source=data_source.name, status="completed").inc()

    except Exception as exc:
        job.status = "failed"
        job.completed_at = datetime.now(UTC)
        job.error_message = str(exc)
        ingestion_jobs_total.labels(source=data_source.name, status="failed").inc()
        await logger.aerror("ingestion_failed", source=data_source.name, error=str(exc))

    return job


async def get_job_status(job_id: uuid.UUID, db: AsyncSession) -> IngestionJob:
    stmt = select(IngestionJob).where(IngestionJob.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if job is None:
        raise NotFoundException("Ingestion job not found")
    return job


async def list_jobs(
    db: AsyncSession,
    data_source_id: uuid.UUID | None = None,
    limit: int = 20,
) -> list[IngestionJob]:
    stmt = select(IngestionJob).order_by(IngestionJob.created_at.desc()).limit(limit)
    if data_source_id:
        stmt = stmt.where(IngestionJob.data_source_id == data_source_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())
