from datetime import datetime
from logging import DEBUG, Logger, getLogger
from typing import Any, Mapping
from uuid import UUID


def _process_values(values: Mapping[str, Any] | None):
    if not values:
        return None

    processed = {}
    for k, v in values.items():
        k = f"${k}"  # prefix keys to avoid conflicts with LogRecord keys
        if isinstance(v, (UUID, datetime)):
            processed[k] = str(v)
        else:
            processed[k] = v
    return processed


# A wrapper around a standard `logging.Logger` instance. The main
# difference is that its logging methods accept arbitrary **kwargs which are
# automatically merged with "extra"
class PlanarLogger:
    def __init__(self, logger: Logger):
        self._logger = logger

    def isDebugEnabled(self) -> bool:
        return self._logger.isEnabledFor(DEBUG)

    def debug(
        self,
        msg: object,
        **kwargs: Any,
    ) -> None:
        return self._logger.debug(
            msg,
            stacklevel=2,
            extra=_process_values(kwargs),
        )

    def info(
        self,
        msg: object,
        **kwargs: Any,
    ) -> None:
        return self._logger.info(
            msg,
            stacklevel=2,
            extra=_process_values(kwargs),
        )

    def warning(
        self,
        msg: object,
        **kwargs: Any,
    ) -> None:
        return self._logger.warning(
            msg,
            stacklevel=2,
            extra=_process_values(kwargs),
        )

    def error(
        self,
        msg: object,
        **kwargs: Any,
    ) -> None:
        return self._logger.error(
            msg,
            stacklevel=2,
            extra=_process_values(kwargs),
        )

    def critical(
        self,
        msg: object,
        **kwargs: Any,
    ) -> None:
        return self._logger.critical(
            msg,
            stacklevel=2,
            extra=_process_values(kwargs),
        )

    def exception(
        self,
        msg: object,
        **kwargs: Any,
    ) -> None:
        return self._logger.exception(
            msg,
            exc_info=True,
            stacklevel=2,
            extra=_process_values(kwargs),
        )

    def setLevel(self, level: int) -> None:
        self._logger.setLevel(level)

    @property
    def handlers(self):
        return self._logger.handlers


def get_logger(name: str) -> PlanarLogger:
    """
    Get a logger instance.

    This will be a PlanarLogger instance which supports structured logging
    by passing keyword arguments to logging methods.
    """
    logger = getLogger(name)
    return PlanarLogger(logger)
