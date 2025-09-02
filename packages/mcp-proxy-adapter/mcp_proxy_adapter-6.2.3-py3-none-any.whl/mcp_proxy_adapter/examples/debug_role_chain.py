#!/usr/bin/env python3
"""
Debug Role Chain - Анализ цепочки блокировки ролей
Этот скрипт анализирует всю цепочку от аутентификации до блокировки доступа.
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
from mcp_security_framework import SecurityManager, AuthManager, PermissionManager
from mcp_security_framework.schemas.config import SecurityConfig, AuthConfig, PermissionConfig
async def debug_role_chain():
    """Debug the complete role chain from authentication to blocking."""
    print("🔍 АНАЛИЗ ЦЕПОЧКИ БЛОКИРОВКИ РОЛЕЙ")
    print("=" * 60)
    # Load configuration
    config_path = project_root / "mcp_proxy_adapter" / "examples" / "server_configs" / "config_http_token.json"
    with open(config_path) as f:
        config = json.load(f)
    security_config = config.get("security", {})
    print("📋 1. КОНФИГУРАЦИЯ API КЛЮЧЕЙ")
    print("-" * 30)
    api_keys = security_config.get("auth", {}).get("api_keys", {})
    for key, value in api_keys.items():
        print(f"  {key}: {value}")
    print("\n📋 2. КОНФИГУРАЦИЯ РОЛЕЙ")
    print("-" * 30)
    roles_config = security_config.get("permissions", {}).get("roles", {})
    for role, permissions in roles_config.items():
        print(f"  {role}: {permissions}")
    print("\n📋 3. СОЗДАНИЕ КОМПОНЕНТОВ БЕЗОПАСНОСТИ")
    print("-" * 30)
    # Create permission config
    perm_config = PermissionConfig(
        roles_file=str(project_root / "mcp_proxy_adapter" / "examples" / "server_configs" / "roles.json"),
        default_role="guest",
        admin_role="admin",
        role_hierarchy=security_config.get("permissions", {}).get("role_hierarchy", {}),
        permission_cache_enabled=True,
        permission_cache_ttl=300,
        wildcard_permissions=False,
        strict_mode=True,
        roles=roles_config
    )
    # Create auth config
    auth_config = AuthConfig(
        enabled=security_config.get("auth", {}).get("enabled", True),
        methods=security_config.get("auth", {}).get("methods", ["api_key"]),
        api_keys=api_keys,
        user_roles=security_config.get("auth", {}).get("user_roles", {}),
        jwt_secret=security_config.get("auth", {}).get("jwt_secret"),
        jwt_algorithm=security_config.get("auth", {}).get("jwt_algorithm", "HS256"),
        jwt_expiry_hours=security_config.get("auth", {}).get("jwt_expiry_hours", 24),
        certificate_auth=security_config.get("auth", {}).get("certificate_auth", False),
        certificate_roles_oid=security_config.get("auth", {}).get("certificate_roles_oid"),
        certificate_permissions_oid=security_config.get("auth", {}).get("certificate_permissions_oid"),
        basic_auth=security_config.get("auth", {}).get("basic_auth", False),
        oauth2_config=security_config.get("auth", {}).get("oauth2_config"),
        public_paths=security_config.get("auth", {}).get("public_paths", [])
    )
    # Create security config
    security_config_obj = SecurityConfig(
        auth=auth_config,
        permissions=perm_config
    )
    print("✅ Конфигурации созданы")
    print("\n📋 4. ИНИЦИАЛИЗАЦИЯ МЕНЕДЖЕРОВ")
    print("-" * 30)
    # Initialize managers
    permission_manager = PermissionManager(perm_config)
    auth_manager = AuthManager(auth_config, permission_manager)
    security_manager = SecurityManager(security_config_obj)
    print("✅ Менеджеры инициализированы")
    print("\n📋 5. ТЕСТИРОВАНИЕ АУТЕНТИФИКАЦИИ")
    print("-" * 30)
    # Test authentication with different tokens
    test_tokens = {
        "admin": "test-token-123",
        "user": "user-token-456",
        "readonly": "readonly-token-123",
        "invalid": "invalid-token-999"
    }
    auth_results = {}
    for role, token in test_tokens.items():
        print(f"\n🔐 Тестирование токена для роли '{role}': {token}")
        try:
            result = auth_manager.authenticate_api_key(token)
            auth_results[role] = result
            print(f"  ✅ Аутентификация: {'УСПЕШНА' if result.is_valid else 'НЕУДАЧНА'}")
            if result.is_valid:
                print(f"  👤 Пользователь: {result.username}")
                print(f"  🏷️ Роли: {result.roles}")
                print(f"  🔑 Метод: {result.auth_method}")
            else:
                print(f"  ❌ Ошибка: {result.error_message}")
        except Exception as e:
            print(f"  ❌ Исключение: {e}")
            auth_results[role] = None
    print("\n📋 6. ТЕСТИРОВАНИЕ ПРАВ ДОСТУПА")
    print("-" * 30)
    # Test permissions for different actions
    test_actions = ["read", "write", "manage", "delete"]
    for role, auth_result in auth_results.items():
        if auth_result and auth_result.is_valid:
            print(f"\n🔒 Тестирование прав для роли '{role}' (роли: {auth_result.roles})")
            for action in test_actions:
                try:
                    # Check permissions using permission manager
                    validation_result = permission_manager.validate_access(
                        auth_result.roles,
                        [action]
                    )
                    status = "✅ РАЗРЕШЕНО" if validation_result.is_valid else "❌ ЗАБЛОКИРОВАНО"
                    print(f"  {action}: {status}")
                    if not validation_result.is_valid:
                        print(f"    📝 Причина: {validation_result.error_message}")
                        print(f"    🎯 Эффективные права: {validation_result.effective_permissions}")
                        print(f"    ❌ Отсутствующие права: {validation_result.missing_permissions}")
                except Exception as e:
                    print(f"  {action}: ❌ ОШИБКА - {e}")
    print("\n📋 7. ТЕСТИРОВАНИЕ ПОЛНОЙ ЦЕПОЧКИ")
    print("-" * 30)
    # Test complete request validation
    for role, token in test_tokens.items():
        print(f"\n🔄 Полная цепочка для роли '{role}'")
        request_data = {
            "api_key": token,
            "required_permissions": ["write"],
            "client_ip": "127.0.0.1"
        }
        try:
            result = security_manager.validate_request(request_data)
            status = "✅ УСПЕШНО" if result.is_valid else "❌ ЗАБЛОКИРОВАНО"
            print(f"  Результат: {status}")
            if not result.is_valid:
                print(f"  📝 Причина: {result.error_message}")
        except Exception as e:
            print(f"  ❌ ОШИБКА: {e}")
    print("\n📋 8. АНАЛИЗ ПРОБЛЕМЫ")
    print("-" * 30)
    print("🔍 ПРОБЛЕМА: Readonly роль получает доступ к write операциям")
    print("\n📋 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
    print("1. Middleware не передает информацию о пользователе в request.state")
    print("2. Framework middleware не блокирует доступ на уровне middleware")
    print("3. Команда role_test не получает правильный контекст пользователя")
    print("4. Интеграция между middleware и командами не работает")
    print("\n📋 РЕКОМЕНДАЦИИ:")
    print("1. Проверить, как framework middleware устанавливает user info")
    print("2. Добавить проверку прав на уровне middleware")
    print("3. Убедиться, что request.state содержит user info")
    print("4. Проверить интеграцию между middleware и командами")
if __name__ == "__main__":
    asyncio.run(debug_role_chain())
