import os

from opentelemetry.sdk.environment_variables import OTEL_SERVICE_NAME
from opentelemetry.sdk.resources import Resource, ResourceDetector

# from opentelemetry.semconv.attributes import service_attributes
from opentelemetry.semconv._incubating.attributes import service_attributes

from odoo import release
from odoo.tools import config

from opentelemetry_distro_odoo.semconv.environment_variables import (
    ODOO_OTEL_RESOURCE_NAMESPACE,
    ODOO_OTEL_SERVICE_VERSION,
    ODOO_VERSION,
)


class OdooResourceDetector(ResourceDetector):
    def detect(self) -> Resource:
        default_service_name = "odoo"
        if config["db_name"]:
            default_service_name = config["db_name"]

        data = {
            service_attributes.SERVICE_NAME: os.getenv(OTEL_SERVICE_NAME, default_service_name),
            service_attributes.SERVICE_NAMESPACE: os.getenv(ODOO_OTEL_RESOURCE_NAMESPACE, "odoo"),
            "odoo.worker": os.getpid(),
            "odoo.version": os.getenv(ODOO_VERSION, release.major_version),
        }
        version = os.getenv(ODOO_OTEL_SERVICE_VERSION) or os.getenv(ODOO_VERSION)
        if version:
            data[service_attributes.SERVICE_VERSION] = version
        return Resource(data)
