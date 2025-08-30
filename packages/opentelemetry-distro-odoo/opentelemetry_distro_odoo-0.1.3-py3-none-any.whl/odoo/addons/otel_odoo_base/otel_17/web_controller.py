from odoo import http

from odoo.addons.web.controllers.dataset import DataSet
from odoo.addons.web.controllers.report import ReportController

from opentelemetry_distro_odoo.odoo_metrics import METRICS


class OTelDataSet(DataSet):
    @http.route()
    def call_kw(self, model, method, args, kwargs, path=None):
        with METRICS.odoo_call_wrapper(model, method):
            return super().call_kw(model, method, args, kwargs, path)

    @http.route()
    def call_button(self, model, method, args, kwargs, path=None):
        with METRICS.odoo_call_wrapper(model, method):
            return super().call_button(model, method, args, kwargs, path)

    @http.route()
    def resequence(self, model, ids, field="sequence", offset=0):
        with METRICS.odoo_call_wrapper(model, "resequence"):
            return super().resequence(model, ids, field, offset)


class OTelReportController(ReportController):
    @http.route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        with METRICS.odoo_call_wrapper(
            "ir.actions.report", "render_" + converter, attrs={"report": reportname, "converter": converter}
        ):
            return super().report_routes(reportname=reportname, docids=docids, converter=converter, **data)
