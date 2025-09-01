from __future__ import annotations

from typing import cast

from structlog.typing import FilteringBoundLogger
from ucam_observe import get_structlog_logger as _get_structlog_logger  # type: ignore


def get_structlog_logger(name: str = "ucam_faas") -> FilteringBoundLogger:
    """Get a logger that emits a JSON object for each log call."""
    return cast(FilteringBoundLogger, _get_structlog_logger(name))


# As well as making a logger available this should setup logging before the flask app is created
logger: FilteringBoundLogger = get_structlog_logger(__name__)
