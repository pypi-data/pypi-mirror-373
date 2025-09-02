#!/usr/bin/env python3
"""
PowerBI Usage Examples - mentorstec package

Este arquivo demonstra como usar a implementação PowerBI seguindo o Repository Pattern.

Examples
--------
Basic usage with project configuration:

>>> from mentorstec import PowerBi
>>>
>>> # Configuração de exemplo (normalmente vem do Airflow Variable)
>>> project_config = [{
...     'api': {
...         'authority': 'https://login.microsoftonline.com/your-tenant-id',
...         'resource': 'https://analysis.windows.net/powerbi/api',
...         'powerbi': 'https://api.powerbi.com/v1.0/myorg'
...     },
...     'credentials': {
...         'client': 'your-application-client-id',
...         'usr': 'powerbi-service-account@company.com',
...         'pass': 'service-account-password'
...     },
...     'datasets': [{
...         'group_id': 'f089354e-8366-4e18-aea3-4cb4a3a50b48',
...         'datasets': [
...             {'tag': 'sales_report', 'id': 'cfafbeb1-8037-4d0c-896e-a46fb27ff229'},
...             {'tag': 'inventory_data', 'id': '3d9b93c6-7b6d-4801-a491-1738910bd1b0'}
...         ]
...     }],
...     'dataflows': [{
...         'group_id': 'f089354e-8366-4e18-aea3-4cb4a3a50b48',
...         'dataflows': [
...             {'tag': 'customer_flow', 'id': '1234abcd-ef56-7890-ghij-klmnopqrstuv'}
...         ]
...     }]
... }]
>>>
>>> # Inicializar cliente PowerBI
>>> powerbi = PowerBi()
>>>
>>> # Obter token de autenticação
>>> token = powerbi.get_token(project_config)
>>> print(f"Token obtido: {token is not None}")
Token obtido: True
>>>
>>> # Gerar URLs para datasets
>>> dataset_urls = powerbi.generate_url('datasets', project_config)
>>> print(f"URLs geradas: {len(dataset_urls)}")
URLs geradas: 2
>>> print(dataset_urls['sales_report'])
https://api.powerbi.com/v1.0/myorg/groups/f089354e-8366-4e18-aea3-4cb4a3a50b48/datasets/cfafbeb1-8037-4d0c-896e-a46fb27ff229

Advanced usage - Refresh specific dataset:

>>> # Refresh de um dataset específico
>>> payload = {
...     "type": "full",
...     "commitMode": "transactional",
...     "applyRefreshPolicy": "false"
... }
>>> success = powerbi.refresh_dataset('sales_report', project_config, payload)
>>> print(f"Refresh iniciado: {success}")
Refresh iniciado: True

Refresh multiple datasets:

>>> # Refresh de todos os datasets
>>> results = powerbi.refresh_all_datasets(project_config)
>>> print(f"Resultados: {results}")
Resultados: {'sales_report': True, 'inventory_data': True}

Using with Airflow Variable:

>>> # Usando com variável do Airflow (requer apache-airflow instalado)
>>> powerbi = PowerBi("powerbi_production_config")
>>> projects = powerbi.get_power_bi_projects()
>>> len(projects) >= 0
True

Error handling:

>>> # Tratamento de erros
>>> try:
...     invalid_config = [{'invalid': 'config'}]
...     token = powerbi.get_token(invalid_config)
...     print(f"Token: {token}")
... except Exception as e:
...     print(f"Erro esperado: {type(e).__name__}")
Token: None

Repository Pattern usage:

>>> from mentorstec import PowerBiRepository
>>>
>>> # Usar a interface abstrata
>>> def process_powerbi_refresh(repository: PowerBiRepository, config, tag):
...     token = repository.get_token(config)
...     if token:
...         urls = repository.generate_url('datasets', config)
...         if tag in urls:
...             return repository.execute(urls[tag], token)
...     return False
>>>
>>> # Funciona com qualquer implementação de PowerBiRepository
>>> result = process_powerbi_refresh(powerbi, project_config, 'sales_report')
>>> isinstance(result, bool)
True
"""


def main():
    """Exemplo de uso completo do PowerBI client"""

    # Este é um exemplo de configuração - substitua pelos seus valores reais
    example_config = [
        {
            "api": {
                "authority": "https://login.microsoftonline.com/YOUR-TENANT-ID",
                "resource": "https://analysis.windows.net/powerbi/api",
                "powerbi": "https://api.powerbi.com/v1.0/myorg",
            },
            "credentials": {
                "client": "YOUR-CLIENT-ID",
                "usr": "service-account@yourcompany.com",
                "pass": "YOUR-SERVICE-ACCOUNT-PASSWORD",
            },
            "datasets": [
                {
                    "group_id": "YOUR-WORKSPACE-ID",
                    "datasets": [{"tag": "my_dataset", "id": "YOUR-DATASET-ID"}],
                }
            ],
        }
    ]

    try:
        from mentorstec import PowerBi

        # Inicializar cliente
        powerbi = PowerBi()

        # Obter token
        print("Obtendo token de autenticação...")
        token = powerbi.get_token(example_config)

        if not token:
            print("❌ Falha ao obter token de autenticação")
            return

        print("✅ Token obtido com sucesso")

        # Gerar URLs
        print("Gerando URLs dos datasets...")
        urls = powerbi.generate_url("datasets", example_config)
        print(f"✅ {len(urls)} URLs geradas")

        # Executar refresh
        for tag, url in urls.items():
            print(f"Executando refresh do dataset: {tag}")
            success = powerbi.execute(url, token)

            if success:
                print(f"✅ Refresh de {tag} concluído com sucesso")
            else:
                print(f"❌ Falha no refresh de {tag}")

    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("Instale as dependências: pip install mentorstec[powerbi]")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()
