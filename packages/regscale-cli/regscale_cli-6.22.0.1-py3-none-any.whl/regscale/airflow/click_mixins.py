"""Provide mixins for click models."""

from typing import Any
from uuid import uuid4
from airflow.operators.python import PythonOperator

from regscale.models.click_models import ClickGroup, ClickCommand
from regscale.airflow.tasks.click import execute_click_command


class AirflowOperatorMixin:
    """Mixin to the ClickGroup to flatten for an Airflow Operator"""

    def flatten_operator(self):
        """Flatten the group to a dictionary of PythonOperator objects"""
        operators_ = {}

        def _flatten_operator(group_: Any, prefix: str = "") -> dict:
            """Flatten the group to a dictionary of PythonOperator objects

            :param Any group_: a click.Group object to generate dags for
            :param str prefix: a string to prefix the command name with, defaults to ""
            :return: a dictionary of PythonOperator objects
            :rtype: dict
            """
            for name, cmd in group_.commands.items():
                if isinstance(cmd, ClickCommand):
                    cmd_name = cmd.name if prefix == "" else f"{prefix}__{cmd.name}"

                    def _make_operator_wrapper(
                        cmd_name_: str, cmd_: ClickCommand, suffix: str = None, **kwargs
                    ) -> PythonOperator:
                        """Create a wrapper to make a python operator."""
                        if suffix is None:
                            suffix = str(uuid4())[:8]
                        op_kwargs = None
                        if "op_kwargs" in kwargs:
                            op_kwargs = kwargs.pop("op_kwargs")
                        inputs = dict(
                            task_id=f"{cmd_name_}-{suffix}",
                            python_callable=execute_click_command,
                        )
                        if kwargs:
                            inputs |= kwargs
                        if op_kwargs:
                            inputs |= {"op_kwargs": {"command": cmd_, **op_kwargs}}
                        else:
                            inputs |= {"op_kwargs": {"command": cmd_}}
                        return PythonOperator(**inputs)

                    def _construct_lambda_wrapper(cmd_name_, cmd_, suffix: str = None, **kwargs):
                        return _make_operator_wrapper(cmd_name_=cmd_name_, cmd_=cmd_, suffix=suffix, **kwargs)

                    operators_[cmd_name] = {
                        "operator": PythonOperator(
                            task_id=cmd_name,
                            python_callable=execute_click_command,
                            op_kwargs={"command": cmd},
                        ),
                        "lambda": lambda cmd_name_=cmd_name, cmd_=cmd, suffix=None, **kwargs: _construct_lambda_wrapper(
                            cmd_name_=cmd_name_, cmd_=cmd_, suffix=suffix, **kwargs
                        ),
                        "command": cmd,
                    }
                elif isinstance(cmd, ClickGroup):
                    new_prefix = f"{prefix}__{cmd.group_name}" if prefix else cmd.group_name
                    _flatten_operator(cmd, new_prefix)

        _flatten_operator(self)
        return operators_


class AirflowClickGroup(AirflowOperatorMixin, ClickGroup):
    """Initialize the AirflowClickGroup object."""


# here's an example of how to generate the OPERATORS AirflowClickGroup class
if __name__ == "__main__":
    from regscale.regscale import cli

    group = AirflowClickGroup.from_group(cli, prefix="regscale")
    operators = group.flatten_operator()
