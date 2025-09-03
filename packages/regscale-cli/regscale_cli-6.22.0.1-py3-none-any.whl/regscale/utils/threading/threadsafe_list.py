"""
This module contains the ThreadSafeList class, which is a thread-safe list.
"""

from threading import RLock
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")  # Declare type variable


class ThreadSafeList(Generic[T]):
    """
    ThreadSafeList class to create a thread-safe list.
    """

    def __init__(self, initial_list: Optional[List[T]] = None):
        """
        Initialize a new ThreadSafeList

        :param List[T]|None initial_list: Optional initial list to populate the ThreadSafeList
        """
        self._list: List[T] = list(initial_list) if initial_list is not None else []
        self._lock = RLock()

    def append(self, item: T) -> None:
        """
        Append an item to the list

        :param T item: Item to append to the list
        :rtype: None
        """
        with self._lock:
            self._list.append(item)

    def __getitem__(self, index: int) -> T:
        """
        Get an item from the list by index

        :param int index: Index of the item to get
        :return: The item at the specified index
        :rtype: T
        """
        with self._lock:
            return self._list[index]

    def __len__(self) -> int:
        """
        Get the length of the list

        :return: The length of the list
        :rtype: int
        """
        with self._lock:
            return len(self._list)

    def __iter__(self):
        """
        Return an iterator over the list

        :return: An iterator over the list
        :rtype: Iterator[T]
        """
        with self._lock:
            return iter(self._list.copy())

    def __list__(self) -> List[T]:
        """
        Convert ThreadSafeList to a regular list when list() is called

        :return: A copy of the internal list
        :rtype: List[T]
        """
        with self._lock:
            return self._list.copy()

    def remove(self, item: T) -> None:
        """
        Remove an item from the list

        :param T item: Item to remove from the list
        :rtype: None
        """
        with self._lock:
            self._list.remove(item)

    def clear(self) -> None:
        """
        Clear the list

        :rtype: None
        """
        with self._lock:
            self._list.clear()
