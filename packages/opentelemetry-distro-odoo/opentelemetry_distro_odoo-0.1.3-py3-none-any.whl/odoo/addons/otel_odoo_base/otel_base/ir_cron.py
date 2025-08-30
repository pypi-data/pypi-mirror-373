from odoo import api, models

from opentelemetry_distro_odoo.odoo_metrics import METRICS


class IrCron(models.Model):
    _inherit = "ir.cron"

    @api.model
    def _callback(self, cron_name, server_action_id, *args, **kwargs):
        attrs = {"odoo.cron.manual": False}
        span_attrs = {"odoo.cron.action_id": server_action_id, "odoo.cron.manual": False}
        METRICS.odoo_run_cron.add(1, attributes=attrs)
        with METRICS.odoo_call_wrapper(self._name, "callback", attrs=attrs, span_attrs=span_attrs):
            return super()._callback(cron_name, server_action_id, *args, **kwargs)

    def method_direct_trigger(self):
        attrs = {"odoo.cron.manual": True}
        for rec in self:
            span_attrs = {
                "odoo.cron.action_id": rec.ir_actions_server_id.id,
                "odoo.cron.manual": True,
            }
            METRICS.odoo_run_cron.add(1, attributes=attrs)
            with METRICS.odoo_call_wrapper(self._name, "callback", attrs=attrs, span_attrs=span_attrs):
                super(IrCron, rec).method_direct_trigger()
