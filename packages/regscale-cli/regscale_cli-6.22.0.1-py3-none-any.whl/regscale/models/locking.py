"""Class to lock a file to prevent concurrent access to it."""

import os
import time
from types import TracebackType
from typing import Optional, Type


class FileLock:
    """
    Class to lock a file to prevent concurrent access to it

    :param str lock_file: File to lock, defaults to "results/xdist_lock.txt"
    :param bool skip_lock: Whether to skip the lock, defaults to False
    """

    lock_file: str
    lock_scope: str
    skip_lock: bool

    def __init__(self, lock_file: str = "results/xdist_lock.txt", skip_lock: bool = False):
        self.lock_file: str = lock_file
        self.lock_scope: str = f"{os.getpid()}".ljust(10, ".")
        self.skip_lock = skip_lock
        lock_folder = os.path.dirname(self.lock_file)
        if not os.path.isdir(lock_folder):
            os.makedirs(lock_folder)

    def __enter__(self) -> "FileLock":
        """
        Enter the context manager.

        :return: The FileLock object
        :rtype: FileLock
        """
        if not self.skip_lock:
            self.acquire_lock()
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        """
        Exit the context manager.

        :param Optional[Type[BaseException]] exc_type: The exception type
        :param Optional[BaseException] exc_val: The exception value
        :param Optional[TracebackType] exc_tb: The traceback
        :rtype: None
        """
        if not self.skip_lock:
            self.release_lock()

    def lock_contents(self) -> str:
        """
        Get the contents of the lock file.

        :return: Contents of the lock file as a string
        :rtype: str
        """
        with open(self.lock_file, "r") as lockfile:
            contents = lockfile.read()
        return contents

    def acquire_lock(self) -> None:
        """
        Acquire the lock.

        :rtype: None
        """
        try:
            while os.path.isfile(self.lock_file):
                # Another process is holding the lock. Waiting to acquire...
                time.sleep(0.1)
            # Create the lock file with the pid inside
            with open(self.lock_file, "w") as lockfile:
                lockfile.write(f"{self.lock_scope}")
            # Read the lock file to make sure the contents is ours
            with open(self.lock_file, "r") as lockfile:
                contents = lockfile.read()
            # If the contents is not ours, race condition -> back to square one
            if contents != f"{self.lock_scope}":
                self.acquire_lock()
        except Exception:
            self.acquire_lock()

    def release_lock(self) -> None:
        """
        Release the lock.

        :rtype: None
        """
        if os.path.isfile(self.lock_file):
            with open(self.lock_file, "r") as lockfile:
                scope = str(lockfile.read().strip())

            if scope == str(self.lock_scope):
                os.remove(self.lock_file)  # Lock released
            else:
                pass  # Lock can only be released by {self.lock_scope}
