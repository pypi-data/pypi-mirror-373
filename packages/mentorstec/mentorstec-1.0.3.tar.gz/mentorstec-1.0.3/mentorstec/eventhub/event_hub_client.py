import functools
import os
import traceback
from typing import Any, Callable, Optional

from ..azure.azure_service_bus_repository import AzureServiceBusRepository
from ..repository.eventhub_repository import EventHubRepository


class EventHubClient:
    """
    Client principal para gerenciar eventos com diferentes provedores

    Args:
        project: Nome do projeto
        layer: Camada da aplicação (web, api, service, etc.)
        repository: Instância do repository para envio de eventos
    """

    def __init__(self, project: str, layer: str, repository: EventHubRepository):
        self.project = project
        self.layer = layer
        self.repository = repository

    @classmethod
    def create_azure_client(
        cls,
        project: str,
        queue_name: str,
        layer: str = "undefined",
        connection_string: Optional[str] = None,
    ) -> "EventHubClient":
        """
        Factory method para criar client com Azure Service Bus

        Args:
            project: Nome do projeto
            queue_name: Nome da fila (obrigatório)
            layer: Camada da aplicação
            connection_string: String de conexão (usa env AZURE_SERVICE_BUS_CONNECTION_STRING se não informado)

        Returns:
            EventHubClient configurado com Azure Service Bus

        Raises:
            ValueError: Se connection_string não for fornecida nem estiver no env
        """
        conn_str = connection_string or os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")

        if not conn_str:
            raise ValueError("Azure Service Bus connection string é obrigatória")

        repository = AzureServiceBusRepository(conn_str, queue_name)
        return cls(project, layer, repository)

    def send_event(
        self, event_type: str = "UNDEFINED", message: str = "", **kwargs: Any
    ) -> None:
        """
        Envia qualquer tipo de evento

        Args:
            event_type: Tipo do evento (INFO, ERROR, WARNING, etc.)
            message: Mensagem principal do evento
            **kwargs: Campos adicionais que serão incluídos no payload:
                - obs: Observações ou detalhes adicionais
                - object: Objeto/função/contexto relacionado
                - tags: Lista de tags para categorização
                - Outros campos customizados também são aceitos

        Example:
            client.send_event(
                event_type="USER_LOGIN",
                message="Usuário fez login",
                object="auth_service",
                tags=["auth", "success"],
                user_id=123
            )
        """
        event_data = {
            "project": self.project,
            "layer": self.layer,
            "event_type": event_type,
            "message": message,
            **kwargs,
        }

        self.repository.event_handler(**event_data)

    def send_error(
        self, exception: Exception, context: str = "", **kwargs: Any
    ) -> None:
        """
        Envia evento de erro com informações da exception

        Args:
            exception: Exception capturada
            context: Contexto onde o erro ocorreu
            **kwargs: Campos adicionais (mesmos do send_event)

        Example:
            try:
                result = 1/0
            except Exception as e:
                client.send_error(e, context="calculate_division", user_id=123)
        """
        self.send_event(
            event_type="ERROR",
            message=str(exception),
            obs=kwargs.get("obs", traceback.format_exc()),
            object=kwargs.get("object", context),
            tags=kwargs.get("tags", [exception.__class__.__name__]),
            **{k: v for k, v in kwargs.items() if k not in ["obs", "object", "tags"]},
        )

    def capture_errors(self, context: str = "") -> Callable:
        """
        Decorator para capturar erros automaticamente

        Args:
            context: Contexto customizado (default: module.function_name)

        Returns:
            Decorator que pode ser aplicado em qualquer função

        Example:
            @client.capture_errors("payment_processing")
            def process_payment(amount):
                if amount <= 0:
                    raise ValueError("Amount must be positive")
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.send_error(
                        exception=e,
                        context=context or f"{func.__module__}.{func.__name__}",
                        object=f"{func.__module__}.{func.__name__}",
                    )
                    raise

            return wrapper

        return decorator
