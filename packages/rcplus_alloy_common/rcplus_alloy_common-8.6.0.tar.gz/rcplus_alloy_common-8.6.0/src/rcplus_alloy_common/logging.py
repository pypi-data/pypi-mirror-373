__all__ = [
    "configure_logger",
    "configure_new_logger",
    "configure_existing_logger",
    "configure_existing_loggers",
    "change_logging_level",
    "logger",
    "AlloyStreamHandler",
]

import logging
import os
import sys
from datetime import datetime, timezone
from typing import Union
from contextlib import contextmanager
try:
    from pythonjsonlogger.json import JsonFormatter
except ImportError:
    # This is only required for backward compatibility with infra workflow and must be removed eventually
    from pythonjsonlogger.jsonlogger import JsonFormatter

from rcplus_alloy_common.constants import (
    LOGGING_DATETIME_FORMAT,
    LOGGING_FORMAT,
    LOG_LEVEL,
    LOG_MODE,
    LOG_NAME,
    LOG_SET_EXCEPTHOOK,
)


def truncate_message(message: str, max_length: int = 2000) -> str:
    if len(message) > max_length:
        return f"{message[: (max_length - 3) // 2]}...{message[-(max_length - 3) // 2 :]}"
    return message


class CustomJsonFormatter(JsonFormatter):
    def formatTime(self, record, datefmt=None):
        return f"{datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(LOGGING_DATETIME_FORMAT)[:-3]}Z"

    @staticmethod
    def _get_lambda_alloy_tag(software_component: str, name: str):
        return f"alloy.lambda.{software_component}.{name.replace(f'alloy-{software_component}-', '')}"

    def process_log_record(self, log_record):  # noqa: PLR0912
        software_component = os.getenv("SOFTWARE_COMPONENT")
        log_record["message"] = truncate_message(log_record["message"])
        if software_component is not None:
            log_record["software_component"] = software_component

        dag_id = os.getenv("DAG_ID")
        if dag_id is not None:
            log_record["dag_id"] = dag_id

        dag_run_id = os.getenv("DAG_RUN_ID")
        if dag_run_id is not None:
            log_record["dag_run_id"] = dag_run_id

        task_id = os.getenv("TASK_ID")
        if task_id is not None:
            log_record["task_id"] = task_id

        aws_lambda_function_name = os.getenv("AWS_LAMBDA_FUNCTION_NAME")
        if aws_lambda_function_name is not None:
            log_record["aws_lambda_function_name"] = aws_lambda_function_name

        aws_lambda_function_version = os.getenv("AWS_LAMBDA_FUNCTION_VERSION")
        if aws_lambda_function_version is not None:
            log_record["aws_lambda_function_version"] = aws_lambda_function_version

        alloy_tag = (
            os.getenv("ALLOY_TAG") or
            (
                self._get_lambda_alloy_tag(software_component, aws_lambda_function_name)
                if "AWS_LAMBDA_FUNCTION_NAME" in os.environ and "SOFTWARE_COMPONENT" in os.environ
                else None
            )
        )

        if alloy_tag is not None:
            log_record["alloy_tag"] = alloy_tag

        tenant = os.getenv("TENANT")
        if tenant is not None:
            log_record["tenant"] = tenant

        env = os.getenv("ENVIRONMENT")
        if env is not None:
            log_record["env"] = env

        version = os.getenv("VERSION")
        if version is not None:
            log_record["version"] = version

        repository = os.getenv("REPOSITORY")
        if repository is not None:
            log_record["repository"] = repository

        if "trace_id" in log_record and log_record["trace_id"] == "0":
            log_record.pop("trace_id")

        if "span_id" in log_record and log_record["span_id"] == "0":
            log_record.pop("span_id")

        if "service_name" in log_record and not log_record["service_name"]:
            log_record.pop("service_name")

        if "trace_sampled" in log_record and log_record["trace_sampled"] == "0":
            log_record.pop("trace_sampled")

        return super().process_log_record(log_record)


class CustomLoggingFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return f"{datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(LOGGING_DATETIME_FORMAT)[:-3]}Z"


def set_formatter(handler: logging.Handler, log_mode: str = LOG_MODE):
    if log_mode == "JSON":
        handler.setFormatter(
            CustomJsonFormatter(
                LOGGING_FORMAT,
                rename_fields={
                    "levelname": "level",
                    "asctime": "time",
                    # NOTE: rename to align with the package used by cockpit (otel js auto-instrumentation for pino)
                    "otelSpanID": "span_id",
                    "otelTraceID": "trace_id",
                    "otelTraceSampled": "trace_sampled",
                    "otelServiceName": "service_name",
                }
            )
        )
    else:
        handler.setFormatter(CustomLoggingFormatter(LOGGING_FORMAT))


