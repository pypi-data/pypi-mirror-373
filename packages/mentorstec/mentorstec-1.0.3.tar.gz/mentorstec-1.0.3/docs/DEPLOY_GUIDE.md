# 🚀 Guia Completo de Deploy para PyPI - Mentorstec

Este documento fornece instruções passo a passo para fazer o build e deploy do pacote `mentorstec` para o PyPI, incluindo os módulos opcionais Dremio e Power BI.

## 📋 Pré-requisitos

### 1. Contas Necessárias
- **PyPI**: https://pypi.org/account/register/
- **TestPyPI** (opcional, para testes): https://test.pypi.org/account/register/

### 2. Ferramentas Necessárias
```bash
# Instalar dependências de build
pip install --upgrade pip
pip install build twine hatchling

# Para desenvolvimento completo
pip install -e ".[dev,powerbi,dremio]"
```

## 🏗️ Arquitetura do Pacote

O `mentorstec` implementa **Repository Pattern** com módulos opcionais:

```
mentorstec/
├── eventhub/               # 🔄 Core (sempre disponível)
├── dremio/                 # 🗄️ Opcional - requer requests
├── powerbi/                # 📊 Opcional - requer adal+requests
├── repository/             # 🏛️ Abstract interfaces
├── azure/                  # ☁️ Azure implementations
└── lakehouse/              # 🏠 Preparado para expansão
```

### Dependências
- **Core**: `azure-servicebus>=7.0.0`
- **PowerBI**: `adal>=1.2.0`, `requests>=2.25.0`
- **Dremio**: `requests>=2.25.0`

## 🔐 Configuração de Tokens

### 1. Criar Token no PyPI

**Para PyPI (Produção):**
1. Acesse: https://pypi.org/manage/account/token/
2. Clique em **"Add API token"**
3. Preencha:
   - **Token name**: `mentorstec-deploy`
   - **Scope**: Selecione "Entire account" ou específico para o projeto
4. Clique **"Add token"**
5. **COPIE O TOKEN** (formato: `pypi-AgEIcHlwaS5vcmcCJ...`)
6. **⚠️ IMPORTANTE**: Salve em local seguro, ele não será mostrado novamente

**Para TestPyPI (Testes):**
1. Acesse: https://test.pypi.org/manage/account/token/
2. Siga os mesmos passos acima
3. Token será similar: `pypi-AgEIcHlwaS5vcmcCJ...`

### 2. Configurar Tokens Localmente

**Opção 1 - Variáveis de Ambiente (Recomendado):**
```bash
# Para PyPI
export PYPI_TOKEN="pypi-AgEIcHlwaS5vcmcCJ...SEU_TOKEN_AQUI"

# Para TestPyPI (opcional)
export PYPI_TEST_TOKEN="pypi-AgEIcHlwaS5vcmcCJ...SEU_TOKEN_TESTPYPI_AQUI"
```

**Opção 2 - Arquivo ~/.pypirc:**
```bash
# Criar arquivo de configuração
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...SEU_TOKEN_AQUI

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...SEU_TOKEN_TESTPYPI_AQUI
EOF

# Proteger o arquivo
chmod 600 ~/.pypirc
```

## 📦 Build e Deploy Manual

### 1. Preparação

```bash
# Navegar para o diretório do projeto
cd /opt/pyMentors

# Verificar se está na branch correta
git branch
git status

# Limpar builds anteriores
rm -rf dist/ build/ *.egg-info/ htmlcov/
```

### 2. Verificar Testes de Qualidade

**Execute a suite completa de testes:**
```bash
# Pipeline completa de qualidade
./run_tests.sh

# Deve mostrar:
# ✅ Black: Formatação correta
# ✅ Ruff: Qualidade do código OK
# ⚠️ MyPy: Alguns tipos podem estar faltando (não crítico)
# ✅ PyTest: Todos os testes passaram
# ✅ Imports: Funcionando corretamente
# 🎉 TODOS OS TESTES PASSARAM!
```

### 3. Atualizar Versão

