"""
Various metrics, logging, retry etc. utils and helpers.

Notes:
    configure_logger supports `capture_warnings` parameter. This parameter configure Python's logging library to capture
    Python's warnings globally and output them as formatted logging messages with the WARNING level. Python's warnings
    are used quite often by various libraries, such as Pandas, to notify their users about things like deprecation
    warnings.
    Usually such warnings are initialized lazily so to capture them correctly the logger with the name `py.warnings`
    should be created in advance and configured. See `app/src/scripts/one_log_data_import.py` for the usage example.
"""

from rcplus_alloy_common.constants import (
    DEFAULT_BACKOFF_VALUE,
    DEFAULT_DELAY_AMOUNT,
    DEFAULT_EXCEPTIONS_TUPLE,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_HTTP_STATUS_CODES,
    DEFAULT_TRIES_COUNT,
    LOGGING_DATETIME_FORMAT,
    LOGGING_FORMAT,
    LOG_LEVEL,
    LOG_MODE,
    LOG_NAME,
    METRIC_SCHEMA,
)
from rcplus_alloy_common.logging import (
    configure_logger,
    configure_new_logger,
    configure_existing_logger,
    configure_existing_loggers,
    logger,
)
from rcplus_alloy_common.metrics import (
    is_valid_metric,
    make_single_metric,
    publish_metrics_async,
    publish_metrics_sync,
)
from rcplus_alloy_common.retry import (
    RetryWithLog,
    get_request_retry_session,
    retry,
)
from rcplus_alloy_common.encoder import encode
from rcplus_alloy_common.cockpit import (
    get_cockpit_credentials,
    get_auth_headers,
    CockpitAuthParams,
    CockpitTenantCredentials,
)

# head_ref is set by default to the version of this pypi package.
# So if someone installs this package and do a `print(rcplus_alloy_common.head_ref)` it returns something like "0.2.0"
# However, the CI build process will replace the value of head_ref to the current git commit hash before uploading
# the files to S3 for Airflow DAGs to use.
from rcplus_alloy_common.version import head_ref


__version__ = head_ref
__all__ = [
    "__version__",
    "head_ref",
    "DEFAULT_BACKOFF_VALUE",
    "DEFAULT_DELAY_AMOUNT",
    "DEFAULT_EXCEPTIONS_TUPLE",
    "DEFAULT_REQUEST_TIMEOUT",
    "DEFAULT_RETRY_BACKOFF",
    "DEFAULT_RETRY_COUNT",
    "DEFAULT_RETRY_HTTP_STATUS_CODES",
    "DEFAULT_TRIES_COUNT",
    "LOGGING_DATETIME_FORMAT",
    "LOGGING_FORMAT",
    "LOG_LEVEL",
    "LOG_MODE",
    "LOG_NAME",
    "METRIC_SCHEMA",
    "configure_existing_logger",
    "configure_existing_loggers",
    "configure_new_logger",
    "configure_logger",
    "get_request_retry_session",
    "is_valid_metric",
    "logger",
    "make_single_metric",
    "publish_metrics_async",
    "publish_metrics_sync",
    "RetryWithLog",
    "retry",
    "encode",
    "get_cockpit_credentials",
    "get_auth_headers",
    "CockpitAuthParams",
    "CockpitTenantCredentials",
]
