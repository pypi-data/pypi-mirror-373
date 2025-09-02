import json
import logging
from typing import Any

from azure.servicebus import ServiceBusClient, ServiceBusMessage

from ..repository.eventhub_repository import EventHubRepository


class AzureServiceBusRepository(EventHubRepository):
    """
    Implementação do EventRepository para Azure Service Bus

    Args:
        connection_string: String de conexão do Azure Service Bus
        queue_name: Nome da fila no Service Bus
    """

    def __init__(self, connection_string: str, queue_name: str):
        self.connection_string = connection_string
        self.queue_name = queue_name
        self.logger = logging.getLogger(__name__)

    def event_handler(self, **kwargs: Any) -> None:
        """
        Envia evento para Azure Service Bus

        Args:
            **kwargs: Dados do evento que serão processados pelo build_payload()
        """
        payload = self.build_payload(**kwargs)
        message = ServiceBusMessage(json.dumps(payload))

        try:
            with ServiceBusClient.from_connection_string(
                self.connection_string
            ) as client:
                sender = client.get_queue_sender(queue_name=self.queue_name)
                with sender:
                    sender.send_messages(message)
                    self.logger.info(
                        f"Evento enviado: {payload.get('event_type', 'UNKNOWN')} - {payload.get('project', 'N/A')}"
                    )
        except Exception as e:
            self.logger.error(f"Falha ao enviar evento para Service Bus: {e}")
            raise