**Edite o arquivo `mentorstec/__init__.py`:**
```python
# Antes
__version__ = "0.1.3"

# Depois (exemplo para versão 0.1.4)
__version__ = "0.1.4"
```

**Commit da nova versão:**
```bash
git add mentorstec/__init__.py
git commit -m "🔖 Bump version to 0.1.4"
git push origin main
```

### 4. Build do Pacote

```bash
# Fazer build do pacote
python3 -m build

# Verificar arquivos gerados
ls -la dist/
# Você deve ver:
# - mentorstec-0.1.4.tar.gz (source distribution)
# - mentorstec-0.1.4-py3-none-any.whl (wheel distribution)
```

### 5. Validar Pacote

```bash
# Verificar se o pacote está correto
python3 -m twine check dist/*

# Resultado esperado:
# Checking dist/mentorstec-0.1.4.tar.gz: PASSED
# Checking dist/mentorstec-0.1.4-py3-none-any.whl: PASSED
```

### 6. Deploy para TestPyPI (Recomendado primeiro)

```bash
# Upload para TestPyPI
twine upload --repository testpypi dist/*

# OU usando variável de ambiente
TWINE_USERNAME=__token__ TWINE_PASSWORD=$PYPI_TEST_TOKEN twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

**Testar instalação do TestPyPI:**
```bash
# Criar ambiente virtual para teste
python3 -m venv test_env
source test_env/bin/activate  # Linux/Mac
# test_env\Scripts\activate     # Windows

# Instalar do TestPyPI (apenas core)
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mentorstec

# Testar módulos opcionais
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mentorstec[powerbi,dremio]

# Testar importações
python3 -c "
from mentorstec import EventHubClient
print('✅ EventHub OK')

try:
    from mentorstec import Dremio
    print('✅ Dremio OK')
except ImportError:
    print('ℹ️ Dremio não disponível (dependências faltantes)')

try:
    from mentorstec import PowerBi
    print('✅ PowerBI OK') 
except ImportError:
    print('ℹ️ PowerBI não disponível (dependências faltantes)')
"

