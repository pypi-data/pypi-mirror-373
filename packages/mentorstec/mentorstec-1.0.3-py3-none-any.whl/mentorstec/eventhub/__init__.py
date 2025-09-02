"""
Mentorstec EventHub - Módulo independente para centralized event logging

Estrutura usando Repository Pattern:
- EventHubRepository: Interface abstrata
- EventHubClient: Cliente principal para gerenciar eventos
- send_event: Decorator simples e eficiente para logging automático
"""

from .event_hub import send_event
from .event_hub_client import EventHubClient

__all__ = [
    "EventHubClient",
    "send_event",
]
