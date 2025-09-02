# 🧪 Guia de Testes e Qualidade de Código - Mentorstec

Este documento fornece instruções completas para executar todos os testes de qualidade e validações que são executadas na pipeline de CI/CD para o pacote **mentorstec** com suporte para EventHub, Dremio e Power BI.

## 📋 Pré-requisitos

### Instalação das Ferramentas

```bash
# Instalar todas as dependências de desenvolvimento
pip install -e ".[dev]"

# Para desenvolvimento completo (com módulos opcionais)
pip install -e ".[dev,powerbi,dremio]"

# OU instalar ferramentas individualmente
pip install black ruff mypy pytest pytest-cov
```

### Estrutura do Projeto
```
mentorstec/
├── mentorstec/                  # 📦 Código fonte
│   ├── __init__.py              #   - Entry point com optional imports
│   ├── eventhub/                #   - 🔄 Azure Service Bus (core)
│   │   ├── event_hub.py
│   │   └── event_hub_client.py
│   ├── dremio/                  #   - 🗄️ Data virtualization (opcional)
│   │   └── dremio.py
│   ├── powerbi/                 #   - 📊 Power BI integration (opcional)
│   │   └── powerbi.py
│   ├── repository/              #   - 🏛️ Abstract interfaces
│   │   ├── eventhub_repository.py
│   │   ├── dremio_repository.py
│   │   └── powerbi_repository.py
│   ├── azure/                   #   - ☁️ Azure implementations
│   └── lakehouse/               #   - 🏠 Reserved for future
├── tests/                       # 🧪 Testes
├── examples/                    # 📚 Exemplos de uso
├── docs/                        # 📖 Documentação
├── pyproject.toml              # ⚙️ Configurações
└── run_tests.sh                # 🚀 Script de testes automatizado
```

## 🎯 Bateria Completa de Testes

### Script Automatizado

**O arquivo `run_tests.sh` já existe e está configurado:**

```bash
#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para prints coloridos
print_step() { echo -e "${BLUE}🔍 $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Contador de falhas
FAILURES=0

echo "🚀 Iniciando bateria completa de testes e qualidade"
echo "================================================="

# 1. FORMATAÇÃO COM BLACK
print_step "1. Verificando formatação do código com Black"
if python3 -m black --check mentorstec/; then
    print_success "Black: Formatação correta"
else
    print_error "Black: Código precisa ser formatado"
    echo "💡 Execute: python3 -m black mentorstec/"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# 2. QUALIDADE COM RUFF
print_step "2. Analisando qualidade do código com Ruff"
if python3 -m ruff check mentorstec/; then
    print_success "Ruff: Qualidade do código OK"
else
    print_error "Ruff: Problemas de qualidade encontrados"
    echo "💡 Execute: python3 -m ruff check --fix mentorstec/"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# 3. TIPOS COM MYPY
print_step "3. Verificando anotações de tipo com MyPy"
if python3 -m mypy mentorstec/ --ignore-missing-imports; then
    print_success "MyPy: Tipos corretos"
else
    print_warning "MyPy: Alguns tipos podem estar faltando (não crítico)"
fi
echo ""

# 4. TESTES COM PYTEST
print_step "4. Executando testes com PyTest"
if python3 -m pytest tests/ -v --cov=mentorstec --cov-report=term --cov-report=html; then
    print_success "PyTest: Todos os testes passaram"
else
    print_error "PyTest: Alguns testes falharam"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# 5. VERIFICAÇÃO DE IMPORTS
print_step "5. Verificando se imports estão funcionando"
if python3 -c "import mentorstec; print('✅ Imports OK')"; then
    print_success "Imports: Funcionando corretamente"
else
    print_error "Imports: Problemas encontrados"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# RESUMO FINAL
echo "================================================="
if [ $FAILURES -eq 0 ]; then
    print_success "🎉 TODOS OS TESTES PASSARAM!"
    echo "✅ Código pronto para produção"
    exit 0
else
    print_error "❌ $FAILURES teste(s) falharam"
    echo "🔧 Corrija os problemas acima antes do deploy"
    exit 1
fi
```

**Uso:**
```bash
# Tornar executável (se necessário)
chmod +x run_tests.sh

# Executar suite completa
./run_tests.sh
```

