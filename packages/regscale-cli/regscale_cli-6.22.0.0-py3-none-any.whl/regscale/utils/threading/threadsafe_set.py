"""
This module contains the ThreadSafeSet class, which is a thread-safe set.
"""

from threading import RLock
from typing import Generic, Iterator, Optional, Set, TypeVar

T = TypeVar("T")  # Declare type variable


class ThreadSafeSet(Generic[T]):
    """
    ThreadSafeSet class to create a thread-safe set.
    """

    def __init__(self, initial_set: Optional[Set[T]] = None):
        """
        Initialize a new ThreadSafeSet

        :param Set[T]|None initial_set: Optional initial set to populate the ThreadSafeSet
        """
        self._set: Set[T] = set(initial_set) if initial_set is not None else set()
        self._lock = RLock()

    def add(self, item: T) -> None:
        """
        Add an item to the set

        :param T item: Item to add to the set
        :rtype: None
        """
        with self._lock:
            self._set.add(item)

    def remove(self, item: T) -> None:
        """
        Remove an item from the set

        :param T item: Item to remove from the set
        :raises KeyError: If the item is not found
        :rtype: None
        """
        with self._lock:
            self._set.remove(item)

    def discard(self, item: T) -> None:
        """
        Remove an item from the set if it exists

        :param T item: Item to remove from the set
        :rtype: None
        """
        with self._lock:
            self._set.discard(item)

    def __len__(self) -> int:
        """
        Get the length of the set

        :return: The length of the set
        :rtype: int
        """
        with self._lock:
            return len(self._set)

    def __iter__(self) -> Iterator[T]:
        """
        Return an iterator over the set

        :return: An iterator over the set
        :rtype: Iterator[T]
        """
        with self._lock:
            return iter(self._set.copy())

    def __contains__(self, item: T) -> bool:
        """
        Check if an item is in the set

        :param T item: Item to check
        :return: True if the item is in the set, False otherwise
        :rtype: bool
        """
        with self._lock:
            return item in self._set

    def clear(self) -> None:
        """
        Clear the set

        :rtype: None
        """
        with self._lock:
            self._set.clear()

    def union(self, other: Set[T]) -> Set[T]:
        """
        Return the union of this set and another

        :param Set[T] other: Other set to union with
        :return: A new set containing the union
        :rtype: Set[T]
        """
        with self._lock:
            return self._set.union(other)

    def intersection(self, other: Set[T]) -> Set[T]:
        """
        Return the intersection of this set and another

        :param Set[T] other: Other set to intersect with
        :return: A new set containing the intersection
        :rtype: Set[T]
        """
        with self._lock:
            return self._set.intersection(other)
