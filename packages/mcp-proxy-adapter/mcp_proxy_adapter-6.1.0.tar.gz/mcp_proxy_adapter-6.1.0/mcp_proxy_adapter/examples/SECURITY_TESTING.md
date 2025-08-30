# Security Testing Framework

This directory contains a comprehensive security testing framework for MCP Proxy Adapter that validates various security configurations and scenarios.

**Author**: Vasiliy Zdanovskiy  
**Email**: vasilyvz@gmail.com

## Overview

The security testing framework provides:

- **Positive Tests**: Valid security configurations that should work
- **Negative Tests**: Invalid configurations that should be rejected
- **Certificate Tests**: mTLS and certificate-based authentication testing
- **Multiple Server Configurations**: HTTP, HTTPS, Token Auth, mTLS
- **Client Testing**: Using mcp_security_framework for comprehensive client testing

## Directory Structure

```
examples/
├── security_test_client.py      # Security test client using mcp_security_framework
├── run_security_tests.py        # Main test runner
├── server_configs/              # Server configuration files
│   ├── config_basic_http.json   # Basic HTTP without security
│   ├── config_http_token.json   # HTTP with token authentication
│   ├── config_https.json        # HTTPS without authentication
│   ├── config_https_token.json  # HTTPS with token authentication
│   ├── config_mtls.json         # mTLS with certificate authentication
│   └── roles.json               # Role definitions for testing
└── SECURITY_TESTING.md          # This file
```

## Server Configurations

### 1. Basic HTTP (config_basic_http.json)
- **Port**: 8000
- **Security**: Disabled
- **Authentication**: None
- **SSL/TLS**: Disabled
- **Use Case**: Basic testing without security

### 2. HTTP + Token (config_http_token.json)
- **Port**: 8001
- **Security**: Enabled
- **Authentication**: API Key
- **SSL/TLS**: Disabled
- **Use Case**: Token-based authentication over HTTP

### 3. HTTPS (config_https.json)
- **Port**: 8443
- **Security**: Enabled
- **Authentication**: None
- **SSL/TLS**: Enabled
- **Use Case**: Secure communication without authentication

### 4. HTTPS + Token (config_https_token.json)
- **Port**: 8444
- **Security**: Enabled
- **Authentication**: API Key
- **SSL/TLS**: Enabled
- **Use Case**: Secure communication with token authentication

### 5. mTLS (config_mtls.json)
- **Port**: 9443
- **Security**: Enabled
- **Authentication**: Certificate-based
- **SSL/TLS**: Enabled with mutual authentication
- **Use Case**: Highest security with certificate validation

## Test Scenarios

### Positive Tests

These tests verify that valid configurations work correctly:

1. **Basic HTTP Tests**
   - Health endpoint access
   - Echo command execution
   - Security command access

2. **HTTP + Token Tests**
   - Authentication with valid API key
   - Role-based access control
   - Rate limiting validation

3. **HTTPS Tests**
   - SSL/TLS handshake
   - Certificate validation
   - Secure communication

4. **HTTPS + Token Tests**
   - Combined SSL and token authentication
   - Security headers validation
   - Mixed authentication methods

5. **mTLS Tests**
   - Mutual certificate authentication
   - Certificate chain validation
   - Role extraction from certificates

### Negative Tests

These tests verify that invalid configurations are properly rejected:

1. **Invalid API Key**
   - Test with wrong API key
   - Expected: Authentication failure

2. **No Authentication on Auth Server**
   - Test without credentials on auth-required server
   - Expected: Access denied

3. **Protocol Mismatch**
   - HTTP client connecting to HTTPS server
   - Expected: Connection failure

4. **Invalid Certificates**
   - Expired certificates
   - Wrong organization certificates
   - Expected: Certificate validation failure

### Certificate Tests

Specific tests for certificate-based authentication:

1. **Admin Certificate**
   - Full administrative access
   - Expected: All operations allowed

2. **User Certificate**
   - Standard user access
   - Expected: Read/write operations allowed

3. **Readonly Certificate**
   - Read-only access
   - Expected: Only read operations allowed

4. **Expired Certificate**
   - Certificate past expiration date
   - Expected: Authentication failure

5. **Wrong Organization Certificate**
   - Certificate from unauthorized organization
   - Expected: Authentication failure

## Usage

### Prerequisites

1. Install dependencies:
```bash
pip install mcp_security_framework aiohttp
```

2. Generate certificates (if not already present):
```bash
python examples/generate_certificates.py
```

### Running Tests

#### Run All Tests
```bash
python examples/run_security_tests.py
```

#### Run Specific Test Types
```bash
# Positive tests only
python examples/run_security_tests.py --positive-only

# Negative tests only
python examples/run_security_tests.py --negative-only

# Certificate tests only
python examples/run_security_tests.py --certificates-only
```

#### Run with Custom Certificate Directory
```bash
python examples/run_security_tests.py --cert-dir ./certs
```

#### Save Results to File
```bash
python examples/run_security_tests.py --output test_results.json
```

### Using the Security Test Client

The security test client can be used independently:

```bash
# Test basic HTTP
python examples/security_test_client.py --server-url http://localhost:8000

# Test HTTPS with certificates
python examples/security_test_client.py --server-url https://localhost:8443 --cert-dir ./certs

# Test with specific API key
python examples/security_test_client.py --server-url http://localhost:8001 --api-key test-api-key
```

