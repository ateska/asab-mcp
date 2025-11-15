# asab-mcp

[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE)

MCP (Model Context Protocol) Server/Proxy implementation built on top of [ASAB](https://github.com/TeskaLabs/asab) - the Asynchronous Server App Boilerplate framework for Python 3 and asyncio.

## Overview

`asab-mcp` provides a production-ready MCP server implementation that leverages the power of ASAB's microservice framework. It enables you to expose tools and resources to MCP-compatible clients through a clean, decorator-based API.

The Model Context Protocol (MCP) is a standardized protocol for connecting AI applications to external data sources and tools. This implementation allows you to build MCP servers as ASAB microservices, benefiting from ASAB's unified configuration, logging, metrics, and HTTP server capabilities.

## Features

- **MCP Protocol Implementation**: Full support for MCP protocol specification (2024-11-05)
- **Decorator-based API**: Easy-to-use decorators for registering tools and resources
- **Built on ASAB**: Leverages ASAB's microservice framework for production-ready applications
- **JSON-RPC over HTTP**: Standard HTTP/JSON-RPC interface for MCP communication
- **Resource Templates**: Support for URI templates and resource listing
- **Example Handler**: Includes a Markdown notes handler as a reference implementation
- **Async/Await**: Fully asynchronous using Python 3 async/await syntax

## Installation

```bash
pip install asab-mcp
```

## Quick Start

### Basic Example

```python
#!/usr/bin/env python3
from asabmcp import ASABMCPApplication
from asabmcp.mcp import mcp_tool, mcp_resource_template
from asabmcp.mcp.datacls import MCPToolResultTextContent

class MyMCPApplication(ASABMCPApplication):
    def __init__(self):
        super().__init__()
        
        # Register your tools
        self.App.MCPService.add_tool(self.hello_world)

    @mcp_tool(
        name="hello_world",
        title="Hello World",
        description="A simple hello world tool",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name to greet"}
            },
            "required": ["name"]
        }
    )
    async def hello_world(self, name: str):
        return MCPToolResultTextContent(
            text=f"Hello, {name}!"
        )

if __name__ == '__main__':
    app = MyMCPApplication()
    app.run()
```

### Running the Server

```bash
python asab-mcp.py
```

The server will start on `http://localhost:8898` by default. You can configure the listen address in your ASAB configuration file.

## Architecture

### Components

- **MCPService**: Core service that handles MCP protocol communication via JSON-RPC
- **MCP Tools**: Callable functions exposed to MCP clients
- **MCP Resources**: Readable resources accessible via URI templates
- **Markdown Notes Handler**: Example implementation showing how to create custom handlers

### MCP Protocol Support

The implementation supports the following MCP protocol methods:

- `initialize` - Initialize the MCP connection
- `tools/list` - List available tools
- `tools/call` - Invoke a tool
- `resources/list` - List available resources
- `resources/read` - Read a resource
- `resources/templates/list` - List resource templates
- `ping` - Health check endpoint

## Creating Custom Handlers

You can create custom MCP handlers by implementing classes that register tools and resources with the MCPService. Here's an example based on the included Markdown notes handler:

```python
from asabmcp.mcp import mcp_tool, mcp_resource_template
from asabmcp.mcp.datacls import MCPToolResultResourceLink

class MyCustomHandler:
    def __init__(self, app):
        self.App = app
        self.App.MCPService.add_tool(self.my_tool)
        self.App.MCPService.add_resource_template(self.my_resource_template)

    @mcp_tool(
        name="my_tool",
        title="My Tool",
        description="Description of my tool",
        inputSchema={
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            }
        }
    )
    async def my_tool(self, param: str):
        # Your tool implementation
        return "Tool result"

    @mcp_resource_template(
        uri_prefix="my://",
        uri_template="my://{path*}",
        name="my_resources",
        title="My Resources",
        description="My custom resources",
        mimeType="text/plain"
    )
    async def my_resource_template(self, uri: str):
        # Your resource reading implementation
        return {
            "uri": uri,
            "mimeType": "text/plain",
            "text": "Resource content"
        }
```

## Configuration

Configuration follows ASAB's standard configuration system. You can configure the web server listen address:

```ini
[web]
listen = 8898
```

## About ASAB

This project is built on top of [ASAB (Asynchronous Server App Boilerplate)](https://github.com/TeskaLabs/asab), a microservice framework for Python 3 and asyncio. ASAB provides:

- Unified configuration management
- Structured logging
- Metrics with InfluxDB and Prometheus support
- HTTP server powered by aiohttp
- Dependency injection using Modules and Services
- Event-driven architecture

For more information about ASAB, visit the [official repository](https://github.com/TeskaLabs/asab) and [documentation](https://docs.teskalabs.com/asab/).

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## References

- [ASAB Framework](https://github.com/TeskaLabs/asab) - The underlying microservice framework
- [Model Context Protocol Specification](https://modelcontextprotocol.io/) - Official MCP specification
