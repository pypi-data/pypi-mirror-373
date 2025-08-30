# MCP Proxy Adapter - Examples and Security Testing

This directory contains examples of using MCP Proxy Adapter with various security configurations and a comprehensive testing system.

## 📁 Directory Structure

```
examples/
├── README.md                           # This documentation
├── README_EN.md                        # English documentation
├── SECURITY_TESTING.md                 # Security testing documentation
├── generate_certificates.py            # Certificate generation script
├── security_test_client.py             # Security testing client
├── run_security_tests.py               # Main test runner script
├── cert_config.json                    # Certificate generation configuration
├── certs/                              # Generated certificates
├── keys/                               # Private keys
├── server_configs/                     # Server configurations
│   ├── config_basic_http.json         # Basic HTTP
│   ├── config_http_token.json         # HTTP + token
│   ├── config_https.json              # HTTPS
│   ├── config_https_token.json        # HTTPS + token
│   ├── config_mtls.json               # mTLS
│   └── roles.json                     # Roles and permissions
└── commands/                           # Custom commands
    └── __init__.py
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### 2. Generate Certificates

```bash
# Generate all necessary certificates
cd mcp_proxy_adapter/examples
python generate_certificates.py
```

### 3. Run Security Tests

```bash
# Run all security tests
python run_security_tests.py
```

## 🔧 Server Configurations

### Basic HTTP (port 8000)
```bash
python -m mcp_proxy_adapter.main --config server_configs/config_basic_http.json
```

### HTTP + Token Authentication (port 8001)
```bash
python -m mcp_proxy_adapter.main --config server_configs/config_http_token.json
```

### HTTPS (port 8443)
```bash
python -m mcp_proxy_adapter.main --config server_configs/config_https.json
```

### HTTPS + Token Authentication (port 8444)
```bash
python -m mcp_proxy_adapter.main --config server_configs/config_https_token.json
```

### mTLS (port 8445)
```bash
python -m mcp_proxy_adapter.main --config server_configs/config_mtls.json
```

## 🧪 Testing

### Testing Individual Server

```bash
# Test basic HTTP server
python security_test_client.py --server http://localhost:8000 --auth none

# Test HTTP with token
python security_test_client.py --server http://localhost:8001 --auth api_key --token test-token-123

# Test HTTPS server
python security_test_client.py --server https://localhost:8443 --auth none

# Test HTTPS with token
python security_test_client.py --server https://localhost:8444 --auth api_key --token test-token-123

# Test mTLS with certificate
python security_test_client.py --server https://localhost:8445 --auth certificate --cert certs/admin_cert.pem --key keys/admin_key.pem --ca-cert certs/ca_cert.pem
```

### Testing All Scenarios

```bash
# Start all servers and test them
python run_security_tests.py
```

## 📋 Testing Scenarios

### 1. Basic HTTP (config_basic_http.json)
- **Port**: 8000
- **Security**: Disabled
- **Authentication**: None
- **Tests**: Health check, echo command

### 2. HTTP + Token (config_http_token.json)
- **Port**: 8001
- **Security**: API Key authentication
- **Tokens**: 
  - `test-token-123` (admin)
  - `user-token-456` (user)
- **Tests**: Role-based authentication, negative tests

### 3. HTTPS (config_https.json)
- **Port**: 8443
- **Security**: SSL/TLS
- **Certificates**: Self-signed
- **Tests**: Secure connections

### 4. HTTPS + Token (config_https_token.json)
- **Port**: 8444
- **Security**: SSL/TLS + API Key
- **Tests**: Combined security

### 5. mTLS (config_mtls.json)
- **Port**: 8445
- **Security**: Mutual certificate authentication
- **Tests**: Certificate authentication

## 🔑 Test Tokens

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

## 📜 Roles and Permissions

```json
{
  "admin": ["*"],
  "user": ["read", "write", "execute"],
  "readonly": ["read"],
  "guest": ["read"]
}
```

## 🛠️ Configuration Generation

Use the built-in configuration generator:

```bash
# Generate all configuration types
python -m mcp_proxy_adapter.utils.config_generator --all --output-dir ./generated_configs

# Generate specific type
python -m mcp_proxy_adapter.utils.config_generator --type https_token --output ./my_config.json
```

Available configuration types:
- `minimal` - Minimal configuration
- `development` - For development
- `secure` - Maximum security
- `full` - Full configuration
- `basic_http` - Basic HTTP
- `http_token` - HTTP + token
- `https` - HTTPS
- `https_token` - HTTPS + token
- `mtls` - mTLS

## 🔍 Monitoring and Logs

Logs are saved to:
- `./logs/server.log` - Server logs
- `./logs/security.log` - Security logs

To view logs in real-time:
```bash
tail -f logs/server.log
tail -f logs/security.log
```

## 🚨 Troubleshooting

### Issue: Certificates not found
```bash
# Check certificate availability
ls -la certs/
ls -la keys/

# Regenerate certificates
python generate_certificates.py
```

### Issue: Port in use
```bash
# Find process using port
lsof -i :8000
lsof -i :8443

# Stop process
kill -9 <PID>
```

### Issue: SSL errors
```bash
# Check certificates
openssl x509 -in certs/server_cert.pem -text -noout

# Check private key
openssl rsa -in keys/server_key.pem -check
```

## 📚 Additional Documentation

- [SECURITY_TESTING.md](SECURITY_TESTING.md) - Detailed security testing guide
- [API Documentation](../docs/api/) - API documentation
- [Configuration Guide](../docs/configuration.md) - Configuration guide

## 🤝 Support

If you encounter issues:

1. Check logs in `./logs/`
2. Ensure all dependencies are installed
3. Verify certificates are generated correctly
4. Refer to troubleshooting documentation

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.

---

**Author**: Vasiliy Zdanovskiy  
**Email**: vasilyvz@gmail.com  
**Version**: 1.0.0
