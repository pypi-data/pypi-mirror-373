__all__ = [
    "is_valid_metric",
    "make_single_metric",
    "publish_metrics_async",
    "publish_metrics_sync",
]

import asyncio
from asyncio import Future
from datetime import datetime
from functools import partial
from typing import Union, List

from jsonschema import validate, ValidationError

from rcplus_alloy_common.constants import (
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_RETRY_COUNT,
    ENV_TAG,
    GRAPHITE_API_ENDPOINT,
    GRAPHITE_API_KEY,
    GRAPHITE_API_USER,
    METRIC_SCHEMA,
    PROJECT_TAG,
    REPOSITORY_TAG,
)
from rcplus_alloy_common.logging import logger
from rcplus_alloy_common.retry import get_request_retry_session


def make_single_metric(  # noqa: PLR0912
        name: str,
        value: Union[int, float],
        interval: int = 3600,
        timestamp: int = 0,
        env_tag: str | None = None,
        project_tag: str | None = None,
        repository_tag: str | None = None,
        extra_tags: List[str] | None = None,
        tenant: str | None = None,
) -> dict:
    """
    Helper function to construct a new single metric dict.
    The env_tag, project_tag, repository_tag are the explicit env, project, repository tag values.
    The extra_tags is a list of "key=value" extra tag strings which also can include the explicit tags.
    """
    tags_list = []
    extra_tags = extra_tags or []

    # Find env, project and repository explicit tags in extra_tags
    extra_env = list(filter(lambda tag: tag.startswith("env="), extra_tags))
    extra_project = list(filter(lambda tag: tag.startswith("project="), extra_tags))
    extra_repository = list(filter(lambda tag: tag.startswith("repository="), extra_tags))

    if env_tag:
        # if the env tag was set explicitly then clean anything related to env in extra_tags
        for _value in extra_env:
            extra_tags.remove(_value)
        # add the explicit env value
        tags_list.append(f"env={env_tag}")
    elif not extra_env and ENV_TAG:
        # if no explicit env value provided and no env tag in extra_tags then use ENV_TAG ENV var
        tags_list.append(f"env={ENV_TAG}")

    if project_tag:
        # if the project tag was set explicitly then clean anything related to project in extra_tags
        for _value in extra_project:
            extra_tags.remove(_value)
        # add the explicit project value
        tags_list.append(f"project={project_tag}")
    elif not extra_project and PROJECT_TAG:
        # if no explicit project value provided and no project tag in extra_tags then use PROJECT_TAG ENV var
        tags_list.append(f"project={PROJECT_TAG}")

    if repository_tag:
        # if the repository tag was set explicitly then clean anything related to repository in extra_tags
        for _value in extra_repository:
            extra_tags.remove(_value)
        # add the explicit repository value
        tags_list.append(f"repository={repository_tag}")
    elif not extra_repository and REPOSITORY_TAG:
        # if no explicit repository value provided and no repository tag in extra_tags then use REPOSITORY_TAG ENV var
        tags_list.append(f"repository={REPOSITORY_TAG}")

    # merge collected explicit tags and extra_tags
    tags_list += extra_tags

    if tenant is not None:
        if not isinstance(tenant, str):
            raise ValueError(f"Expecting tenant value as string received {tenant} {type(tenant)}")

        # Check the tags list for existing tenant tag
        for tag in tags_list:
            if tag.startswith("tenant="):
                logger.warning(f"The provided tenant value `{tenant}` overrides the value already set in tags `{tag}`")
                tags_list.remove(tag)
                break

        # The explicit tenant parameter has more priority than the previously set tag
        tags_list.append(f"tenant={tenant}")

    return {
        "name": name,
        "value": value,
        "interval": interval,
        "time": timestamp or int(datetime.utcnow().timestamp()),
        "tags": tags_list,
    }


def is_valid_metric(metric: dict) -> bool:
    """
    Validate a metric dict against metric schema.
    """
    try:
        validate(metric, schema=METRIC_SCHEMA)
        return True
    except ValidationError as ex:
        error = str(ex).split("\n", maxsplit=1)[0]
        logger.error(f"Failed to validate metric because of `{error}`.")
        return False


def publish_metrics_sync(
        metrics: Union[dict, list],
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        request_timeout: int = DEFAULT_REQUEST_TIMEOUT,
        api_key: str | None = GRAPHITE_API_KEY,
        api_user: str = GRAPHITE_API_USER,
        api_endpoint: str = GRAPHITE_API_ENDPOINT,
) -> None:
    """
    Publish metrics to Grafana synchronous (blocking) way.
    """
    if any(param is None for param in (api_key, api_user, api_endpoint)):
        logger.warning("Skip metrics publishing because some of parameters api_key, api_user, api_endpoint are None.")
        return

    if isinstance(metrics, dict):
        metrics = [metrics]

    metrics = [metric for metric in metrics if is_valid_metric(metric)]
    if not metrics:
        logger.warning("No valid metrics to publish found after the validation.")
        return

    headers = {
        "Authorization": f"Bearer {api_user}:{api_key}"
    }

    try:
        session = get_request_retry_session(retry_count=retry_count, retry_backoff=retry_backoff)
        response = session.post(api_endpoint, headers=headers, json=metrics, timeout=request_timeout)
        response.raise_for_status()
        logger.info("Metrics published successfully.")
        return

    # Many errors are possible here, I tested at least ConnectTimeout, HTTPError, RetryError, ConnectionError.
    # I"m not sure if this is a complete list, so I decided to capture everything because metrics publishing failures
    # must not disrupt any code executions.
    except Exception as ex:  # pylint: disable=broad-except
        logger.error(f"Failed to publish metrics in {retry_count} attempts because of `{ex}`.")


def publish_metrics_async(
        metrics: Union[dict, list],
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        request_timeout: int = DEFAULT_REQUEST_TIMEOUT,
        api_key: str | None = GRAPHITE_API_KEY,
        api_user: str = GRAPHITE_API_USER,
        api_endpoint: str = GRAPHITE_API_ENDPOINT,
) -> Future:
    """
    Publish metrics to Grafana asynchronous (non-blocking) way.
    This function will continue to work until the end even if the main thread which called it is finished.
    """
    loop = asyncio.get_event_loop()
    publish_metrics_sync_partial = partial(
        publish_metrics_sync, metrics, retry_count, retry_backoff, request_timeout,
        api_key, api_user, api_endpoint,
    )
    return loop.run_in_executor(None, publish_metrics_sync_partial)
