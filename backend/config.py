from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    groq_api_key: str = ""
    github_app_id: int = Field(default=3222129)
    github_private_key: str = ""
    github_webhook_secret: str = ""
    database_url: str = ""
    langchain_api_key: str = ""
    langsmith_project: str = "smart-pr-review-agent"
    chroma_persist_dir: str = "./chroma"
    github_mcp_url: str = "https://api.githubcopilot.com/mcp/"
    frontend_url: str = "http://localhost:5173"


settings = Settings()
