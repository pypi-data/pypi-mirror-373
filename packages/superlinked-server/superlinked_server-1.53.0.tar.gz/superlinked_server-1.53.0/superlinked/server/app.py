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

from json import JSONDecodeError

import sentry_sdk
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

from superlinked.framework.common.exception import (
    ExternalException,
    FeatureNotSupportedException,
    InternalException,
    InvalidInputException,
    NotFoundException,
    RequestTimeoutException,
    UnexpectedResponseException,
)
from superlinked.framework.common.telemetry.telemetry_registry import MetricType, telemetry
from superlinked.framework.common.util.version_resolver import VersionResolver
from superlinked.server.configuration.settings import settings
from superlinked.server.dependency_register import register_dependencies
from superlinked.server.exception.exception_handler import (
    handle_bad_request,
    handle_generic_exception,
    handle_not_found,
    handle_request_timeout,
    handle_unprocessable_entity,
)
from superlinked.server.middleware.lifespan_event import lifespan
from superlinked.server.middleware.timing_middleware import add_timing_middleware
from superlinked.server.router.management_router import router as management_router
from superlinked.server.util.superlinked_app_downloader_util import download_from_gcs


class ServerApp:
    def __init__(self) -> None:
        self.app = self._create_app()

    def _setup_exception_handler(self, app: FastAPI) -> None:
        app.add_exception_handler(RequestTimeoutException, handle_request_timeout)
        app.add_exception_handler(NotFoundException, handle_not_found)
        app.add_exception_handler(InvalidInputException, handle_unprocessable_entity)
        app.add_exception_handler(JSONDecodeError, handle_bad_request)
        app.add_exception_handler(UnexpectedResponseException, handle_bad_request)
        app.add_exception_handler(FeatureNotSupportedException, handle_bad_request)
        app.add_exception_handler(ExternalException, handle_bad_request)
        app.add_exception_handler(InternalException, handle_generic_exception)
        app.add_exception_handler(Exception, handle_generic_exception)

    def _create_app(self) -> FastAPI:
        if settings.IS_DOCKERIZED:
            if not settings.BUCKET_NAME or not settings.BUCKET_PREFIX:
                raise ValueError(
                    "Environment variables BUCKET_NAME and BUCKET_PREFIX must be defined when IS_DOCKERIZED is enabled"
                )
            download_from_gcs(
                settings.BUCKET_NAME, settings.BUCKET_PREFIX, settings.APP_MODULE_PATH, settings.PROJECT_ID
            )
        self._init_sentry()
        app = FastAPI(lifespan=lifespan)
        self._init_opentelemetry()
        self._setup_exception_handler(app)
        app.include_router(management_router)

        add_timing_middleware(app, debug_endpoints=["/health", "/version"])
        app.add_middleware(CorrelationIdMiddleware)  # This must be the last middleware

        register_dependencies()

        return app

    def _init_sentry(self) -> None:
        if settings.SENTRY_ENABLE:
            sentry_sdk.init(
                dsn=settings.SENTRY_URL,
                send_default_pii=settings.SENTRY_SEND_DEFAULT_PII,
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
            )

    def _init_opentelemetry(self) -> None:
        if not settings.OPENTELEMETRY_ENABLE:
            return

        server_version = VersionResolver.get_version_for_package("superlinked-server") or "unknown"
        labels = {
            "service.name": settings.OPENTELEMETRY_COMPONENT_NAME,
            "service.version": server_version,
            "environment": settings.ENVIRONMENT_NAME,
        }
        telemetry.add_labels(labels)

        telemetry.create_metric(MetricType.COUNTER, "exception.internal", "Count of system errors", "1")
        telemetry.create_metric(MetricType.COUNTER, "exception.external", "Count of user errors", "1")
        telemetry.create_metric(MetricType.COUNTER, "http_requests_total", "Count of HTTP requests", "1")
        telemetry.create_metric(
            MetricType.HISTOGRAM, "http_request_duration_ms", "HTTP request duration in milliseconds", "ms"
        )
        telemetry.create_metric(
            MetricType.COUNTER,
            "ingested_items_with_data_loader_total",
            "Count of ingested items with data loader",
            "item",
        )

        metric_exporter = OTLPMetricExporter(endpoint=settings.OPENTELEMETRY_COLLECTOR_ENDPOINT, insecure=True)
        metric_reader = PeriodicExportingMetricReader(exporter=metric_exporter)

        trace_exporter = OTLPSpanExporter(
            endpoint=settings.OPENTELEMETRY_COLLECTOR_ENDPOINT,
            insecure=True,
        )
        tracer_provider = TracerProvider(sampler=TraceIdRatioBased(settings.OPENTELEMETRY_TRACE_SAMPLING_RATE))
        tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

        telemetry.initialize(
            MeterProvider(metric_readers=[metric_reader]),
            tracer_provider=tracer_provider,
            component_name=settings.OPENTELEMETRY_COMPONENT_NAME,
        )