## 🔧 Comandos Individuais

### 1. 🎨 Formatação (Black)

**Verificar formatação:**
```bash
python3 -m black --check mentorstec/
```

**Formatar código:**
```bash
python3 -m black mentorstec/
```

**Configuração no `pyproject.toml`:**
```toml
[tool.black]
line-length = 88
target-version = ["py38"]
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.mypy_cache
  | build
  | dist
)/
'''
```

### 2. 🔍 Qualidade (Ruff)

**Verificar qualidade:**
```bash
python3 -m ruff check mentorstec/
```

**Corrigir automaticamente:**
```bash
python3 -m ruff check --fix mentorstec/
```

**Configuração no `pyproject.toml`:**
```toml
[tool.ruff]
target-version = "py38"
line-length = 88

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]
```

### 3. 🏷️ Tipos (MyPy)

**Verificar tipos:**
```bash
python3 -m mypy mentorstec/ --ignore-missing-imports
```

**Verificação rigorosa:**
```bash
python3 -m mypy mentorstec/ --strict
```

**Configuração no `pyproject.toml`:**
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
```

### 4. 🧪 Testes (Pytest)

**Executar todos os testes:**
```bash
python3 -m pytest tests/ -v
```

**Com cobertura:**
```bash
python3 -m pytest tests/ -v --cov=mentorstec --cov-report=term
```

**Com relatório HTML:**
```bash
python3 -m pytest tests/ -v --cov=mentorstec --cov-report=html
# Ver relatório em htmlcov/index.html
```

**Configuração no `pyproject.toml`:**
```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = [
    "tests",
]
```

## 🔍 Testes Específicos por Módulo

### EventHub (Core - Sempre Testado)
```bash
# Testes específicos do EventHub
python3 -m pytest tests/test_event_hub_client.py -v

# Verificar import core
python3 -c "from mentorstec import EventHubClient; print('✅ EventHub OK')"

# Testar criação de client
python3 -c "
from mentorstec import EventHubClient
import os
os.environ['AZURE_SERVICE_BUS_CONNECTION_STRING'] = 'test-connection'
try:
    client = EventHubClient.create_azure_client('test', 'queue', 'layer')
    print('✅ EventHub client criado')
except Exception as e:
    print(f'ℹ️ Esperado em ambiente de teste: {e}')
"
```

### Dremio (Opcional - Testado se requests disponível)
```bash
# Verificar se Dremio está disponível
python3 -c "
try:
    from mentorstec import Dremio
    print('✅ Dremio disponível')
    
    # Testar inicialização
    dremio = Dremio('localhost', 9047, 'user', 'pass')
    print('✅ Dremio client criado')
except ImportError:
    print('ℹ️ Dremio não disponível (requests não instalado)')
except Exception as e:
    print(f'ℹ️ Dremio disponível mas erro de conexão esperado: {e}')
"

# Instalar dependência e testar
pip install requests
python3 -c "from mentorstec import Dremio; print('✅ Dremio com requests OK')"
```

### Power BI (Opcional - Testado se adal+requests disponíveis)
```bash
# Verificar se PowerBI está disponível
python3 -c "
try:
    from mentorstec import PowerBi
    print('✅ PowerBI disponível')
    
    # Testar inicialização
    powerbi = PowerBi('config_var')
    print('✅ PowerBI client criado')
except ImportError as e:
    print(f'ℹ️ PowerBI não disponível: {e}')
except Exception as e:
    print(f'ℹ️ PowerBI disponível mas erro esperado: {e}')
"

