from setuptools import setup, find_packages

setup(
    name="mcp-proxy-adapter",
    version="6.1.1",
    description="Adapter for MCP Proxy JSON-RPC communications",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Vasiliy Zdanovskiy",
    author_email="vasilyvz@gmail.com",
    url="https://github.com/maverikod/mcp-proxy-adapter",
    packages=find_packages(exclude=["mcp_sdk*"]) + ['examples', 
               'examples.minimal_example', 
               'examples.basic_example',
               'examples.complete_example',
               'examples.anti_patterns'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.95.0,<1.0.0",
        "pydantic>=2.0.0",
        "uvicorn>=0.22.0,<1.0.0",
        "docstring-parser>=0.15,<1.0.0",
        "typing-extensions>=4.5.0,<5.0.0",
        "jsonrpc>=1.2.0",
        "psutil>=5.9.0",
        "mcp_security_framework>=1.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
        ],
    },
    package_data={
        'examples': ['**/*.py', '**/*.json', '**/*.yaml']
    },
    include_package_data=True,
) 