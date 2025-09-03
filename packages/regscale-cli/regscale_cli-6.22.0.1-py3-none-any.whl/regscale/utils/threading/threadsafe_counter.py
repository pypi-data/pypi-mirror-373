"""
This module contains the ThreadSafeCounter class, which is a thread-safe counter.
"""

import threading


class ThreadSafeCounter:
    """
    Class to create a thread-safe counter
    """

    def __init__(self):
        self.value: int = 0
        self._lock = threading.Lock()

    def increment(self) -> int:
        """
        Increment the counter by 1

        :return: The new value of the counter after incrementing
        :rtype: int
        """
        with self._lock:
            self.value += 1
            return self.value

    def decrement(self) -> int:
        """
        Decrement the counter by 1

        :return: The new value of the counter after decrementing
        :rtype: int
        """
        with self._lock:
            self.value -= 1
            return self.value

    def set(self, value: int) -> None:
        """
        Set the counter to a value

        :param int value: Value to set the counter to
        :rtype: None
        """
        with self._lock:
            self.value = value
