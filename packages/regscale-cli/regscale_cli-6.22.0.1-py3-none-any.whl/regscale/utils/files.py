"""Provide functions for dealing with files."""

import os
from pathlib import Path
from tempfile import gettempdir
from types import TracebackType
from typing import Union, TextIO, Optional, Type


def print_file_contents(file_path: Union[str, Path]) -> None:
    """
    Print a file's contents to the console.

    :param Union[str, Path] file_path: a string or Path object
    :rtype: None
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if file_path.is_file():
        print(f'File "{file_path}" found!')
        print(file_path.read_text(encoding="utf-8"))


def print_current_directory(print_yaml: bool = False) -> None:
    """
    Print the contents of the current directory and its path

    :param bool print_yaml: should the contents of the yaml file be printed, defaults to False
    :rtype: None
    """
    current_dir = os.getcwd()
    print(f"Current Working Directory: {current_dir}")
    if print_yaml:
        init_file = os.path.join(current_dir, "init.yaml")
        print_file_contents(init_file)


class CustomTempFile:
    """
    A context manager for creating temporary files

    :param Union[str, Path] filename: the name of the file
    :param bool delete: should the file be deleted when the context is exited? (default: True)
    """

    def __init__(self, filename: Union[str, Path], delete: bool = True):
        self.temp_dir = gettempdir()
        self.temp_filename = os.path.join(self.temp_dir, filename)
        self.delete = delete
        self.temp_file = None

    def __enter__(self) -> TextIO:
        """
        Open the file with read/write permissions

        :return: the file object
        :rtype: TextIO
        """
        self.temp_file = open(self.temp_filename, "w+")
        return self.temp_file

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        """
        Close the file

        :param Optional[Type[BaseException]] exc_type: The exception type
        :param Optional[BaseException] exc_val: The exception value
        :param Optional[TracebackType] exc_tb: The traceback
        :rtype: None
        """
        # Close the file
        if self.temp_file:
            self.temp_file.close()

        # Optionally, delete the file
        if self.delete:
            os.remove(self.temp_filename)
