from airflow.datasets import Dataset

from rcplus_alloy_common.version import head_ref
from rcplus_alloy_common.airflow.utils import set_default_callbacks, AlloyProject


def alloyize(cls):
    """Alloyize a BaseOperator or BaseSensor with default Alloy arguments.

    Usage:
        ```
        from airflow.operators.bash_operator import BashOperator
        from rcplus_alloy_common.airflow.operators import alloyize

        @alloyize
        class AlloyBashOperator(BashOperator):
            pass
        ```
    """
    orig_init = cls.__init__
    orig_execute = cls.execute

    def get_alloy_tag(self, app_specific_identifier: str) -> str:
        dag = self.get_dag()
        if dag is None:
            raise RuntimeError(
                "Dag is not initialized, please call `self.get_alloy_tag` after instantiating the task"
            )
        if self.project is None:
            raise RuntimeError(
                "AlloyProject is not initialized, please call `self.get_alloy_tag` after instantiating the task"
            )
        parts = [
            self.project.config.get("project_id", "unknown"),
            self.service_name,
            self.project.config.get("software_component", "unknown"),
            "-".join(
                filter(
                    None,
                    [
                        dag.tenant if hasattr(dag, "tenant") and dag.tenant else None,
                        dag.base_dag_id if hasattr(dag, "base_dag_id") else dag.dag_id,
                        app_specific_identifier.replace(
                            f"{self.project['project_id']}-{self.project['software_component']}-", ""
                        ),
                    ]
                )
            )
        ]
        return ".".join(parts)

    def new_init(self, *args, default_args=None, **kwargs):
        self.project_depth = self.project_depth if hasattr(self, "project_depth") else 4
        if default_args is None:
            default_args = {}
        default_args = set_default_callbacks(default_args)
        orig_init(self, *args, default_args=default_args, **kwargs)

        # add default outlet if not already added
        dag_id = self.get_dag().dag_id
        dataset_uri = f"{dag_id}-{self.task_id}"
        outlets = any(
            True for outlet in self.get_outlet_defs() if isinstance(outlet, Dataset) and Dataset.uri == dataset_uri
        )

        # __init__, _load_project_config, new_init, apply_defaults, dag_fun
        self.project = AlloyProject(self.project_depth)

        if not outlets:
            self.add_outlets([Dataset(dataset_uri)])

    def new_execute(self, *args, **kwargs):
        self.log.info(f"Running task `{self.task_id}` of dag `{self.dag_id}` with `rcplus_alloy_common@{head_ref}`")
        return orig_execute(self, *args, **kwargs)

    cls.__init__ = cls._apply_defaults(new_init)  # pylint: disable=protected-access
    cls.execute = new_execute
    cls.get_alloy_tag = get_alloy_tag
    return cls
