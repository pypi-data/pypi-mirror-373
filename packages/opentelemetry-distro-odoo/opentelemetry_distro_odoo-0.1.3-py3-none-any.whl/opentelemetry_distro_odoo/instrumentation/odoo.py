from typing import Any, Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

from ..odoo_metrics import METRICS


class OdooInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return []

    def _instrument(self, **kwargs: Any):
        METRICS.create_metrics()

    def _uninstrument(self, **kwargs: Any):
        pass
