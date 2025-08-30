from __future__ import annotations

import logging
from typing import Any, Collection

import psycopg2
import requests
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.metrics import (
    CallbackOptions,
    Observation,
    get_meter,
)

import odoo
from odoo.tools.cache import STAT

from opentelemetry_distro_odoo.semconv.metrics.odoo import (
    ODOO_CACHE_USAGE,
    ODOO_LIMIT_MEMORY,
    ODOO_LIMIT_TIME,
    ODOO_UP,
    ODOO_WORKER_MAX,
)
from opentelemetry_distro_odoo.version import __version__

from ..semconv.attributes.odoo import ODOO_ATTR_TYPE, ODOO_CURSOR_DB, ODOO_MODEL_FUNCTION_NAME, ODOO_MODEL_NAME

_logger = logging.getLogger(__name__)


class OdooSystemMetricsInstrumentor(BaseInstrumentor):
    def _uninstrument(self, **kwargs: Any):
        pass

    def instrumentation_dependencies(self) -> Collection[str]:
        return ()

    def _instrument(self, **kwargs: Any):
        # pylint: disable=too-many-branches,too-many-statements
        meter_provider = kwargs.get("meter_provider")
        self._meter = get_meter(
            __name__,
            __version__,
            meter_provider,
            schema_url="https://opentelemetry.io/schemas/1.11.0",
        )
        self._meter.create_observable_gauge(
            name=ODOO_LIMIT_MEMORY,
            callbacks=[self._get_limit_memory],
            description="Odoo limits set in config",
            unit="By",
        )
        self._meter.create_observable_gauge(
            name=ODOO_LIMIT_TIME,
            callbacks=[self._get_limit_time],
            description="Odoo limits time CPU set in config",
            unit="s",
        )
        self._meter.create_observable_gauge(ODOO_WORKER_MAX, callbacks=[self._callback_max_worker])
        self._meter.create_observable_gauge(
            name=ODOO_CACHE_USAGE, callbacks=[self._callback_cache_usage], description="Odoo orm_cache Stat", unit="1"
        )
        self.odoo_up = self._meter.create_observable_gauge(
            ODOO_UP,
            callbacks=[self._callback_up, self._callback_up_wkhtml, self._callback_up_pg],
            unit="1",
        )

    def _callback_up(self, opt: CallbackOptions) -> list[Observation]:
        port = odoo.tools.config["http_port"] or "8069"
        ok = 0
        try:
            requests.post(
                f"http://localhost:{port}/web/webclient/version_info", json={}, timeout=opt.timeout_millis / 1000
            )
            ok = 1
        except requests.exceptions.RequestException:
            pass

        return [Observation(ok, {ODOO_ATTR_TYPE: "web"})]

    def _callback_up_wkhtml(self, opt: CallbackOptions) -> list[Observation]:
        from odoo.addons.base.models.ir_actions_report import wkhtmltopdf_state

        return [Observation(int(wkhtmltopdf_state == "ok"), {ODOO_ATTR_TYPE: "wkhtmltopdf"})]

    def _callback_up_pg(self, opt: CallbackOptions) -> list[Observation]:
        ok = 0
        try:
            if odoo.release.major_version >= "16.0":
                odoo.sql_db.db_connect("postgres").cursor().close()
            else:
                odoo.sql_db.db_connect("postgres").cursor(serialized=False).close()

            ok = 1
        except psycopg2.Error:
            pass
        return [Observation(ok, {ODOO_ATTR_TYPE: "database"})]

    def _callback_max_worker(self, opt: CallbackOptions) -> list[Observation]:
        workers = odoo.tools.config["workers"] or 0
        return [
            Observation(
                workers,
            )
        ]

    def _get_limit_memory(selfself, opt: CallbackOptions) -> list[Observation]:
        limit_memory_hard = odoo.tools.config["limit_memory_hard"] or 0
        limit_memory_soft = odoo.tools.config["limit_memory_soft"] or 0
        return [
            Observation(
                limit_memory_hard,
                {"type": "hard"},
            ),
            Observation(
                limit_memory_soft,
                {"type": "soft"},
            ),
        ]

    def _get_limit_time(selfself, opt: CallbackOptions) -> list[Observation]:
        return [
            Observation(
                odoo.tools.config["limit_time_real"] or 0,
                {"type": "real"},
            ),
            Observation(
                odoo.tools.config["limit_time_cpu"] or 0,
                {"type": "cpu"},
            ),
            Observation(
                odoo.tools.config["limit_time_real_cron"] or 0,
                {"type": "cron"},
            ),
        ]

    def _callback_cache_entries(self, opt: CallbackOptions) -> list[Observation]:
        return []

    def _callback_cache_usage(self, opt: CallbackOptions) -> list[Observation]:
        obs: list[Observation] = []
        for (dbname, model, method), stat in STAT.items():
            dbname_display = dbname or "no_db"
            attrs = {ODOO_CURSOR_DB: dbname_display, ODOO_MODEL_NAME: model, ODOO_MODEL_FUNCTION_NAME: method.__name__}
            obs.extend(
                [
                    Observation(
                        getattr(stat, prop),
                        attributes={**attrs, ODOO_ATTR_TYPE: prop},
                    )
                    for prop in ["hit", "miss", "err"]
                ]
            )
        return obs
