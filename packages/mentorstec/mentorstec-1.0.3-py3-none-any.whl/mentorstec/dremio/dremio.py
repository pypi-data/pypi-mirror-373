import json
import logging
import time
from typing import Any, Dict, List, Optional

from requests import request

from ..repository.dremio_repository import DremioRepository


class Dremio(DremioRepository):
    """
    Cliente Dremio - implementação simplificada com Repository Pattern

    Baseada no código original, mantém compatibilidade total mas com estrutura mais simples.
    Todos os métodos usam o método genérico execute_sql() para executar queries.

    Args:
        host: Host do servidor Dremio (ex: 'localhost:9047')
        credentials: Dicionário com credenciais {'username': 'user', 'password': 'pass'}
    """

    def __init__(self, host: str, credentials: Dict[str, str]) -> None:
        self.host = host
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
        self._token: Optional[str] = None

    def authenticate(self) -> bool:
        """
        Autentica com Dremio e obtém token de acesso

        Returns:
            True se autenticação foi bem-sucedida
        """
        url = f"http://{self.host}/apiv2/login"
        headers = {"Content-Type": "application/json"}
        payload = self.credentials

        try:
            response = request(
                method="post", url=url, headers=headers, data=json.dumps(payload)
            )

            if response.status_code == 200:
                json_response = response.json()
                self._token = json_response["token"]
                logging.debug(f"Token obtido: {self._token}")
                return True
            else:
                logging.error(
                    f"Erro ao obter o token, Codigo {response.status_code} - {response.reason}"
                )
                return False

        except Exception as e:
            logging.error(f"Erro na autenticação: {e}")
            return False

    def execute_sql(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Executa uma query SQL no Dremio e retorna o resultado

        Args:
            query: Query SQL para executar

        Returns:
            Resultado da query ou None em caso de erro
        """
        # Garantir que temos token válido
        if not self._token:
            if not self.authenticate():
                return None

        url = f"http://{self.host}/api/v3/sql"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        payload = {"sql": query}

        try:
            response = request(
                method="post", url=url, headers=headers, data=json.dumps(payload)
            )

            if response.status_code == 200:
                json_response = response.json()
                job_id = json_response["id"]
                logging.debug(f"Job executado com sucesso, ID: {job_id}")

                # Aguardar conclusão e retornar resultado
                return self._wait_and_get_result(job_id)
            else:
                logging.error(
                    f"Erro ao executar query, Codigo {response.status_code} - {response.reason}"
                )
                return None

        except Exception as e:
            logging.error(f"Erro ao executar SQL: {e}")
            return None

    def get_tables(self, path: str) -> List[str]:
        """
        Obtém lista de tabelas em um caminho específico

        Args:
            path: Caminho no catálogo Dremio

        Returns:
            Lista de nomes de tabelas
        """
        # Garantir que temos token válido
        if not self._token:
            if not self.authenticate():
                return []

        url = f"http://{self.host}/api/v3/catalog/by-path/{path}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        try:
            response = request(method="GET", url=url, headers=headers)
            tables = []

            if response.status_code == 200:
                json_response = response.json()
                children = json_response.get("children", [])
                for c in children:
                    tables.append(c["path"][-1])
                    logging.debug(f"Localizando a tabela: {c}")
                return tables
            else:
                logging.error(
                    f"Erro ao obter tabelas, Codigo {response.status_code} - {response.reason}"
                )
                return tables

        except Exception as e:
            logging.error(f"Erro ao obter tabelas: {e}")
            return []

    def _wait_and_get_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Aguarda conclusão do job e retorna resultado

        Args:
            job_id: ID do job

        Returns:
            Resultado do job ou None em caso de erro
        """
        if not self._token:
            return None

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        url_result = f"http://{self.host}/api/v3/job/{job_id}/results"
        url_job = f"http://{self.host}/api/v3/job/{job_id}"

        # Aguardar conclusão do job
        job_status = self._get_job_status(url_job, headers)
        while job_status != "COMPLETED":
            if job_status in ["FAILED", "CANCELLED"]:
                logging.error(f"Job {job_id} falhou com status: {job_status}")
                return None
            job_status = self._get_job_status(url_job, headers)
            time.sleep(15)

        # Obter resultado
        try:
            response = request(method="GET", url=url_result, headers=headers)

            if response.status_code == 200:
                json_response = response.json()
                logging.debug("Resultado obtido com sucesso")
                return json_response
            else:
                logging.error(
                    f"Erro ao obter resultado, Codigo {response.status_code} - {response.reason}"
                )
                return None

        except Exception as e:
            logging.error(f"Erro ao obter resultado: {e}")
            return None

    def _get_job_status(self, url_job: str, headers: Dict[str, str]) -> Optional[str]:
        """
        Obtém status de um job

        Args:
            url_job: URL do endpoint de job
            headers: Headers HTTP

        Returns:
            Status do job ou None em caso de erro
        """
        try:
            result_job = request(method="GET", url=url_job, headers=headers)
            if result_job.status_code == 200:
                json_result = result_job.json()
                return json_result.get("jobState")
            else:
                logging.error(f"Erro ao obter status: {result_job.status_code}")
                return None
        except Exception as e:
            logging.error(f"Erro ao obter status do job: {e}")
            return None

    @property
    def token(self) -> Optional[str]:
        """Token de autenticação atual"""
        return self._token

    # Métodos de conveniência usando execute_sql()

    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """
        Cria uma tabela no Dremio

        Args:
            table_name: Nome da tabela
            columns: Dicionário com nome_coluna: tipo_dados

        Returns:
            True se tabela foi criada com sucesso
        """
        columns_def = ", ".join([f"{name} {dtype}" for name, dtype in columns.items()])
        create_query = f"CREATE TABLE {table_name} ({columns_def})"

        result = self.execute_sql(create_query)
        return result is not None

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """
        Insere dados em uma tabela

        Args:
            table_name: Nome da tabela
            data: Dados para inserir

        Returns:
            True se inserção foi bem-sucedida
        """
        columns = ", ".join(data.keys())
        values = ", ".join(
            [f"'{v}'" if isinstance(v, str) else str(v) for v in data.values()]
        )

        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        result = self.execute_sql(insert_query)

        return result is not None

    def count_rows(self, table_name: str) -> Optional[int]:
        """
        Conta linhas de uma tabela

        Args:
            table_name: Nome da tabela

        Returns:
            Número de linhas ou None em caso de erro
        """
        query = f"SELECT COUNT(*) as row_count FROM {table_name}"
        result = self.execute_sql(query)

        if result and "rows" in result and len(result["rows"]) > 0:
            return result["rows"][0].get("row_count", 0)
        return None

    def describe_table(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de uma tabela

        Args:
            table_name: Nome da tabela

        Returns:
            Informações da tabela ou None em caso de erro
        """
        query = f"DESCRIBE {table_name}"
        return self.execute_sql(query)
