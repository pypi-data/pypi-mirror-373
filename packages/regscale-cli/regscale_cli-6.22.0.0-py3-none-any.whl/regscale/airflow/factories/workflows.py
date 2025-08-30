"""Provide workflow factory functions."""

from typing import Union
from uuid import uuid4

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

from regscale.airflow.sensors.sql import build_sql_sensor_xcon
from regscale.airflow.sessions.sql.sql_server_queries import (
    CHECK_IF_COMPLETED_SQL_QUERY,
)
from regscale.airflow.tasks.branches import tri_branch_func
from regscale.airflow.tasks.workflows import (
    build_complete,
    build_rejected,
)


def workflow_listener_factory(
    workflow_name: str,
    dag: DAG,
    next_step_name: str,
    next_step: Union[TaskGroup, PythonOperator],
    unique: bool = False,
    **kwargs,
) -> TaskGroup:
    """Build a workflow listener task group

    :param str workflow_name: the name of the workflow
    :param DAG dag: the DAG to add the task group to
    :param str next_step_name: the name of the next step
    :param Union[TaskGroup, PythonOperator] next_step: the next step
    :param dict kwargs: keyword arguments to pass to the task group
    :param bool unique: whether to make the task group unique
    :return: a workflow listener task group
    :rtype: TaskGroup
    """
    uid = None
    if unique:
        uid = str(uuid4())[:8]
        name = f"{workflow_name}-{uid}"
    else:
        name = f"{workflow_name}"
    with TaskGroup(
        group_id=name,
        dag=dag,
        **kwargs,
    ) as task_group:
        # You need to have this factory upstream from the is_completed_listener_name
        is_completed_listener_name = f"{name}-listener"
        complete_name = f"{name}-complete"
        # this task needs to be the name of the next listener
        rejected_name = f"{name}-rejected"
        is_completed = build_sql_sensor_xcon(
            sql=CHECK_IF_COMPLETED_SQL_QUERY,
            step_name=next_step_name,
            name=is_completed_listener_name,
            dag=dag,
        )
        complete = build_complete(uid=uid or complete_name, dag=dag)
        rejected = build_rejected(uid=uid or rejected_name, dag=dag)
        decision = PythonOperator(
            task_id=f"decision-{uid or name}",
            python_callable=tri_branch_func,
            op_kwargs={
                "pull_from": is_completed_listener_name,
                "negative_task": rejected_name,
                "neutral_task": next_step,  # neutral_step_name in DAG
                "positive_task": complete_name,
            },
            dag=dag,
        )

        is_completed >> decision >> [complete, next_step, rejected]

        return task_group
