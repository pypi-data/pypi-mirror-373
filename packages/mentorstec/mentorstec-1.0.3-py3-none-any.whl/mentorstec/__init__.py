"""
Mentorstec - Centralized event logging and data platform with Repository Pattern
"""

__version__ = "1.0.3"

from .eventhub import EventHubClient, send_event
from .repository.eventhub_repository import EventHubRepository

__all__ = [
    "EventHubClient",
    "EventHubRepository",
    "send_event",
]

# Optional imports with graceful fallback
try:
    from .dremio import Dremio  # noqa: F401
    from .repository.dremio_repository import DremioRepository  # noqa: F401

    __all__.extend(["Dremio", "DremioRepository"])
except ImportError:
    pass

try:
    from .powerbi import PowerBi  # noqa: F401
    from .repository.powerbi_repository import PowerBiRepository  # noqa: F401

    __all__.extend(["PowerBi", "PowerBiRepository"])
except ImportError:
    pass
