# mcpbytes-lambda-core

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP 2025-06-18](https://img.shields.io/badge/MCP-2025--06--18-green.svg)](https://spec.modelcontextprotocol.io/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Transport-agnostic [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server core for AWS Lambda. Build production-ready MCP servers that work across multiple transports without vendor lock-in.

## 🚀 **Quick Start**

```python
from mcpbytes_lambda.core import MCPServer, ToolResult, TextContent

# Create server with default 1MB payload limit
mcp = MCPServer(name="math-server", version="1.0.0")

@mcp.tool(name="math.add", read_only=True, idempotent=True)
def add_numbers(a: float, b: float) -> ToolResult:
    """Add two numbers with high precision."""
    result = a + b
    return ToolResult(
        content=[TextContent(text=f"{a} + {b} = {result}")],
        isError=False
    )

# Use with any transport (API Gateway, stdio, etc.)
def lambda_handler(event, context):
    from mcpbytes_lambda.apigw import ApiGatewayAdapter
    return mcp.handle(event, ApiGatewayAdapter())
```

## ⚙️ **Payload Size Configuration**

Configure maximum request payload size based on your transport:

```python
# Default (1MB) - works across all transports
mcp = MCPServer(name="my-server")

# API Gateway optimized (10MB maximum)
mcp = MCPServer(name="api-server", max_payload_size=10_000_000)

# Stdio unlimited (for local development)
mcp = MCPServer(name="stdio-server", max_payload_size=100_000_000)

# Conservative (512KB for ALB)
mcp = MCPServer(name="alb-server", max_payload_size=512_000)
```

**Transport Limits:**
- **API Gateway**: 10MB maximum
- **Lambda Direct**: 6MB maximum  
- **ALB**: 1MB maximum
- **Stdio**: No inherent limit

## ✨ **Features**

- **🔌 Transport Agnostic** - Works with API Gateway, stdio, Lambda Function URLs, ALB
- **📝 Auto Schema Generation** - JSON Schema from Python type hints
- **🛡️ Built-in Validation** - Parameter validation with clear error messages
- **⚡ Sync + Async Support** - Handle both synchronous and asynchronous tools
- **📊 Structured Output** - MCP 2025-06-18 structured data support
- **🎯 Zero Cold Start** - Optimized for AWS Lambda performance
- **🔒 Production Ready** - Comprehensive error handling and logging

## 📋 **Requirements**

- Python 3.12+
- No runtime dependencies (pure Python)

## 🏗️ **Architecture**

The core provides the foundation for MCP servers without transport coupling:

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Transport      │───▶│   Core       │───▶│   Your Tools    │
│  (HTTP/stdio)   │    │  Protocol    │    │   & Prompts     │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## 🛠️ **Usage Examples**

### **Simple Tool**

```python
@mcp.tool(name="greet", description="Greet a user")
def greet(name: str) -> ToolResult:
    return ToolResult(
        content=[TextContent(text=f"Hello, {name}!")],
        isError=False
    )
```

### **Structured Output Tool** (MCP 2025-06-18)

```python
@mcp.tool(name="calculate", structured_output=True)
def calculate(operation: str, values: List[float]) -> Dict[str, Any]:
    """Returns structured data with auto-generated schema."""
    result = sum(values) if operation == "sum" else max(values)
    return {
        "operation": operation,
        "input_values": values,
        "result": result,
        "timestamp": "2025-06-18T12:00:00Z"
    }
```

### **Async Tool**

```python
@mcp.tool(name="fetch_data", read_only=True)
async def fetch_data(url: str) -> ToolResult:
    # Async operations supported natively
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return ToolResult(
            content=[TextContent(text=response.text[:500])],
            isError=False
        )
```

### **Prompt Templates**

```python
@mcp.prompt(name="code_review")
def code_review_prompt(language: str, code: str) -> str:
    """Generate code review prompt."""
    return f"Review this {language} code for best practices:\n\n```{language}\n{code}\n```"
```

## 🔌 **Transport Adapters**

The core works with multiple transport adapters:

- **`mcpbytes-lambda-apigw`** - API Gateway + Lambda
- **`mcpbytes-lambda-stdio`** - stdin/stdout (local MCP servers)  
- **`mcpbytes-lambda-invoke`** - Direct Lambda invocation
- **`mcpbytes-lambda-alb`** - Application Load Balancer + Lambda

## 📖 **API Reference**

### **MCPServer**

```python
MCPServer(
    name: str,                           # Server name
    version: str = "1.0.0",             # Server version  
    description: Optional[str] = None,   # Server description
    log_level: str = "INFO",             # Logging level
    max_payload_size: int = 1_000_000    # Maximum request payload size in bytes
)
```

### **@tool Decorator**

```python
@mcp.tool(
    name: Optional[str] = None,           # Tool name (defaults to function name)
    description: Optional[str] = None,    # Description (from docstring)
    title: Optional[str] = None,          # Human-readable title
    read_only: bool = False,              # Tool only reads data
    destructive: bool = False,            # Tool can destroy data
    idempotent: bool = False,             # Safe to call repeatedly
    open_world: bool = True,              # Interacts with external systems
    structured_output: bool = False       # Enable structured output (MCP 2025-06-18)
)
```

### **ToolResult**

```python
ToolResult(
    content: List[ContentBlock],                    # Text/resource content blocks
    isError: bool = False,                         # Whether this is an error
    structuredContent: Optional[Dict] = None       # Structured data (MCP 2025-06-18)
)
```

## 🧪 **Testing**

```python
# Test your tools directly
def test_add_tool():
    result = add_numbers(2, 3)
    assert not result.isError
    assert "5" in result.content[0].text

# Test with mock transport
def test_server_integration():
    event = {"body": '{"jsonrpc":"2.0","method":"tools/list","id":"1"}'}
    from mcpbytes_lambda.apigw import ApiGatewayAdapter
    
    response = mcp.handle(event, ApiGatewayAdapter())
    assert response["statusCode"] == 200
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `python -m pytest`
5. Submit a pull request

## 📄 **License**

Apache 2.0 License - see [LICENSE](../../LICENSE) for details.

## 🔗 **Related Packages**

- [`mcpbytes-lambda-apigw`](../apigw/) - API Gateway transport adapter
- [`mcpbytes-lambda-stdio`](../stdio/) - Stdio transport adapter  
- [`mcpbytes-lambda-invoke`](../invoke/) - Direct Lambda invocation adapter

## 📚 **Documentation**

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Project Examples](../../examples/)

---

Built with ❤️ for the MCP ecosystem
