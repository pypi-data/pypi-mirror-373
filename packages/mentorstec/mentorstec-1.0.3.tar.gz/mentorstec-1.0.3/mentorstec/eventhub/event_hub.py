# Decorator simples e eficiente para send_event
import functools
from typing import Any, Callable, Optional

from .event_hub_client import EventHubClient


def send_event(
    project: str,
    queue_name: str,
    event_type: str = "FUNCTION_CALL",
    layer: str = "undefined",
    include_args: bool = False,
    include_result: bool = False,
    context: Optional[str] = None,
    connection_string: Optional[str] = None,
) -> Callable:
    """
    Decorator simples e eficiente para automaticamente enviar eventos

    Args:
        project: Nome do projeto
        queue_name: Nome da fila (obrigatório)
        event_type: Tipo do evento a ser logado
        layer: Camada da aplicação (web, api, service, etc.)
        include_args: Se True, inclui argumentos da função no log
        include_result: Se True, inclui resultado da função no log
        context: Contexto customizado (default: nome da função)
        connection_string: Connection string opcional (usa env var se não informado)

    Returns:
        Decorator que automaticamente envia eventos

    Example:
        >>> @send_event("my-project", "events-queue", "USER_ACTION")
        ... def process_payment(amount, currency="USD"):
        ...     return {"charged": amount, "currency": currency}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Criar cliente local para esta execução
            client = EventHubClient.create_azure_client(
                project=project,
                queue_name=queue_name,
                layer=layer,
                connection_string=connection_string,
            )

            func_context = context or func.__name__

            # Preparar dados básicos do evento
            event_data = {
                "object": func_context,
                "function_name": func.__name__,
            }

            # Incluir argumentos se solicitado
            if include_args:
                event_data.update({"args": args, "kwargs": kwargs})

            try:
                # Executar função
                result = func(*args, **kwargs)

                # Incluir resultado se solicitado
                if include_result:
                    event_data["result"] = result

                # Enviar evento de sucesso
                client.send_event(
                    event_type=event_type,
                    message=f"Function {func.__name__} executed successfully",
                    **event_data,
                )

                return result

            except Exception as e:
                # Enviar evento de erro
                client.send_error(
                    exception=e,
                    context=func_context,
                    function_name=func.__name__,
                    args=args if include_args else None,
                    kwargs=kwargs if include_args else None,
                )
                raise

        return wrapper

    return decorator
