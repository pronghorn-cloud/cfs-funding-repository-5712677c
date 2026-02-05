"""Abstract base class for data source adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IngestionRecord:
    indicator_name: str
    region_code: str
    value: float
    year: int
    metadata: dict | None = None


class AbstractDataSourceAdapter(ABC):
    """Base class for all data source adapters."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        ...

    @abstractmethod
    async def fetch_data(self, year: int | None = None) -> list[IngestionRecord]:
        """Fetch data from the source and return normalized records."""
        ...

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Check if the data source is accessible."""
        ...
