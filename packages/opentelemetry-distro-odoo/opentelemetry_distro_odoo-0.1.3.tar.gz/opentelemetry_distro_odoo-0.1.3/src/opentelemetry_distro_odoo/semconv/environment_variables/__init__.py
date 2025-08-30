ODOO_OTEL_LOG_FORMAT = "ODOO_OTEL_LOG_FORMAT"
"""
The format to use for logging.
Default is "%(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
If `logfmter` is installed then this varaibles is ignored
"""
ODOO_OTEL_LOG_FORMAT_DEFAULT = "%(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"

ODOO_OTEL_LOGS_FILTER = "ODOO_OTEL_LOGS_FILTER"
"""
List of logs to filter out (comma separated values)
Default is :
 - werkzeug
 - longpolling
 - odoo.addons.bus.models.bus
"""
ODOO_OTEL_DISTRO_DEFAULT_RESOURCE_DETECTORS = "ODOO_OTEL_DISTRO_DEFAULT_RESOURCE"
"""
If set to True (or `true`) then OTEL_EXPERIMENTAL_RESOURCE_DETECTORS will have the following values:
 - os
 - process
 - host
 - otel
 - odoo
"""
ODOO_OTEL_TRACE_CUSTOM_DEFAULT = "ODOO_OTEL_TRACE_CUSTOM_DEFAULT"
"""
The default sampler name if a tuple in ODOO_OTEL_TRACE_CUSTOM is only a name
"""
ODOO_OTEL_TRACE_CUSTOM_DEFAULT_ARGS = "ODOO_OTEL_TRACE_CUSTOM_DEFAULT_ARGS"
"""
The default sampler args if a tuple in ODOO_OTEL_TRACE_CUSTOM is only a name and a sampler
"""
ODOO_OTEL_TRACE_CUSTOM = "ODOO_OTEL_TRACE_CUSTOM"
"""
A comma separated list of tuples in the following format:
 - span_name[:sampler_name[:sampler_args]]

The default sampler name is the default sampler defined in ODOO_OTEL_TRACE_CUSTOM_DEFAULT
The default sampler args is the default sampler args defined in ODOO_OTEL_TRACE_CUSTOM_DEFAULT_ARGS

Example:
 - login                   => login:$ODOO_OTEL_TRACE_CUSTOM_DEFAULT:$ODOO_OTEL_TRACE_CUSTOM_DEFAULT_ARGS
 - login:traceidratio      => login:traceidratio:$ODOO_OTEL_TRACE_CUSTOM_DEFAULT_ARGS
 - login:traceidratio:0.1  => login:traceidratio:0.1

If the sampler name ends with `traceidratio` then the sampler args must be a float
"""
ODOO_VERSION = "ODOO_VERSION"
"""
The odoo version has env var, if not set then the one from odoo.release will be used
"""
ODOO_OTEL_SERVICE_VERSION = "ODOO_OTEL_SERVICE_VERSION"
"""
The odoo service version has env var, if not set then the one from odoo.release will be used
"""
ODOO_OTEL_RESOURCE_NAMESPACE = "ODOO_OTEL_RESOURCE_NAMESPACE"
"""
The odoo resource namespace has env var. By default is `odoo`
Will set the `service.namespace` in the resource
"""
ODOO_OTEL_EXCLUDE_RECORDS = "ODOO_OTEL_EXCLUDE_RECORDS"
"""
A CSV values of record to exclude from metrics.
"""
