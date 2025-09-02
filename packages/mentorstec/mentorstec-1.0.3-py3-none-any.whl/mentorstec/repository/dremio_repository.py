from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DremioRepository(ABC):
    """
    Repository abstrato para operações no Dremio

    Define a interface padrão que todas as implementações Dremio devem seguir.
    Permite executar queries SQL genéricas no Dremio.
    """

    @abstractmethod
    def execute_sql(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Executa uma query SQL no Dremio

        Args:
            query: Query SQL para executar

        Returns:
            Resultado da query ou None em caso de erro
        """
        pass

    @abstractmethod
    def get_tables(self, path: str) -> List[str]:
        """
        Obtém lista de tabelas em um caminho específico

        Args:
            path: Caminho no catálogo Dremio

        Returns:
            Lista de nomes de tabelas
        """
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Autentica com o Dremio

        Returns:
            True se autenticação foi bem-sucedida
        """
        pass
