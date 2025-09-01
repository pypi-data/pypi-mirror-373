# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pydantic_settings import SettingsConfigDict

from superlinked.framework.common.settings import YAML_FILENAME, YamlBasedSettings

SERVER_SECTION = "server"


class Settings(YamlBasedSettings):
    APP_MODULE_PATH: str = "superlinked_app"
    LOG_LEVEL: str = "INFO"
    PERSISTENCE_FOLDER_PATH: str = "in_memory_vdb"
    SERVER_PORT: int = 8080
    SERVER_HOST: str = "0.0.0.0"
    DISABLE_RECENCY_SPACE: bool = True
    JSON_LOG_FILE: str | None = None
    LOG_AS_JSON: bool = False
    EXPOSE_PII: bool = False
    ENVIRONMENT_NAME: str = "DEV"

    # API key
    API_KEY: str | None = None

    # Uvicorn specific settings
    WORKER_COUNT: int = 1

    # Dockerization specific settings
    IS_DOCKERIZED: bool = False
    BUCKET_NAME: str | None = None
    BUCKET_PREFIX: str | None = None
    PROJECT_ID: str | None = None

    # Sentry
    SENTRY_ENABLE: bool = False
    SENTRY_URL: str | None = None
    SENTRY_SEND_DEFAULT_PII: bool = True
    SENTRY_TRACES_SAMPLE_RATE: float = 0.01
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.01

    # OpenTelemetry
    OPENTELEMETRY_ENABLE: bool = False
    OPENTELEMETRY_COLLECTOR_ENDPOINT: str | None = "127.0.0.1:4317"
    OPENTELEMETRY_COMPONENT_NAME: str = "superlinked-server"
    OPENTELEMETRY_TRACE_SAMPLING_RATE: float = 0.1

    model_config = SettingsConfigDict(
        yaml_file=YAML_FILENAME, yaml_config_section=SERVER_SECTION, extra="ignore", frozen=True
    )


settings = Settings(_env_nested_delimiter="__")

__all__ = ["settings"]
