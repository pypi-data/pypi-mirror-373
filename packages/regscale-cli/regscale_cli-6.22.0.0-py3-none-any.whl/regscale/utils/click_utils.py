"""Provide utilities for interacting with click Objects."""

from typing import Any, Dict, Optional, Union

import click


def process_click_group(
    group: Union[click.Group, click.Command],
    prefix: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process a click group into a dictionary

    :param Union[click.Group, click.Command] group: a click.Group or click.Command to extract info from
    :param Optional[str] prefix: an optional prefix to name the application, defaults to `group.name`
    :return: a dictionary of the click group
    :rtype: Dict[str, Any]
    """
    prefix = f"{group.name}" if prefix is None else f"{prefix}__{group.name}"
    cmd_dict = {
        "group": group,
        "group_name": prefix,
    }
    for cmd_name, cmd in group.commands.items():
        new_prefix = f"{prefix}__{cmd_name}"
        if isinstance(cmd, click.Group):
            cmd_dict[cmd_name] = process_click_group(cmd, new_prefix)
        elif isinstance(cmd, click.Command):
            cmd_dict[cmd_name] = process_command(cmd, new_prefix)
    return cmd_dict


def process_command(
    cmd: click.Command,
    cmd_name: str,
) -> Dict[str, Any]:
    """
    Process a click command into a dictionary

    :param click.Command cmd: a click.Command object
    :param str cmd_name: the name of the command
    :return: a dictionary of the click command
    :rtype: Dict[str, Any]
    """
    return {
        "cmd": cmd,
        "name": cmd_name,
        "params": {param.name: process_option(param) for param in cmd.params if isinstance(param, click.Option)},
        "callback": cmd.callback,
    }


def process_option(
    option: click.Option,
) -> Dict[str, Any]:
    """
    Process a click Option

    :param click.Option option: a click Option object
    :return: a dictionary of the click option
    :rtype: Dict[str, Any]
    """
    return {
        "option": option,
        "name": option.name,
        "default": option.default,
        "type": str(option.type),
        "prompt": option.prompt,
        "confirmation_prompt": option.confirmation_prompt,
        "is_flag": option.is_flag,
        "is_bool_flag": option.is_bool_flag,
        "count": option.count,
        "allow_from_autoenv": option.allow_from_autoenv,
        "expose_value": option.expose_value,
        "is_eager": option.is_eager,
        "callback": option.callback,
    }


def find_file_path_parameters(group: Union[click.Group, click.Command], prefix: str = None) -> dict:
    """
    Find all file path parameters in a click group

    :param Union[click.Group, click.Command] group: a click.Group or click.Command to extract info from
    :param str prefix: an optional prefix to name the application, defaults to `group.name`
    :return: a dictionary of file path parameters
    :rtype: dict
    """
    file_path_parameters = {}

    def add_to_dict(_key: str, _param: Any) -> None:
        """
        Helper function to add to the dictionary

        :param str _key: the key to add to the dictionary
        :param Any _param: the parameter to add to the dictionary
        :rtype: None
        """
        if _key not in file_path_parameters:
            file_path_parameters[_key] = []
        file_path_parameters[_key].append(_param)

    for cmd_name, cmd in group.commands.items():
        current_suffix = cmd_name if not prefix else f"{prefix}__{cmd_name}"

        if isinstance(cmd, click.Group):
            file_path_parameters[cmd_name] = find_file_path_parameters(cmd, prefix)
            inner_parameters = find_file_path_parameters(cmd, current_suffix)
            for key, values in inner_parameters.items():
                add_to_dict(key, values)
        else:
            for param in cmd.params:
                if isinstance(param.type, (click.Path, click.File)):
                    add_to_dict(current_suffix, param)
                elif "file" in param.name or "path" in param.name:
                    add_to_dict(current_suffix, param)
    return file_path_parameters