# Instalar dependências e testar
pip install adal requests
python3 -c "from mentorstec import PowerBi; print('✅ PowerBI com dependências OK')"
```

### Repositórios (Interfaces Abstratas)
```bash
# Testar imports das interfaces
python3 -c "
from mentorstec import EventHubRepository, DremioRepository, PowerBiRepository
print('✅ Repositórios abstratos OK')
print(f'EventHub: {EventHubRepository}')
print(f'Dremio: {DremioRepository}') 
print(f'PowerBI: {PowerBiRepository}')
"
```

## 📊 Interpretação dos Resultados

### ✅ **Sucesso - Pipeline Passará**
- **Black**: `All done! ✨ 🍰 ✨` ou `X files left unchanged`
- **Ruff**: `All checks passed!`
- **MyPy**: `Success: no issues found` (ou apenas warnings)
- **Pytest**: `X passed, 0 failed`
- **Imports**: `✅ Imports OK`

### ❌ **Falha - Pipeline Falhará**
- **Black**: `would reformat X files`
- **Ruff**: `Found X errors`
- **Pytest**: `X failed, Y passed`
- **Imports**: Qualquer exception

### ⚠️ **Avisos - Pipeline Passa mas com Warnings**
- **MyPy**: 
  - `Library stubs not installed for "requests"`
  - `Returning Any from function`
  - Estas são não-críticas e não bloqueiam o deploy

### 📈 **Cobertura de Testes**
```bash
# Verificar cobertura atual
python3 -m pytest tests/ --cov=mentorstec --cov-report=term

# Relatório esperado:
# Name                           Stmts   Miss  Cover
# --------------------------------------------------
# mentorstec/__init__.py            16      4    75%
# mentorstec/eventhub/...           34      0   100%  ✅ Core bem coberto
# mentorstec/dremio/...            126    107    15%  ⚠️ Opcional - baixa cobertura OK
# mentorstec/powerbi/...           167    161     4%  ⚠️ Opcional - baixa cobertura OK
# --------------------------------------------------
# TOTAL                            435    308    29%  ✅ Aceitável para módulos opcionais
```

## 🚀 Integração com CI/CD

### GitHub Actions - Pipeline Equivalente

**O arquivo `.github/workflows/pipeline.yml` executa os mesmos comandos:**

```yaml
# Testes de qualidade
- name: 🎨 Verificar formatação
  run: |
    echo "🎨 Verificando formatação..."
    black --check mentorstec/ || (echo "❌ Execute: black mentorstec/" && exit 1)

- name: 🔍 Análise de código
  run: |
    echo "🔍 Analisando código..."
    ruff check mentorstec/

- name: 🏷️ Verificação de tipos
  run: |
    echo "🏷️ Verificando tipos..."
    mypy mentorstec/ --ignore-missing-imports || echo "⚠️ Avisos de tipo"

- name: 🧪 Executar testes
  run: |
    echo "🧪 Executando testes..."
    pytest tests/ -v --cov=mentorstec --cov-report=xml

- name: 🔍 Verificar imports
  run: |
    echo "🔍 Testando imports..."
    python -c "import mentorstec; print('✅ Imports OK')"
```

### Executar Pipeline Localmente

```bash
# Simular exatamente o que a pipeline faz
python3 -m black --check mentorstec/              # ✅ Deve passar
python3 -m ruff check mentorstec/                 # ✅ Deve passar
python3 -m mypy mentorstec/ --ignore-missing-imports  # ⚠️ Warnings OK
python3 -m pytest tests/ -v --cov=mentorstec --cov-report=xml  # ✅ Deve passar
python3 -c "import mentorstec; print('✅ Imports OK')"  # ✅ Deve passar
```

## 🔧 Resolução de Problemas

### Erro: "black: command not found"
```bash
# Instalar black
pip install black
# OU instalar tudo
pip install -e ".[dev]"
```

### Erro: "No module named 'mentorstec'"
```bash
# Instalar em modo desenvolvimento
pip install -e .
# OU com dependências opcionais
pip install -e ".[dev,powerbi,dremio]"
```

### Erro: Import de módulo opcional falha
```bash
# Normal - módulos opcionais só funcionam com dependências
pip install requests  # Para Dremio
pip install adal      # Para PowerBI

# OU instalar tudo junto
pip install mentorstec[powerbi,dremio]
```

### Erro: Mock não funciona nos testes
```bash
# Verificar se o patch está no local correto
@patch('mentorstec.eventhub.event_hub_client.AzureServiceBusRepository')  # ✅ Correto
@patch('mentorstec.azure.azure_service_bus_repository.AzureServiceBusRepository')  # ❌ Incorreto
```

### Erro: MyPy - Dependências de tipo faltantes
```bash
# Instalar stubs de tipos (opcional)
pip install types-requests

