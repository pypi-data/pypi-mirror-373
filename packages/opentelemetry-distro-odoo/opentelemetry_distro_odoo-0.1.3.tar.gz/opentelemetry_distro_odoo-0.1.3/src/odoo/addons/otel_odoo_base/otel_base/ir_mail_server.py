from opentelemetry.trace import SpanKind

from odoo import api, models

from opentelemetry_distro_odoo.odoo_metrics import METRICS


class OpenTelemetryBase(models.AbstractModel):
    _inherit = "ir.mail_server"

    @api.model
    def send_email(self, *args, **kwargs):
        METRICS.odoo_send_mail.add(1)
        with self.start_as_current_span("send mail", kind=SpanKind.CLIENT):
            return super().send_email(*args, **kwargs)
