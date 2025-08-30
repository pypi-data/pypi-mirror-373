import logging

from opentelemetry.test.wsgitestutil import TestBase

from odoo.tests import TransactionCase

from opentelemetry_distro_odoo.trace.odoo import odoo_sampler_factory

_logger = logging.getLogger(__name__)


class OdooMetricsCase(TransactionCase, TestBase):
    _sample_rate = 1

    @staticmethod
    def create_tracer_provider(**kwargs):
        return TestBase.create_tracer_provider(sampler=odoo_sampler_factory("1"))
