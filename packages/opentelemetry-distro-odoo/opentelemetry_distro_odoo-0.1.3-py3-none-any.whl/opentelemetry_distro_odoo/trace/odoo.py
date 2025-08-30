import logging
import os
from typing import Optional, Sequence

from opentelemetry.context import Context
from opentelemetry.sdk.trace.sampling import (
    _KNOWN_SAMPLERS,
    ALWAYS_OFF,
    DEFAULT_ON,
    ParentBasedTraceIdRatio,
    Sampler,
    SamplingResult,
    TraceIdRatioBased,
)
from opentelemetry.semconv.attributes import url_attributes
from opentelemetry.trace import Link, SpanKind, TraceState
from opentelemetry.util.types import Attributes

from ..semconv.environment_variables import (
    ODOO_OTEL_TRACE_CUSTOM,
    ODOO_OTEL_TRACE_CUSTOM_DEFAULT,
    ODOO_OTEL_TRACE_CUSTOM_DEFAULT_ARGS,
)
from ..utils import import_sampler

_logger = logging.getLogger(__name__)


class OdooTraceSampler(ParentBasedTraceIdRatio):
    def __init__(self, rate=1.0):
        super().__init__(rate)
        self._sampler_by_name = {}
        self._sampler_by_name.update(
            {
                "SELECT": ParentBasedTraceIdRatio(0.001),
                "WITH": ParentBasedTraceIdRatio(0.01),
                "ALTER": DEFAULT_ON,
            }
        )
        self.add_sampler_for_name(
            "queue.job#perform", TraceIdRatioBased(os.environ.get("ODOO_OTEL_TRACE_QUEUE_JOB", 0.1))
        )

    def get_description(self) -> str:
        return "Odoo Trace Sampler"

    def add_sampler_for_name(self, span_name: str, sampler: Sampler):
        self._sampler_by_name["odoo: " + span_name] = sampler

    def should_sample(
        self,
        parent_context: Optional["Context"],
        trace_id: int,
        name: str,
        kind: Optional[SpanKind] = None,
        attributes: Attributes = None,
        links: Optional[Sequence["Link"]] = None,
        trace_state: Optional["TraceState"] = None,
    ) -> "SamplingResult":
        attr = attributes or {}
        if attr.get(url_attributes.URL_PATH, "").startswith("/longpolling/"):
            return ALWAYS_OFF.should_sample(parent_context, trace_id, name, kind, attributes, links, trace_state)
        used_sampler = self._sampler_by_name.get(name) or super()
        return used_sampler.should_sample(parent_context, trace_id, name, kind, attributes, links, trace_state)


_KNOWN_SAMPLERS["odoo"] = OdooTraceSampler


def odoo_sampler_factory(arg: str) -> Sampler:
    try:
        rate = float(arg)
    except (ValueError, TypeError):
        _logger.warning("Could not convert TRACES_SAMPLER_ARG to float.")
        rate = 1.0
    sampler = OdooTraceSampler(rate)
    default_custom_sampler = os.environ.get(ODOO_OTEL_TRACE_CUSTOM_DEFAULT, "parentbased_traceidratio")
    default_custom_sampler_args = os.environ.get(ODOO_OTEL_TRACE_CUSTOM_DEFAULT_ARGS, "0.1")
    for custom_sampler in os.environ.get(ODOO_OTEL_TRACE_CUSTOM, "").split(","):
        if not custom_sampler:
            continue
        parts = custom_sampler.strip().split(":")
        if len(parts) == 1:
            span_name, sampler_name, sampler_args = parts[0], default_custom_sampler, default_custom_sampler_args
        elif len(parts) == 2:
            span_name, sampler_name, sampler_args = parts[0], parts[1], default_custom_sampler_args
        elif len(parts) == 3:
            span_name, sampler_name, sampler_args = parts[0], parts[1], parts[2]
        else:
            raise ValueError(
                "ODOO_OTEL_TRACE_CUSTOM must be a comma separated list in format : "
                "span_name[:sampler_name[:sampler_args]]"
            )
        sub_sampler = import_sampler(sampler_name, sampler_args)
        sampler.add_sampler_for_name(span_name, sub_sampler)
    return sampler
