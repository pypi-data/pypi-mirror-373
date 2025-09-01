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

from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager

import inject
import structlog
from fastapi import Depends, FastAPI, status

from superlinked.framework.common.util.class_helper import ClassHelper
from superlinked.framework.dsl.app.rest.rest_app import RestApp
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.result import QueryResult
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.space.recency_space import RecencySpace
from superlinked.server.configuration.settings import Settings
from superlinked.server.middleware.api_key_auth import verify_api_key
from superlinked.server.service.data_loader import DataLoader
from superlinked.server.service.persistence_service import PersistenceService
from superlinked.server.util.fast_api_handler import FastApiHandler
from superlinked.server.util.open_api_schema_generator import OpenApiSchemaGenerator

logger = structlog.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_application(app)
    yield
    teardown_application(app)


def setup_application(app: FastAPI) -> None:
    persistence_service: PersistenceService = inject.instance(PersistenceService)
    data_loader: DataLoader = inject.instance(DataLoader)
    settings: Settings = inject.instance(Settings)

    ClassHelper.import_module(settings.APP_MODULE_PATH, recursive=True, ignore_missing_modules=["superlinked.batch"])

    if rest_executors := [
        executor for executor in SuperlinkedRegistry.get_executors() if isinstance(executor, RestExecutor)
    ]:
        _setup_executors(app, rest_executors, persistence_service, data_loader, settings)

    persistence_service.restore()


def teardown_application(_: FastAPI) -> None:
    persistence_service: PersistenceService = inject.instance(PersistenceService)
    logger.info("shutdown event detected")
    persistence_service.persist()


def _setup_executors(
    app: FastAPI,
    rest_executors: Sequence[RestExecutor],
    persistence_service: PersistenceService,
    data_loader: DataLoader,
    settings: Settings,
) -> None:
    for executor in rest_executors:
        _validate_recency_space(executor, settings)
        try:
            rest_app = executor.run()
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("failed to startup")
            continue
        data_loader.register_data_loader_sources(rest_app.data_loader_sources)
        persistence_service.register(rest_app.storage_manager._vdb_connector)
        _register_routes(app, rest_app)


def _validate_recency_space(executor: RestExecutor, settings: Settings) -> None:
    if _has_recency_space(executor._indices) and settings.DISABLE_RECENCY_SPACE:
        msg = "RecencySpace found in Index but is disabled. Either enable RecencySpace or remove it from the Index."
        raise ValueError(msg)


def _register_routes(app: FastAPI, rest_app: RestApp) -> None:
    fast_api_handler: FastApiHandler = FastApiHandler(rest_app.handler)
    for path, source in rest_app.handler.path_to_source_map.items():
        app.add_api_route(
            path=path,
            endpoint=fast_api_handler.ingest,
            methods=["POST"],
            status_code=status.HTTP_202_ACCEPTED,
            openapi_extra=OpenApiSchemaGenerator.generate_ingest_spec(source._schema),
            dependencies=[Depends(verify_api_key)],
        )
        logger.info("registered ingest endpoint", path=path, method="POST")
    for path, query in rest_app.handler.path_to_query_map.items():
        app.add_api_route(
            path=path,
            endpoint=fast_api_handler.query,
            methods=["POST"],
            response_model=QueryResult,
            openapi_extra=OpenApiSchemaGenerator.generate_query_spec(query.query_descriptor),
            dependencies=[Depends(verify_api_key)],
        )
        logger.info("registered query endpoint", path=path, method="POST")


def _has_recency_space(indices: Sequence[Index]) -> bool:
    return any(
        isinstance(space, RecencySpace) for index in indices if hasattr(index, "__spaces") for space in index.__spaces
    )