## Test Client Features

The `SecurityTestClient` provides:

### Authentication Methods
- **None**: No authentication
- **API Key**: Token-based authentication
- **Certificate**: mTLS certificate authentication

### SSL/TLS Support
- SSL context creation
- Certificate validation
- Hostname verification
- TLS version configuration

### Test Endpoints
- **Health Check**: `/health`
- **Echo Command**: `/cmd` (JSON-RPC)
- **Security Command**: `/cmd` (JSON-RPC)

### Error Handling
- Connection timeout handling
- SSL/TLS error detection
- Authentication failure detection
- Detailed error reporting

## Security Features Tested

### 1. SSL/TLS Security
- Certificate validation
- TLS version enforcement
- Cipher suite selection
- Hostname verification

### 2. Authentication
- API key validation
- Certificate-based authentication
- Role extraction from certificates
- Permission checking

### 3. Authorization
- Role-based access control
- Permission inheritance
- Resource-level permissions
- Admin privilege validation

### 4. Rate Limiting
- Request rate enforcement
- Burst limit validation
- Role-based exemptions
- Time window management

### 5. Security Headers
- Content-Type-Options
- Frame-Options
- XSS-Protection
- HSTS (HTTP Strict Transport Security)

### 6. Certificate Management
- Certificate expiration checking
- Certificate revocation list (CRL)
- Certificate chain validation
- Organization validation

## Expected Test Results

### Positive Tests
All positive tests should:
- ✅ Successfully connect to server
- ✅ Authenticate properly
- ✅ Execute commands successfully
- ✅ Return expected responses
- ✅ Complete within reasonable time

### Negative Tests
All negative tests should:
- ❌ Fail to authenticate
- ❌ Return appropriate error codes
- ❌ Log security violations
- ❌ Prevent unauthorized access
- ❌ Handle errors gracefully

### Certificate Tests
Certificate tests should:
- ✅ Accept valid certificates
- ❌ Reject expired certificates
- ❌ Reject wrong organization certificates
- ✅ Extract roles correctly
- ✅ Enforce role-based permissions

## Troubleshooting

### Common Issues

1. **Certificate Not Found**
   ```
   Error: Certificate files not found
   Solution: Run generate_certificates.py first
   ```

2. **Port Already in Use**
   ```
   Error: Address already in use
   Solution: Stop existing servers or change ports in config
   ```

3. **SSL Handshake Failed**
   ```
   Error: SSL handshake failed
   Solution: Check certificate validity and CA certificate
   ```

4. **Authentication Failed**
   ```
   Error: Authentication failed
   Solution: Verify API key or certificate configuration
   ```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Set debug environment variable
export DEBUG=1

# Run tests with verbose output
python examples/run_security_tests.py --verbose
```

### Certificate Validation

To validate certificates manually:

```bash
# Check certificate validity
openssl x509 -in certs/admin.crt -text -noout

# Verify certificate chain
openssl verify -CAfile certs/ca_cert.pem certs/admin.crt

# Check certificate expiration
openssl x509 -in certs/admin.crt -noout -dates
```

## Integration with CI/CD

The security testing framework can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Security Tests
on: [push, pull_request]

jobs:
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install mcp_security_framework aiohttp
      - name: Generate certificates
        run: python examples/generate_certificates.py
      - name: Run security tests
        run: python examples/run_security_tests.py --output results.json
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: security-test-results
          path: results.json
```

## Performance Considerations

### Test Execution Time
- **Basic HTTP**: ~1-2 seconds per test
- **HTTPS**: ~2-3 seconds per test
- **mTLS**: ~3-5 seconds per test
- **Full Test Suite**: ~30-60 seconds

### Resource Usage
- **Memory**: ~50-100 MB per server instance
- **CPU**: Low usage during normal operation
- **Network**: Minimal traffic for test scenarios

### Optimization Tips
1. Run tests in parallel (with different ports)
2. Use connection pooling for multiple requests
3. Implement test result caching
4. Use lightweight certificates for testing

## Security Best Practices

### For Testing
1. Use dedicated test certificates
2. Never use production certificates in tests
3. Implement proper cleanup after tests
4. Validate all security headers
5. Test both positive and negative scenarios

### For Production
1. Use strong certificate authorities
2. Implement certificate rotation
3. Monitor certificate expiration
4. Use secure cipher suites
5. Enable security headers
6. Implement rate limiting
7. Log security events

## Contributing

When adding new security tests:

1. **Follow Naming Convention**
   - Test files: `test_<feature>_<scenario>.py`
   - Config files: `config_<type>_<auth>.json`

2. **Include Both Positive and Negative Tests**
   - Test valid configurations
   - Test invalid configurations
   - Verify error handling

3. **Document Test Scenarios**
   - Describe expected behavior
   - Document test prerequisites
   - Include troubleshooting steps

4. **Update This Documentation**
   - Add new test scenarios
   - Update usage examples
   - Document new features

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review test logs for detailed error messages
3. Verify certificate and configuration files
4. Test with minimal configuration first
5. Contact the development team

## License

This security testing framework is part of the MCP Proxy Adapter project and follows the same license terms.
