"""Connector Types Enum"""

from enum import Enum


class ConnectorType(str, Enum):
    """Different ConnectorTypes"""

    Assets = "assets"
    Edr = "edr"
    Hooks = "hooks"
    Identity = "identity"
    Notifications = "notifications"
    Siem = "siem"
    Sink = "sink"
    Storage = "storage"
    Ticketing = "ticketing"
    Vulnerabilities = "vulnerabilities"

    def __str__(self):
        """Return the value of the Enum"""
        return self.value
