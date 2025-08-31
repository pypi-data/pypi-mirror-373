# MCP Proxy Adapter

A powerful framework for creating JSON-RPC-enabled microservices with built-in security, authentication, and proxy registration capabilities.

## Features

- **JSON-RPC Framework**: Complete JSON-RPC 2.0 implementation
- **Security Integration**: Built-in support for mcp_security_framework
- **Authentication**: Multiple auth methods (API Key, JWT, Certificate, Basic Auth)
- **Proxy Registration**: Automatic registration and discovery of services
- **Command System**: Extensible command framework with role-based access control
- **SSL/TLS Support**: Full SSL/TLS support including mTLS
- **Async Support**: Built on FastAPI with full async support
- **Extensible**: Plugin system for custom commands and middleware

## Quick Start

### Installation

```bash
pip install mcp-proxy-adapter
```

### Basic Usage

```python
from mcp_proxy_adapter import create_app, Command, SuccessResult

# Create a custom command
class HelloCommand(Command):
    name = "hello"
    descr = "Say hello"
    
    async def execute(self, **kwargs) -> SuccessResult:
        name = kwargs.get("name", "World")
        return SuccessResult(f"Hello, {name}!")

# Create and run the application
app = create_app()
```

### Configuration

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "security": {
    "enabled": true,
    "framework": "mcp_security_framework"
  },
  "commands": {
    "auto_discovery": true,
    "builtin_commands": ["echo", "health", "config"]
  }
}
```

## Examples

### Proxy Registration Example

```python
# Example of proxy registration with authentication
import asyncio
from mcp_proxy_adapter.examples.proxy_registration_example import ProxyRegistrationExample

async def main():
    async with ProxyRegistrationExample("http://localhost:8002", "your-token") as client:
        result = await client.test_registration({
            "server_id": "my-server",
            "server_url": "http://localhost:8001",
            "server_name": "My Server"
        })
        print(f"Registration result: {result}")

asyncio.run(main())
```

### Security Testing

The framework includes comprehensive security testing examples:

- HTTP with Token Authentication
- HTTPS with Certificate Authentication  
- mTLS (Mutual TLS) Authentication
- Role-based Access Control
- Permission Validation

## Documentation

For detailed documentation, examples, and API reference, see the [documentation](https://github.com/maverikod/mcp-proxy-adapter).

## Development

### Setup Development Environment

```bash
git clone https://github.com/maverikod/mcp-proxy-adapter.git
cd mcp-proxy-adapter
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Running Examples

```bash
# Start server
python -m mcp_proxy_adapter.main --config examples/server_configs/config_simple.json

# Run proxy registration example
python examples/proxy_registration_example.py
```

## License

MIT License - see LICENSE file for details.

## Author

**Vasiliy Zdanovskiy** - vasilyvz@gmail.com

## Version

6.1.0 - Major release with security framework integration and proxy registration capabilities. 