from __future__ import annotations

from opentelemetry._events import set_event_logger_provider
from opentelemetry._logs import set_logger_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._events import EventLoggerProvider
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs._internal.export import SimpleLogRecordProcessor
from opentelemetry.sdk._logs._internal.export.in_memory_log_exporter import InMemoryLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.export import InMemoryMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.trace import set_tracer_provider

_METRICS_EXPORTER = InMemoryMetricReader()
_TRACE_EXPORTER = InMemorySpanExporter()
_LOG_EXPORTER = InMemoryLogExporter()


def set_inmemory_tracer_provider(resource: Resource | None = None):
    if not resource:
        resource = Resource.create({"odoo.test": True})
    t_provider = TracerProvider(
        sampler=ALWAYS_ON,
        resource=resource,
    )
    t_provider.add_span_processor(SimpleSpanProcessor(_TRACE_EXPORTER))
    set_tracer_provider(t_provider)
    m_provider = MeterProvider(
        [_METRICS_EXPORTER],
        resource=resource,
    )
    set_meter_provider(m_provider)

    log_provider = LoggerProvider(resource=resource)
    log_provider.add_log_record_processor(SimpleLogRecordProcessor(_LOG_EXPORTER))
    set_logger_provider(log_provider)
    set_event_logger_provider(EventLoggerProvider(logger_provider=log_provider))


class _OdooInMemoryExporters:
    def reset_exporters(self):
        _METRICS_EXPORTER.get_metrics_data()
        _TRACE_EXPORTER.clear()
        _LOG_EXPORTER.clear()

    def metrics(self) -> InMemoryMetricReader:
        return _METRICS_EXPORTER

    def spans(self) -> InMemorySpanExporter:
        return _TRACE_EXPORTER

    def logs(self) -> InMemoryLogExporter:
        return _LOG_EXPORTER


OdooInMemoryExporters = _OdooInMemoryExporters()
