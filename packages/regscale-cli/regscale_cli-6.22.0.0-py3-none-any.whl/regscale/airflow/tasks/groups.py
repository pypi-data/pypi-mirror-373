"""Define pre-made TaskGroups for usage across DAGs."""

from uuid import uuid4

from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

from airflow import AirflowException, DAG
from regscale.airflow.hierarchy import AIRFLOW_CLICK_OPERATORS as OPERATORS
from regscale.airflow.tasks.click import execute_click_command


def generate_name(name: str, tag: str = None) -> str:
    """Generate a unique name for a TaskGroup

    :param str name: the name of the TaskGroup
    :param str tag: a unique identifier for the TaskGroup
    :return: a unique name for the TaskGroup
    :rtype: str
    """
    if not tag:
        tag = str(uuid4())[:8]  # give the task group a unique name for tracking
    return f"{name}-{tag}"


def setup_task_group(
    dag: DAG,
    setup_tag: str = None,
) -> TaskGroup:
    """Create a TaskGroup for setting up the init.yaml and initialization of the DAG

    :param DAG dag: an Airflow DAG
    :param str setup_tag: a unique identifier for the task
    :return: a setup TaskGroup
    :rtype: TaskGroup
    """
    setup_name = generate_name("setup", setup_tag)
    with TaskGroup(setup_name, dag=dag) as setup:
        login = PythonOperator(
            task_id=f"login-{setup_tag}",
            task_group=setup,
            python_callable=execute_click_command,
            op_kwargs={
                "command": OPERATORS["login"]["command"],
                "token": '{{ dag_run.conf.get("token") }}',
                "domain": '{{ dag_run.conf.get("domain") }}',
            },
        )
        login
        return setup


def email_on_fail(task, **_):
    """
    Send an email if any of the upstream DAGs failed

    :param task: The task that has failed
    :return: The PythonOperator to send an email if any of the DAG tasks fail
    :rtype: TaskGroup
    """
    from regscale.core.app.application import Application
    from regscale.models import Email

    dag = task["dag"]
    config = task["params"]
    app = Application(config=config)

    if email := config.get("email"):
        email = Email(
            fromEmail="Support@RegScale.com",
            emailSenderId=app.config["userId"],
            to=email,
            subject=f"An Automated Job Has Failed: {config['jobName']} ({config['cadence']})",
            body=f"{dag.dag_id} with ID: {task['run_id']} job has failed. "
            + f"Please check the logs for more information: {config['job_url']}",
        )

        if email.send():
            app.logger.info(f"Email sent to {email} about {task['run_id']} job failure.")
        raise AirflowException("Failing task because one or more upstream tasks failed.")