class AlloyStreamHandler(logging.StreamHandler):
    def __init__(self, *args, log_mode=LOG_MODE, **kwargs):
        super().__init__(*args, **kwargs)
        set_formatter(self, log_mode=log_mode)


def configure_new_logger(*args, **kwargs) -> logging.Logger:
    return configure_logger(*args, **kwargs)


def configure_root_logger(
    log_mode: str = LOG_MODE,
    capture_warnings: bool = True,
    skip_handler_types: tuple[type[logging.Handler]] | None = None,
    skip_handler_names: tuple[str] | tuple[()] | None = None,
    skip_handler_modules: tuple[str] | tuple[()] | None = ("airflow.utils.log.logging_mixin",),
    skip_handler_formatter_modules: tuple[str] | tuple[()] | None = ("celery",),
):
    """
    Configure the root logger and return it.
    """
    logging.captureWarnings(capture_warnings)
    if not logging.root.handlers:
        handler = AlloyStreamHandler(log_mode=log_mode)
        logging.root.addHandler(handler)
    else:
        # NOTE: detecting celery handlers is pretty fragile, since we need to rely on the formatter module name
        patched_handlers = []
        for _handler in logging.root.handlers:
            if (
                isinstance(_handler, skip_handler_types or tuple())
                or _handler.__class__.__name__ in (skip_handler_names or tuple())
                or any(shm in _handler.__class__.__module__ for shm in (skip_handler_modules or tuple()))
                or any(
                    shfm in _handler.formatter.__class__.__module__
                    for shfm in (skip_handler_formatter_modules or tuple())
                )
            ):
                continue
            # in case we change a handler which is not an AlloyStreamHandler or a NullHandler or
            # a LambdaLoggerHandler or a pytest handler let's log a warning
            if (
                not isinstance(_handler, AlloyStreamHandler)
                and not isinstance(_handler, logging.NullHandler)
                and _handler.__class__.__name__ != "LambdaLoggerHandler"
                and "_pytest" not in _handler.__class__.__module__
            ):
                logging.warning(
                    f"Found an handler of type {_handler.__class__.__name__} in the root logger. "
                    "Changing the formatter of this handler may cause unexpected behavior."
                )
            set_formatter(_handler, log_mode=log_mode)
            patched_handlers.append(_handler)
        if len(patched_handlers) > 1:
            logging.warning(
                f"Found more than one handler in the root logger. "
                f"Changed the formatter of {len(patched_handlers)} handlers: {patched_handlers}"
            )


def configure_logger(
    log_name: str = LOG_NAME,
    log_mode: str = LOG_MODE,
    log_level: Union[str, int] = LOG_LEVEL,
    capture_warnings: bool = True,
    **kwargs,
) -> logging.Logger:
    """
    Configure the root logger and return a new logger with the given name.
    """
    configure_root_logger(log_mode=log_mode, capture_warnings=capture_warnings, **kwargs)
    new_logger = logging.getLogger(log_name)
    new_logger.setLevel(log_level)
    return new_logger


def configure_existing_loggers(
    log_level: Union[str, int] = LOG_LEVEL,
    log_name_filter: str | None = None,
) -> dict[logging.Logger, int]:
    """
    Configure all existing loggers to be the same (output as text/json, level) or
    configure only some specific 3rd party loggers (like urllib3 etc.) using log_name_filter.
    """
    # logging.captureWarnings(capture_warnings)
    prev_state = {}

    for log_name in logging.root.manager.loggerDict:
        if log_name_filter is not None and log_name_filter not in log_name:
            continue
        existing_logger = logging.getLogger(log_name)
        prev_state[existing_logger] = existing_logger.getEffectiveLevel()
        configure_existing_logger(existing_logger, log_level)
    return prev_state


def configure_existing_logger(
    existing_logger: logging.Logger,
    log_level: Union[str, int] = LOG_LEVEL,
) -> None:
    """
    (Re-)Configure an existing logger.
    """
    existing_logger.setLevel(log_level)


@contextmanager
def change_logging_level(logger: logging.Logger, log_level: Union[str, int]):
    old_level = logger.getEffectiveLevel()
    logger.setLevel(log_level)
    try:
        yield
    finally:
        logger.setLevel(old_level)


# The default utility logger.
logger = configure_logger(__name__)


def excepthook(exc_type, exc_value, traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, traceback)
        return

    logger.error(f"Uncaught exception: {exc_type.__name__}: {exc_value}", exc_info=(exc_type, exc_value, traceback))


if LOG_SET_EXCEPTHOOK.lower() in {"true", "1"}:
    logger.debug("Setting excepthook")
    sys.excepthook = excepthook
elif LOG_SET_EXCEPTHOOK.lower() not in {"false", "0"}:
    logger.warning(f"LOG_SET_EXCEPTHOOK is set to an invalid value: {LOG_SET_EXCEPTHOOK}")
