"""
Description: A class to handle reading and writing data to a pickle file in a thread-safe manner.
"""

import logging
import pickle
import threading
from os import PathLike
from pickle import UnpicklingError
from typing import Any, Generator

from pathlib import Path

logger = logging.getLogger(__name__)


class PickleFileHandler:
    """
    A class to handle reading and writing data to a pickle file in a thread-safe manner.

    :param PathLike[str] file_path: The path to the pickle file.
    """

    def __init__(self, file_path: PathLike[str]):
        self.file_path: Path = Path(file_path)
        self.lock = threading.Lock()

    def write(self, data: Any):
        """
        Writes data to the pickle file in a thread-safe manner.

        :param Any data: The data to be pickled and written to the file.
        """
        with self.lock:
            with open(self.file_path, "wb") as file:
                pickle.dump(data, file)

    def read(self) -> Generator[Any, None, None]:
        """
        Reads data from the pickle file in a thread-safe manner and returns a generator.

        :returns: A generator yielding the data read from the pickle file.
        :yields: Any -- The data read from the pickle file.
        """
        with open(self.file_path, "rb") as file:
            data = None
            try:
                data = pickle.load(file)
            except EOFError:
                pass
            except UnpicklingError as e:
                logger.debug("Error reading pickle file: %s", e)
            if data:
                if isinstance(data, list):
                    yield from data
                else:
                    yield data
