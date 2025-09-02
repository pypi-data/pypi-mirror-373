# 🏗️ Guia de Arquitetura - Mentorstec

Este documento detalha a arquitetura do **mentorstec**, explicando o Repository Pattern, modularidade opcional e decisões de design.

## 📋 Visão Geral

O **mentorstec** é uma plataforma centralizada de dados e logging que implementa **Repository Pattern** com arquitetura modular e dependências opcionais.

### 🎯 Objetivos de Design
- **Modularidade**: Core sempre disponível, módulos opcionais carregados sob demanda
- **Repository Pattern**: Interfaces abstratas com implementações concretas
- **Backward Compatibility**: APIs antigas mantidas durante transições
- **Extensibilidade**: Fácil adição de novos módulos e provedores
- **Production Ready**: Testes, CI/CD e distribuição automatizada

## 🏗️ Estrutura do Projeto

```
mentorstec/
├── 📦 mentorstec/                   # Core Package
│   ├── __init__.py                  #   🔑 Entry point com optional imports
│   │
│   ├── 🔄 eventhub/                 #   CORE MODULE (sempre disponível)
│   │   ├── __init__.py              #     - Exports: setup_global_hub, send_event
│   │   ├── event_hub.py             #     - Funções globais de conveniência
│   │   └── event_hub_client.py      #     - Cliente principal EventHubClient
│   │
│   ├── 🗄️ dremio/                   #   OPTIONAL MODULE (requer: requests)
│   │   ├── __init__.py              #     - Export: Dremio
│   │   └── dremio.py                #     - Cliente data virtualization
│   │
│   ├── 📊 powerbi/                  #   OPTIONAL MODULE (requer: adal+requests)
│   │   ├── __init__.py              #     - Export: PowerBi
│   │   └── powerbi.py               #     - Cliente Power BI refresh
│   │
│   ├── 🏛️ repository/               #   ABSTRACT INTERFACES
│   │   ├── __init__.py              #     - Exports: *Repository
│   │   ├── eventhub_repository.py   #     - EventHubRepository (ABC)
│   │   ├── dremio_repository.py     #     - DremioRepository (ABC)
│   │   └── powerbi_repository.py    #     - PowerBiRepository (ABC)
│   │
│   ├── ☁️ azure/                    #   AZURE IMPLEMENTATIONS
│   │   ├── __init__.py              #     - Export: AzureServiceBusRepository
│   │   └── azure_service_bus_repository.py  # - Concrete Azure impl
│   │
│   └── 🏠 lakehouse/                #   RESERVED FOR FUTURE
│       └── __init__.py              #     - Preparado para Data Lakehouse
│
├── 🧪 tests/                        # Testes unitários
├── 📚 examples/                     # Exemplos de uso
├── 📖 docs/                         # Documentação
├── ⚙️ pyproject.toml               # Configurações e dependências
├── 🚀 run_tests.sh                 # Script de testes automatizado
└── 🔄 .github/workflows/           # CI/CD pipeline
```

## 🎨 Repository Pattern Implementation

### Conceito

O **Repository Pattern** é implementado de forma que cada módulo possui:
1. **Interface Abstrata** (`*Repository`) - Define contratos
2. **Implementação Concreta** (`Class`) - Executa funcionalidades
3. **Optional Loading** - Carregado apenas se dependências existem

### Fluxo de Carregamento

```python
# mentorstec/__init__.py - Smart Loading

# 1. Core sempre disponível
from .eventhub import EventHubClient
from .repository.eventhub_repository import EventHubRepository

# 2. Módulos opcionais com graceful fallback
try:
    from .dremio import Dremio  # noqa: F401
    from .repository.dremio_repository import DremioRepository  # noqa: F401
    __all__.extend(["Dremio", "DremioRepository"])
except ImportError:
    pass  # Requests não disponível - módulo não carregado

try:
    from .powerbi import PowerBi  # noqa: F401
    from .repository.powerbi_repository import PowerBiRepository  # noqa: F401
    __all__.extend(["PowerBi", "PowerBiRepository"])
except ImportError:
    pass  # Adal não disponível - módulo não carregado
```

## 🔧 Dependências e Modularidade

### Core Dependencies (Sempre Requeridas)
```toml
dependencies = [
    "azure-servicebus>=7.0.0",
]
```

