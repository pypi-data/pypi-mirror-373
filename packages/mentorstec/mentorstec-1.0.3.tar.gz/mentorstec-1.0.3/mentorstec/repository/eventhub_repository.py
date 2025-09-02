from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Para Python < 3.9, usar backport
    from backports.zoneinfo import ZoneInfo


class EventHubRepository(ABC):
    """
    Repository abstrato para EventHub

    Define a interface padrão que todas as implementações de EventHub devem seguir.
    """

    @abstractmethod
    def event_handler(self, **kwargs: Any) -> None:
        """
        Processa e envia o evento para o provedor específico

        Args:
            **kwargs: Dados do evento conforme build_payload()
        """
        pass

    @classmethod
    def build_payload(cls, **kwargs: Any) -> Dict[str, Any]:
        """
        Constrói o payload padrão do evento

        Args:
            **kwargs: Campos do evento com valores opcionais:
                - project: Nome do projeto (default: "undefined")
                - layer: Camada da aplicação (default: "undefined")
                - message: Mensagem do evento (default: "")
                - obs: Observações adicionais (default: "")
                - timestamp: Timestamp ISO (default: utcnow)
                - event_type: Tipo do evento (default: "UNDEFINED")
                - object: Objeto/contexto relacionado (default: "")
                - tags: Lista de tags (default: [])

        Returns:
            Dict com estrutura padronizada do evento
        """
        return {
            "project": kwargs.get("project", "undefined"),
            "layer": kwargs.get("layer", "undefined"),
            "message": kwargs.get("message", ""),
            "obs": kwargs.get("obs", ""),
            "timestamp": kwargs.get(
                "timestamp",
                datetime.now(ZoneInfo("America/Sao_Paulo")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            ),
            "event_type": kwargs.get("event_type", "UNDEFINED").upper(),
            "object": kwargs.get("object", ""),
            "tags": kwargs.get("tags", []),
        }
