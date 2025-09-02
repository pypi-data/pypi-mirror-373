"""OpenAPI Navigator - Specification manager for loading, validating, and indexing specs."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import requests
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


class OpenAPISpec:
    """Represents a loaded OpenAPI specification with indexes for fast lookups."""

    def __init__(self, spec_id: str, spec_data: Dict[str, Any]):
        self.spec_id = spec_id
        self.spec_data = spec_data
        self.version = self._detect_version()
        self._build_indexes()

    def _detect_version(self) -> str:
        """Detect if this is OpenAPI 3.x or Swagger 2.x."""
        if "openapi" in self.spec_data:
            return "openapi3"
        elif "swagger" in self.spec_data:
            return "swagger2"
        else:
            raise ValueError("Could not determine OpenAPI/Swagger version")

    def _build_indexes(self) -> None:
        """Build fast lookup indexes for endpoints and schemas."""
        self.endpoints = []
        self.schemas = {}

        # Extract endpoints
        if self.version == "openapi3":
            paths = self.spec_data.get("paths", {})
            logger.info(
                f"Building indexes for OpenAPI 3.x spec with {len(paths)} paths"
            )
            for path, path_item in paths.items():
                for method, operation in path_item.items():
                    if method in [
                        "get",
                        "post",
                        "put",
                        "delete",
                        "patch",
                        "head",
                        "options",
                        "trace",
                    ]:
                        self.endpoints.append(
                            {
                                "method": method.upper(),
                                "path": path,
                                "summary": operation.get("summary", ""),
                                "operationId": operation.get("operationId", ""),
                                "tags": operation.get("tags", []),
                                "operation": operation,
                            }
                        )
        else:  # swagger2
            paths = self.spec_data.get("paths", {})
            logger.info(
                f"Building indexes for Swagger 2.x spec with {len(paths)} paths"
            )
            for path, path_item in paths.items():
                for method, operation in path_item.items():
                    if method in [
                        "get",
                        "post",
                        "put",
                        "delete",
                        "patch",
                        "head",
                        "options",
                    ]:
                        self.endpoints.append(
                            {
                                "method": method.upper(),
                                "path": path,
                                "summary": operation.get("summary", ""),
                                "operationId": operation.get("operationId", ""),
                                "tags": operation.get("tags", []),
                                "operation": operation,
                            }
                        )

        # Extract schemas
        if self.version == "openapi3":
            schemas = self.spec_data.get("components", {}).get("schemas", {})
        else:  # swagger2
            schemas = self.spec_data.get("definitions", {})

        self.schemas = schemas

        logger.info(
            f"Built indexes: {len(self.endpoints)} endpoints, {len(self.schemas)} schemas"
        )
        if self.endpoints:
            logger.info(f"Sample endpoint: {self.endpoints[0]}")
        if self.schemas:
            logger.info(f"Sample schema names: {list(self.schemas.keys())[:5]}")

    def get_endpoint(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """Get a specific endpoint by path and method."""
        for endpoint in self.endpoints:
            if endpoint["path"] == path and endpoint["method"] == method:
                return endpoint["operation"]
        return None

    def list_endpoints(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """List endpoints, optionally filtered by tag."""
        logger.info(
            f"list_endpoints called with tag={tag}, self.endpoints has {len(self.endpoints)} items"
        )
        if tag is None:
            result = [
                {
                    "method": e["method"],
                    "path": e["path"],
                    "summary": e["summary"],
                    "operationId": e["operationId"],
                }
                for e in self.endpoints
            ]
            logger.info(f"Returning {len(result)} endpoints (no tag filter)")
            return result

        filtered = []
        for endpoint in self.endpoints:
            if tag in endpoint["tags"]:
                filtered.append(
                    {
                        "method": endpoint["method"],
                        "path": endpoint["path"],
                        "summary": endpoint["summary"],
                        "operationId": endpoint["operationId"],
                    }
                )
        logger.info(f"Returning {len(filtered)} endpoints filtered by tag '{tag}'")
        return filtered

    def search_endpoints(self, query: str) -> List[Dict[str, Any]]:
        """Search endpoints using fuzzy matching."""
        # If query is empty or very short, return all endpoints with high scores
        if not query or len(query.strip()) <= 2:
            results = []
            for endpoint in self.endpoints:
                results.append(
                    {
                        "method": endpoint["method"],
                        "path": endpoint["path"],
                        "summary": endpoint["summary"],
                        "operationId": endpoint["operationId"],
                        "score": 100,
                    }
                )
            return results

        try:
            from fuzzywuzzy import fuzz
        except ImportError:
            # Fallback to simple substring search if fuzzywuzzy is not available
            results = []
            query_lower = query.lower()
            for endpoint in self.endpoints:
                if (
                    query_lower in endpoint["path"].lower()
                    or query_lower in endpoint["summary"].lower()
                    or query_lower in endpoint["operationId"].lower()
                ):
                    results.append(
                        {
                            "method": endpoint["method"],
                            "path": endpoint["path"],
                            "summary": endpoint["summary"],
                            "operationId": endpoint["operationId"],
                            "score": 100,
                        }
                    )
            return results

        results = []
        for endpoint in self.endpoints:
            # Search in path, summary, operationId
            path_score = fuzz.partial_ratio(query.lower(), endpoint["path"].lower())
            summary_score = fuzz.partial_ratio(
                query.lower(), endpoint["summary"].lower()
            )
            op_id_score = fuzz.partial_ratio(
                query.lower(), endpoint["operationId"].lower()
            )

            # Use the best score
            best_score = max(path_score, summary_score, op_id_score)

            if best_score > 50:  # Threshold for relevance
                results.append(
                    {
                        "method": endpoint["method"],
                        "path": endpoint["path"],
                        "summary": endpoint["summary"],
                        "operationId": endpoint["operationId"],
                        "score": best_score,
                    }
                )

        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def search_schemas(self, query: str) -> List[Dict[str, Any]]:
        """Search schema names using fuzzy matching."""
        # If query is empty or very short, return all schemas with high scores
        if not query or len(query.strip()) <= 2:
            results = []
            for schema_name in self.schemas.keys():
                results.append({"name": schema_name, "score": 100})
            return results

        try:
            from fuzzywuzzy import fuzz
        except ImportError:
            # Fallback to simple substring search if fuzzywuzzy is not available
            results = []
            query_lower = query.lower()
            for schema_name in self.schemas.keys():
                if query_lower in schema_name.lower():
                    results.append({"name": schema_name, "score": 100})
            return results

        results = []
        for schema_name in self.schemas.keys():
            # Search in schema name
            score = fuzz.partial_ratio(query.lower(), schema_name.lower())

            if score > 50:  # Threshold for relevance
                results.append({"name": schema_name, "score": score})

        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def get_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific schema by name."""
        return self.schemas.get(schema_name)

    def get_spec_metadata(self) -> Dict[str, Any]:
        """Get metadata about the OpenAPI specification."""
        metadata = {
            "spec_id": self.spec_id,
            "version": self.version,
            "openapi_version": self.spec_data.get(
                "openapi", self.spec_data.get("swagger", "unknown")
            ),
            "title": self.spec_data.get("info", {}).get("title", ""),
            "description": self.spec_data.get("info", {}).get("description", ""),
            "version_info": self.spec_data.get("info", {}).get("version", ""),
            "contact": self.spec_data.get("info", {}).get("contact", {}),
            "license": self.spec_data.get("info", {}).get("license", {}),
            "terms_of_service": self.spec_data.get("info", {}).get(
                "termsOfService", ""
            ),
            "servers": self.spec_data.get("servers", []),
            "host": self.spec_data.get("host", ""),
            "base_path": self.spec_data.get("basePath", ""),
            "schemes": self.spec_data.get("schemes", []),
            "tags": self.spec_data.get("tags", []),
            "endpoint_count": len(self.endpoints),
            "schema_count": len(self.schemas),
        }
        return metadata

    def list_schemas(self, prefix: Optional[str] = None) -> List[str]:
        """List schema names, optionally filtered by prefix."""
        logger.info(
            f"list_schemas called with prefix={prefix}, self.schemas has {len(self.schemas)} items"
        )
        schema_names = list(self.schemas.keys())
        if prefix:
            schema_names = [
                name for name in schema_names if name.lower().startswith(prefix.lower())
            ]
        logger.info(
            f"Returning {len(schema_names)} schema names (filtered by prefix '{prefix}')"
        )
        return sorted(schema_names)


