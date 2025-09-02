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
from beartype.typing import Any, Mapping
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sentry_sdk import capture_exception, set_context

from superlinked.framework.common.exception import InternalException
from superlinked.framework.common.telemetry.telemetry_registry import TelemetryAttributeType, telemetry

logger = structlog.getLogger(__name__)


def handle_bad_request(_: Request, exception: Exception) -> JSONResponse:
    _record_exception(exception, external=True)
    return _build_json_response(exception, status.HTTP_400_BAD_REQUEST)


def handle_not_found(_: Request, exception: Exception) -> JSONResponse:
    _record_exception(exception, external=True)
    return _build_json_response(exception, status.HTTP_404_NOT_FOUND)


def handle_request_timeout(_: Request, exception: Exception) -> JSONResponse:
    _record_exception(exception, external=True)
    return _build_json_response(exception, status.HTTP_408_REQUEST_TIMEOUT)


def handle_unprocessable_entity(_: Request, exception: Exception) -> JSONResponse:
    _record_exception(exception, external=True)
    return _build_json_response(exception, status.HTTP_422_UNPROCESSABLE_ENTITY)


async def handle_generic_exception(_: Request, exception: Exception) -> JSONResponse:
    context = exception.kwargs if isinstance(exception, InternalException) else {}
    _record_exception(exception, external=False, context=context)
    return _build_json_response(exception, status.HTTP_500_INTERNAL_SERVER_ERROR)


def _build_json_response(
    exception: Exception, status_code: int, context: Mapping[str, Any] | None = None
) -> JSONResponse:
    detail = str(exception) + (f" {context}" if context else "")
    return JSONResponse(
        status_code=status_code,
        content={"exception": str(exception.__class__.__name__), "detail": detail},
    )


def _record_exception(exception: Exception, external: bool, context: Mapping[str, Any] | None = None) -> None:
    if external:
        logger.info("user error", reason=str(exception))
    else:
        logger.warning(
            "internal error", reason=str(exception), exception_type=type(exception).__name__, context=context
        )
        if context:
            set_context("exception_context", dict(context))
        capture_exception(exception)
    metric_suffix = "external" if external else "internal"
    labels: dict[str, TelemetryAttributeType] = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
    }
    telemetry.record_metric(f"exception.{metric_suffix}", 1, labels)
