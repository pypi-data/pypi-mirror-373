"""Tasks for the workflows to do the following"""

from airflow import DAG
from airflow.operators.python import PythonOperator

from regscale.airflow.tasks.states import mark_dag_run_as_success, fail_dag_run


def build_complete(uid: str, dag: DAG) -> PythonOperator:
    """Build a complete task

    :param str uid: a unique identifier for the task
    :param DAG dag: the DAG to add the task to
    :return: a complete task
    :rtype: PythonOperator
    """
    return PythonOperator(
        task_id=uid,
        python_callable=mark_dag_run_as_success,
        dag=dag,
    )


def build_rejected(uid: str, dag: DAG) -> PythonOperator:
    """Reject the workflow

    :param str uid: a unique identifier for the task
    :param DAG dag: the DAG to add the task to
    :return: a rejected task
    :rtype: PythonOperator
    """
    return PythonOperator(
        task_id=uid,
        python_callable=fail_dag_run,
        dag=dag,
    )
