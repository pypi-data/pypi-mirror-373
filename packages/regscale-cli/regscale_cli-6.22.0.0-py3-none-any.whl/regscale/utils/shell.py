"""Define methods for use with CLI operations."""

from pprint import pprint
from shlex import split as shlexsplit
from subprocess import (
    check_output,
    Popen,
    PIPE,
    run,
    CalledProcessError,
)
from typing import Union


def strbyte(string: str, encoding: str = "utf-8") -> bytes:
    """Convert a string to bytes

    String will have `\n` append and converted to encoding.

    :param str string: the string to convert to bytes
    :param str encoding: the encoding to use, defaults to "utf-8"
    :return: a bytes object
    :rtype: bytes
    """
    if not string.endswith("\n"):
        string += "\n"
    return bytes(string, encoding=encoding)


# FIXME - this was useful early on -- will any of this be useful once the SDK is in-place?
def send_input_to_process_via_communicate(
    process: Popen,
    input_: str,
    encoding: str = "utf-8",
) -> tuple:
    """Send an input string to a process

    When passed a Popen process, send the input as an encoded bytes

    :param Popen process: the Popen process
    :param str input_: a string to send to the process
    :param str encoding: specify the encoding, defaults to "utf-8"
    :return: a tuple of stdout, stderr
    :rtype: tuple
    """
    return process.communicate(strbyte(string=input_, encoding=encoding))


def run_command(
    cmd: Union[str, list],
) -> bool:
    """Run a shell command

    Use python subprocess to run a command.

    :param Union[str, list] cmd: a list or string of commands to execute
    :raises CalledProcessError: if the command returns an error
    :return: a bool indicating success or failure
    :rtype: bool
    """
    if isinstance(cmd, str):
        cmd = shlexsplit(cmd)
    try:
        run(cmd, check=True, stdout=PIPE, stderr=PIPE)
        return True
    except CalledProcessError as exc:
        print(f"Command '{' '.join(cmd)}' returned with error (code {exc.returncode}): {exc.output.decode()}")
        raise exc


def run_command_and_store_output(
    cmd: Union[str, list],
    output: bool = False,
) -> str:
    """Run a shell command and store the output

    Runs a simple shell command and stores the output as a string.

    :param Union[str, list] cmd: a list or string of commands
    :param bool output: should pprint be used to display, defaults to False
    :return: A string of the command output
    :rtype: str
    """
    if isinstance(cmd, list):
        cmd = " ".join(cmd)
    cmd_output = check_output(cmd, shell=True, text=True)
    if output:
        pprint(f"Command output:\n{cmd_output}")
    return cmd_output


def send_input_to_process(
    process: Popen,
    input_: str,
) -> None:
    """Send an input string to a process

    When passed a Popen process, send the input as an encoded bytes

    :param Popen process: the Popen process
    :param str input_: a string to send to the process
    return: None
    """
    process.stdin.write(input_)
    process.stdin.flush()


def run_command_interactively(
    cmd: Union[str, list],
    inputs: Union[str, list],
    output: bool = False,
    include_error: bool = False,
) -> str:
    """Run a command by sending inputs

    Runs a shell command and send inputs to it

    :param Union[str, list] cmd: the initial command to invoke
    :param Union[str, list] inputs: a single str of inputs or a list to pass to the command interactively
    :param bool output: should output be pprinted? defaults to False
    :param bool include_error: should error be output as well?, default False
    :return: A string of the command output
    :rtype: str
    """
    if isinstance(cmd, list):
        cmd = " ".join(cmd)

    process = Popen(shlexsplit(cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)

    if isinstance(inputs, str):
        inputs = [inputs]

    for input_ in inputs:
        send_input_to_process(process=process, input_=input_)

    stdout, stderr = process.communicate()
    output_std = stdout or ""
    output_err = stderr or ""

    if output:
        pprint(output_std)
        if include_error:
            pprint(output_err)

    result = output_std
    if include_error:
        result += "\n" + output_err
    return result
