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

import time
from collections.abc import Awaitable, Callable

import structlog
from asgi_correlation_id.context import correlation_id
from beartype.typing import Sequence, cast
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from uvicorn._types import HTTPScope
from uvicorn.protocols.utils import get_path_with_query_string

from superlinked.framework.common.telemetry.telemetry_registry import telemetry

access_logger = structlog.stdlib.get_logger("api.access")


def add_timing_middleware(app: FastAPI, debug_endpoints: Sequence[str] | None = None) -> None:
    debug_endpoints = debug_endpoints or []
    known_routes = {route.path for route in app.routes if isinstance(route, APIRoute)}

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        structlog.contextvars.clear_contextvars()
        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter_ns()
        response = await call_next(request)
        process_time = time.perf_counter_ns() - start_time
        duration_ms = process_time / 1_000_000  # Convert nanoseconds to milliseconds
        url: str = get_path_with_query_string(cast(HTTPScope, request.scope))
        client_host = request.client.host if request.client else "no-client"
        client_port = request.client.port if request.client else "no-client"
        http_version = request.scope["http_version"]

        log_level = "debug" if request.url.path in debug_endpoints else "info"
        log_method = getattr(access_logger, log_level)

        log_method(
            "[%s] %s HTTP/%s - %s",
            request.method,
            url,
            http_version,
            response.status_code,
            url=str(request.url),
            status_code=response.status_code,
            method=request.method,
            request_id=request_id,
            version=http_version,
            client_ip=client_host,
            client_port=client_port,
            duration=f"{duration_ms:.2f} ms",
        )

        # TODO: FAB-3723 - Until WAF (INF-540) is in place, we only record metrics for known routes
        if request.url.path in known_routes:
            labels = {"path": request.url.path, "method": request.method, "status_code": str(response.status_code)}
            telemetry.record_metric("http_requests_total", 1, labels)
            telemetry.record_metric("http_request_duration_ms", duration_ms, labels)

        response.headers["X-Process-Time"] = str(process_time / 10**9)
        return response
