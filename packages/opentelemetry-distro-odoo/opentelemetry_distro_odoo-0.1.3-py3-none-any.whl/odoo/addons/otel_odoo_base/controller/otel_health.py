import json

import psycopg2
import werkzeug

import odoo
from odoo import http


class HealthCheck(http.Controller):
    @http.route("/system/health", type="http", auth="none", save_session=False)
    def health(self, db_server_status=False):
        health_info = {"status": "pass"}
        status = 200
        if db_server_status:
            try:
                odoo.sql_db.db_connect("postgres").cursor().close()
                health_info["db_server_status"] = True
            except psycopg2.Error:
                health_info["db_server_status"] = False
                health_info["status"] = "fail"
                status = 500
        data = json.dumps(health_info)
        headers = [("Content-Type", "application/json"), ("Cache-Control", "no-store")]
        if status != 200:
            return werkzeug.wrappers.Response(status=status)
        return http.request.make_response(data, headers)
