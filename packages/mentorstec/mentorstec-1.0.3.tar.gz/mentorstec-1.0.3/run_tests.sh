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