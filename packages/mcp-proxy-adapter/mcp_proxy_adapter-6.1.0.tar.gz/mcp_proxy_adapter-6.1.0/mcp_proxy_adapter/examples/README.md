# MCP Proxy Adapter - Examples and Security Testing

Этот каталог содержит примеры использования MCP Proxy Adapter с различными конфигурациями безопасности и комплексную систему тестирования.

## 📁 Структура каталога

```
examples/
├── README.md                           # Эта документация
├── SECURITY_TESTING.md                 # Документация по тестированию безопасности
├── generate_certificates.py            # Скрипт генерации сертификатов
├── security_test_client.py             # Клиент для тестирования безопасности
├── run_security_tests.py               # Основной скрипт запуска тестов
├── cert_config.json                    # Конфигурация для генерации сертификатов
├── certs/                              # Сгенерированные сертификаты
├── keys/                               # Приватные ключи
├── server_configs/                     # Конфигурации серверов
│   ├── config_basic_http.json         # Базовый HTTP
│   ├── config_http_token.json         # HTTP + токен
│   ├── config_https.json              # HTTPS
│   ├── config_https_token.json        # HTTPS + токен
│   ├── config_mtls.json               # mTLS
│   └── roles.json                     # Роли и разрешения
└── commands/                           # Пользовательские команды
    └── __init__.py
```

## 🚀 Быстрый старт

### 1. Подготовка окружения

```bash
# Активируйте виртуальную среду
source .venv/bin/activate

# Установите зависимости
pip install -e .
```

### 2. Генерация сертификатов

```bash
# Сгенерируйте все необходимые сертификаты
cd mcp_proxy_adapter/examples
python generate_certificates.py
```

### 3. Запуск тестов безопасности

```bash
# Запустите все тесты безопасности
python run_security_tests.py
```

## 🔧 Конфигурации серверов

### Базовый HTTP (порт 8000)
```bash
python -m mcp_proxy_adapter.main --config server_configs/config_basic_http.json
```

### HTTP + Токен аутентификация (порт 8001)
```bash
python -m mcp_proxy_adapter.main --config server_configs/config_http_token.json
```

### HTTPS (порт 8443)
```bash
python -m mcp_proxy_adapter.main --config server_configs/config_https.json
```

### HTTPS + Токен аутентификация (порт 8444)
```bash
python -m mcp_proxy_adapter.main --config server_configs/config_https_token.json
```

### mTLS (порт 8445)
```bash
python -m mcp_proxy_adapter.main --config server_configs/config_mtls.json
```

## 🧪 Тестирование

### Тестирование отдельного сервера

```bash
# Тест базового HTTP сервера
python security_test_client.py --server http://localhost:8000 --auth none

# Тест HTTP с токеном
python security_test_client.py --server http://localhost:8001 --auth api_key --token test-token-123

# Тест HTTPS сервера
python security_test_client.py --server https://localhost:8443 --auth none

# Тест HTTPS с токеном
python security_test_client.py --server https://localhost:8444 --auth api_key --token test-token-123

# Тест mTLS с сертификатом
python security_test_client.py --server https://localhost:8445 --auth certificate --cert certs/admin_cert.pem --key keys/admin_key.pem --ca-cert certs/ca_cert.pem
```

### Тестирование всех сценариев

```bash
# Запустите все серверы и протестируйте их
python run_security_tests.py
```

## 📋 Сценарии тестирования

### 1. Базовый HTTP (config_basic_http.json)
- **Порт**: 8000
- **Безопасность**: Отключена
- **Аутентификация**: Нет
- **Тесты**: Health check, echo command

### 2. HTTP + Токен (config_http_token.json)
- **Порт**: 8001
- **Безопасность**: API Key аутентификация
- **Токены**: 
  - `test-token-123` (admin)
  - `user-token-456` (user)
- **Тесты**: Ролевая аутентификация, негативные тесты

### 3. HTTPS (config_https.json)
- **Порт**: 8443
- **Безопасность**: SSL/TLS
- **Сертификаты**: Самоподписанные
- **Тесты**: Защищенные соединения

### 4. HTTPS + Токен (config_https_token.json)
- **Порт**: 8444
- **Безопасность**: SSL/TLS + API Key
- **Тесты**: Комбинированная безопасность

### 5. mTLS (config_mtls.json)
- **Порт**: 8445
- **Безопасность**: Взаимная аутентификация сертификатами
- **Тесты**: Сертификатная аутентификация

## 🔑 Токены для тестирования

```json
{
  "test-token-123": {
    "roles": ["admin"],
    "permissions": ["*"]
  },
  "user-token-456": {
    "roles": ["user"],
    "permissions": ["read", "execute"]
  }
}
```

## 📜 Роли и разрешения

```json
{
  "admin": ["*"],
  "user": ["read", "write", "execute"],
  "readonly": ["read"],
  "guest": ["read"]
}
```

## 🛠️ Генерация конфигураций

Используйте встроенный генератор конфигураций:

```bash
# Генерация всех типов конфигураций
python -m mcp_proxy_adapter.utils.config_generator --all --output-dir ./generated_configs

# Генерация конкретного типа
python -m mcp_proxy_adapter.utils.config_generator --type https_token --output ./my_config.json
```

Доступные типы конфигураций:
- `minimal` - Минимальная конфигурация
- `development` - Для разработки
- `secure` - Максимальная безопасность
- `full` - Полная конфигурация
- `basic_http` - Базовый HTTP
- `http_token` - HTTP + токен
- `https` - HTTPS
- `https_token` - HTTPS + токен
- `mtls` - mTLS

## 🔍 Мониторинг и логи

Логи сохраняются в:
- `./logs/server.log` - Логи сервера
- `./logs/security.log` - Логи безопасности

Для просмотра логов в реальном времени:
```bash
tail -f logs/server.log
tail -f logs/security.log
```

## 🚨 Устранение неполадок

### Проблема: Сертификаты не найдены
```bash
# Проверьте наличие сертификатов
ls -la certs/
ls -la keys/

# Перегенерируйте сертификаты
python generate_certificates.py
```

### Проблема: Порт занят
```bash
# Найдите процесс, использующий порт
lsof -i :8000
lsof -i :8443

# Остановите процесс
kill -9 <PID>
```

### Проблема: SSL ошибки
```bash
# Проверьте сертификаты
openssl x509 -in certs/server_cert.pem -text -noout

# Проверьте приватный ключ
openssl rsa -in keys/server_key.pem -check
```

## 📚 Дополнительная документация

- [SECURITY_TESTING.md](SECURITY_TESTING.md) - Подробное руководство по тестированию безопасности
- [API Documentation](../docs/api/) - Документация API
- [Configuration Guide](../docs/configuration.md) - Руководство по конфигурации

## 🤝 Поддержка

Если у вас возникли проблемы:

1. Проверьте логи в `./logs/`
2. Убедитесь, что все зависимости установлены
3. Проверьте, что сертификаты сгенерированы корректно
4. Обратитесь к документации по устранению неполадок

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](../../LICENSE) для подробностей.

---

**Автор**: Vasiliy Zdanovskiy  
**Email**: vasilyvz@gmail.com  
**Версия**: 1.0.0
