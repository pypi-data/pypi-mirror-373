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

import structlog
from beartype.typing import Any
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import Field

from superlinked.framework.common.telemetry.telemetry_registry import TelemetryAttributeType, telemetry
from superlinked.framework.common.util.immutable_model import ImmutableBaseModel
from superlinked.framework.dsl.executor.rest.rest_handler import RestHandler
from superlinked.framework.dsl.query.query_user_config import QueryUserConfig
from superlinked.framework.storage.redis.query.redis_vector_query_params import (
    HYBRID_POLICY_ADHOC_BF,
    HYBRID_POLICY_BATCHES,
)

logger = structlog.getLogger(__name__)


class QueryResponse(ImmutableBaseModel):
    schema_: str = Field(..., alias="schema")
    results: list[dict[str, Any]]
    metadata: dict[str, Any] | None


class FastApiHandler:
    def __init__(self, rest_handler: RestHandler) -> None:
        self.__rest_handler = rest_handler

    async def ingest(self, request: Request) -> Response:
        payload = await request.json()
        with telemetry.span("api_handler.ingest", attributes={"path": request.url.path}):
            await self.__rest_handler._ingest_handler(payload, request.url.path)
        logger.debug("ingested data", path=request.url.path, pii_payload=payload)
        return Response(status_code=status.HTTP_202_ACCEPTED)

    async def query(self, request: Request) -> Response:
        payload = await request.json()
        query_user_config = self.calculate_query_user_config(request)
        labels: dict[str, TelemetryAttributeType] = {
            "path": request.url.path,
            "include_metadata": query_user_config.with_metadata,
        }
        with telemetry.span("api_handler.query", attributes=labels):
            query_result = await self.__rest_handler._query_handler(payload, request.url.path, query_user_config)
        logger.debug(
            "queried data",
            path=request.url.path,
            include_metadata=query_user_config.with_metadata,
            redis_hybrid_policy=query_user_config.redis_hybrid_policy,
            redis_batch_size=query_user_config.redis_batch_size,
            result_entity_count=len(query_result.entries),
            pii_payload=payload,
            pii_result=query_result,
        )
        exclude_set = set() if query_user_config.with_metadata else {"metadata"}
        return JSONResponse(
            content=query_result.model_dump(exclude=exclude_set),
            status_code=status.HTTP_200_OK,
        )

    def calculate_query_user_config(self, request: Request) -> QueryUserConfig:
        include_metadata = request.headers.get("x-include-metadata", "false").lower() == "true"
        redis_hybrid_policy = self._calculate_redis_hybrid_policy(request)
        redis_batch_size = self._calculate_redis_batch_size(request)
        config_params: dict[str, Any] = {"with_metadata": include_metadata}
        if redis_hybrid_policy is not None:
            config_params["redis_hybrid_policy"] = redis_hybrid_policy
        if redis_batch_size is not None:
            config_params["redis_batch_size"] = redis_batch_size
        return QueryUserConfig(**config_params)

    def _calculate_redis_hybrid_policy(self, request: Request) -> str | None:
        hybrid_policy = request.headers.get("x-redis-hybrid-policy")
        if not hybrid_policy:
            return None
        hybrid_policy = hybrid_policy.upper()
        valid_values = [HYBRID_POLICY_BATCHES, HYBRID_POLICY_ADHOC_BF]
        if hybrid_policy not in valid_values:
            raise ValueError(f"Invalid hybrid policy: {hybrid_policy}. Only {valid_values} is allowed.")
        return hybrid_policy

    def _calculate_redis_batch_size(self, request: Request) -> int | None:
        batch_size_str = request.headers.get("x-redis-batch-size")
        if not batch_size_str:
            return None
        try:
            return int(batch_size_str)
        except ValueError as e:
            raise ValueError(f"Invalid batch size: {batch_size_str}. Must be an integer.") from e
