"""Application configuration via Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "CFS Funding Portal"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    allowed_origins: list[str] = ["http://localhost:5173"]

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cfs_portal"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_echo: bool = False

    # Azure AD / MSAL
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    azure_redirect_uri: str = "http://localhost:8000/api/v1/auth/callback"
    azure_authority: str = ""

    @property
    def azure_authority_url(self) -> str:
        if self.azure_authority:
            return self.azure_authority
        return f"https://login.microsoftonline.com/{self.azure_tenant_id}"

    # JWT
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_minutes: int = 1440  # 24 hours

    # Azure Blob Storage
    azure_storage_connection_string: str = (
        "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;"
        "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/"
        "K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1"
    )
    azure_storage_container: str = "documents"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
