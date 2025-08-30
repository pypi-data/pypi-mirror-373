"""Initialize init.yaml and set shared keys as variables for the DAG."""

import logging
from pathlib import Path
from typing import Optional, Union

import yaml
from airflow.exceptions import AirflowException

from regscale.airflow.hierarchy import AIRFLOW_CLICK_OPERATORS as OPERATORS
from regscale.airflow.tasks.click import execute_click_command


def get_shared_keys(
    yaml_file_path: Optional[Union[str, Path]] = Path("init.yaml"),
    **context,
) -> list:
    """Get shared keys between init.yaml and a dag_run_conf obj

    :param Optional[Union[str, Path]] yaml_file_path: the Path to where the yaml file is expected, defaults to Path("init.yaml")
    :param context: context from Airflow DAG
    :return: a list of shared keys
    :rtype: list
    """
    if "dag_run" not in context:
        logging.error(f"context contains {list(context.keys())}")
    if isinstance(yaml_file_path, str):
        yaml_file_path = Path(yaml_file_path)
    yaml_keys = list(yaml.safe_load(yaml_file_path.open("r")).keys())
    dag_run_conf = context["dag_run"].conf
    if shared_keys := list(set(list(dag_run_conf.keys())).intersection(set(yaml_keys))):
        for key in shared_keys:
            logging.info(f"Shared key: {key}")
            value = dag_run_conf[key]
            temp_context = context | {"param": key, "val": value}
            execute_click_command(command=OPERATORS["config"]["command"], **temp_context)
    return shared_keys


def set_shared_config_values(shared_keys_task: str = None, **context: dict) -> None:
    """Get the shared keys and set them as a variable

    :param str shared_keys_task: the task_id of the task that will get the shared keys, defaults to None
    :param dict **context: context from Airflow DAG
    :raises AirflowException: if no dag_run or dag.conf found or setup_tag specified
    :rtype: None
    """
    logging.info(f"Initial shared_keys_task: {shared_keys_task=}")
    dag_run_conf = context["dag_run"].conf
    if not shared_keys_task:
        if "op_kwargs" not in dag_run_conf:
            raise AirflowException("No dag_run or dag.conf found or setup_tag specified")
        shared_keys_task = dag_run_conf["op_kwargs"]["shared_keys_task"]
    if shared_keys := context["ti"].xcom_pull(key="shared_keys", task_ids=shared_keys_task):
        for key in shared_keys:
            value = dag_run_conf[key]
            temp_context = context | {"param": key, "val": value}
            execute_click_command(command=OPERATORS["config"]["command"], **temp_context)
    else:
        logging.warning(f"No shared keys found: {shared_keys=}")
