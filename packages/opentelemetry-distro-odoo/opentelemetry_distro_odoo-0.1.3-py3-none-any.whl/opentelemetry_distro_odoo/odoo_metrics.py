from __future__ import annotations

import contextlib
import logging
import os
import re
import threading
import timeit
from typing import Callable

from opentelemetry.metrics import (
    Counter,
    Histogram,
    MeterProvider,
    NoOpMeter,
    NoOpMeterProvider,
    ObservableGauge,
    UpDownCounter,
    get_meter,
)
from opentelemetry.semconv.attributes.error_attributes import ERROR_TYPE
from opentelemetry.trace import Span, Status, StatusCode, get_tracer
from opentelemetry.util import types

from odoo import tools

from opentelemetry_distro_odoo.semconv.attributes import odoo as odoo_attributes
from opentelemetry_distro_odoo.semconv.attributes.odoo import ODOO_CURSOR_DB
from opentelemetry_distro_odoo.semconv.environment_variables import ODOO_OTEL_EXCLUDE_RECORDS
from opentelemetry_distro_odoo.semconv.metrics import odoo as odoo_metrics
from opentelemetry_distro_odoo.version import __version__

Default_exclude_record = {
    (None, "get_views"),
    (None, "load_views"),
    (None, "name_get"),
    (None, "name_search"),
    (None, "name_create"),
    (None, "has_group"),
    (None, "get_formview_action"),
    (None, "search_panel_select_range"),
    ("ir.ui.view", None),
}
_logger = logging.getLogger(__name__)


def _get_db_name():
    db = tools.config["db_name"]
    # If the database name is not provided on the command-line,
    # use the one on the thread (which means if it is provided on
    # the command-line, this will break when installing another
    # database from XML-RPC).
    if not db and hasattr(threading.current_thread(), "dbname"):
        return threading.current_thread().dbname
    return db


class _OdooMetrics:
    odoo_call_sql_queries_count: Counter
    odoo_call_sql_queries_duration: Histogram
    odoo_call_error: Counter
    odoo_call_duration: Histogram
    odoo_report_duration: Histogram
    odoo_send_mail: Counter
    odoo_run_cron: Counter
    worker_count: UpDownCounter
    worker_max: ObservableGauge
    odoo_up: ObservableGauge

    def __init__(
        self,
        exclude_exception: list[str] | None = None,
        exclude_records: list[tuple[str | None, str | None]] | None = None,
    ):
        _logger.info("Init %s", type(self).__qualname__)
        self.exclude_exception: set[str] = set(exclude_exception or [])
        _exclude_pattern: set[str] = {
            f"{record_name or '.*'}#{function_name or '.*'}"
            for record_name, function_name in Default_exclude_record.union(exclude_records or ())
        }
        _exclude_pattern |= {
            f"{record_name or '.*'}#{function_name or '.*'}"
            for v in (os.getenv(ODOO_OTEL_EXCLUDE_RECORDS) or "").split(",")
            if v
            for record_name, function_name in v.split("#")
        }
        self._exclude_pattern = {re.compile(str_pattern) for str_pattern in _exclude_pattern}
        self._function_map_name = {
            "search_read": "web_search_read",
            "read_group": "web_read_group",
            "read": "web_read",
            "load_views": "get_views",
        }
        self.create_metrics(NoOpMeterProvider())

    def create_metrics(self, meter_provider: MeterProvider = None):
        self._meter = get_meter(
            __name__,
            __version__,
            meter_provider,
            schema_url="https://opentelemetry.io/schemas/1.11.0",
        )
        self.odoo_call_error = odoo_metrics.create_odoo_call_error(self._meter)
        self.odoo_call_duration = odoo_metrics.create_odoo_call_duration(self._meter)
        self.odoo_call_sql_queries_count = odoo_metrics.create_odoo_call_sql_queries_count(self._meter)
        self.odoo_call_sql_queries_duration = odoo_metrics.create_call_sql_queries_duration(self._meter)
        self.odoo_send_mail = odoo_metrics.create_odoo_send_mail(self._meter)
        self.odoo_run_cron = odoo_metrics.create_odoo_run_cron(self._meter)
        self.worker_count = odoo_metrics.create_worker_count(self._meter)

    @property
    def meter(self):
        return get_meter(__name__, __version__)

    @property
    def tracer(self):
        return get_tracer(__name__, __version__)

    def get_attributes_metrics(self, odoo_record_name, method_name):
        current_thread = threading.current_thread()
        return {
            odoo_attributes.ODOO_MODEL_NAME: odoo_record_name,
            odoo_attributes.ODOO_MODEL_FUNCTION_NAME: method_name,
            odoo_attributes.ODOO_CURSOR_MODE: getattr(current_thread, "cursor_mode", "rw"),
        }

    @contextlib.contextmanager
    def odoo_call_wrapper(
        self,
        odoo_record_name: str,
        method_name: str,
        *,
        attrs: types.Attributes = None,
        metrics_attrs: types.Attributes = None,
        span_attrs: types.Attributes = None,
        post_span_callback: Callable[[Span], None] = None,
    ):
        if isinstance(self._meter, NoOpMeter):
            _logger.debug("NoOp Meter by opentelemetry")
            yield
            return

        m_name = self._function_map_name.get(method_name) or method_name
        if any(pat.match(f"{odoo_record_name}#{m_name}") for pat in self._exclude_pattern):
            _logger.debug("Exclude Metrcis on %s#%s", odoo_record_name, m_name)
            yield
            return

        odoo_attr = self.get_attributes_metrics(odoo_record_name, m_name)

        odoo_attr[ODOO_CURSOR_DB] = _get_db_name()

        metrics_attr = dict(odoo_attr)
        metrics_attr.update(attrs or {})
        metrics_attr.update(metrics_attrs or {})

        span_attr = dict(odoo_attr)
        span_attr.update(attrs or {})
        span_attr.update(span_attrs or {})

        start = timeit.default_timer()
        with self.tracer.start_as_current_span(f"{odoo_record_name}#{m_name}", attributes=span_attr) as span:
            try:
                yield
            except Exception as ex:
                if type(ex).__qualname__ in self.exclude_exception:
                    raise ex

                metrics_attr[ERROR_TYPE] = type(ex).__qualname__
                self.odoo_call_error.add(1, metrics_attr)
                span.record_exception(ex)
                span.set_attribute(ERROR_TYPE, type(ex).__qualname__)
                span.set_status(Status(StatusCode.ERROR, str(ex)))
                _logger.exception("Exception :", exc_info=ex)
                raise ex
            finally:
                if post_span_callback:
                    post_span_callback(span)
                duration_s = timeit.default_timer() - start
                metrics = self.odoo_call_duration
                metrics.record(duration_s, metrics_attr)
                current_thread = threading.current_thread()
                if hasattr(current_thread, "query_count"):
                    self.odoo_call_sql_queries_count.add(current_thread.query_count, metrics_attr)
                if hasattr(current_thread, "query_time"):
                    self.odoo_call_sql_queries_duration.record(current_thread.query_time, metrics_attr)


METRICS = _OdooMetrics()
