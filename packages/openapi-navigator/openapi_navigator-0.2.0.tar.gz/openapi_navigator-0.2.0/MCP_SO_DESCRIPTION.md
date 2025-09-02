# OpenAPI Navigator

**Navigate OpenAPI specifications with AI agents - no more manual JSON/YAML parsing!**

## What it does

OpenAPI Navigator is an MCP server that makes OpenAPI specs easily accessible to AI agents. Load specs from files or URLs, then search endpoints and schemas using natural language queries.

## Key features

- **Load specs** from local files or URLs (supports OpenAPI 3.x & Swagger 2.x)
- **Smart search** - find endpoints and schemas with fuzzy matching
- **Multiple specs** - manage several APIs simultaneously  
- **Reference preservation** - maintains `$ref` structures for agent decision-making
- **Fast indexing** - instant lookups and searches

## Perfect for

- **API exploration** - quickly understand API structure and capabilities
- **Code generation** - extract endpoint/schema info for automated code creation
- **Documentation** - generate comprehensive API docs
- **Integration planning** - discover API features before implementation
- **Testing** - find endpoints and parameters for test automation

## Quick start

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

## Example workflow

1. Load your API spec: `load_spec("/path/to/api.yaml", "my-api")`
2. Find all endpoints: `search_endpoints("my-api", "")`  
3. Search for specific functionality: `search_endpoints("my-api", "user authentication")`
4. Get endpoint details: `get_endpoint("my-api", "/users", "POST")`

**Stop wrestling with OpenAPI JSON/YAML files - let AI agents navigate them for you!**

🔗 **Install**: `uvx openapi-navigator` | **Docs**: [GitHub](https://github.com/mikegaruccio/openapi-navigator)
