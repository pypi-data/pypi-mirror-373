#!/usr/bin/env python3
"""
Debug Request State - Проверка request.state
Этот скрипт проверяет, как middleware устанавливает информацию о пользователе в request.state.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import asyncio
import json
import sys
from pathlib import Path
# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from mcp_proxy_adapter.api.app import create_app
async def debug_request_state():
    """Debug request state handling."""
    print("🔍 ОТЛАДКА REQUEST.STATE")
    print("=" * 50)
    # Create test app with proper configuration
    config_path = project_root / "mcp_proxy_adapter" / "examples" / "server_configs" / "config_http_token.json"
    with open(config_path) as f:
        config = json.load(f)
    # Override global config for testing
    import mcp_proxy_adapter.config
    mcp_proxy_adapter.config.config = config
    app = create_app(config)
    client = TestClient(app)
    print("📋 1. ТЕСТИРОВАНИЕ БЕЗ АУТЕНТИФИКАЦИИ")
    print("-" * 30)
    # Test without authentication
    response = client.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "echo",
        "params": {"message": "test"},
        "id": 1
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("\n📋 2. ТЕСТИРОВАНИЕ С ADMIN ТОКЕНОМ")
    print("-" * 30)
    # Test with admin token
    response = client.post("/cmd",
        json={
            "jsonrpc": "2.0",
            "method": "echo",
            "params": {"message": "test"},
            "id": 1
        },
        headers={"X-API-Key": "test-token-123"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("\n📋 3. ТЕСТИРОВАНИЕ С USER ТОКЕНОМ")
    print("-" * 30)
    # Test with user token
    response = client.post("/cmd",
        json={
            "jsonrpc": "2.0",
            "method": "echo",
            "params": {"message": "test"},
            "id": 1
        },
        headers={"X-API-Key": "user-token-456"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("\n📋 4. ТЕСТИРОВАНИЕ С READONLY ТОКЕНОМ")
    print("-" * 30)
    # Test with readonly token
    response = client.post("/cmd",
        json={
            "jsonrpc": "2.0",
            "method": "echo",
            "params": {"message": "test"},
            "id": 1
        },
        headers={"X-API-Key": "readonly-token-123"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("\n📋 5. ТЕСТИРОВАНИЕ ROLE_TEST КОМАНДЫ")
    print("-" * 30)
    # Test role_test command with readonly token
    response = client.post("/cmd",
        json={
            "jsonrpc": "2.0",
            "method": "role_test",
            "params": {"action": "write"},
            "id": 1
        },
        headers={"X-API-Key": "readonly-token-123"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("\n📋 6. АНАЛИЗ ПРОБЛЕМЫ")
    print("-" * 30)
    print("🔍 ПРОБЛЕМА: Readonly роль получает доступ к командам")
    print("\n📋 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
    print("1. Framework middleware не устанавливает user info в request.state")
    print("2. Нет проверки прав на уровне middleware")
    print("3. Команды не проверяют права доступа")
    print("4. Интеграция между middleware и командами не работает")
    print("\n📋 РЕКОМЕНДАЦИИ:")
    print("1. Добавить CommandPermissionMiddleware")
    print("2. Убедиться, что framework middleware устанавливает user info")
    print("3. Добавить проверку прав в команды")
    print("4. Проверить интеграцию middleware")
if __name__ == "__main__":
    asyncio.run(debug_request_state())