### Optional Dependencies (Sob Demanda)
```toml
[project.optional-dependencies]
powerbi = [
    "adal>=1.2.0",       # Azure AD auth
    "requests>=2.25.0",  # HTTP client
]
dremio = [
    "requests>=2.25.0",  # HTTP client apenas
]
dev = [
    "pytest>=7.0",       # Testes
    "black",              # Formatação
    "ruff",               # Linting
    "mypy",               # Type checking
    # ... outras deps de dev
]
```

### Cenários de Instalação

#### 1. **Instalação Mínima** (Core)
```bash
pip install mentorstec
```
**Disponível:**
- ✅ `EventHubClient` - Azure Service Bus
- ✅ `EventHubRepository` - Interface abstrata
- ✅ `setup_global_hub`, `send_event`, `send_error` - Funções globais
- ❌ `Dremio` - Não disponível (requests faltando)
- ❌ `PowerBi` - Não disponível (adal faltando)

#### 2. **Com Power BI**
```bash
pip install mentorstec[powerbi]
```
**Disponível:**
- ✅ Tudo do core +
- ✅ `PowerBi` - Power BI refresh client
- ✅ `PowerBiRepository` - Interface Power BI
- ❌ `Dremio` - Ainda não disponível

#### 3. **Com Dremio**
```bash
pip install mentorstec[dremio]
```
**Disponível:**
- ✅ Tudo do core +
- ✅ `Dremio` - Data virtualization client
- ✅ `DremioRepository` - Interface Dremio
- ❌ `PowerBi` - Ainda não disponível

#### 4. **Instalação Completa**
```bash
pip install mentorstec[powerbi,dremio]
```
**Disponível:**
- ✅ **Todos os módulos**

## 🏛️ Abstract Repositories (Interfaces)

### EventHubRepository
```python
class EventHubRepository(ABC):
    """Interface para event logging systems"""
    
    @abstractmethod
    def event_handler(self, **kwargs: Any) -> None:
        """Processar evento"""
        pass
        
    @classmethod
    def build_payload(cls, **kwargs: Any) -> Dict[str, Any]:
        """Construir payload padrão"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "project": kwargs.get("project"),
            "layer": kwargs.get("layer"),
            # ... campos padrão
        }
```

### DremioRepository
```python
class DremioRepository(ABC):
    """Interface para data virtualization systems"""
    
    @abstractmethod
    def execute_sql(self, query: str) -> Optional[Dict[str, Any]]:
        """Método central - executa qualquer SQL"""
        pass
        
    @abstractmethod
    def get_tables(self, path: str) -> List[str]:
        """Listar tabelas (usa execute_sql internamente)"""
        pass
        
    @abstractmethod  
    def authenticate(self) -> bool:
        """Autenticar no sistema"""
        pass
```

### PowerBiRepository
```python
class PowerBiRepository(ABC):
    """Interface para Power BI operations"""
    
    @abstractmethod
    def get_token(self, project_config: List[Dict[str, Any]]) -> Optional[str]:
        """Obter token JWT"""
        pass
        
    @abstractmethod
    def refresh_resource(self, url: str, token: str, payload_json: Optional[Dict] = None) -> bool:
        """Refresh dataset/dataflow"""
        pass
        
    @abstractmethod
    def execute(self, url: str, token: str, payload_json: Optional[Dict] = None) -> bool:
        """Operação completa com wait"""
        pass
```

## 🔄 Concrete Implementations

### EventHubClient (Azure Service Bus)
```python
class EventHubClient:
    """Implementação concreta para Azure Service Bus"""
    
    def __init__(self, project: str, layer: str, repository: EventHubRepository):
        self.project = project
        self.layer = layer
        self.repository = repository
    
    @classmethod
    def create_azure_client(cls, project: str, queue_name: str, layer: str = "undefined"):
        """Factory method - cria client com Azure Service Bus"""
        connection_string = os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("Azure Service Bus connection string é obrigatória")
            
        # Usa implementação concreta Azure
        azure_repo = AzureServiceBusRepository(connection_string, queue_name)
        return cls(project, layer, azure_repo)
```

### Dremio (Data Virtualization)
```python
class Dremio(DremioRepository):
    """Implementação concreta para Dremio"""
    
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
    def execute_sql(self, query: str) -> Optional[Dict[str, Any]]:
        """Método central - todos os outros métodos usam este"""
        # Implementação com requests
        response = requests.post(
            url=f"http://{self.host}:{self.port}/apiv2/sql",
            json={"sql": query},
            headers=self.headers
        )
        return response.json() if response.ok else None
        
    def get_tables(self, path: str) -> List[str]:
        """Usa execute_sql() internamente"""
        result = self.execute_sql(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{path}'")
        return [row['TABLE_NAME'] for row in result.get('rows', [])] if result else []
```

