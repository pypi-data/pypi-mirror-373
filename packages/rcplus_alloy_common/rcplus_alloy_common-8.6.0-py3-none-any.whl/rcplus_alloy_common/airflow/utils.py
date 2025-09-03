import os
import sys
import json
from typing import Any, TypedDict
from enum import Enum

import yaml

from airflow.datasets import Dataset

from rcplus_alloy_common.logging import logger
from rcplus_alloy_common.airflow.observability import (
    slack_alert_on_retry,
    slack_alert_on_failure,
    publish_task_metrics_callback,
)
from rcplus_alloy_common.multitenancy import TenantConfig


class AlloyTagServiceName(str, Enum):
    DBT_ECS = "dbt-ecs"
    ECS = "ecs"
    GLUE = "glue"
    LAMBDA = "lambda"
    SYSTEMD = "systemd"
    UNKNOWN = "unknown"


class EnvironmentVariable(TypedDict):
    name: str
    value: str


class AlloyProject:
    """Load Alloy project configuration.

    The convention is to put the project.yml in the same directory as the dag script.
    """
    def __init__(self, depth=2) -> None:
        self._depth = depth
        self.config = self._load_project_config()
        self.tenant_configs = self._load_tenant_configs()

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, value: int):
        self._depth = value
        self.config = self._load_project_config()

    def __getitem__(self, key):
        return self.config[key]

    def __contains__(self, key):
        return key in self.config

    def get(self, key, default=None):
        return self.config.get(key, default)

    def _get_fileloc(self):
        back = sys._getframe(self.depth + 1)  # pylint: disable=protected-access
        fileloc = back.f_code.co_filename if back else ""
        return fileloc

    def _load_project_config(self):
        fileloc = self._get_fileloc()
        config_filepath = os.path.join(os.path.dirname(fileloc), "project.yml")

        with open(config_filepath) as f:
            project = yaml.safe_load(f)
        return project

    def _load_tenant_configs(self) -> list[TenantConfig]:
        fileloc = self._get_fileloc()
        # go back until we find the tenant_configs.json
        max_iters = 4
        for _ in range(max_iters):
            fileloc = os.path.dirname(fileloc)
            config_filepath = os.path.join(fileloc, "..", "tenant_configs.json")
            if os.path.exists(config_filepath):
                break
        try:
            with open(config_filepath) as f:
                config: list[dict[str, Any]] = json.load(f)
            return [TenantConfig(**tenant_obj) for tenant_obj in config]
        except FileNotFoundError:
            logger.warning("tenant_configs.json not found")
            return []

    def get_templated_var(self, variable_name, prefix=None):
        if prefix is None:
            prefix = self["software_component"]
        return f"{{{{ var.value.get('{prefix}/{variable_name}') }}}}"

    def get_dataset(
        self,
        task_id: str,
        dag_name: str,
        tenant: str | None = None,
        software_component: str | None = None
    ) -> Dataset:
        if software_component is None:
            software_component = self["software_component"]
        if tenant is not None:
            return Dataset(f"{self['project_id']}-{software_component}-{tenant}-{dag_name}-{task_id}")
        else:
            return Dataset(f"{self['project_id']}-{software_component}-{dag_name}-{task_id}")

    def make_dag_id(self, dag_id: str, tenant: str | None = None):
        dag_id_prefix = f"{self['project_id']}-{self['software_component']}"
        if tenant is not None and not isinstance(tenant, str):
            raise ValueError(f"Malformed tenant parameter. Expected `str` received `{tenant}`")

        if tenant:
            dag_id_prefix = f"{dag_id_prefix}-{tenant}"

        if not dag_id.startswith(dag_id_prefix):
            dag_id = f"{dag_id_prefix}-{dag_id}"

        return dag_id


def set_default_callbacks(default_args):
    """
    Set default callbacks for tasks.

    NOTE: It is better to have all callbacks as lists because it was adopted by Airflow relatively recently.
    """

    # NOTE: by default `on_success_callback` contains only `publish_task_metrics_callback`
    if "on_success_callback" not in default_args:
        default_args["on_success_callback"] = [publish_task_metrics_callback]
    elif isinstance(default_args["on_success_callback"], list):
        default_args["on_success_callback"] = (
            [x for x in default_args["on_success_callback"] if x is not publish_task_metrics_callback]
        )
        default_args["on_success_callback"] += [publish_task_metrics_callback]
    elif default_args["on_success_callback"] is not publish_task_metrics_callback:
        default_args["on_success_callback"] = [default_args["on_success_callback"], publish_task_metrics_callback]

    # NOTE: by default `on_retry_callback` contains only `slack_alert_on_retry`
    if "on_retry_callback" not in default_args:
        default_args["on_retry_callback"] = [slack_alert_on_retry]
    elif isinstance(default_args["on_retry_callback"], list):
        default_args["on_retry_callback"] = (
            [x for x in default_args["on_retry_callback"] if x is not slack_alert_on_retry]
        )
        default_args["on_retry_callback"] += [slack_alert_on_retry]
    elif default_args["on_retry_callback"] is not slack_alert_on_retry:
        default_args["on_retry_callback"] = [default_args["on_retry_callback"], slack_alert_on_retry]
    else:
        default_args["on_retry_callback"] = [default_args["on_retry_callback"]]

        # NOTE: by default `on_failure_callback` contains `slack_alert_on_failure` and `publish_task_metrics_callback`
    default_failure_callbacks = [slack_alert_on_failure, publish_task_metrics_callback]
    if "on_failure_callback" not in default_args:
        default_args["on_failure_callback"] = default_failure_callbacks
    elif isinstance(default_args["on_failure_callback"], list):
        default_args["on_failure_callback"] = [
            callback for callback in default_args["on_failure_callback"]
            if callback not in default_failure_callbacks
        ]
        default_args["on_failure_callback"] += default_failure_callbacks
    elif default_args["on_failure_callback"] not in default_failure_callbacks:
        default_args["on_failure_callback"] = [default_args["on_failure_callback"]] + default_failure_callbacks
    else:
        default_args["on_failure_callback"] = default_failure_callbacks

    return default_args
