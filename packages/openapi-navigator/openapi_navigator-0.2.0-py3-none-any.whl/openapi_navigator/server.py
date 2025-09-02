"""OpenAPI Navigator - Tools for navigating OpenAPI specifications."""

import logging
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP
from openapi_navigator.spec_manager import SpecManager

logger = logging.getLogger(__name__)

# Create a global spec manager instance that all tools share
_spec_manager = SpecManager()

# Create the main MCP server instance for CLI tools to find
mcp = FastMCP("openapi-navigator")


# Register all tools
@mcp.tool
def load_spec(file_path: str, spec_id: Optional[str] = None) -> str:
    """
    Load an OpenAPI specification from a local file.

    Args:
        file_path: Absolute path to the OpenAPI spec file (YAML or JSON)
        spec_id: Optional custom identifier for the spec. If not provided, will use 'file:{file_path}'

    Returns:
        The spec ID that was assigned to the loaded specification

    Note:
        File path must be absolute for security reasons.
    """
    try:
        return _spec_manager.load_spec_from_file(file_path, spec_id)
    except Exception as e:
        logger.error(f"Failed to load spec from file: {e}")
        raise


@mcp.tool
def load_spec_from_url(url: str, spec_id: Optional[str] = None) -> str:
    """
    Load an OpenAPI specification from a URL.

    Args:
        url: URL to the OpenAPI spec (YAML or JSON)
        spec_id: Optional custom identifier for the spec. If not provided, will use 'url:{url}'

    Returns:
        The spec ID that was assigned to the loaded specification
    """
    try:
        return _spec_manager.load_spec_from_url(url, spec_id)
    except Exception as e:
        logger.error(f"Failed to load spec from URL: {e}")
        raise


@mcp.tool
def unload_spec(spec_id: str) -> str:
    """
    Unload an OpenAPI specification from memory.

    Args:
        spec_id: ID of the loaded spec to unload

    Returns:
        Confirmation message
    """
    success = _spec_manager.unload_spec(spec_id)
    if success:
        return f"Successfully unloaded spec: {spec_id}"
    else:
        return f"Spec not found or already unloaded: {spec_id}"


@mcp.tool
def list_loaded_specs() -> List[str]:
    """
    List all currently loaded OpenAPI specifications.

    Returns:
        List of spec IDs that are currently loaded
    """
    return _spec_manager.list_loaded_specs()


@mcp.tool
def get_endpoint(spec_id: str, path: str, method: str) -> Optional[Dict[str, Any]]:
    """
    Get the complete operation definition for a specific endpoint.

    Args:
        spec_id: ID of the loaded spec to query
        path: API path (e.g., '/users/{id}')
        method: HTTP method (e.g., 'GET', 'POST')

    Returns:
        The raw operation object from the OpenAPI spec, or None if not found
    """
    spec = _spec_manager.get_spec(spec_id)
    if not spec:
        raise ValueError(f"No spec found with ID: {spec_id}")

    return spec.get_endpoint(path, method.upper())


@mcp.tool
def search_endpoints(spec_id: str, query: str) -> List[Dict[str, Any]]:
    """
    Search endpoints using fuzzy matching across paths, summaries, and operation IDs.

    To get a full list of all endpoints, use an empty string "" or a very short query like "a" as the search term.
    The search will return all endpoints with a relevance score of 100 when the query is very short.

    Args:
        spec_id: ID of the loaded spec to query
        query: Search query string. Use "" or "a" to get all endpoints.

    Returns:
        List of matching endpoints with relevance scores
    """
    spec = _spec_manager.get_spec(spec_id)
    if not spec:
        raise ValueError(f"No spec found with ID: {spec_id}")

    return spec.search_endpoints(query)


@mcp.tool
def get_schema(spec_id: str, schema_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific schema definition from a loaded OpenAPI specification.

    Args:
        spec_id: ID of the loaded spec to query
        schema_name: Name of the schema to retrieve

    Returns:
        The raw schema object from the OpenAPI spec, or None if not found
    """
    spec = _spec_manager.get_spec(spec_id)
    if not spec:
        raise ValueError(f"No spec found with ID: {spec_id}")

    return spec.get_schema(schema_name)


@mcp.tool
def search_schemas(spec_id: str, query: str) -> List[Dict[str, Any]]:
    """
    Search schema names using fuzzy matching.

    To get a full list of all schemas, use an empty string "" or a very short query like "a" as the search term.
    The search will return all schemas with a relevance score of 100 when the query is very short.

    Args:
        spec_id: ID of the loaded spec to query
        query: Search query string. Use "" or "a" to get all schemas.

    Returns:
        List of matching schema names with relevance scores
    """
    spec = _spec_manager.get_spec(spec_id)
    if not spec:
        raise ValueError(f"No spec found with ID: {spec_id}")

    return spec.search_schemas(query)


@mcp.tool
def get_spec_metadata(spec_id: str) -> Dict[str, Any]:
    """
    Get comprehensive metadata about a loaded OpenAPI specification.

    This includes information about the spec version, title, description, base path,
    servers, contact info, license, and counts of endpoints and schemas.

    Args:
        spec_id: ID of the loaded spec to query

    Returns:
        Dictionary containing spec metadata including base path and help text
    """
    spec = _spec_manager.get_spec(spec_id)
    if not spec:
        raise ValueError(f"No spec found with ID: {spec_id}")

    return spec.get_spec_metadata()


def main():
    """Main entry point for the OpenAPI MCP server."""
    logging.basicConfig(level=logging.INFO)
    # Use the module-level mcp instance
    mcp.run()


if __name__ == "__main__":
    main()
