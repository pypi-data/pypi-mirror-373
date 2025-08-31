# Руководство по устранению неполадок

Это руководство посвящено решению распространенных проблем с фреймворком MCP Proxy Adapter, особенно связанных с ProtocolMiddleware и конфигурацией SSL/TLS.

## Распространенные проблемы

### Проблема 1: ProtocolMiddleware блокирует HTTPS запросы

**Проблема:** ProtocolMiddleware инициализируется с дефолтными настройками и не обновляется при изменении конфигурации SSL.

**Симптомы:**
```
Protocol 'https' not allowed for request to /health
INFO: 127.0.0.1:42038 - "GET /health HTTP/1.1" 403 Forbidden
```

**Причина:** ProtocolMiddleware создавался как глобальный экземпляр с дефолтными настройками и не обновлялся при включении SSL.

**Решение:** 
1. **Использовать обновленный ProtocolManager** (Исправлено в v1.1.0):
   - ProtocolManager теперь динамически обновляется на основе конфигурации SSL
   - Автоматически разрешает HTTPS при включении SSL

2. **Отключить ProtocolMiddleware для HTTPS** (Временное решение):
   ```json
   {
     "server": {"host": "127.0.0.1", "port": 10004},
     "ssl": {"enabled": true, "cert_file": "./certs/server.crt", "key_file": "./certs/server.key"},
     "security": {"enabled": true, "auth": {"enabled": true, "methods": ["api_key"]}},
     "protocols": {"enabled": false}
   }
   ```

### Проблема 2: Конфликты конфигурации SSL

**Проблема:** Фреймворк читает конфигурацию SSL из двух мест: `ssl` (legacy) и `security.ssl`, что приводит к путанице.

**Симптомы:**
```
🔍 Debug: SSL config at start of validation: enabled=False
🔍 Debug: Root SSL section found: enabled=True
🔍 Debug: _get_ssl_config: security.ssl key_file=None
🔍 Debug: _get_ssl_config: legacy ssl key_file=./certs/server.key
```

**Решение:**
1. **Использовать унифицированную конфигурацию SSL** (Рекомендуется):
   ```json
   {
     "security": {
       "ssl": {
         "enabled": true,
         "cert_file": "./certs/server.crt",
         "key_file": "./certs/server.key"
       }
     }
   }
   ```

2. **Использовать legacy конфигурацию SSL** (Обратная совместимость):
   ```json
   {
     "ssl": {
       "enabled": true,
       "cert_file": "./certs/server.crt",
       "key_file": "./certs/server.key"
     }
   }
   ```

### Проблема 3: Ошибки инициализации security framework

**Проблема:** Security framework падает при инициализации из-за отсутствующих или null значений конфигурации.

**Симптомы:**
```
Failed to initialize security components: Failed to load roles configuration: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'
```

**Решение:**
1. **Предоставить файл ролей** (Если используются роли):
   ```json
   {
     "security": {
       "permissions": {
         "enabled": true,
         "roles_file": "./roles.json"
       }
     }
   }
   ```

2. **Отключить permissions** (Если роли не используются):
   ```json
   {
     "security": {
       "permissions": {
         "enabled": false
       }
     }
   }
   ```

3. **Использовать graceful fallback** (Исправлено в v1.1.0):
   - Security framework теперь продолжает работу без ролей, если roles_file равен null
   - Логирует предупреждение вместо падения

## Примеры конфигураций

### HTTP Simple
```json
{
  "server": {"host": "127.0.0.1", "port": 10001},
  "ssl": {"enabled": false},
  "security": {"enabled": false},
  "protocols": {"enabled": true, "allowed_protocols": ["http"]}
}
```

### HTTPS Simple
```json
{
  "server": {"host": "127.0.0.1", "port": 10002},
  "ssl": {"enabled": true, "cert_file": "./certs/server.crt", "key_file": "./certs/server.key"},
  "security": {"enabled": false},
  "protocols": {"enabled": true, "allowed_protocols": ["http", "https"]}
}
```

