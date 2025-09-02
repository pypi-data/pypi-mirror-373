# OpenAPI Navigator

[![CI](https://github.com/mikegaruccio/openapi-navigator/workflows/CI/badge.svg)](https://github.com/mikegaruccio/openapi-navigator/actions/workflows/ci.yml)
[![Build](https://github.com/mikegaruccio/openapi-navigator/workflows/Build/badge.svg)](https://github.com/mikegaruccio/openapi-navigator/actions/workflows/build.yml)
[![Release](https://github.com/mikegaruccio/openapi-navigator/workflows/Release/badge.svg)](https://github.com/mikegaruccio/openapi-navigator/actions/workflows/release.yml)

An MCP (Model Context Protocol) server that provides tools for navigating and querying OpenAPI specifications. This server makes it easy for AI agents to explore, search, and understand OpenAPI specs without having to manually parse complex JSON/YAML files.

## Features

- **Load OpenAPI specs** from local files or URLs
- **Navigate endpoints** with filtering by tags
- **Search endpoints** using fuzzy matching across paths, summaries, and operation IDs
- **Explore schemas** and their definitions
- **Multiple spec support** - load and manage multiple OpenAPI specifications simultaneously
- **Smart indexing** for fast lookups and searches
- **Reference preservation** - maintains `$ref` structures for agents to decide when to resolve

## Installation

This project uses `uv` for dependency management. Install dependencies with:

```bash
uvx sync
```

## Usage

### Running the Server

The server can be run in several ways:

#### 1. Using the package command (recommended)
```bash
uvx openapi-navigator
```

#### 2. Using FastMCP CLI (local development)
```bash
uv run fastmcp run src/openapi_mcp/server.py --transport stdio
```

#### 3. Using FastMCP CLI with HTTP transport (local development)
```bash
uv run fastmcp run src/openapi_mcp/server.py --transport http --host 127.0.0.1 --port 8000
```

## Available Tools

The OpenAPI Navigator provides the following tools:

### Core Operations
- **`load_spec`** - Load an OpenAPI specification from a local file (requires absolute path)
- **`load_spec_from_url`** - Load an OpenAPI specification from a URL
- **`list_loaded_specs`** - List all currently loaded specifications
- **`unload_spec`** - Remove a specification from memory

### Endpoint Operations
- **`search_endpoints`** - Search endpoints using fuzzy matching. Use `""` or `"a"` as the query to get all endpoints
- **`get_endpoint`** - Get detailed information for a specific endpoint by path and method

### Schema Operations
- **`search_schemas`** - Search schema names using fuzzy matching. Use `""` or `"a"` as the query to get all schemas
- **`get_schema`** - Get detailed information for a specific schema by name

## Example Workflow

1. **Load a specification:**
   ```
   load_spec("/absolute/path/to/schema.yaml", "my-api")
   ```

2. **Get all endpoints:**
   ```
   search_endpoints("my-api", "")
   ```

3. **Get all schemas:**
   ```
   search_schemas("my-api", "")
   ```

4. **Search for specific endpoints:**
   ```
   search_endpoints("my-api", "virtual machine")
   ```

5. **Get endpoint details:**
   ```
   get_endpoint("my-api", "/api/virtualization/virtual-machines/", "GET")
   ```

6. **Get schema details:**
   ```
   get_schema("my-api", "VirtualMachine")
   ```

## Development

### Testing

The OpenAPI Navigator includes a comprehensive test suite with both unit and integration tests.

#### Running Tests

**All tests:**
```bash
uv run pytest
```

**Unit tests only (fast):**
```bash
uv run pytest tests/unit/
```

**Integration tests only:**
```bash
uv run pytest tests/integration/
```

**With coverage report:**
```bash
uv run pytest --cov=src --cov-report=html
```

#### Using the Makefile

For convenience, a Makefile is provided with common test targets:

```bash
# Run all tests
make test

# Run only unit tests (fast feedback)
make test-unit

# Run integration tests
make test-integration

# Run tests with coverage report
make test-cov

# Clean up generated files
make clean

# Format code
make format

# Lint code
make lint
```

#### Test Structure

- **`tests/unit/`** - Unit tests for individual components
  - `test_spec_manager.py` - Tests for the core specification management
- **`tests/integration/`** - Integration tests for complete workflows
  - `test_integration.py` - End-to-end workflow testing
- **`tests/conftest.py`** - Shared test fixtures and configuration

#### Test Coverage

The test suite aims for at least 65% code coverage and includes:
- **31 unit tests** covering core functionality
- **5 integration tests** covering complete workflows
- **Mock testing** for external dependencies
- **Error handling** validation
- **Edge case** coverage

### Inspecting the Server

Use FastMCP CLI to inspect the server:
```bash
uv run fastmcp inspect src/openapi_mcp/server.py
```

This will generate a `server-info.json` file with detailed information about all available tools.

## CI/CD Pipeline

The OpenAPI Navigator uses GitHub Actions for continuous integration and deployment.

### Workflows

#### 🔄 **CI** (`ci.yml`)
- **Triggers**: Pull requests and pushes to main
- **Runs**: Tests on Python 3.10, 3.11, and 3.12
- **Features**:
  - Full test suite execution
  - Code coverage reporting
  - Linting and formatting checks with ruff
  - Code formatting with black

#### 🏗️ **Build** (`build.yml`)
- **Triggers**: Merges to main branch
- **Features**:
  - Comprehensive testing
  - Package building
  - Code quality checks
  - Artifact uploads

#### 🚀 **Release** (`release.yml`)
- **Triggers**: GitHub releases
- **Features**:
  - Automatic PyPI publishing (supports trusted publisher OIDC)
  - GitHub release creation
  - Pre-release testing

#### 📦 **Dependencies** (`dependencies.yml`)
- **Triggers**: Weekly (Mondays) + manual
- **Features**:
  - Automatic dependency updates
  - Pull request creation
  - Test validation

### Setup Requirements

#### **Option 1: Trusted Publisher (Recommended)**
1. **PyPI Account**: Create account at [pypi.org](https://pypi.org)
2. **Configure Trusted Publisher**: In PyPI settings, add GitHub as a trusted publisher
3. **Push to GitHub**: Workflows will automatically activate

#### **Option 2: API Token (Traditional)**
1. **PyPI Account**: Create account at [pypi.org](https://pypi.org)
2. **Generate API Token**: In PyPI settings, create an API token
3. **GitHub Secrets**: Add `PYPI_API_TOKEN` with your PyPI token
4. **Update Workflow**: Uncomment the `UV_TOKEN` line in `.github/workflows/release.yml`
5. **Push to GitHub**: Workflows will automatically activate

### Release Process

1. **Create Release**: Tag a new version in GitHub
2. **Automated Testing**: CI runs full test suite
3. **Package Building**: Creates distributable packages
4. **PyPI Publishing**: Automatically publishes to PyPI
5. **Release Notes**: Generates comprehensive release notes

### Quality Gates

- ✅ **Test Coverage**: Minimum 65% required
- ✅ **All Tests Pass**: Unit and integration tests
- ✅ **Code Quality**: Linting and formatting with ruff and black
- ✅ **Dependencies**: Up-to-date and secure

## Architecture

The OpenAPI Navigator consists of two main components:

1. **SpecManager**: Handles loading, validation, and indexing of OpenAPI specifications
2. **MCP Server**: Exposes tools through the Model Context Protocol

### SpecManager Features

- **Multi-format support**: Handles both YAML and JSON OpenAPI specs
- **Version detection**: Automatically detects OpenAPI 3.x vs Swagger 2.x
- **Smart indexing**: Builds indexes for fast endpoint and schema lookups
- **Fuzzy search**: Provides intelligent search across endpoint metadata
- **Reference handling**: Preserves `$ref` structures without automatic resolution

### Error Handling

- **Validation warnings**: Warns on validation issues but continues if possible
- **Graceful degradation**: Only rejects specs that prevent core functionality
- **Helpful error messages**: Provides clear feedback on what went wrong

## Security Considerations

- **Absolute paths only**: Local file loading requires absolute paths for security
- **No automatic execution**: The server only reads and parses specs, never executes code
- **Input validation**: All inputs are validated before processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.