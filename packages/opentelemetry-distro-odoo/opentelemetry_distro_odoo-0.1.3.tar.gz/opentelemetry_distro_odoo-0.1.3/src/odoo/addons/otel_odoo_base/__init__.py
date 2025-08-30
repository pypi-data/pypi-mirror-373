import odoo
from odoo import release
import logging
from . import otel_base
from . import controller

_logger = logging.getLogger(__name__)

if release.serie == "18.0":
    _logger.info("OTEL Serie 18.0")
    from . import otel_18
if release.serie == "17.0":
    _logger.info("OTEL Serie 17.0")
    from . import otel_17
if release.serie == "16.0":
    _logger.info("OTEL Serie 16.0")
    from . import otel_16
if release.serie == "15.0":
    _logger.info("OTEL Serie 15.0")
    from . import otel_15
if release.serie == "14.0":
    _logger.info("OTEL Serie 14.0")
    from . import otel_14
# if release.serie == "12.0":
#     from . import otel_12
