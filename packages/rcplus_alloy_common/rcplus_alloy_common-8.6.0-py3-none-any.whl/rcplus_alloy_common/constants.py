"""
Various constants and ENV variables.
"""
__all__ = [
    "DEFAULT_ALLOWED_METHODS",
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
    "ENV_TAG",
    "PROJECT_TAG",
    "REPOSITORY_TAG",
    "GRAPHITE_API_ENDPOINT",
    "GRAPHITE_API_KEY",
    "GRAPHITE_API_USER",
    "LOG_SET_EXCEPTHOOK",
]

import os

# Graphite ENV variables
GRAPHITE_API_KEY = os.environ.get("GRAPHITE_API_KEY")
GRAPHITE_API_USER = os.environ.get("GRAPHITE_API_USER", "602312")
GRAPHITE_API_ENDPOINT = os.environ.get(
    "GRAPHITE_API_ENDPOINT", "https://graphite-prod-01-eu-west-0.grafana.net/graphite/metrics")

# Metric default tags ENV variables
ENV_TAG = os.environ.get("ENV_TAG", "undefined")
PROJECT_TAG = os.environ.get("PROJECT_TAG", "undefined")
REPOSITORY_TAG = os.environ.get("REPOSITORY_TAG", "undefined")

# Logging ENV variables
LOG_NAME = os.getenv("LOG_NAME", "alloy")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_MODE = os.getenv("LOG_MODE", "JSON")
LOG_SET_EXCEPTHOOK = os.getenv("LOG_SET_EXCEPTHOOK", "False")

# Constants for HTTP requests retry
DEFAULT_RETRY_COUNT = 5
DEFAULT_RETRY_BACKOFF = 0.25
DEFAULT_REQUEST_TIMEOUT = 2  # seconds
DEFAULT_ALLOWED_METHODS = (
    "GET",
    "POST",
)
DEFAULT_RETRY_HTTP_STATUS_CODES = (
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
)
METRIC_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "interval": {"type": "number"},
        "value": {"type": "number"},
        "time": {"type": "number"},
        "tags": {"type": "array", "items": {"type": "string"}, "minItems": 3, "uniqueItems": True},
    },
    "required": ["name", "interval", "value", "time", "tags"],
}

# Logging constants
LOGGING_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
LOGGING_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

# logz.io parameters
LOGZIO_TOKEN = os.environ.get("LOGZIO_TOKEN")
LOGZIO_ENDPOINT = os.environ.get("LOGZIO_ENDPOINT", "https://listener-eu.logz.io:8071")

# Constants for functions retry
DEFAULT_TRIES_COUNT = 1
DEFAULT_DELAY_AMOUNT = 2.  # in seconds
DEFAULT_BACKOFF_VALUE = 2.
DEFAULT_EXCEPTIONS_TUPLE = (Exception,)
