import os

import psutil
from opentelemetry.sdk.resources import OTELResourceDetector, Resource, ResourceDetector
from opentelemetry.semconv._incubating.attributes import cloud_attributes
from opentelemetry.semconv._incubating.attributes.service_attributes import SERVICE_INSTANCE_ID, SERVICE_NAMESPACE
from opentelemetry.semconv.attributes.service_attributes import SERVICE_NAME, SERVICE_VERSION

from ..semconv.attributes.clevercloud import (
    CC_APP_ID,
    CC_APP_NAME,
    CC_COMMIT,
    CC_COMMIT_SHORT,
    CC_DEPLOYMENT,
    CC_INSTANCE_ID,
    CC_INSTANCE_NUMBER,
    CC_OWNER,
    CC_SCALE,
)


def to_mb(v: int) -> int:
    return v / 1024 / 1024


class CleverCloudResourceDetector(ResourceDetector):
    def detect(self) -> Resource:
        return Resource(
            {
                CC_SCALE: self._clevercloud_scales(),
                CC_APP_NAME: os.getenv("CC_APP_NAME"),
                CC_APP_ID: os.getenv("CC_APP_ID"),
                CC_COMMIT: os.getenv("CC_COMMIT_ID"),
                CC_COMMIT_SHORT: os.getenv("CC_COMMIT_ID")[:7],
                CC_INSTANCE_ID: os.getenv("CC_INSTANCE_ID"),
                CC_INSTANCE_NUMBER: os.getenv("INSTANCE_NUMBER"),
                CC_OWNER: os.getenv("CC_OWNER_ID"),
                CC_DEPLOYMENT: os.getenv("CC_DEPLOYMENT"),
                cloud_attributes.CLOUD_RESOURCE_ID: os.getenv("CC_INSTANCE_ID") + "/" + os.getenv("INSTANCE_NUMBER"),
                cloud_attributes.CLOUD_PROVIDER: "clevercloud",
                cloud_attributes.CLOUD_ACCOUNT_ID: os.getenv("CC_OWNER_ID"),
            }
        )

    def _clevercloud_scales(self):
        if to_mb(psutil.virtual_memory().total) <= 600:  # 600MB
            return "nano"
        cpu = psutil.cpu_count()
        if cpu == 1:
            return "XS"
        if cpu == 2:
            return "S"
        if cpu == 4:
            return "M"
        if cpu == 6:
            return "L"
        if cpu == 8:
            return "XL"
        if cpu == 12:
            return "XXL"
        if cpu == 16:
            return "XXXL"
        return "unknow"


class CleverCloudServiceResourceDetector(ResourceDetector):
    def detect(self) -> Resource:
        otel_r = OTELResourceDetector().detect()
        return Resource(
            {
                SERVICE_NAME: otel_r.attributes.get(SERVICE_NAME) or os.getenv("CC_APP_NAME"),
                SERVICE_VERSION: otel_r.attributes.get(SERVICE_VERSION) or os.getenv("CC_DEPLOYMENT_ID"),
                SERVICE_NAMESPACE: otel_r.attributes.get(SERVICE_NAMESPACE) or os.getenv("INSTANCE_TYPE"),
                SERVICE_INSTANCE_ID: otel_r.attributes.get(SERVICE_INSTANCE_ID) or os.getenv("INSTANCE_NUMBER+-"),
            }
        )
