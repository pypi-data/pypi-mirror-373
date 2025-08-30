from __future__ import annotations

import contextlib
import logging

from opentelemetry import trace
from opentelemetry.trace import SpanKind

from odoo import api, models

from opentelemetry_distro_odoo.odoo_metrics import METRICS

_logger = logging.getLogger(__name__)


class OpenTelemetryBase(models.AbstractModel):
    _inherit = "base"

    @api.model
    def flush(self, fnames=None, records=None):
        if self._name != "base" and not fnames and not records:
            with self.start_as_current_span(f"full flush {self._name}"):
                return super().flush()
        return super().flush(fnames, records)

    def _compute_field_value(self, field):
        attr = {
            "odoo.compute.field": str(field),
            "odoo.compute.ids": self.ids,
            "odoo.compute.name": self._name,
        }
        with self.start_as_current_span(f"compute {field}", attributes=attr):
            return super()._compute_field_value(field)

    @api.model
    def get_current_span(self):
        return trace.get_current_span()

    def start_span(
        self,
        name,
        context=None,
        kind=SpanKind.INTERNAL,
        attributes=None,
        links=None,
        start_time=None,
        record_exception=True,
        set_status_on_exception=True,
    ):
        return METRICS.tracer.start_span(
            name,
            context=context,
            kind=kind,
            attributes=attributes,
            links=links,
            start_time=start_time,
            record_exception=record_exception,
            set_status_on_exception=set_status_on_exception,
        )

    @contextlib.contextmanager
    def start_as_current_span(
        self,
        name,
        context=None,
        kind=SpanKind.INTERNAL,
        attributes=None,
        links=None,
        start_time=None,
        record_exception=True,
        set_status_on_exception=True,
        end_on_exit=True,
    ):
        with METRICS.tracer.start_as_current_span(
            name,
            context=context,
            kind=kind,
            attributes=attributes,
            links=links,
            start_time=start_time,
            record_exception=record_exception,
            set_status_on_exception=set_status_on_exception,
            end_on_exit=end_on_exit,
        ) as span:
            yield span
