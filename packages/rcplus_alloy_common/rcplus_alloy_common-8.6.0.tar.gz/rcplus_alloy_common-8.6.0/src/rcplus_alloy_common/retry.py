__all__ = [
    "RetryWithLog",
    "get_request_retry_session",
    "retry",
]

import functools
import logging
from time import sleep
from typing import Tuple, Type, Union, Callable, Collection

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from rcplus_alloy_common.constants import (
    DEFAULT_ALLOWED_METHODS,
    DEFAULT_BACKOFF_VALUE,
    DEFAULT_DELAY_AMOUNT,
    DEFAULT_EXCEPTIONS_TUPLE,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_HTTP_STATUS_CODES,
    DEFAULT_TRIES_COUNT,
)
from rcplus_alloy_common.logging import logger


class RetryWithLog(Retry):
    def sleep(self, response=None):
        attempt = len(self.history)
        history = self.history[-1]
        error = history.error or f"Status {history.status}"
        logger.warning(f"Failed to publish metrics in attempt {attempt} because of `{error}`.")
        super().sleep()


def get_request_retry_session(
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        allowed_methods: Collection[str] = DEFAULT_ALLOWED_METHODS,
        retry_status_codes: Collection[int] = DEFAULT_RETRY_HTTP_STATUS_CODES,
) -> requests.Session:
    retries = RetryWithLog(
        total=retry_count,
        backoff_factor=retry_backoff,
        allowed_methods=allowed_methods,
        status_forcelist=retry_status_codes,
    )

    session = requests.Session()
    # noinspection HttpUrlsUsage
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def retry(  # noqa: MC0001
        *,
        tries: int = DEFAULT_TRIES_COUNT,
        delay: float = DEFAULT_DELAY_AMOUNT,
        backoff: float = DEFAULT_BACKOFF_VALUE,
        exceptions: Tuple[Type[Exception], ...] = DEFAULT_EXCEPTIONS_TUPLE,
        exceptions_filter: str | None = None,
        decorator_logger: logging.Logger | None = None,
        decorator_logger_level: Union[int, str] = logging.WARNING,
) -> Callable:
    """
    Retry decorator. It retries any Python callable in case of any exception thrown.

    if the exceptions_filter is set then retry only exceptions with the specific text, for example,
    if two ValueError exceptions can be raised for different reasons then one of them can be retried
    but another is skipped and raised.
    """
    if tries < 1:
        raise ValueError(f"The tries value must be 1 or greater. Received {tries} value.")

    if delay <= 0:
        raise ValueError(f"The delay value must be greater than 0. Received {delay} value.")

    if backoff < 1:
        raise ValueError(f"The backoff value must be 1 or greater. Received {backoff} value.")

    if not exceptions:
        raise ValueError(f"The exceptions tuple must not be empty. Received {exceptions} value.")

    def _decorator(func: Callable):
        # functools.wraps is required to preserve the original callable metadata like __name__

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):  # pylint: disable=inconsistent-return-statements
            _tries, _delay = tries, delay

            while _tries >= 0:
                try:
                    return func(*args, **kwargs)
                except exceptions as ex:
                    ex_str = str(ex)
                    if exceptions_filter and exceptions_filter not in ex_str:
                        raise

                    if _tries == 0:
                        raise

                    if decorator_logger is not None:
                        decorator_logger.log(
                            level=decorator_logger_level,
                            msg=f"Callable `{func.__name__}` failed because of `{ex}`, retrying in {_delay} seconds.")

                sleep(_delay)
                _tries -= 1
                _delay *= backoff

        return _wrapper

    return _decorator
