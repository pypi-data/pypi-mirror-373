import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import adal
import requests
from requests.exceptions import RequestException

from ..repository.powerbi_repository import PowerBiRepository


class PowerBi(PowerBiRepository):
    """
    Cliente Power BI - implementação com Repository Pattern

    Baseada no código original, mantém compatibilidade total mas com estrutura simplificada.
    Implementa operações de refresh de datasets e dataflows no Power BI.

    Args:
        airflow_variable: Nome da variável do Airflow com configurações (opcional)

    Examples
    --------
    >>> from mentorstec import PowerBi
    >>> powerbi = PowerBi("my_powerbi_config")
    >>> projects = powerbi.get_power_bi_projects()
    >>> len(projects) >= 0
    True
    >>> token = powerbi.get_token(projects) if projects else None
    >>> isinstance(token, (str, type(None)))
    True
    """

    def __init__(self, airflow_variable: Optional[str] = None) -> None:
        self.airflow_variable = airflow_variable
        self.logger = logging.getLogger(__name__)

    def get_power_bi_projects(
        self, airflow_variable: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém configuração dos projetos Power BI

        Args:
            airflow_variable: Nome da variável do Airflow (usa self.airflow_variable se não informado)

        Returns:
            Lista de configurações de projetos

        Examples
        --------
        >>> powerbi = PowerBi("powerbi_configs")
        >>> projects = powerbi.get_power_bi_projects()
        >>> isinstance(projects, list)
        True
        >>> # Exemplo de estrutura esperada
        >>> example_project = {
        ...     'api': {'powerbi': 'https://api.powerbi.com/v1.0/myorg'},
        ...     'credentials': {'client': 'client-id', 'usr': 'user@domain.com'},
        ...     'datasets': [{'group_id': 'group-123', 'datasets': []}]
        ... }
        >>> isinstance(example_project, dict)
        True
        """
        variable_name = airflow_variable or self.airflow_variable

        if not variable_name:
            raise ValueError("airflow_variable deve ser fornecida")

        try:
            # Importação dinâmica para evitar dependência obrigatória do Airflow
            from airflow.models import Variable

            powerbi_settings = Variable.get(key=variable_name)
            projects = json.loads(powerbi_settings)["projects"]

            self.logger.debug(f"Projetos Power BI carregados: {len(projects)}")
            return projects

        except ImportError:
            self.logger.error(
                "Airflow não está disponível. Instale apache-airflow para usar esta funcionalidade."
            )
            raise
        except Exception as e:
            self.logger.error(f"Erro ao obter projetos Power BI: {e}")
            raise

    def get_token(self, project_config: List[Dict[str, Any]]) -> Optional[str]:
        """
        Obtém token de autenticação do Power BI

        Args:
            project_config: Configuração dos projetos

        Returns:
            Token de acesso ou None em caso de erro

        Examples
        --------
        >>> project_config = [{
        ...     'api': {
        ...         'authority': 'https://login.microsoftonline.com/tenant-id',
        ...         'resource': 'https://analysis.windows.net/powerbi/api'
        ...     },
        ...     'credentials': {
        ...         'client': 'your-client-id',
        ...         'usr': 'user@company.com',
        ...         'pass': 'your-password'
        ...     }
        ... }]
        >>> powerbi = PowerBi()
        >>> token = powerbi.get_token(project_config)
        >>> token is None or len(token) > 50  # JWT tokens are long
        True
        """
        try:
            for setting in project_config:
                authority_url = setting["api"]["authority"]
                resource_url = setting["api"]["resource"]
                client_id = setting["credentials"]["client"]
                username = setting["credentials"]["usr"]
                password = setting["credentials"]["pass"]

            context = adal.AuthenticationContext(
                authority=authority_url, validate_authority=True, api_version=None
            )

            token = context.acquire_token_with_username_password(
                resource=resource_url,
                client_id=client_id,
                username=username,
                password=password,
            )

            access_token = token.get("accessToken")
            if access_token:
                self.logger.info("Token obtido com sucesso!")
                return access_token
            else:
                self.logger.error("Token não foi obtido")
                return None

        except Exception as e:
            self.logger.error(f"Erro ao obter token: {e}")
            return None

    def generate_url(
        self, resource_type: str, project_config: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Gera URLs para recursos baseado na configuração

        Args:
            resource_type: Tipo do recurso (datasets, dataflows)
            project_config: Configuração dos projetos

        Returns:
            Dicionário com tag -> URL

        Examples
        --------
        >>> project_config = [{
        ...     'api': {'powerbi': 'https://api.powerbi.com/v1.0/myorg'},
        ...     'datasets': [{
        ...         'group_id': 'abc-123',
        ...         'datasets': [
        ...             {'tag': 'sales', 'id': 'dataset-456'},
        ...             {'tag': 'inventory', 'id': 'dataset-789'}
        ...         ]
        ...     }]
        ... }]
        >>> powerbi = PowerBi()
        >>> urls = powerbi.generate_url('datasets', project_config)
        >>> urls['sales']
        'https://api.powerbi.com/v1.0/myorg/groups/abc-123/datasets/dataset-456'
        >>> len(urls) == 2
        True
        """
        urls = {}

        try:
            for project in project_config:
                api = project["api"]["powerbi"]

                if resource_type not in project:
                    continue

                for item in project[resource_type]:
                    group_id = item["group_id"]

                    if resource_type not in item:
                        continue

                    for sub_item in item[resource_type]:
                        tag = sub_item["tag"]
                        target_id = sub_item["id"]
                        url = f"{api}/groups/{group_id}/{resource_type}/{target_id}"
                        urls[tag] = url

            self.logger.debug(f"URLs geradas para {resource_type}: {len(urls)}")
            return urls

        except Exception as e:
            self.logger.error(f"Erro ao gerar URLs: {e}")
            return {}

    def refresh_resource(
        self, url: str, token: str, payload_json: Optional[Dict] = None
    ) -> bool:
        """
        Executa refresh de um recurso (dataset/dataflow)

        Args:
            url: URL do recurso
            token: Token de autenticação
            payload_json: Payload opcional para a requisição

        Returns:
            True se refresh foi iniciado com sucesso
        """
        url_refresh = f"{url}/refreshes"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            if payload_json:
                response = requests.post(
                    url=url_refresh, headers=headers, json=payload_json, timeout=30
                )
            else:
                response = requests.post(url=url_refresh, headers=headers, timeout=30)

            self.logger.info(f"Refresh iniciado: {url}")
            self.logger.debug(f"Response: {response.status_code}")

            time.sleep(10)  # Aguardar processamento inicial

            if response.status_code not in [200, 202]:
                error_msg = f"Unexpected status code: {response.status_code}, {response.text}, {response.reason}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

            return True

        except RequestException as e:
            self.logger.error(f"Erro na requisição de refresh: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao executar refresh: {e}")
            raise

    def check_status(self, url: str, token: str) -> Optional[str]:
        """
        Verifica status de uma operação

        Args:
            url: URL para verificar status
            token: Token de autenticação

        Returns:
            Status da operação ou None em caso de erro
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = json.dumps(
            {
                "type": "full",
                "commitMode": "transactional",
                "applyRefreshPolicy": "false",
            }
        )

        try:
            response = requests.get(url=url, headers=headers, data=payload, timeout=30)

            if response.status_code in [200, 202]:
                response_data = response.json()

                if "value" in response_data and len(response_data["value"]) > 0:
                    response_status = response_data["value"][0].get("status")
                    self.logger.debug(f"Status verificado: {response_status}")
                    return response_status
                else:
                    self.logger.warning("Resposta não contém dados de status esperados")
                    return None
            else:
                error_msg = f"Unexpected status code: {response.status_code}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

        except RequestException as e:
            self.logger.error(f"Erro na requisição de status: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Ocorreu um erro ao verificar status: {e}")
            return None

    def execute(
        self, url: str, token: str, payload_json: Optional[Dict] = None
    ) -> bool:
        """
        Executa operação completa (refresh + aguardar conclusão)

        Args:
            url: URL do recurso
            token: Token de autenticação
            payload_json: Payload opcional

        Returns:
            True se operação foi concluída com sucesso
        """
        try:
            # Iniciar refresh
            if not self.refresh_resource(
                url=url, token=token, payload_json=payload_json
            ):
                return False

            # Determinar URL de verificação baseado no tipo de recurso
            if "dataflows" in url:
                url_check = f"{url}/transactions"
            else:
                url_check = f"{url}/refreshes"

            # Aguardar conclusão
            status = self.check_status(url=url_check, token=token)

            while status not in ["Success", "Completed", None]:
                current_time = datetime.now()
                print(f"{current_time} - Atualização em execução - Status: {status}")
                self.logger.info(f"Aguardando conclusão - Status: {status}")

                time.sleep(60)  # Aguardar 1 minuto
                status = self.check_status(url=url_check, token=token)

                if status is None:
                    self.logger.error(
                        "Erro ao verificar status - interrompendo operação"
                    )
                    return False

            if status in ["Success", "Completed"]:
                current_time = datetime.now()
                print(f"{current_time} - Atualização concluída com sucesso")
                self.logger.info("Operação concluída com sucesso")
                return True
            else:
                self.logger.error(f"Operação falhou com status: {status}")
                return False

        except Exception as e:
            self.logger.error(f"Erro na execução: {e}")
            return False

    # Métodos de conveniência adicionais

    def refresh_dataset(
        self,
        tag: str,
        project_config: List[Dict[str, Any]],
        payload_json: Optional[Dict] = None,
    ) -> bool:
        """
        Refresh de um dataset específico

        Args:
            tag: Tag do dataset
            project_config: Configuração dos projetos
            payload_json: Payload opcional

        Returns:
            True se refresh foi concluído com sucesso

        Examples
        --------
        >>> project_config = [{
        ...     'api': {'powerbi': 'https://api.powerbi.com/v1.0/myorg'},
        ...     'credentials': {'client': 'client-id', 'usr': 'user@domain.com', 'pass': 'pass'},
        ...     'datasets': [{
        ...         'group_id': 'group-123',
        ...         'datasets': [{'tag': 'sales_data', 'id': 'dataset-456'}]
        ...     }]
        ... }]
        >>> powerbi = PowerBi()
        >>> payload = {"type": "full", "commitMode": "transactional"}
        >>> success = powerbi.refresh_dataset('sales_data', project_config, payload)
        >>> isinstance(success, bool)
        True
        """
        token = self.get_token(project_config)
        if not token:
            return False

        urls = self.generate_url("datasets", project_config)
        if tag not in urls:
            self.logger.error(f"Dataset com tag '{tag}' não encontrado")
            return False

        return self.execute(urls[tag], token, payload_json)

    def refresh_dataflow(
        self,
        tag: str,
        project_config: List[Dict[str, Any]],
        payload_json: Optional[Dict] = None,
    ) -> bool:
        """
        Refresh de um dataflow específico

        Args:
            tag: Tag do dataflow
            project_config: Configuração dos projetos
            payload_json: Payload opcional

        Returns:
            True se refresh foi concluído com sucesso

        Examples
        --------
        >>> project_config = [{
        ...     'api': {'powerbi': 'https://api.powerbi.com/v1.0/myorg'},
        ...     'credentials': {'client': 'client-id', 'usr': 'user@domain.com', 'pass': 'pass'},
        ...     'dataflows': [{
        ...         'group_id': 'group-456',
        ...         'dataflows': [{'tag': 'customer_flow', 'id': 'dataflow-789'}]
        ...     }]
        ... }]
        >>> powerbi = PowerBi()
        >>> success = powerbi.refresh_dataflow('customer_flow', project_config)
        >>> isinstance(success, bool)
        True
        """
        token = self.get_token(project_config)
        if not token:
            return False

        urls = self.generate_url("dataflows", project_config)
        if tag not in urls:
            self.logger.error(f"Dataflow com tag '{tag}' não encontrado")
            return False

        return self.execute(urls[tag], token, payload_json)

    def refresh_all_datasets(
        self, project_config: List[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """
        Refresh de todos os datasets

        Args:
            project_config: Configuração dos projetos

        Returns:
            Dicionário com tag -> resultado do refresh

        Examples
        --------
        >>> project_config = [{
        ...     'api': {'powerbi': 'https://api.powerbi.com/v1.0/myorg'},
        ...     'credentials': {'client': 'client-id', 'usr': 'user@domain.com', 'pass': 'pass'},
        ...     'datasets': [{
        ...         'group_id': 'group-123',
        ...         'datasets': [
        ...             {'tag': 'sales', 'id': 'dataset-456'},
        ...             {'tag': 'inventory', 'id': 'dataset-789'}
        ...         ]
        ...     }]
        ... }]
        >>> powerbi = PowerBi()
        >>> results = powerbi.refresh_all_datasets(project_config)
        >>> isinstance(results, dict)
        True
        >>> all(isinstance(v, bool) for v in results.values())
        True
        """
        token = self.get_token(project_config)
        if not token:
            return {}

        urls = self.generate_url("datasets", project_config)
        results = {}

        for tag, url in urls.items():
            self.logger.info(f"Iniciando refresh do dataset: {tag}")
            results[tag] = self.execute(url, token)

        return results