### PowerBi (Power BI Integration)
```python
class PowerBi(PowerBiRepository):
    """Implementação concreta para Power BI"""
    
    def __init__(self, airflow_variable: Optional[str] = None):
        self.airflow_variable = airflow_variable
        
    def get_token(self, project_config: List[Dict[str, Any]]) -> Optional[str]:
        """Autenticação via ADAL"""
        context = adal.AuthenticationContext(authority=authority_url)
        token = context.acquire_token_with_username_password(...)
        return token.get('accessToken')
        
    def refresh_resource(self, url: str, token: str, payload_json: Optional[Dict] = None) -> bool:
        """Refresh via Power BI REST API"""
        response = requests.post(
            url=f'{url}/refreshes',
            headers={'Authorization': f'Bearer {token}'},
            json=payload_json
        )
        return response.status_code in [200, 202]
```

## 🚀 Factory Patterns e Entry Points

### Smart Entry Point
```python
# mentorstec/__init__.py

# 1. Core sempre exportado
__all__ = [
    "EventHubClient",
    "EventHubRepository", 
    "setup_global_hub",
    "send_event",
    "send_error",
    "capture_errors",
]

# 2. Módulos opcionais adicionados dinamicamente
try:
    from .dremio import Dremio
    from .repository.dremio_repository import DremioRepository
    __all__.extend(["Dremio", "DremioRepository"])
except ImportError:
    pass

try:
    from .powerbi import PowerBi  
    from .repository.powerbi_repository import PowerBiRepository
    __all__.extend(["PowerBi", "PowerBiRepository"])
except ImportError:
    pass
```

### Factory Methods
```python
# EventHub Factory
EventHubClient.create_azure_client("project", "queue", "layer")

# Dremio Factory  
Dremio("host", 9047, "user", "pass")

# PowerBI Factory
PowerBi("airflow_variable_name")
```

## 🎯 Usage Patterns

### 1. **Direct Usage** (Usuários Finais)
```python
# Core sempre funciona
from mentorstec import EventHubClient
client = EventHubClient.create_azure_client("proj", "queue", "web")
client.send_event(event_type="LOGIN", message="User logged in")

# Opcionais carregados se disponíveis
from mentorstec import Dremio, PowerBi
dremio = Dremio("host", 9047, "user", "pass")
powerbi = PowerBi("config_var")
```

### 2. **Repository Pattern** (Desenvolvedores Avançados)
```python
# Usando interfaces para flexibilidade
from mentorstec import EventHubRepository, DremioRepository

def process_data(event_repo: EventHubRepository, data_repo: DremioRepository):
    """Função genérica que funciona com qualquer implementação"""
    data = data_repo.execute_sql("SELECT * FROM orders")
    
    for row in data.get('rows', []):
        event_repo.event_handler(
            event_type="DATA_PROCESSED",
            message="Row processed",
            row_id=row['id']
        )
```

### 3. **Pipeline Integration** (Data Engineers)
```python
from mentorstec import EventHubClient, Dremio, PowerBi

# Pipeline completo
event_client = EventHubClient.create_azure_client("pipeline", "events", "etl")
dremio = Dremio("dremio.company.com", 9047, "etl_user", "password")  
powerbi = PowerBi("powerbi_etl_config")

def daily_pipeline():
    # Log início
    event_client.send_event(event_type="PIPELINE_START", message="Starting daily ETL")
    
    # Extrair dados
    data = dremio.execute_sql("SELECT * FROM daily_sales WHERE date = CURRENT_DATE")
    event_client.send_event(event_type="DATA_EXTRACTED", message=f"Extracted {len(data.get('rows', []))} rows")
    
    # Refresh Power BI
    projects = powerbi.get_power_bi_projects()
    results = powerbi.refresh_all_datasets(projects)
    
    # Log resultado
    if all(results.values()):
        event_client.send_event(event_type="PIPELINE_SUCCESS", message="Pipeline completed successfully")
    else:
        event_client.send_event(event_type="PIPELINE_PARTIAL", message="Some refreshes failed")
```

## 🔧 Extensibility Guide

### Adicionando Novo Módulo (ex: Snowflake)

