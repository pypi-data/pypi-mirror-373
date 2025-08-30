import logging

from opentelemetry.propagate import inject

from odoo import api, models

from odoo.addons.base.models.ir_actions_report import _get_wkhtmltopdf_bin

_logger = logging.getLogger(__name__)


class OpenTelemetryBase(models.AbstractModel):
    _inherit = "ir.actions.report"

    def _build_wkhtmltopdf_args(self, *args, **kwargs):
        res = super()._build_wkhtmltopdf_args(*args, **kwargs)
        carrier = {}
        inject(carrier)
        res.extend(["--custom-header-propagation", "--custom-header", "TRACEPARENT", carrier["traceparent"]])
        return res

    def _render(self, *args, **kwargs):
        _logger.info("Rendering Report %s", self.name_get())
        with self.start_as_current_span(f"_render {self.report_type} template"):
            return super()._render(*args, **kwargs)

    @api.model
    def _run_wkhtmltopdf(self, bodies, *args, **kwargs):
        with self.start_as_current_span(
            "_run_wkhtmltopdf",
            attributes={
                "cli": _get_wkhtmltopdf_bin(),
                "bodies_count": len(bodies),
            },
        ):
            return super()._run_wkhtmltopdf(bodies, *args, **kwargs)
