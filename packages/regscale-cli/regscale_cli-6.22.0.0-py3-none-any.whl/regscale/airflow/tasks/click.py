"""
This module contains functions to help Airflow execute a click command.
"""

import logging

from pydantic import ValidationError

from regscale.models.click_models import ClickCommand


def execute_click_command_old(command: ClickCommand, **context: dict) -> None:
    """Execute a click command

    :param ClickCommand command: a click command to execute
    :param dict **context: get dag_run from conf
    :raises ValueError: If required parameters are missing
    :rtype: None
    """
    dag_run = context["dag_run"]
    try:
        command_model = command.model_validate(dag_run.conf)
    except ValidationError as exc:
        # This will raise a ValidationError if any required parameters are missing
        raise ValueError(f"Invalid parameters for command '{command.name}': {str(exc)}") from exc
    valid_params = {name: value for name, value in command_model.dict().items() if name in command.params}
    command.callback(**valid_params)


def execute_click_command(command: ClickCommand, **context: dict) -> None:
    """Execute a click command

    :param ClickCommand command: a click command to execute
    :param dict **context: get dag_run from conf
    :raises ValueError: if no dag_run in context
    :rtype: None
    """
    # Get the dag_run from the context, or raise an error if it's not present
    dag_run = context.get("dag_run")
    parameters = command.parameters
    logging.debug(f"{parameters=}")
    op_kwargs = {param: context.get(param) for param in parameters}
    logging.debug(f"{op_kwargs.keys()}")
    if dag_run is None:
        raise ValueError("No dag_run in context")
    if dag_run.conf is None:
        dag_run.conf = {}
    # merge the dictionaries, giving precedence to op_kwargs
    command_defaults = command.defaults
    command_parameters = {**command_defaults, **dag_run.conf, **op_kwargs}
    for key, value in command_parameters.items():
        logging.debug(f"{key=}, {value=}")
    try:
        valid_params = {key: value for key, value in command_parameters.items() if key in command.parameters}
        logging.debug(f"{valid_params=}")
    except Exception as exc:
        # Catch any other exceptions that might be raised
        logging.error(f"Error parsing command {command.name} parameters: {str(exc)}")
        raise
    try:
        if dag_run.conf:
            from regscale.core.app.application import Application

            _ = Application(config=dag_run.conf)
            command.context_settings["CONFIG"] = dag_run.conf
        command.call(**valid_params)
    except UnboundLocalError as exc:
        if "callback_results" in str(exc):
            return None
        # Catch any exceptions that might be raised by the command callback
        logging.error(f"Error executing command '{command.name}': {str(exc)}")
        raise
    return None