class SpecManager:
    """Manages multiple loaded OpenAPI specifications."""

    def __init__(self):
        self.specs: Dict[str, OpenAPISpec] = {}
        self._openapi3_schema = None
        self._swagger2_schema = None

    def _get_openapi3_schema(self) -> Dict[str, Any]:
        """Get OpenAPI 3.x JSON schema for validation."""
        if self._openapi3_schema is None:
            # Basic OpenAPI 3.x schema - we could load the full one from json-schema.org
            self._openapi3_schema = {
                "type": "object",
                "required": ["openapi", "info", "paths"],
                "properties": {
                    "openapi": {"type": "string"},
                    "info": {"type": "object"},
                    "paths": {"type": "object"},
                },
            }
        return self._openapi3_schema

    def _get_swagger2_schema(self) -> Dict[str, Any]:
        """Get Swagger 2.x JSON schema for validation."""
        if self._swagger2_schema is None:
            # Basic Swagger 2.x schema
            self._swagger2_schema = {
                "type": "object",
                "required": ["swagger", "info", "paths"],
                "properties": {
                    "swagger": {"type": "string"},
                    "info": {"type": "object"},
                    "paths": {"type": "object"},
                },
            }
        return self._swagger2_schema

    def load_spec_from_file(self, file_path: str, spec_id: Optional[str] = None) -> str:
        """Load an OpenAPI spec from a local file."""
        if not Path(file_path).is_absolute():
            raise ValueError("File path must be absolute")

        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.endswith((".yaml", ".yml")):
                    spec_data = yaml.safe_load(f)
                else:
                    spec_data = json.load(f)

            return self._load_spec(spec_data, spec_id or f"file:{file_path}")

        except Exception as e:
            logger.error(f"Failed to load spec from file {file_path}: {e}")
            raise

    def load_spec_from_url(self, url: str, spec_id: Optional[str] = None) -> str:
        """Load an OpenAPI spec from a URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "yaml" in content_type or "yml" in content_type:
                spec_data = yaml.safe_load(response.text)
            else:
                spec_data = response.json()

            return self._load_spec(spec_data, spec_id or f"url:{url}")

        except Exception as e:
            logger.error(f"Failed to load spec from URL {url}: {e}")
            raise

    def _load_spec(self, spec_data: Dict[str, Any], spec_id: str) -> str:
        """Internal method to load and validate a spec."""
        try:
            # Basic validation
            if "openapi" in spec_data:
                validate(spec_data, self._get_openapi3_schema())
            elif "swagger" in spec_data:
                validate(spec_data, self._get_swagger2_schema())
            else:
                raise ValueError(
                    "Spec does not appear to be a valid OpenAPI or Swagger document"
                )

            # Create the spec object
            spec = OpenAPISpec(spec_id, spec_data)
            self.specs[spec_id] = spec

            logger.info(
                f"Successfully loaded spec {spec_id} with {len(spec.endpoints)} endpoints and {len(spec.schemas)} schemas"
            )
            return spec_id

        except ValidationError as e:
            logger.warning(f"Spec validation warnings for {spec_id}: {e}")
            # Continue anyway - just warn
            spec = OpenAPISpec(spec_id, spec_data)
            self.specs[spec_id] = spec
            return spec_id
        except Exception as e:
            logger.error(f"Failed to load spec {spec_id}: {e}")
            raise

    def get_spec(self, spec_id: str) -> Optional[OpenAPISpec]:
        """Get a loaded spec by ID."""
        return self.specs.get(spec_id)

    def list_loaded_specs(self) -> List[str]:
        """List IDs of all loaded specs."""
        return list(self.specs.keys())

    def unload_spec(self, spec_id: str) -> bool:
        """Unload a spec by ID."""
        if spec_id in self.specs:
            del self.specs[spec_id]
            logger.info(f"Unloaded spec {spec_id}")
            return True
        return False
