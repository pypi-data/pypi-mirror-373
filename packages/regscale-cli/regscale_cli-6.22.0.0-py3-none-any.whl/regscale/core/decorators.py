"""
Decorators for the regscale package
"""

from typing import Any, Type, Dict


def singleton(cls: Type[Any]) -> Type[Any]:
    """
    Singleton decorator to ensure a class only has one instance.

    :param Type[Any] cls: The class to be decorated as a singleton.
    :return: The singleton instance of the class.
    :rtype: Type[Any]
    """
    instances: Dict[Type[Any], Any] = {}

    def get_instance(*args: Any, **kwargs: Any) -> Any:
        """
        Get the singleton instance of the class.

        :param Any *args: Positional arguments to instantiate the class.
        :param Any **kwargs: Keyword arguments to instantiate the class.
        :return: The singleton instance of the class.
        :rtype: Any
        """
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance  # type: ignore
