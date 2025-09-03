from abc import abstractmethod
from regscale.core.app.application import Application


class Integration(Application):
    """
    Base class for all integrations
    """

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __str__(self):
        return f"{self.__class__.__name__}"

    @abstractmethod
    def authenticate(self, **kwargs):
        """
        Authenticate to the integration
        """
        pass
