import sys
import logging


class UncaughtException(Exception):
    pass


def raise_exception(
    message: str,
    exception: type[BaseException] = UncaughtException,
    from_exc: BaseException | None = None,
    fatal: bool = True,
    exit_code: int = 1,
    logger: logging.Logger | None = None
):
    if logger is None:
        logger = logging.getLogger(__name__)
    try:
        if from_exc is not None:
            raise exception(message) from from_exc
        raise exception(message)
    except exception:
        logger.error(message, exc_info=True)
        if fatal:
            sys.exit(exit_code)