### HTTPS с токен-аутентификацией
```json
{
  "server": {"host": "127.0.0.1", "port": 10003},
  "ssl": {"enabled": true, "cert_file": "./certs/server.crt", "key_file": "./certs/server.key"},
  "security": {
    "enabled": true,
    "auth": {"enabled": true, "methods": ["api_key"]}
  },
  "protocols": {"enabled": true, "allowed_protocols": ["http", "https"]}
}
```

### HTTPS без ProtocolMiddleware
```json
{
  "server": {"host": "127.0.0.1", "port": 10004},
  "ssl": {"enabled": true, "cert_file": "./certs/server.crt", "key_file": "./certs/server.key"},
  "security": {
    "enabled": true,
    "auth": {"enabled": true, "methods": ["api_key"]}
  },
  "protocols": {"enabled": false}
}
```

### mTLS Simple
```json
{
  "server": {"host": "127.0.0.1", "port": 10005},
  "ssl": {
    "enabled": true,
    "cert_file": "./certs/server.crt",
    "key_file": "./certs/server.key",
    "ca_cert": "./certs/ca.crt",
    "verify_client": true
  },
  "security": {
    "enabled": true,
    "auth": {"enabled": true, "methods": ["certificate"]}
  },
  "protocols": {"enabled": true, "allowed_protocols": ["https", "mtls"]}
}
```

## Тестирование конфигурации

### Тест HTTP
```bash
curl http://127.0.0.1:10001/health
```

### Тест HTTPS
```bash
curl -k https://127.0.0.1:10002/health
```

### Тест HTTPS с аутентификацией
```bash
curl -k -H "Authorization: Bearer your-api-key" https://127.0.0.1:10003/health
```

### Тест mTLS
```bash
curl -k --cert ./certs/client.crt --key ./certs/client.key https://127.0.0.1:10005/health
```

## Отладка

### Включить debug логирование
```json
{
  "logging": {
    "level": "DEBUG",
    "console_output": true
  }
}
```

### Проверить статус Protocol Manager
```python
from mcp_proxy_adapter.core.protocol_manager import get_protocol_manager
from mcp_proxy_adapter.config import config

pm = get_protocol_manager(config.get_all())
print(f"Allowed protocols: {pm.get_allowed_protocols()}")
print(f"Protocol info: {pm.get_protocol_info()}")
```

### Проверить конфигурацию SSL
```python
from mcp_proxy_adapter.config import config

ssl_config = config.get("ssl", {})
security_ssl = config.get("security", {}).get("ssl", {})
print(f"Legacy SSL: {ssl_config}")
print(f"Security SSL: {security_ssl}")
```

## Руководство по миграции

### От legacy к новой конфигурации

**Старая (Legacy):**
```json
{
  "ssl": {"enabled": true, "cert_file": "./certs/server.crt", "key_file": "./certs/server.key"}
}
```

**Новая (Рекомендуется):**
```json
{
  "security": {
    "ssl": {"enabled": true, "cert_file": "./certs/server.crt", "key_file": "./certs/server.key"}
  }
}
```

### Добавление управления протоколами

**Без управления протоколами:**
```json
{
  "protocols": {"enabled": false}
}
```

**С управлением протоколами:**
```json
{
  "protocols": {
    "enabled": true,
    "allowed_protocols": ["http", "https"]
  }
}
```

## Лучшие практики

1. **Используйте security.ssl вместо legacy ssl** для новых конфигураций
2. **Отключайте ProtocolMiddleware** если не нужна валидация протоколов
3. **Предоставляйте roles_file** или отключайте permissions при использовании security framework
4. **Тестируйте конфигурации** перед развертыванием в продакшене
5. **Используйте debug логирование** для отладки
6. **Храните сертификаты и ключи в безопасности** и правильно настраивайте

## Поддержка

Если вы столкнулись с проблемами, не описанными в этом руководстве:

1. Проверьте логи для получения подробных сообщений об ошибках
2. Включите debug логирование для получения дополнительной информации
3. Убедитесь, что файлы сертификатов существуют и доступны для чтения
4. Тестируйте с простыми конфигурациями сначала
5. Сообщайте о проблемах с полной конфигурацией и логами ошибок
