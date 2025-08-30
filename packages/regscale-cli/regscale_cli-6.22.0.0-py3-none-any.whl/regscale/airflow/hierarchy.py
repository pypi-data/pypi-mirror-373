"""Generate a hierarchy for Airflow based on Click."""

from typing import Optional

from regscale.regscale import cli
from regscale.models.click_models import ClickCommand
from regscale.airflow.click_mixins import AirflowClickGroup

AIRFLOW_CLICK_GROUP = AirflowClickGroup.from_group(cli, prefix="regscale")
AIRFLOW_CLICK_OPERATORS = AIRFLOW_CLICK_GROUP.flatten_operator()


def iter_operators(operators: dict = AIRFLOW_CLICK_OPERATORS) -> dict:
    """Iterate over the operators and create a structured dict"""

    def _nested_dict(data: tuple, value: ClickCommand, result: dict = None) -> Optional[dict]:
        """Create a single dict from a nested dict."""
        if result is None:
            result = {}
        if len(data) > 1:
            key = data[0]
            if key not in result:
                result[key] = {}
            _nested_dict(data=data[1:], value=value, result=result[key])
        else:
            if data[0] in result:
                if isinstance(result[data[0]], dict):
                    result[data[0]].update(_make_platform_params(value))
                else:
                    result[data[0]] = [result[data[0]], _make_platform_params(value)]
            else:
                result[data[0]] = _make_platform_params(value)
        return result

    def _make_platform_params(command: ClickCommand) -> dict:
        """Create a dict from a command of what platform would need."""
        return {
            "name": command.name,
            "params": command.parameters,
            "parameters": {**command.params},
        }

    new_dict = {}
    for operator, op_dict in operators.items():
        if "__" in operator:
            operator_split = operator.split("__")
            new_dict = _nested_dict(data=operator_split, value=op_dict["command"], result=new_dict)
        else:
            if operator in new_dict:
                if isinstance(new_dict[operator], dict):
                    new_dict[operator].update(_make_platform_params(op_dict["command"]))
                else:
                    new_dict[operator] = [
                        new_dict[operator],
                        _make_platform_params(op_dict["command"]),
                    ]
            else:
                new_dict[operator] = _make_platform_params(op_dict["command"])
    return new_dict


AIRFLOW_CLI_HIERARCHY = iter_operators()


def get_command_params(cmd: str) -> list:
    """Get the parameters for a command

    :param str cmd: the command to get the parameters for
    :return: a list of parameters
    :rtype: list
    """
    cmd_split = cmd.split(" ")
    if len(cmd_split) == 1:
        return AIRFLOW_CLI_HIERARCHY[cmd_split[0]]["params"]
    elif len(cmd_split) == 2:
        return AIRFLOW_CLI_HIERARCHY[cmd_split[0]][cmd_split[1]]["params"]


def return_all_commands_and_params() -> dict:
    """Return all commands and parameters

    :return: a dict of commands and parameters
    :rtype: dict
    """
    dct = {}
    for operator in AIRFLOW_CLICK_OPERATORS:
        click_name = " ".join(operator.split("__"))
        dct[click_name] = {"parameters": AIRFLOW_CLICK_OPERATORS[operator]["command"].parameters}
