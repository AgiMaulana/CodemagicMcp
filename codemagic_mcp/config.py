from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    codemagic_api_key: str
    codemagic_base_url: str = "https://api.codemagic.io"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

