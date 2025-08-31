# Troubleshooting Guide

This guide addresses common issues with MCP Proxy Adapter Framework, particularly related to ProtocolMiddleware and SSL/TLS configuration.

## Common Issues

### Issue 1: ProtocolMiddleware blocks HTTPS requests

**Problem:** ProtocolMiddleware is initialized with default settings and doesn't update when SSL configuration changes.

**Symptoms:**
```
Protocol 'https' not allowed for request to /health
INFO: 127.0.0.1:42038 - "GET /health HTTP/1.1" 403 Forbidden
```

**Root Cause:** ProtocolMiddleware was created as a global instance with default settings and didn't update when SSL was enabled.

**Solution:** 
1. **Use updated ProtocolManager** (Fixed in v1.1.0):
   - ProtocolManager now dynamically updates based on SSL configuration
   - Automatically allows HTTPS when SSL is enabled

2. **Disable ProtocolMiddleware for HTTPS** (Temporary workaround):
   ```json
   {
     "server": {"host": "127.0.0.1", "port": 10004},
     "ssl": {"enabled": true, "cert_file": "./certs/server.crt", "key_file": "./certs/server.key"},
     "security": {"enabled": true, "auth": {"enabled": true, "methods": ["api_key"]}},
     "protocols": {"enabled": false}
   }
   ```

### Issue 2: SSL Configuration Conflicts

**Problem:** Framework reads SSL configuration from both `ssl` (legacy) and `security.ssl` sections, causing confusion.

**Symptoms:**
```
🔍 Debug: SSL config at start of validation: enabled=False
🔍 Debug: Root SSL section found: enabled=True
🔍 Debug: _get_ssl_config: security.ssl key_file=None
🔍 Debug: _get_ssl_config: legacy ssl key_file=./certs/server.key
```

**Solution:**
1. **Use unified SSL configuration** (Recommended):
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

2. **Use legacy SSL configuration** (Backward compatible):
   ```json
   {
     "ssl": {
       "enabled": true,
       "cert_file": "./certs/server.crt",
       "key_file": "./certs/server.key"
     }
   }
   ```

### Issue 3: Security Framework Initialization Errors

**Problem:** Security framework fails to initialize due to missing or null configuration values.

**Symptoms:**
```
Failed to initialize security components: Failed to load roles configuration: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'
```

**Solution:**
1. **Provide roles file** (If using roles):
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

2. **Disable permissions** (If not using roles):
   ```json
   {
     "security": {
       "permissions": {
         "enabled": false
       }
     }
   }
   ```

3. **Use graceful fallback** (Fixed in v1.1.0):
   - Security framework now continues without roles if roles_file is null
   - Logs warning instead of crashing

## Configuration Examples

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

### HTTPS with Token Auth
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

### HTTPS without ProtocolMiddleware
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

## Testing Your Configuration

### Test HTTP
```bash
curl http://127.0.0.1:10001/health
```

### Test HTTPS
```bash
curl -k https://127.0.0.1:10002/health
```

### Test HTTPS with Auth
```bash
curl -k -H "Authorization: Bearer your-api-key" https://127.0.0.1:10003/health
```

### Test mTLS
```bash
curl -k --cert ./certs/client.crt --key ./certs/client.key https://127.0.0.1:10005/health
```

## Debugging

### Enable Debug Logging
```json
{
  "logging": {
    "level": "DEBUG",
    "console_output": true
  }
}
```

### Check Protocol Manager Status
```python
from mcp_proxy_adapter.core.protocol_manager import get_protocol_manager
from mcp_proxy_adapter.config import config

pm = get_protocol_manager(config.get_all())
print(f"Allowed protocols: {pm.get_allowed_protocols()}")
print(f"Protocol info: {pm.get_protocol_info()}")
```

### Check SSL Configuration
```python
from mcp_proxy_adapter.config import config

ssl_config = config.get("ssl", {})
security_ssl = config.get("security", {}).get("ssl", {})
print(f"Legacy SSL: {ssl_config}")
print(f"Security SSL: {security_ssl}")
```

## Migration Guide

### From Legacy to New Configuration

**Old (Legacy):**
```json
{
  "ssl": {"enabled": true, "cert_file": "./certs/server.crt", "key_file": "./certs/server.key"}
}
```

**New (Recommended):**
```json
{
  "security": {
    "ssl": {"enabled": true, "cert_file": "./certs/server.crt", "key_file": "./certs/server.key"}
  }
}
```

### Adding Protocol Management

**Without Protocol Management:**
```json
{
  "protocols": {"enabled": false}
}
```

**With Protocol Management:**
```json
{
  "protocols": {
    "enabled": true,
    "allowed_protocols": ["http", "https"]
  }
}
```

## Best Practices

1. **Use security.ssl instead of legacy ssl** for new configurations
2. **Disable ProtocolMiddleware** if you don't need protocol validation
3. **Provide roles_file** or disable permissions if using security framework
4. **Test configurations** before deploying to production
5. **Use debug logging** for troubleshooting
6. **Keep certificates and keys secure** and properly configured

## Support

If you encounter issues not covered in this guide:

1. Check the logs for detailed error messages
2. Enable debug logging for more information
3. Verify certificate files exist and are readable
4. Test with simple configurations first
5. Report issues with full configuration and error logs
