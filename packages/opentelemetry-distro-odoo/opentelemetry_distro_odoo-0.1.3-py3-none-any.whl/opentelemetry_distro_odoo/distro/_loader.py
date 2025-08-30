from __future__ import annotations

import logging
import os
from typing import Sequence

from opentelemetry.environment_variables import OTEL_LOGS_EXPORTER, OTEL_METRICS_EXPORTER, OTEL_TRACES_EXPORTER
from opentelemetry.instrumentation.auto_instrumentation import _load_instrumentors
from opentelemetry.instrumentation.distro import BaseDistro
from opentelemetry.sdk._configuration import (
    _get_exporter_entry_point,
    _import_exporters,
    _init_logging,
    _init_metrics,
    _init_tracing,
)
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry.sdk.environment_variables import (
    OTEL_TRACES_SAMPLER,
    OTEL_TRACES_SAMPLER_ARG,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.sampling import _KNOWN_SAMPLERS, Sampler
from typing_extensions import Literal

from odoo import tools

from ..semconv.environment_variables import (
    ODOO_OTEL_LOG_FORMAT,
    ODOO_OTEL_LOG_FORMAT_DEFAULT,
    ODOO_OTEL_LOGS_FILTER,
)
from ..utils import import_sampler

try:
    from logfmter import Logfmter
except ImportError:
    Logfmter = None

_logger = logging.getLogger(__name__)


class OdooFilter(logging.Filter):
    def __init__(self):
        self._exclude = {
            "werkzeug",
            "longpolling",
            "odoo.addons.bus.models.bus",
            "opentelemetry_distro_odoo",
        }
        self._exclude.union(set(os.getenv(ODOO_OTEL_LOGS_FILTER, "").split(",")))

    def filter(self, record):
        return record.name not in self._exclude


_EXPORTER_ENV_BY_SIGNAL_TYPE = {
    "traces": OTEL_TRACES_EXPORTER,
    "metrics": OTEL_METRICS_EXPORTER,
    "logs": OTEL_LOGS_EXPORTER,
}


def _get_exporter_names(signal_type: Literal["traces", "metrics", "logs"]) -> Sequence[str]:
    names = os.environ.get(_EXPORTER_ENV_BY_SIGNAL_TYPE.get(signal_type, ""))
    if not names or names.lower().strip() == "none":
        return []
    return [_get_exporter_entry_point(_exporter.strip(), signal_type) for _exporter in names.split(",")]


class OtelLoader:
    def __init__(self, distro: BaseDistro):
        self.resource: Resource | None = None
        self._distro = distro
        self._sampler: Sampler = None

    def load_ressource(self) -> Resource:
        self.resource = Resource.create({})
        _logger.info("resource %s", self.resource.to_json(indent=4))

    def in_test_mode(self) -> bool:
        return tools.config.get("test_enable") or False

    def load_exporters(self):
        if self.in_test_mode():
            _logger.info("No exporter set in odoo test mode")
            return
        span_exporters, metric_exporters, log_exporters = _import_exporters(
            _get_exporter_names("traces"), _get_exporter_names("metrics"), _get_exporter_names("logs")
        )
        _logger.debug("span_exporters %s", span_exporters)
        _logger.debug("metric_exporters %s", metric_exporters)
        _logger.debug("log_exporters %s", log_exporters)
        _init_tracing(span_exporters, resource=self.resource, sampler=self._sampler)
        _init_metrics(metric_exporters, resource=self.resource)
        _init_logging(log_exporters, resource=self.resource, setup_logging_handler=False)

    def load_samplers(self):
        sampler = os.environ.get(OTEL_TRACES_SAMPLER)
        sampler_args = os.environ.get(OTEL_TRACES_SAMPLER_ARG)
        if sampler not in _KNOWN_SAMPLERS:
            _logger.debug("Custom sampler [%s] auto importing it", sampler)
        self._sampler = import_sampler(sampler, sampler_args)
        _logger.debug("Custom sampler [%s] imported : %s", sampler, self._sampler.get_description())

    def load_instrument(self):
        _load_instrumentors(self._distro)

    def setup_logging(self):
        if tools.config.get("test_enable"):
            _logger.info("No OTEL Logging setup in odoo test mode")
            return
        handler = LoggingHandler(level=logging.DEBUG)
        handler.addFilter(OdooFilter())
        if Logfmter:
            handler.setFormatter(Logfmter())
        else:
            handler.setFormatter(logging.Formatter(os.getenv(ODOO_OTEL_LOG_FORMAT) or ODOO_OTEL_LOG_FORMAT_DEFAULT))
        logging.getLogger().addHandler(handler)
