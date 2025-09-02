#!/usr/bin/env python3
"""
Teste do decorator send_event simplificado
"""
import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, "/opt/pyMentors")

# Mock da connection string para teste
os.environ["AZURE_SERVICE_BUS_CONNECTION_STRING"] = (
    "Endpoint=sb://test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=test"
)

from mentorstec import send_event


def test_simplified_decorator():
    print("🧪 Testando decorator send_event simplificado")

    # Teste 1: Uso básico do decorator
    print("\n1. Testando uso básico...")
    try:

        @send_event("test-project", "events-queue", "USER_ACTION")
        def simple_function(x, y):
            return x + y

        result = simple_function(5, 3)
        print(f"✅ Decorator básico OK - Resultado: {result}")
    except Exception as e:
        print(f"❌ Erro no decorator básico: {e}")

    # Teste 2: Com argumentos e resultado incluídos
    print("\n2. Testando com argumentos e resultado...")
    try:

        @send_event(
            "test-project",
            "events-queue",
            "CALCULATION",
            include_args=True,
            include_result=True,
        )
        def calculation_function(x, y, operation="multiply"):
            if operation == "multiply":
                return {"result": x * y, "operation": operation}
            elif operation == "add":
                return {"result": x + y, "operation": operation}
            else:
                raise ValueError("Operação não suportada")

        result = calculation_function(4, 7, "multiply")
        print(f"✅ Decorator com args/result OK - Resultado: {result}")
    except Exception as e:
        print(f"❌ Erro no decorator com args/result: {e}")

    # Teste 3: Captura de erro
    print("\n3. Testando captura de erro...")
    try:

        @send_event("test-project", "events-queue", "ERROR_PRONE", include_args=True)
        def error_function(should_fail=True):
            if should_fail:
                raise ValueError("Erro intencional para teste")
            return "success"

        try:
            error_function(should_fail=True)
        except ValueError:
            print("✅ Captura de erro OK - Erro logado e re-lançado")
    except Exception as e:
        print(f"❌ Erro inesperado na captura: {e}")

    # Teste 4: Contexto personalizado
    print("\n4. Testando contexto personalizado...")
    try:

        @send_event(
            "test-project",
            "events-queue",
            "PAYMENT",
            context="payment.processing",
            include_result=True,
        )
        def payment_function(amount, currency="USD"):
            return {
                "charged": amount,
                "currency": currency,
                "status": "success",
                "transaction_id": f"tx_{amount}_{currency}",
            }

        result = payment_function(100.50, "BRL")
        print(f"✅ Contexto personalizado OK - Resultado: {result}")
    except Exception as e:
        print(f"❌ Erro no contexto personalizado: {e}")

    print("\n🎉 Testes do decorator simplificado concluídos!")
    print(
        "✨ Agora o módulo é simples, eficiente e focado apenas no decorator send_event!"
    )


if __name__ == "__main__":
    test_simplified_decorator()
