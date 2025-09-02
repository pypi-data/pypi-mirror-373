import os
from pathlib import Path

from pydantic import AnyWebsocketUrl, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from bigdata_client.clerk.constants import ClerkInstanceType
from bigdata_client.models.search import Ranking


class LLMSettings(BaseSettings):
    USE_HYBRID: bool = True
    RANKING: Ranking = Ranking.STABLE


DEFAULT_CONF_FILE = (
    Path(__file__).parent.joinpath("environments").resolve(strict=True) / "default"
)
SETTINGS_PREFIX = "BIGDATA_"


class Settings(BaseSettings):
    PACKAGE_NAME: str = "bigdata-client"  # The name of the python package
    BACKEND_WS_API_URL: AnyWebsocketUrl
    BACKEND_API_URL: HttpUrl
    UPLOAD_API_URL: HttpUrl
    CLERK_FRONTEND_URL: HttpUrl
    CLERK_INSTANCE_TYPE: ClerkInstanceType
    LLM: LLMSettings = LLMSettings()
    MAX_PARALLEL_REQUESTS: int = 10

    model_config = SettingsConfigDict(
        env_prefix=SETTINGS_PREFIX, env_file_encoding="utf-8"
    )


file_config_path = os.environ.get(f"{SETTINGS_PREFIX}FILE_CONFIG")
if file_config_path:
    # Validate that the file exists
    file_config_path = Path(file_config_path).resolve(strict=True)

settings = Settings(_env_file=file_config_path or DEFAULT_CONF_FILE)
