"""Generate PythonOperators based on a click.Command."""

from typing import Union, Optional

import click
from airflow.operators.python import PythonOperator

from airflow import DAG
from regscale.airflow.tasks.click import execute_click_command
from regscale.models.click_models import ClickCommand


def generate_operator_for_command(
    command: Union[click.Command, ClickCommand],
    command_name: Optional[str] = None,
    dag: Optional[DAG] = None,
    **kwargs: dict,
) -> PythonOperator:
    """Generate a PythonOperator for a Click Command

    :param Union[click.Command, ClickCommand] command: the command to generate the operator for
    :param Optional[str] command_name: optional command name to specify as task_id, defaults to None
    :param Optional[DAG] dag: an Optional airflow DAG to pass, defaults to None
    :param dict **kwargs: additional named parameters to pass to PythonOperator
    :return: a PythonOperator configured to execute the Click Command
    :rtype: PythonOperator
    """
    if isinstance(command, click.Command):
        command = ClickCommand.from_command(command)
    return PythonOperator(
        task_id=command_name or command.name,
        python_callable=execute_click_command,
        op_kwargs={"command": command.callback},
        dag=dag,
        **kwargs,
    )
