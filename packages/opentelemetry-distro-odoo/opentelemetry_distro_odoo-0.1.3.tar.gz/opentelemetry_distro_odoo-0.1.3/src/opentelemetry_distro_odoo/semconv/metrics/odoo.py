from opentelemetry.instrumentation._semconv import HTTP_DURATION_HISTOGRAM_BUCKETS_NEW
from opentelemetry.metrics import Counter, Histogram, Meter, UpDownCounter

ODOO_TRACER_API_NAME = "odoo.api"
"""

"""

ODOO_CALL_SQL_COUNT = "odoo.call.sql.queries.count"
"""
Count of odoo sql query executed by web calls (call_kw)
Instrument: counter
Unit: 1
"""


def create_odoo_call_sql_queries_count(meter: Meter) -> Counter:
    """Count of odoo sql query executed by web calls (call_kw)"""
    return meter.create_counter(
        name=ODOO_CALL_SQL_COUNT,
        description="Count of odoo sql query executed by web calls (call_kw)",
        unit="1",
    )


ODOO_CALL_SQL_DURATION = "odoo.call.sql.queries.duration"
"""
The time it took per odoo web call (call_kw)
Instrument: histogram
Unit: s
"""


def create_call_sql_queries_duration(meter: Meter) -> Histogram:
    """The time it took per odoo web call (call_kw)"""
    return meter.create_histogram(
        name=ODOO_CALL_SQL_DURATION,
        description="The time it took per odoo web call (call_kw)",
        unit="s",
        explicit_bucket_boundaries_advisory=HTTP_DURATION_HISTOGRAM_BUCKETS_NEW,
    )


ODOO_CALL_ERROR = "odoo.call.error"
"""
Number of error for odoo call web call (call_kw)
Instrument: counter
Unit: 1
"""


def create_odoo_call_error(meter: Meter) -> Counter:
    """Number of error for odoo call web call (call_kw)"""
    return meter.create_counter(
        name=ODOO_CALL_ERROR,
        description="Number of error for odoo call web call (call_kw)",
        unit="1",
    )


ODOO_CALL_DURATION = "odoo.call.duration"
"""
Duration of odoo web call (call_kw)
Instrument: histogram
Unit: s
"""


def create_odoo_call_duration(meter: Meter) -> Histogram:
    """Duration of odoo web call (call_kw)"""
    return meter.create_histogram(
        name=ODOO_CALL_DURATION,
        description="Duration of odoo web call (call_kw)",
        unit="s",
        explicit_bucket_boundaries_advisory=HTTP_DURATION_HISTOGRAM_BUCKETS_NEW,
    )


ODOO_SEND_MAIL = "odoo.send.mail"
"""
Number of send mail
Instrument: counter
Unit: 1
"""


def create_odoo_send_mail(meter: Meter) -> Counter:
    """Number of send mail"""
    return meter.create_counter(
        name=ODOO_SEND_MAIL,
        description="Number of send mail",
        unit="1",
    )


ODOO_RUN_CRON = "odoo.run.cron"
"""
Number of run cron
Instrument: counter
Unit: 1
"""


def create_odoo_run_cron(meter: Meter) -> Counter:
    """Number of run cron"""
    return meter.create_counter(
        name=ODOO_RUN_CRON,
        description="Number of run cron",
        unit="1",
    )


ODOO_WORKER = "odoo.worker"
"""
Number of workers created by Odoo Prefork server
Instrument: UpDownCounter
Unit: 1
"""


def create_worker_count(meter: Meter) -> UpDownCounter:
    """Number of workers created by Odoo Prefork server"""
    return meter.create_up_down_counter(
        name=ODOO_WORKER,
        description="Number of workers created by Odoo Prefork server",
        unit="1",
    )


ODOO_WORKER_MAX = "odoo.worker.max"
"""
Number of workers created by Odoo Prefork server
Instrument: UpDownCounter
Unit: 1
"""


def create_worker_max(meter: Meter) -> UpDownCounter:
    """Number of workers created by Odoo Prefork server"""
    return meter.create_up_down_counter(
        name=ODOO_WORKER_MAX,
        description="Number of workers created by Odoo Prefork server",
        unit="1",
    )


ODOO_UP = "odoo.up"
ODOO_CACHE_USAGE = "odoo.cache.usage"
ODOO_LIMIT_TIME = "odoo.limit.time"
ODOO_LIMIT_MEMORY = "odoo.limit.memory"
