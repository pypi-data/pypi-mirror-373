# Mentorstec

![Pipeline](https://github.com/Mentorstec/mentorstec/actions/workflows/pipeline.yml/badge.svg)
![PyPI Version](https://img.shields.io/pypi/v/mentorstec?color=blue&logo=pypi&logoColor=white)
![Python Versions](https://img.shields.io/pypi/pyversions/mentorstec?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/Mentorstec/mentorstec?color=green)
![Downloads](https://img.shields.io/pypi/dm/mentorstec?color=orange&logo=pypi)

Plataforma centralizada de dados e logging com Repository Pattern. Suporte para Azure Service Bus, Dremio e Power BI com arquitetura modular e extensível.

## 🚀 Instalação

### Instalação Básica
```bash
pip install mentorstec
```

### Com Módulos Opcionais
```bash
# Power BI support
pip install mentorstec[powerbi]

# Dremio support
pip install mentorstec[dremio]

# Todas as funcionalidades
pip install mentorstec[powerbi,dremio]

# Desenvolvimento
pip install mentorstec[dev]
```

### Desenvolvimento Local
```bash
git clone https://github.com/mentorstec/mentorstec.git
cd mentorstec
pip install -e ".[dev,powerbi,dremio]"
```

## 🏗️ Arquitetura Completa

O Mentorstec implementa **Repository Pattern** para máxima flexibilidade e extensibilidade:

```
mentorstec/
├── eventhub/                     # 🔄 Azure Service Bus Integration
│   ├── event_hub.py              #   - Funções globais de conveniência
│   └── event_hub_client.py       #   - Cliente principal para eventos
│
├── dremio/                       # 🗄️ Data Virtualization (Opcional)
│   └── dremio.py                 #   - Cliente para consultas SQL
│
├── powerbi/                      # 📊 Power BI Integration (Opcional)
│   └── powerbi.py                #   - Refresh de datasets e dataflows
│
├── repository/                   # 🏛️ Abstract Interfaces
│   ├── eventhub_repository.py    #   - Interface para event logging
│   ├── dremio_repository.py      #   - Interface para data queries
│   └── powerbi_repository.py     #   - Interface para Power BI ops
│
├── azure/                        # ☁️ Azure Implementations
│   └── azure_service_bus_repository.py  # - Service Bus concrete impl
│
└── lakehouse/                    # 🏠 Reserved for Future Use
    └── __init__.py               #   - Preparado para expansão
```

### 🎯 Design Principles

- **Repository Pattern**: Interfaces abstratas com implementações concretas
- **Optional Dependencies**: Módulos carregados apenas se dependências existem
- **Backward Compatibility**: APIs antigas mantidas para compatibilidade
- **Extensibility**: Fácil adição de novos módulos e provedores
- **Production Ready**: Testes, CI/CD e distribuição automatizada

## 📋 Configuração

### Azure Service Bus (Core)
```bash
export AZURE_SERVICE_BUS_CONNECTION_STRING="Endpoint=sb://..."
```

### Power BI (Opcional)
Configuração via variáveis do Airflow ou configuração manual:
```python
project_config = [{
    'api': {
        'authority': 'https://login.microsoftonline.com/your-tenant-id',
        'resource': 'https://analysis.windows.net/powerbi/api',
        'powerbi': 'https://api.powerbi.com/v1.0/myorg'
    },
    'credentials': {
        'client': 'your-client-id',
        'usr': 'service-account@company.com',
        'pass': 'service-account-password'
    }
}]
```

### Dremio (Opcional)
```python
dremio_config = {
    'host': 'your-dremio-host',
    'port': 9047,
    'username': 'your-username',
    'password': 'your-password'
}
```

## 🎯 Exemplos de Uso

### 🔄 EventHub - Azure Service Bus

#### Client Direto (Recomendado)
```python
from mentorstec import EventHubClient

# Criar client - queue_name agora é obrigatório
client = EventHubClient.create_azure_client("meu-projeto", "events-queue", layer="web")

# Enviar evento
client.send_event(
    event_type="USER_LOGIN",
    message="Usuário fez login com sucesso",
    object="auth_service",
    tags=["auth", "success", "production"],
    user_id=12345,
    session_id="sess_abc123",
    ip_address="192.168.1.100"
)

# Capturar erros automaticamente
@client.capture_errors("payment_process")
def process_payment(amount, currency="USD"):
    if amount <= 0:
        raise ValueError("Valor inválido para pagamento")
    if currency not in ["USD", "BRL", "EUR"]:
        raise ValueError("Moeda não suportada")
    return {"status": "success", "amount": amount}

# Enviar erro contextualizado
try:
    process_payment(-100)
except Exception as e:
    client.send_error(
        e, 
        context="payment_validation",
        user_id=12345,
        order_id="ord_789",
        additional_data={"attempted_amount": -100}
    )
```

#### Handler Global de Exceções
```python
import sys
from mentorstec import EventHubClient

client = EventHubClient.create_azure_client("production-app", "critical-events", "global")

def global_exception_handler(exc_type, exc_value, exc_traceback):
    import traceback
    client.send_event(
        event_type="CRITICAL_ERROR",
        message=str(exc_value),
        obs="".join(traceback.format_exception(exc_type, exc_value, exc_traceback)),
        object="uncaught_exception",
        tags=["critical", "uncaught", exc_type.__name__],
        severity="HIGH"
    )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = global_exception_handler
```

### 🗄️ Dremio - Data Virtualization

```python
from mentorstec import Dremio

# Inicializar cliente Dremio
dremio = Dremio(
    host="dremio.company.com",
    port=9047,
    username="data_analyst",
    password="secure_password"
)

# Autenticar
if dremio.authenticate():
    print("✅ Conectado ao Dremio com sucesso")
    
    # Consulta SQL genérica - método central
    sales_data = dremio.execute_sql("""
        SELECT 
            region,
            product_category,
            SUM(revenue) as total_revenue,
            COUNT(orders) as total_orders,
            AVG(order_value) as avg_order_value
        FROM sales.fact_orders 
        WHERE order_date >= '2024-01-01'
        GROUP BY region, product_category
        ORDER BY total_revenue DESC
        LIMIT 100
    """)
    
    if sales_data:
        print(f"📊 Encontrados {len(sales_data.get('rows', []))} registros")
        
    # Listar tabelas em um path
    tables = dremio.get_tables("sales")
    print(f"📁 Tabelas disponíveis: {tables}")
    
    # Obter metadados de uma tabela
    metadata = dremio.get_table_metadata("sales.fact_orders")
    if metadata:
        print(f"🔍 Colunas: {[col['name'] for col in metadata.get('columns', [])]}")
    
    # Query com parâmetros para análise avançada
    customer_analysis = dremio.execute_sql("""
        WITH customer_metrics AS (
            SELECT 
                customer_id,
                COUNT(DISTINCT order_id) as total_orders,
                SUM(order_value) as lifetime_value,
                AVG(order_value) as avg_order_value,
                MAX(order_date) as last_order_date
            FROM sales.fact_orders 
            WHERE customer_id IS NOT NULL
            GROUP BY customer_id
        )
        SELECT 
            CASE 
                WHEN lifetime_value > 10000 THEN 'VIP'
                WHEN lifetime_value > 5000 THEN 'Premium'
                WHEN lifetime_value > 1000 THEN 'Regular'
                ELSE 'New'
            END as customer_tier,
            COUNT(*) as customer_count,
            AVG(lifetime_value) as avg_lifetime_value,
            AVG(total_orders) as avg_orders_per_customer
        FROM customer_metrics
        GROUP BY 1
        ORDER BY avg_lifetime_value DESC
    """)
```

### 📊 Power BI - Datasets e Dataflows

```python
from mentorstec import PowerBi

# Inicializar com variável do Airflow
powerbi = PowerBi("powerbi_production_config")

# Ou configuração manual
project_config = [{
    'api': {
        'authority': 'https://login.microsoftonline.com/your-tenant-id',
        'resource': 'https://analysis.windows.net/powerbi/api',
        'powerbi': 'https://api.powerbi.com/v1.0/myorg'
    },
    'credentials': {
        'client': 'your-application-client-id',
        'usr': 'powerbi-service@company.com',
        'pass': 'service-account-password'
    },
    'datasets': [{
        'group_id': 'f089354e-8366-4e18-aea3-4cb4a3a50b48',
        'datasets': [
            {'tag': 'sales_dashboard', 'id': 'cfafbeb1-8037-4d0c-896e-a46fb27ff229'},
            {'tag': 'financial_report', 'id': '3d9b93c6-7b6d-4801-a491-1738910bd1b0'},
            {'tag': 'customer_analytics', 'id': 'a1b2c3d4-e5f6-7890-ghij-klmnopqrstuv'}
        ]
    }],
    'dataflows': [{
        'group_id': 'f089354e-8366-4e18-aea3-4cb4a3a50b48',
        'dataflows': [
            {'tag': 'customer_etl', 'id': '1234abcd-ef56-7890-ghij-klmnopqrstuv'},
            {'tag': 'sales_etl', 'id': 'abcd1234-5678-90ef-ghij-klmnopqrstuv'}
        ]
    }]
}]

# Refresh de dataset específico
success = powerbi.refresh_dataset(
    tag='sales_dashboard',
    project_config=project_config,
    payload_json={
        "type": "full",
        "commitMode": "transactional",
        "applyRefreshPolicy": "false"
    }
)

if success:
    print("✅ Dashboard de vendas atualizado com sucesso")

# Refresh de dataflow
etl_success = powerbi.refresh_dataflow(
    tag='customer_etl',
    project_config=project_config
)

# Refresh em lote de todos os datasets
results = powerbi.refresh_all_datasets(project_config)
print("📊 Resultados do refresh em lote:")
for dataset_tag, result in results.items():
    status = "✅ Sucesso" if result else "❌ Falhou"
    print(f"  {dataset_tag}: {status}")

# Operação completa com controle manual
token = powerbi.get_token(project_config)
if token:
    urls = powerbi.generate_url('datasets', project_config)
    
    for tag, url in urls.items():
        print(f"🔄 Processando {tag}...")
        
        # Executa refresh e aguarda conclusão
        success = powerbi.execute(
            url=url,
            token=token,
            payload_json={
                "type": "full", 
                "commitMode": "transactional",
                "applyRefreshPolicy": "false"
            }
        )
        
        if success:
            print(f"  ✅ {tag} concluído")
        else:
            print(f"  ❌ {tag} falhou")
```

## 🎯 Integração Combinada

### Pipeline de Dados Completo
```python
from mentorstec import EventHubClient, Dremio, PowerBi
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Inicializar clientes
event_client = EventHubClient.create_azure_client("data-pipeline", "pipeline-events", "etl")
dremio = Dremio(host="dremio.company.com", port=9047, username="etl_user", password="password")
powerbi = PowerBi("powerbi_etl_config")

def run_daily_pipeline():
    """Pipeline diário de dados completo"""
    
    try:
        # 1. Log início do pipeline
        event_client.send_event(
            event_type="PIPELINE_START",
            message="Iniciando pipeline diário de dados",
            object="daily_etl",
            tags=["pipeline", "etl", "daily"]
        )
        
        # 2. Extrair dados do Dremio
        if dremio.authenticate():
            daily_metrics = dremio.execute_sql("""
                SELECT 
                    DATE(order_date) as date,
                    SUM(revenue) as daily_revenue,
                    COUNT(*) as daily_orders,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM sales.fact_orders 
                WHERE order_date >= CURRENT_DATE - INTERVAL '1' DAY
                GROUP BY 1
            """)
            
            if daily_metrics and daily_metrics.get('rows'):
                event_client.send_event(
                    event_type="DATA_EXTRACTED",
                    message=f"Extraídos {len(daily_metrics['rows'])} registros do Dremio",
                    object="dremio_extraction",
                    tags=["success", "extraction"]
                )
            else:
                raise Exception("Nenhum dado encontrado no Dremio")
        else:
            raise Exception("Falha na autenticação do Dremio")
        
        # 3. Atualizar Power BI
        projects = powerbi.get_power_bi_projects()
        refresh_results = powerbi.refresh_all_datasets(projects)
        
        successful_refreshes = sum(1 for success in refresh_results.values() if success)
        total_datasets = len(refresh_results)
        
        if successful_refreshes == total_datasets:
            event_client.send_event(
                event_type="POWERBI_SUCCESS",
                message=f"Todos os {total_datasets} datasets atualizados com sucesso",
                object="powerbi_refresh",
                tags=["success", "powerbi", "complete"]
            )
        else:
            event_client.send_event(
                event_type="POWERBI_PARTIAL",
                message=f"{successful_refreshes}/{total_datasets} datasets atualizados",
                object="powerbi_refresh",
                tags=["warning", "powerbi", "partial"],
                failed_datasets=[tag for tag, success in refresh_results.items() if not success]
            )
        
        # 4. Log sucesso do pipeline
        event_client.send_event(
            event_type="PIPELINE_SUCCESS",
            message="Pipeline diário concluído com sucesso",
            object="daily_etl",
            tags=["pipeline", "success", "complete"],
            datasets_processed=total_datasets,
            records_extracted=len(daily_metrics.get('rows', []))
        )
        
    except Exception as e:
        # Log erro detalhado
        event_client.send_error(
            e,
            context="daily_pipeline",
            tags=["pipeline", "failure", "critical"],
            pipeline_stage="data_extraction"
        )
        raise

# Executar pipeline
if __name__ == "__main__":
    run_daily_pipeline()
```

## 📊 Estrutura do Payload

### EventHub - Formato Padrão
```json
{
    "project": "meu-projeto",
    "layer": "web",
    "queue_name": "events-queue",
    "message": "Usuário fez login",
    "obs": "",
    "timestamp": "2025-01-11T10:30:45.123456Z",
    "event_type": "USER_LOGIN", 
    "object": "auth_service",
    "tags": ["auth", "success", "production"],
    "user_id": 12345,
    "session_id": "sess_abc123"
}
```

## 🧪 Testes e Qualidade

```bash
# Executar suite completa de testes
./run_tests.sh

# Apenas testes unitários
pytest tests/ -v --cov=mentorstec

# Formatação e lint
black mentorstec/
ruff check mentorstec/
mypy mentorstec/ --ignore-missing-imports
```

## 🚀 Deploy e CI/CD

### Deploy Automático
O projeto possui pipeline completa de CI/CD:

- **Push/PR para `main`**: Executa testes e deploy automático
- **TestPyPI**: Deploy automático em PRs
- **PyPI**: Deploy automático em merge para main

### Configuração de Secrets
Configure no GitHub os tokens:
- `PYPI_TOKEN`: Token do PyPI oficial
- `PYPI_TEST_TOKEN`: Token do TestPyPI

### Versionamento
Incrementar versão em `mentorstec/__init__.py`:
```python
__version__ = "0.1.4"  # Próxima versão
```

## 🔧 Extensibilidade

### Adicionando Novos Módulos
```python
# Exemplo: novo módulo para Snowflake
from mentorstec import EventHubClient

class SnowflakeClient:
    def __init__(self, connection_params):
        self.event_client = EventHubClient.create_azure_client(
            "snowflake-ops", "snowflake-events", "data"
        )
        # Sua implementação aqui
    
    def execute_query(self, query):
        try:
            # Lógica de execução
            result = self._execute(query)
            
            self.event_client.send_event(
                event_type="QUERY_SUCCESS",
                message="Query executada com sucesso",
                object="snowflake_query",
                tags=["snowflake", "success"],
                query_hash=hash(query),
                row_count=len(result)
            )
            return result
            
        except Exception as e:
            self.event_client.send_error(
                e, context="snowflake_query",
                query=query[:100]  # Primeiros 100 chars
            )
            raise
```

## 📚 Documentação Completa

- **Exemplos Avançados**: `/examples/powerbi_usage_examples.py`
- **Guias de Deploy**: `/docs/DEPLOY_GUIDE.md`
- **Guias de Teste**: `/docs/TESTING_GUIDE.md`
- **Configuração de Secrets**: `/.github/SECRETS.md`

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/nova-feature`)
3. Execute os testes (`./run_tests.sh`)
4. Commit suas mudanças (`git commit -m 'Add nova feature'`)
5. Push para a branch (`git push origin feature/nova-feature`)
6. Abra um Pull Request

## 📞 Suporte

- **Email**: diego@mentorstec.com.br
- **Issues**: [GitHub Issues](https://github.com/mentorstec/mentorstec/issues)
- **Documentação**: [GitHub Wiki](https://github.com/mentorstec/mentorstec/wiki)

---

**Mentorstec v0.1.3** - Plataforma completa de dados e logging com arquitetura modular 🚀