# OU ignorar (configurado no pyproject.toml)
mypy mentorstec/ --ignore-missing-imports
```

### Erro: Cobertura muito baixa
**Não é um erro!** Para módulos opcionais:
- **EventHub**: Core bem coberto (~100%)
- **Dremio/PowerBI**: Baixa cobertura OK (dependências opcionais)
- **Total**: ~29% é aceitável devido à natureza modular

## 📈 Testando Diferentes Cenários

### Cenário 1: Instalação Mínima (Core)
```bash
# Simular usuário que só instala o core
pip install mentorstec

python3 -c "
import mentorstec
print(f'Disponível: {[x for x in dir(mentorstec) if not x.startswith(\"_\")]}')
# Deve mostrar: EventHubClient, EventHubRepository, etc.
# NÃO deve mostrar: Dremio, PowerBi (dependências faltantes)
"
```

### Cenário 2: Com PowerBI
```bash
pip install mentorstec[powerbi]

python3 -c "
from mentorstec import PowerBi, PowerBiRepository
print('✅ PowerBI funcionando')
"
```

### Cenário 3: Com Dremio
```bash
pip install mentorstec[dremio]

python3 -c "
from mentorstec import Dremio, DremioRepository  
print('✅ Dremio funcionando')
"
```

### Cenário 4: Instalação Completa
```bash
pip install mentorstec[powerbi,dremio]

python3 -c "
from mentorstec import EventHubClient, Dremio, PowerBi
from mentorstec import EventHubRepository, DremioRepository, PowerBiRepository
print('✅ Todos os módulos funcionando')
"
```

## 🎯 Checklist de Qualidade

Antes de fazer commit ou deploy:

### ✅ **Testes Obrigatórios (Devem Passar)**
- [ ] `python3 -m black --check mentorstec/` - ✅ Formatação
- [ ] `python3 -m ruff check mentorstec/` - ✅ Qualidade
- [ ] `python3 -m pytest tests/ -v` - ✅ Testes unitários
- [ ] `python3 -c "import mentorstec"` - ✅ Import básico

### ⚠️ **Testes com Warnings (Podem Ter Avisos)**
- [ ] `python3 -m mypy mentorstec/ --ignore-missing-imports` - ⚠️ Tipos

### 📊 **Testes de Cobertura (Para Informação)**
- [ ] Core EventHub bem coberto (>80%)
- [ ] Módulos opcionais podem ter baixa cobertura
- [ ] Total >20% (devido à modularidade)

### 🔍 **Testes de Módulos Opcionais**
- [ ] Graceful imports (não falha se dependência ausente)
- [ ] Funciona quando dependências estão presentes
- [ ] Estrutura Repository Pattern correta

## 🚨 Pipeline CI/CD - Status

**Status que devem ser GREEN para deploy:**
- 🟢 **Formatação (Black)**: Código formatado corretamente
- 🟢 **Qualidade (Ruff)**: Sem problemas de qualidade críticos
- 🟢 **Testes (PyTest)**: Todos os testes unitários passando
- 🟢 **Imports**: Importações básicas funcionando
- 🟢 **Build**: Pacote constrói sem erros

**Status que podem ser YELLOW (não bloqueiam):**
- 🟡 **Tipos (MyPy)**: Warnings sobre stubs faltantes
- 🟡 **Cobertura**: Baixa em módulos opcionais

**Comandos críticos para deploy:**
```bash
# Estes 4 comandos DEVEM passar:
python3 -m black --check mentorstec/              # ✅ Crítico
python3 -m ruff check mentorstec/                 # ✅ Crítico  
python3 -m pytest tests/ -v                       # ✅ Crítico
python3 -c "import mentorstec"                     # ✅ Crítico

# Este pode ter warnings (não bloqueia):
python3 -m mypy mentorstec/ --ignore-missing-imports    # ⚠️ Informativo
```

## 🎉 Executar Suite Completa

**Comando único que simula toda a pipeline:**
```bash
# Execute isto antes de qualquer commit/deploy
./run_tests.sh

# Se tudo passar:
# 🎉 TODOS OS TESTES PASSARAM!
# ✅ Código pronto para produção

# Então pode fazer o build e deploy:
python3 -m build
python3 -m twine check dist/*
```

---

🧪 **Com este guia, a pipeline de CI/CD passará consistentemente e o pacote será deployado com qualidade garantida!**

**Mentorstec v0.1.3** - Testes robustos para arquitetura modular com Repository Pattern! 🚀