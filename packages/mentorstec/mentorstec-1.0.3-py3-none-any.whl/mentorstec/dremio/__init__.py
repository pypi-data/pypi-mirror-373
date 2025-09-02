"""
Mentorstec Dremio - Módulo independente para data virtualization

Estrutura simplificada usando Repository Pattern:
- DremioRepository: Interface abstrata
- Dremio: Implementação concreta com método genérico execute_sql()
"""

from .dremio import Dremio

__all__ = [
    "Dremio",
]
