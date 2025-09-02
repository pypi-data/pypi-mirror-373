#!/usr/bin/env python3
"""
Teste rápido para validar os novos decorators e funcionalidades
"""
import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, "/opt/pyMentors")

from mentorstec import (
    capture_errors,
    clear_global_client,
    log_event,
    send_event,
    setup_global_hub,
)

# Limpar client global anterior (se existir)
clear_global_client()

# Mock da connection string para teste
os.environ["AZURE_SERVICE_BUS_CONNECTION_STRING"] = (
    "Endpoint=sb://test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=test"
)


def test_new_functionality():
    print("🧪 Testando nova funcionalidade do event_hub.py")

    # 1. Testar setup_global_hub com queue_name obrigatório
    print("\n1. Testando setup_global_hub...")
    try:
        client = setup_global_hub("test-project", "events-queue", "testing")
        print(f"✅ setup_global_hub OK - Cliente: {client.project}")
    except Exception as e:
        print(f"❌ Erro no setup_global_hub: {e}")
        return

    # 2. Testar send_event simples
    print("\n2. Testando send_event...")
    try:
        send_event(
            "TEST_EVENT", "Test message from refactored module", test_field="test_value"
        )
        print("✅ send_event OK")
    except Exception as e:
        print(f"❌ Erro no send_event: {e}")

    # 3. Testar novo decorator log_event
    print("\n3. Testando decorator log_event...")
    try:

        @log_event("USER_ACTION", include_args=True, include_result=True)
        def test_function(x, y, operation="add"):
            """Função de teste para o decorator"""
            if operation == "add":
                return {"result": x + y, "operation": operation}
            elif operation == "multiply":
                return {"result": x * y, "operation": operation}
            else:
                raise ValueError("Operação não suportada")

        # Testar execução com sucesso
        result = test_function(5, 3, operation="add")
        print(f"✅ log_event (sucesso) OK - Resultado: {result}")

        result2 = test_function(4, 7, operation="multiply")
        print(f"✅ log_event (sucesso 2) OK - Resultado: {result2}")

    except Exception as e:
        print(f"❌ Erro no decorator log_event: {e}")

    # 4. Testar log_event com erro
    print("\n4. Testando log_event com captura de erro...")
    try:

        @log_event("ERROR_PRONE_ACTION", include_args=True)
        def error_function(should_fail=True):
            if should_fail:
                raise ValueError("Erro intencional para teste")
            return "success"

        # Esta deve gerar erro mas ser capturado
        try:
            error_function(should_fail=True)
        except ValueError:
            print("✅ log_event (erro) OK - Erro capturado e logado")

    except Exception as e:
        print(f"❌ Erro inesperado no teste de erro: {e}")

    # 5. Testar capture_errors tradicional
    print("\n5. Testando capture_errors tradicional...")
    try:

        @capture_errors("traditional_error_capture")
        def traditional_error_function():
            raise RuntimeError("Erro tradicional")

        try:
            traditional_error_function()
        except RuntimeError:
            print("✅ capture_errors OK - Erro capturado")
    except Exception as e:
        print(f"❌ Erro no capture_errors: {e}")

    # 6. Teste de contexto personalizado
    print("\n6. Testando contexto personalizado...")
    try:

        @log_event("CUSTOM_CONTEXT", context="payment.processing")
        def payment_function(amount, currency="USD"):
            return {"charged": amount, "currency": currency, "status": "success"}

        result = payment_function(100.50, "BRL")
        print(f"✅ Contexto personalizado OK - Resultado: {result}")
    except Exception as e:
        print(f"❌ Erro no contexto personalizado: {e}")

    print("\n🎉 Testes concluídos!")


if __name__ == "__main__":
    test_new_functionality()
