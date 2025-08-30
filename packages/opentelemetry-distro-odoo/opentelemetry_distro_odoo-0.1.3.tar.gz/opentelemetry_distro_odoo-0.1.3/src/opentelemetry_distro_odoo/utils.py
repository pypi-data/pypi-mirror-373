from __future__ import annotations

import logging

from opentelemetry.sdk._configuration import _import_sampler_factory
from opentelemetry.sdk.trace.sampling import Sampler

_logger = logging.getLogger(__name__)


def import_sampler(sampler_name: str, sampler_args: str) -> Sampler | None:
    if not sampler_name:
        return None
    try:
        sampler_factory = _import_sampler_factory(sampler_name)
        if sampler_name.endswith("traceidratio"):
            try:
                rate = float(sampler_args)
            except (ValueError, TypeError):
                _logger.warning("Could not convert TRACES_SAMPLER_ARG to float. Using default value 1.0.")
                rate = 1.0
            arg = rate
        else:
            arg = sampler_args

        sampler = sampler_factory(arg)
        if not isinstance(sampler, Sampler):
            message = f"Sampler factory, {sampler_factory}, produced output, {sampler}, which is not a Sampler."
            _logger.warning(message)
            raise ValueError(message)
        return sampler
    except Exception as exc:  # pylint: disable=broad-exception-caught
        _logger.warning(
            "Using default sampler. Failed to initialize sampler, %s: %s",
            sampler_name,
            exc,
        )
        return None
