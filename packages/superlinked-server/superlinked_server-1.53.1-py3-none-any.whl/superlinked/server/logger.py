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

import logging

from structlog_sentry import SentryProcessor

from superlinked.framework.common.logging import LoggerConfigurator
from superlinked.framework.common.util.custom_structlog_processor import (
    CustomStructlogProcessor,
)
from superlinked.server.configuration.settings import settings


class ServerLoggerConfigurator:
    @staticmethod
    def setup_logger() -> None:
        root_logger = logging.getLogger()
        root_logger.setLevel(settings.LOG_LEVEL)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

        for _log in [
            "uvicorn",
            "uvicorn.lifespan",
            "uvicorn.error",
        ]:
            logger = logging.getLogger(_log)
            logger.handlers.clear()
            root_logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            logger.propagate = True

        for _log in ["sentence_transformers", "uvicorn.access"]:
            logging.getLogger(_log).setLevel(logging.WARNING)

        processors = LoggerConfigurator._get_structlog_processors(  # noqa:SLF001 Private member
            settings.JSON_LOG_FILE, settings.EXPOSE_PII, settings.LOG_AS_JSON
        )
        processors += [
            SentryProcessor(event_level=logging.ERROR, active=settings.SENTRY_ENABLE),
            CustomStructlogProcessor.drop_color_message_key,  # Drop color must be the last processor
        ]
        LoggerConfigurator.configure_structlog_logger(
            settings.JSON_LOG_FILE,
            processors,
            settings.EXPOSE_PII,
            settings.LOG_AS_JSON,
        )
