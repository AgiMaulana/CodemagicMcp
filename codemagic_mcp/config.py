from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    codemagic_api_key: str
    codemagic_base_url: str = "https://api.codemagic.io"
    codemagic_default_app_id: Optional[str] = None
    codemagic_log_temp_dir: Path = Path("/tmp/codemagic-mcp")
    codemagic_log_ttl_seconds: int = Field(default=3600, ge=1)
    codemagic_log_cleanup_interval_seconds: int = Field(default=300, ge=1)
    codemagic_log_max_total_bytes: int = Field(default=524288000, ge=1)
    codemagic_log_max_file_count: int = Field(default=200, ge=1)

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
