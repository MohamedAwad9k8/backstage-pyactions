from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "Backstage-PyActions"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # Security
    API_TOKEN: str | None = None

    # Git Provider (optional — only needed if using providers)
    GIT_PROVIDER: str = "gitlab"
    GITLAB_URL: str = "https://gitlab.com"
    GITLAB_TOKEN: str | None = None
    GITHUB_TOKEN: str | None = None


settings = Settings()
