from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class PowerBiRepository(ABC):
    """
    Repository abstrato para operações no Power BI

    Define a interface padrão que todas as implementações Power BI devem seguir.
    Permite executar operações genéricas no Power BI como refresh de datasets e dataflows.

    Examples
    --------
    >>> from mentorstec import PowerBi
    >>> powerbi = PowerBi("powerbi_config_variable")
    >>> projects = powerbi.get_power_bi_projects()
    >>> token = powerbi.get_token(projects)
    >>> 'Bearer' in token
    False
    >>> isinstance(token, str)
    True
    """

    @abstractmethod
    def get_token(self, project_config: List[Dict[str, Any]]) -> Optional[str]:
        """
        Obtém token de autenticação do Power BI

        Args:
            project_config: Lista de configurações dos projetos contendo credenciais e endpoints

        Returns:
            Token de acesso JWT ou None em caso de erro

        Examples
        --------
        >>> project_config = [{
        ...     'api': {
        ...         'authority': 'https://login.microsoftonline.com/tenant-id',
        ...         'resource': 'https://analysis.windows.net/powerbi/api'
        ...     },
        ...     'credentials': {
        ...         'client': 'client-id',
        ...         'usr': 'user@domain.com',
        ...         'pass': 'password'
        ...     }
        ... }]
        >>> powerbi = PowerBi()
        >>> token = powerbi.get_token(project_config)
        >>> token is not None
        True
        >>> len(token) > 100  # JWT tokens are typically long
        True
        """
        pass

    @abstractmethod
    def refresh_resource(
        self, url: str, token: str, payload_json: Optional[Dict] = None
    ) -> bool:
        """
        Executa refresh de um recurso (dataset/dataflow)

        Args:
            url: URL completa do recurso no Power BI
            token: Token de autenticação JWT
            payload_json: Payload JSON opcional com configurações específicas do refresh

        Returns:
            True se refresh foi iniciado com sucesso, False caso contrário

        Examples
        --------
        >>> powerbi = PowerBi()
        >>> url = "https://api.powerbi.com/v1.0/myorg/groups/group-id/datasets/dataset-id"
        >>> token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsI..."
        >>> payload = {"type": "full", "commitMode": "transactional"}
        >>> result = powerbi.refresh_resource(url, token, payload)
        >>> isinstance(result, bool)
        True
        """
        pass

    @abstractmethod
    def check_status(self, url: str, token: str) -> Optional[str]:
        """
        Verifica status de uma operação de refresh

        Args:
            url: URL para verificar status (endpoint /refreshes ou /transactions)
            token: Token de autenticação JWT

        Returns:
            Status da operação ('InProgress', 'Success', 'Failed', etc.) ou None em caso de erro

        Examples
        --------
        >>> powerbi = PowerBi()
        >>> status_url = "https://api.powerbi.com/v1.0/myorg/groups/group-id/datasets/dataset-id/refreshes"
        >>> token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsI..."
        >>> status = powerbi.check_status(status_url, token)
        >>> status in ['InProgress', 'Success', 'Failed', 'Completed']
        True
        """
        pass

    @abstractmethod
    def generate_url(
        self, resource_type: str, project_config: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Gera URLs para recursos baseado na configuração dos projetos

        Args:
            resource_type: Tipo do recurso ('datasets' ou 'dataflows')
            project_config: Lista de configurações dos projetos

        Returns:
            Dicionário mapeando tag do recurso para sua URL completa

        Examples
        --------
        >>> project_config = [{
        ...     'api': {'powerbi': 'https://api.powerbi.com/v1.0/myorg'},
        ...     'datasets': [{
        ...         'group_id': 'group-123',
        ...         'datasets': [{'tag': 'sales_data', 'id': 'dataset-456'}]
        ...     }]
        ... }]
        >>> powerbi = PowerBi()
        >>> urls = powerbi.generate_url('datasets', project_config)
        >>> urls['sales_data']
        'https://api.powerbi.com/v1.0/myorg/groups/group-123/datasets/dataset-456'
        >>> len(urls) >= 1
        True
        """
        pass

    @abstractmethod
    def execute(
        self, url: str, token: str, payload_json: Optional[Dict] = None
    ) -> bool:
        """
        Executa operação completa (refresh + aguardar conclusão)

        Args:
            url: URL completa do recurso
            token: Token de autenticação JWT
            payload_json: Payload opcional com configurações do refresh

        Returns:
            True se operação foi concluída com sucesso, False caso contrário

        Examples
        --------
        >>> powerbi = PowerBi()
        >>> url = "https://api.powerbi.com/v1.0/myorg/groups/group-id/datasets/dataset-id"
        >>> token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsI..."
        >>> payload = {"type": "full", "commitMode": "transactional"}
        >>> success = powerbi.execute(url, token, payload)
        >>> isinstance(success, bool)
        True
        """
        pass
