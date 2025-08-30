from odoo import http

from odoo.addons.web.controllers.main import DataSet, ReportController

from opentelemetry_distro_odoo.odoo_metrics import METRICS


class OTelDataSet14(DataSet):
    @http.route()
    def search_read(self, model, fields=False, offset=0, limit=False, domain=None, sort=None):
        with METRICS.odoo_call_wrapper(model, "search_read"):
            return super().search_read(model, fields, offset, limit, domain, sort)

    @http.route()
    def load(self, model, id, fields):
        with METRICS.odoo_call_wrapper(model, "load"):
            return super().search_read(model, id, fields)

    @http.route()
    def call(self, model, method, args, domain_id=None, context_id=None):
        with METRICS.odoo_call_wrapper(model, method):
            return super().call(model, method, args, domain_id, context_id)

    @http.route()
    def call_kw(self, model, method, args, kwargs, path=None):
        with METRICS.odoo_call_wrapper(model, method):
            return super().call_kw(model, method, args, kwargs, path)

    @http.route()
    def call_button(self, model, method, args, kwargs):
        with METRICS.odoo_call_wrapper(model, method):
            return super().call_button(model, method, args, kwargs)

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
