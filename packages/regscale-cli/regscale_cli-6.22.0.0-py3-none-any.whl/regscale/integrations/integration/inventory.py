from abc import ABC, abstractmethod


class Inventory(ABC):
    def __init__(
        self,
        **kwargs,
    ):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def pull(self):
        """
        Pull inventory from an Integration platform into RegScale
        """
        pass
