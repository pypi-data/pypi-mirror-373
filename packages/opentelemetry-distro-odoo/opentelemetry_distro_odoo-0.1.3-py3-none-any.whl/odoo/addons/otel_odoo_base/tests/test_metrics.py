import logging
import threading
from unittest.mock import patch

from opentelemetry.instrumentation._semconv import HTTP_DURATION_HISTOGRAM_BUCKETS_NEW
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv._incubating.attributes import cloud_attributes, service_attributes

from opentelemetry_distro_odoo.distro.odoo import OdooDistro
from opentelemetry_distro_odoo.odoo_metrics import METRICS
from opentelemetry_distro_odoo.semconv.attributes.clevercloud import (
    CC_APP_ID,
    CC_APP_NAME,
    CC_COMMIT,
    CC_COMMIT_SHORT,
    CC_DEPLOYMENT,
    CC_INSTANCE_ID,
    CC_INSTANCE_NUMBER,
    CC_OWNER,
    # CC_SCALE,
)
from opentelemetry_distro_odoo.semconv.metrics.odoo import (
    ODOO_CALL_DURATION,
    ODOO_CALL_SQL_COUNT,
    ODOO_CALL_SQL_DURATION,
)

from .case import OdooMetricsCase

_logger = logging.getLogger(__name__)


class TestMetrics(OdooMetricsCase):
    def setUp(self):
        super().setUp()
        METRICS.create_metrics(self.meter_provider)
        current_thread = threading.current_thread()
        current_thread.query_time = 0
        current_thread.query_count = 0

    def wrapped_func(self):
        with METRICS.odoo_call_wrapper("fake.model", "wrapped_func"):
            self.env.cr.execute("select count(1) from res_partner")
            return self.env.cr.dictfetchall()

    def create_histogram_data_point(
        self, sum_data_point, count, max_data_point, min_data_point, attributes, explicit_bounds=None
    ):
        from importlib.metadata import version

        if version("opentelemetry-test-utils") >= "0.55":
            return super().create_histogram_data_point(
                sum_data_point, count, max_data_point, min_data_point, attributes, explicit_bounds
            )
        else:
            return super().create_histogram_data_point(
                sum_data_point, count, max_data_point, min_data_point, attributes
            )

    def test_odoo_call_wrapper(self):
        self.wrapped_func()
        metrics = {m.name: m for m in self.get_sorted_metrics()}
        # _logger.info("%s", pformat(metrics))
        self.assertEqual(len(metrics), 3)
        self.assert_metric_expected(
            metrics[ODOO_CALL_DURATION],
            [
                self.create_histogram_data_point(
                    sum_data_point=0,
                    count=1,
                    max_data_point=0,
                    min_data_point=0,
                    attributes={
                        "odoo.record.name": "fake.model",
                        "odoo.record.function": "wrapped_func",
                        "odoo.cursor_mode": "rw",
                        "odoo.database": self.env.cr.dbname,
                    },
                    explicit_bounds=HTTP_DURATION_HISTOGRAM_BUCKETS_NEW,
                )
            ],
            est_value_delta=100,
        )
        self.assert_metric_expected(
            metrics[ODOO_CALL_SQL_DURATION],
            [
                self.create_histogram_data_point(
                    sum_data_point=0,
                    count=1,
                    max_data_point=0,
                    min_data_point=0,
                    attributes={
                        "odoo.record.name": "fake.model",
                        "odoo.record.function": "wrapped_func",
                        "odoo.cursor_mode": "rw",
                        "odoo.database": self.env.cr.dbname,
                    },
                    explicit_bounds=HTTP_DURATION_HISTOGRAM_BUCKETS_NEW,
                )
            ],
            est_value_delta=100,
        )
        self.assert_metric_expected(
            metrics[ODOO_CALL_SQL_COUNT],
            [
                self.create_number_data_point(
                    1,
                    attributes={
                        "odoo.record.name": "fake.model",
                        "odoo.record.function": "wrapped_func",
                        "odoo.cursor_mode": "rw",
                        "odoo.database": self.env.cr.dbname,
                    },
                )
            ],
            est_value_delta=0,
        )


class TestDistro(OdooMetricsCase):
    def test_01(self):
        """
        Assert Odoo OpenTelemetry is loaded
        """
        self.assertTrue(OdooDistro().loaded)

    def test_wrapt_patch(self):
        from odoo.service.server import ThreadedServer, WorkerHTTP

        self.assertTrue(hasattr(ThreadedServer.start, "__wrapped__"), msg="Should be patch with wrapt")
        self.assertTrue(hasattr(WorkerHTTP.start, "__wrapped__"), msg="Should be patch with wrapt")
        self.assertTrue(hasattr(WorkerHTTP.signal_handler, "__wrapped__"), msg="Should be patch with wrapt")

    def test_otel_resource(self):
        res = OdooDistro().loader.resource
        self.assertIn(service_attributes.SERVICE_NAME, res.attributes)
        self.assertIn(service_attributes.SERVICE_NAMESPACE, res.attributes)
        # self.assertIn(service_attributes.SERVICE_VERSION, res.attributes)

    @patch.dict(
        "os.environ",
        {
            "CC_APP_ID": "app_0001",
            "CC_APP_NAME": "test_app",
            "CC_COMMIT_ID": "0102030405060708090a0b0c0d0e0f",
            "CC_INSTANCE_ID": "abcdef",
            "INSTANCE_NUMBER": "1",
            "CC_OWNER_ID": "orga_987654321",
            "CC_DEPLOYMENT": "090807060504030201",
            "OTEL_EXPERIMENTAL_RESOURCE_DETECTORS": "clevercloud",
        },
    )
    def test_otel_resoource_clevercloud(self):
        res = Resource.create({})
        expected = {
            CC_APP_ID: "app_0001",
            CC_APP_NAME: "test_app",
            CC_COMMIT: "0102030405060708090a0b0c0d0e0f",
            CC_COMMIT_SHORT: "0102030",
            CC_INSTANCE_ID: "abcdef",
            CC_INSTANCE_NUMBER: "1",
            CC_OWNER: "orga_987654321",
            CC_DEPLOYMENT: "090807060504030201",
            cloud_attributes.CLOUD_RESOURCE_ID: "abcdef/1",
            cloud_attributes.CLOUD_PROVIDER: "clevercloud",
            cloud_attributes.CLOUD_ACCOUNT_ID: "orga_987654321",
        }
        for expected_key, expected_value in expected.items():
            self.assertEqual(res.attributes[expected_key], expected_value, msg=f"Key={expected_key}")