# Limpar teste
deactivate
rm -rf test_env/
```

### 7. Deploy para PyPI (Produção)

```bash
# Upload para PyPI oficial
twine upload dist/*

# OU usando variável de ambiente
TWINE_USERNAME=__token__ TWINE_PASSWORD=$PYPI_TOKEN twine upload dist/*
```

**Verificar no PyPI:**
- Acesse: https://pypi.org/project/mentorstec/
- Confirme que a nova versão está disponível
- Teste os diferentes tipos de instalação:
  ```bash
  pip install mentorstec                    # Core
  pip install mentorstec[powerbi]          # Com PowerBI
  pip install mentorstec[dremio]           # Com Dremio
  pip install mentorstec[powerbi,dremio]   # Completo
  ```

## 🚀 Deploy Automático via CI/CD

### Configuração do GitHub Actions

O projeto já possui pipeline completa configurada em `.github/workflows/pipeline.yml`:

**Fluxo automático:**
1. **PR para main**: Deploy automático no TestPyPI
2. **Merge para main**: Deploy automático no PyPI oficial

**Configurar Secrets no GitHub:**
1. Vá para **Settings** → **Secrets and variables** → **Actions**
2. Adicione os secrets:
   - `PYPI_TOKEN`: Token do PyPI oficial
   - `PYPI_TEST_TOKEN`: Token do TestPyPI

**Triggers de Deploy:**
- **TestPyPI**: Qualquer PR aberto para `main`
- **PyPI**: Push direto na `main` ou PR mergeado na `main`

### Pipeline Equivalente Manual

```bash
# Mesmos passos que o GitHub Actions executa
python3 -m black --check mentorstec/
python3 -m ruff check mentorstec/
python3 -m mypy mentorstec/ --ignore-missing-imports
python3 -m pytest tests/ -v --cov=mentorstec --cov-report=xml
python3 -c "import mentorstec; print('✅ Imports OK')"
python3 -m build
python3 -m twine check dist/*
twine upload dist/*
```

## 🛠️ Scripts Automatizados

### Script de Release Completo

**O arquivo `scripts/release.py` já existe:**
```bash
# Executar release automatizado
python3 scripts/release.py

# Ou usando o script bash se disponível
./scripts/release.sh
```

### Usando Makefile

**Criar `Makefile` se ainda não existir:**
```makefile
.PHONY: clean build test upload upload-test release help

PYTHON = python3
PIP = pip3
PACKAGE_NAME = mentorstec

help: ## Mostrar ajuda
	@echo "Comandos disponíveis para mentorstec:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

clean: ## Limpar arquivos de build
	@echo "🧹 Limpando arquivos de build..."
	rm -rf dist/ build/ *.egg-info/ htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install-dev: ## Instalar dependências completas
	@echo "📦 Instalando dependências completas..."
	$(PIP) install --upgrade pip
	$(PIP) install build twine hatchling
	$(PIP) install -e ".[dev,powerbi,dremio]"

test: ## Executar suite completa de testes
	@echo "🧪 Executando suite completa..."
	./run_tests.sh

lint: ## Verificar qualidade do código
	@echo "🔍 Verificando qualidade..."
	$(PYTHON) -m black --check mentorstec/
	$(PYTHON) -m ruff check mentorstec/
	$(PYTHON) -m mypy mentorstec/ --ignore-missing-imports

format: ## Formatar código
	@echo "🎨 Formatando código..."
	$(PYTHON) -m black mentorstec/
	$(PYTHON) -m ruff check --fix mentorstec/

build: clean ## Build do pacote
	@echo "🏗️ Fazendo build do pacote mentorstec..."
	$(PYTHON) -m build
	@echo "📄 Arquivos criados:"
	@ls -la dist/

check: build ## Validar pacote
	@echo "✅ Validando pacote..."
	$(PYTHON) -m twine check dist/*

test-imports: ## Testar imports dos módulos
	@echo "🔍 Testando imports..."
	@$(PYTHON) -c "from mentorstec import EventHubClient; print('✅ EventHub OK')"
	@$(PYTHON) -c "from mentorstec import Dremio; print('✅ Dremio OK')" 2>/dev/null || echo "ℹ️ Dremio indisponível"
	@$(PYTHON) -c "from mentorstec import PowerBi; print('✅ PowerBI OK')" 2>/dev/null || echo "ℹ️ PowerBI indisponível"

upload-test: check ## Upload para TestPyPI
	@echo "🧪 Fazendo upload para TestPyPI..."
	@if [ -z "$$PYPI_TEST_TOKEN" ]; then \
		echo "❌ PYPI_TEST_TOKEN não configurado"; \
		exit 1; \
	fi
	TWINE_USERNAME=__token__ TWINE_PASSWORD=$$PYPI_TEST_TOKEN twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload: check ## Upload para PyPI
	@echo "🚀 Fazendo upload para PyPI..."
	@if [ -z "$$PYPI_TOKEN" ]; then \
		echo "❌ PYPI_TOKEN não configurado"; \
		exit 1; \
	fi
	TWINE_USERNAME=__token__ TWINE_PASSWORD=$$PYPI_TOKEN twine upload dist/*

release: test upload ## Release completo
	@echo "🎉 Release do mentorstec concluído!"
	@$(PYTHON) -c "import mentorstec; print(f'📦 Nova versão: {mentorstec.__version__}')"
	@echo "🔗 Disponível em: https://pypi.org/project/mentorstec/"

version: ## Mostrar versão atual
	@$(PYTHON) -c "import mentorstec; print(f'Versão atual: {mentorstec.__version__}')"
```

**Usar o Makefile:**
```bash
# Ver comandos disponíveis
make help

# Release completo (recomendado)
make release

# Apenas upload para teste
make upload-test

# Build e validação
make check

# Testar imports
make test-imports
```

## 🧪 Validação de Módulos Opcionais

### Testar Instalações Diferentes

```bash
# 1. Apenas core (sempre funciona)
pip install mentorstec
python3 -c "
from mentorstec import EventHubClient
client = EventHubClient.create_azure_client('test', 'queue', 'layer')
print('✅ Core funcionando')
"

# 2. Com PowerBI
pip install mentorstec[powerbi] 
python3 -c "
from mentorstec import PowerBi
powerbi = PowerBi()
print('✅ PowerBI disponível')
"

# 3. Com Dremio
pip install mentorstec[dremio]
python3 -c "
from mentorstec import Dremio
dremio = Dremio('host', 9047, 'user', 'pass')
print('✅ Dremio disponível')
"

# 4. Instalação completa
pip install mentorstec[powerbi,dremio]
python3 -c "
from mentorstec import EventHubClient, Dremio, PowerBi
print('✅ Todos os módulos disponíveis')
print(f'EventHub: {EventHubClient}')
print(f'Dremio: {Dremio}')
print(f'PowerBI: {PowerBi}')
"
```

## 🚨 Resolução de Problemas

### Erro: "Invalid or non-existent authentication information"
```bash
# Verificar se o token está correto
echo $PYPI_TOKEN  # Deve começar com "pypi-"

# Testar token manualmente
twine upload --repository testpypi dist/* --verbose
```

### Erro: "Package already exists"
- **Causa**: Tentativa de upload da mesma versão
- **Solução**: Incrementar versão em `mentorstec/__init__.py`

### Erro: "Repository not found"
```bash
# Verificar URLs corretas
# PyPI: https://upload.pypi.org/legacy/
# TestPyPI: https://test.pypi.org/legacy/
```

### Erro: Módulo opcional não funciona
```bash
# Verificar dependências instaladas
pip list | grep -E "(adal|requests)"

# Reinstalar com dependências opcionais
pip install mentorstec[powerbi,dremio] --force-reinstall
```

### Erro: Import falha
```bash
# Verificar estrutura da instalação
python3 -c "import mentorstec; print(mentorstec.__file__)"
python3 -c "import mentorstec; print(dir(mentorstec))"

# Verificar __all__ exports
python3 -c "import mentorstec; print(mentorstec.__all__)"
```

## 🎯 Checklist de Release

### Pré-Release
- [ ] Código testado e funcionando com `./run_tests.sh`
- [ ] Todos os módulos (EventHub, Dremio, PowerBI) funcionando
- [ ] Versão incrementada em `mentorstec/__init__.py`
- [ ] Changelog/README atualizado
- [ ] Token do PyPI configurado
- [ ] Build limpo (`rm -rf dist/ htmlcov/`)

### Validação
- [ ] `python3 -m build` executado com sucesso
- [ ] `twine check dist/*` passou
- [ ] Teste no TestPyPI realizado
- [ ] Importações testadas:
  - [ ] `from mentorstec import EventHubClient` ✅
  - [ ] `from mentorstec import Dremio` ✅ (se requests instalado)
  - [ ] `from mentorstec import PowerBi` ✅ (se adal instalado)

### Deploy
- [ ] Upload para TestPyPI OK
- [ ] Teste de instalação do TestPyPI OK
- [ ] Upload para PyPI produção OK
- [ ] Verificação no https://pypi.org/project/mentorstec/ OK
- [ ] Teste de instalação com diferentes combinações:
  - [ ] `pip install mentorstec`
  - [ ] `pip install mentorstec[powerbi]`
  - [ ] `pip install mentorstec[dremio]` 
  - [ ] `pip install mentorstec[powerbi,dremio]`

### Pós-Release
- [ ] Tag e release no GitHub
- [ ] Documentação atualizada
- [ ] Pipeline CI/CD funcionando
- [ ] Notificação das equipes (se aplicável)

## 📞 Suporte

### Documentação
- **README**: Exemplos completos de uso
- **Código**: Docstrings com exemplos práticos
- **Pipeline**: `.github/workflows/pipeline.yml`
- **Secrets**: `.github/SECRETS.md`

### Em caso de problemas:
1. Consulte os logs detalhados com `--verbose`
2. Execute `./run_tests.sh` para verificar qualidade
3. Teste imports individuais dos módulos
4. Verifique a documentação oficial: https://packaging.python.org/
5. Abra uma issue: https://github.com/mentorstec/mentorstec/issues

---

🚀 **Mentorstec v0.1.3** - Plataforma completa pronta para deploy com arquitetura modular!