#### 1. Criar Interface Abstrata
```python
# mentorstec/repository/snowflake_repository.py
from abc import ABC, abstractmethod

class SnowflakeRepository(ABC):
    @abstractmethod
    def execute_query(self, query: str) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def get_warehouses(self) -> List[str]:
        pass
```

#### 2. Implementação Concreta
```python
# mentorstec/snowflake/snowflake.py
import snowflake.connector
from ..repository.snowflake_repository import SnowflakeRepository

class Snowflake(SnowflakeRepository):
    def __init__(self, account: str, user: str, password: str):
        self.account = account
        self.user = user
        self.password = password
        
    def execute_query(self, query: str) -> Optional[Dict[str, Any]]:
        conn = snowflake.connector.connect(
            account=self.account,
            user=self.user,
            password=self.password
        )
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
```

#### 3. Adicionar Dependência Opcional
```toml
# pyproject.toml
[project.optional-dependencies]
snowflake = [
    "snowflake-connector-python>=3.0.0",
]
```

#### 4. Atualizar Entry Point
```python
# mentorstec/__init__.py
try:
    from .snowflake import Snowflake
    from .repository.snowflake_repository import SnowflakeRepository
    __all__.extend(["Snowflake", "SnowflakeRepository"])
except ImportError:
    pass
```

#### 5. Usage
```python
# Usuário instala e usa
pip install mentorstec[snowflake]

from mentorstec import Snowflake
snowflake = Snowflake("account", "user", "pass")
data = snowflake.execute_query("SELECT * FROM orders")
```

## 🧪 Testing Strategy

### Test Architecture
```python
# tests/test_integration.py
def test_optional_modules_graceful_import():
    """Test que módulos opcionais carregam graciosamente"""
    import mentorstec
    
    # Core sempre deve estar disponível
    assert hasattr(mentorstec, 'EventHubClient')
    assert hasattr(mentorstec, 'EventHubRepository')
    
    # Opcionais dependem das dependências
    has_dremio = hasattr(mentorstec, 'Dremio')
    has_powerbi = hasattr(mentorstec, 'PowerBi')
    
    # Pelo menos core deve funcionar
    assert True  # Test passa se chegou até aqui
```

### Mock Testing para Módulos Opcionais
```python
# tests/test_dremio.py
@pytest.mark.skipif(not HAS_REQUESTS, reason="requests not installed")
class TestDremio:
    @patch('requests.post')
    def test_execute_sql(self, mock_post):
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {"rows": []}
        
        dremio = Dremio("host", 9047, "user", "pass")
        result = dremio.execute_sql("SELECT 1")
        
        assert result is not None
```

## 📊 Decision Log

### Why Repository Pattern?
1. **Testability**: Fácil mock de dependências externas
2. **Flexibility**: Trocar implementações sem mudar código cliente  
3. **Separation of Concerns**: Interface vs Implementação
4. **Future-proof**: Adicionar provedores sem quebrar código existente

### Why Optional Dependencies?
1. **Lightweight Core**: Usuários que só precisam de EventHub não instalam dependências desnecessárias
2. **Graceful Degradation**: Pacote funciona mesmo com dependências faltantes
3. **Production Ready**: Deploy não falha por dependência opcional faltante
4. **User Choice**: Instalam apenas o que precisam

### Why Modular Structure?
1. **Maintainability**: Cada módulo é independente
2. **Team Development**: Diferentes equipes podem trabalhar em módulos diferentes
3. **Deployment**: Módulos podem ter ciclos de release independentes
4. **Performance**: Import apenas do necessário

## 🔮 Future Roadmap

### Planned Modules
```
mentorstec/
├── lakehouse/          # 🏠 Data Lakehouse (Delta Lake, Iceberg)
├── streaming/          # 🌊 Stream Processing (Kafka, EventHub Streams)  
├── ml/                 # 🤖 ML Operations (MLflow, Kubeflow)
├── monitoring/         # 📊 APM (DataDog, New Relic)
└── security/           # 🔐 Security (Vault, Key Management)
```

### Evolution Path
1. **v0.1.x**: Core + Dremio + PowerBI
2. **v0.2.x**: Add Lakehouse module
3. **v0.3.x**: Add Streaming module
4. **v0.4.x**: Add ML module
5. **v1.0.x**: Stable API, full ecosystem

---

🏗️ **Mentorstec v0.1.3** - Arquitetura robusta e extensível com Repository Pattern modular! 🚀