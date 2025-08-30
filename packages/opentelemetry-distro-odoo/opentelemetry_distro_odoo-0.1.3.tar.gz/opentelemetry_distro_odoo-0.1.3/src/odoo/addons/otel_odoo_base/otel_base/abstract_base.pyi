from __future__ import annotations

import contextlib
from typing import Iterator

from opentelemetry.context import Context
from opentelemetry.trace import Span, SpanKind, _Links
from opentelemetry.util import types

from odoo import api, models

class OpenTelemetryBase(models.AbstractModel):
    _inherit = "base"

    @api.model
    def flush(self, fnames=None, records=None): ...
    def _compute_field_value(self, field: str): ...
    @api.model
    def get_current_span(self) -> Span: ...
    def start_span(
        self,
        name: str,
        context: Context | None = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: types.Attributes = None,
        links: _Links = None,
        start_time: int | None = None,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
    ) -> Span: ...
    @contextlib.contextmanager
    def start_as_current_span(
        self,
        name: str,
        context: Context | None = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: types.Attributes = None,
        links: _Links = None,
        start_time: int | None = None,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
        end_on_exit: bool = True,
    ) -> Iterator[Span]: ...
