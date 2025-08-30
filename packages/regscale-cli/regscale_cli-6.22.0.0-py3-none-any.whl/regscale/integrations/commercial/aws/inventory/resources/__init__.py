"""AWS resource collectors package."""

from .compute import ComputeCollector
from .storage import StorageCollector
from .database import DatabaseCollector
from .networking import NetworkingCollector
from .security import SecurityCollector
from .integration import IntegrationCollector
from .containers import ContainerCollector

__all__ = [
    "ComputeCollector",
    "StorageCollector",
    "DatabaseCollector",
    "NetworkingCollector",
    "SecurityCollector",
    "IntegrationCollector",
    "ContainerCollector",
]
