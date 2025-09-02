# OpenAPI Navigator v0.1.0 - Initial Release 🚀

## 🎉 What's New

**OpenAPI Navigator** is now available on PyPI! This MCP (Model Context Protocol) server makes it easy for AI agents to explore, search, and understand OpenAPI specifications without manually parsing complex JSON/YAML files.

## ✨ Key Features

### 🔍 **Smart Navigation**
- **Load OpenAPI specs** from local files or URLs
- **Navigate endpoints** with filtering by tags
- **Search endpoints** using fuzzy matching across paths, summaries, and operation IDs
- **Explore schemas** and their definitions

### 🚀 **Advanced Capabilities**
- **Multiple spec support** - load and manage multiple OpenAPI specifications simultaneously
- **Smart indexing** for fast lookups and searches
- **Reference preservation** - maintains `$ref` structures for agents to decide when to resolve
- **Version detection** - automatically handles OpenAPI 3.x and Swagger 2.x formats

## 🛠️ Available Tools

### Core Operations
- `load_spec` - Load an OpenAPI specification from a local file
- `load_spec_from_url` - Load an OpenAPI specification from a URL
- `list_loaded_specs` - List all currently loaded specifications
- `unload_spec` - Remove a specification from memory
- `get_spec_metadata` - Get comprehensive spec information (title, description, version, base path, etc.)

### Endpoint Operations
- `search_endpoints` - Search endpoints using fuzzy matching
- `get_endpoint` - Get detailed information for a specific endpoint

### Schema Operations
- `search_schemas` - Search schema names using fuzzy matching
- `get_schema` - Get detailed information for a specific schema

## 📦 Installation

```bash
# Using uvx (recommended)
uvx openapi-navigator

# Or install globally with pip
pip install openapi-navigator
```

## ⚙️ Quick Setup

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "openapi-navigator": {
      "command": "uvx",
      "args": ["openapi-navigator"],
      "env": {}
    }
  }
}
```

## 🧪 Quality Assurance

- **36 comprehensive tests** (31 unit + 5 integration)
- **68% code coverage** with robust error handling
- **Multi-format support** for YAML and JSON OpenAPI specs
- **Cross-platform compatibility** tested on Python 3.10, 3.11, and 3.12

## 🔧 Example Workflow

1. **Load a specification:**
   ```
   load_spec("/path/to/schema.yaml", "my-api")
   ```

2. **Get all endpoints:**
   ```
   search_endpoints("my-api", "")
   ```

3. **Search for specific functionality:**
   ```
   search_endpoints("my-api", "virtual machine")
   ```

4. **Get detailed endpoint info:**
   ```
   get_endpoint("my-api", "/api/virtualization/virtual-machines/", "GET")
   ```

## 🏗️ Built With

- **FastMCP** - Modern MCP server framework
- **Pydantic** - Data validation and settings management
- **FuzzyWuzzy** - Intelligent fuzzy string matching
- **PyYAML** - YAML parsing support
- **Requests** - HTTP client for URL-based specs

## 🎯 Use Cases

- **API Documentation** - Quickly explore and understand API structures
- **Code Generation** - Extract endpoint and schema information for code generation
- **API Testing** - Discover available endpoints and their parameters
- **Integration Planning** - Understand API capabilities before implementation
- **Documentation** - Generate comprehensive API documentation

## 🔒 Security

- **Absolute paths only** for local file loading
- **No code execution** - only reads and parses specifications
- **Input validation** on all operations
- **Safe URL handling** with proper error handling

## 📚 Documentation

- **Comprehensive README** with setup instructions
- **Example workflows** for common use cases
- **API documentation** for all available tools
- **Development guide** for contributors

## 🚀 What's Next

This initial release provides a solid foundation for OpenAPI navigation. Future releases will include:
- Enhanced search capabilities
- Schema validation tools
- Export functionality
- Performance optimizations

## 🙏 Acknowledgments

Built with ❤️ for the AI agent community. Special thanks to the FastMCP team for the excellent framework.

---

**Ready to explore your OpenAPI specs?** Install OpenAPI Navigator and start navigating your APIs with AI agents today!

🔗 **PyPI**: https://pypi.org/project/openapi-navigator/  
📖 **Documentation**: https://github.com/mikegaruccio/openapi-navigator  
🐛 **Issues**: https://github.com/mikegaruccio/openapi-navigator/issues
