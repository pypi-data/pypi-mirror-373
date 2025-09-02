"""Unit tests for the SpecManager class."""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch
from openapi_navigator.spec_manager import SpecManager, OpenAPISpec


class TestOpenAPISpec:
    """Test the OpenAPISpec class."""

    def test_init_openapi_3(self, sample_openapi_spec):
        """Test initialization with OpenAPI 3.0 spec."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)

        assert spec.spec_id == "test-spec"
        assert spec.version == "openapi3"
        assert spec.spec_data == sample_openapi_spec
        assert len(spec.endpoints) == 3
        assert len(spec.schemas) == 1
        assert "Pet" in spec.schemas

    def test_init_swagger_2(self, sample_swagger_spec):
        """Test initialization with Swagger 2.0 spec."""
        spec = OpenAPISpec("test-spec", sample_swagger_spec)

        assert spec.spec_id == "test-spec"
        assert spec.version == "swagger2"
        assert spec.spec_data == sample_swagger_spec
        assert len(spec.endpoints) == 2
        assert len(spec.schemas) == 1
        assert "User" in spec.schemas

    def test_get_endpoint_found(self, sample_openapi_spec):
        """Test getting an endpoint that exists."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        endpoint = spec.get_endpoint("/pets", "GET")

        assert endpoint is not None
        assert endpoint["summary"] == "List all pets"
        assert endpoint["operationId"] == "listPets"

    def test_get_endpoint_not_found(self, sample_openapi_spec):
        """Test getting an endpoint that doesn't exist."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        endpoint = spec.get_endpoint("/nonexistent", "GET")

        assert endpoint is None

    def test_get_schema_found(self, sample_openapi_spec):
        """Test getting a schema that exists."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        schema = spec.get_schema("Pet")

        assert schema is not None
        assert schema["type"] == "object"
        assert "id" in schema["required"]
        assert "name" in schema["required"]

    def test_get_schema_not_found(self, sample_openapi_spec):
        """Test getting a schema that doesn't exist."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        schema = spec.get_schema("Nonexistent")

        assert schema is None

    def test_search_endpoints_empty_query(self, sample_openapi_spec):
        """Test searching endpoints with empty query returns all."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        results = spec.search_endpoints("")

        assert len(results) == 3
        # All should have score 100 for empty query
        assert all(result["score"] == 100 for result in results)

    def test_search_endpoints_specific_query(self, sample_openapi_spec):
        """Test searching endpoints with specific query."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        results = spec.search_endpoints("create")

        assert len(results) == 1
        assert results[0]["summary"] == "Create a new pet"
        assert results[0]["score"] == 100

    def test_search_endpoints_fuzzy_match(self, sample_openapi_spec):
        """Test fuzzy matching in endpoint search."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        results = spec.search_endpoints("pet")

        assert len(results) == 3
        # Should find all pet-related endpoints
        assert all("pet" in result["summary"].lower() for result in results)

    def test_search_schemas_empty_query(self, sample_openapi_spec):
        """Test searching schemas with empty query returns all."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        results = spec.search_schemas("")

        assert len(results) == 1
        assert results[0]["name"] == "Pet"
        assert results[0]["score"] == 100

    def test_search_schemas_specific_query(self, sample_openapi_spec):
        """Test searching schemas with specific query."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        results = spec.search_schemas("Pet")

        assert len(results) == 1
        assert results[0]["name"] == "Pet"
        assert results[0]["score"] == 100

    def test_search_schemas_fuzzy_match(self, sample_openapi_spec):
        """Test fuzzy matching in schema search."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        results = spec.search_schemas("et")

        assert len(results) == 1
        assert results[0]["name"] == "Pet"

    def test_get_spec_metadata_openapi_3(self, sample_openapi_spec):
        """Test getting metadata from OpenAPI 3.0 spec."""
        spec = OpenAPISpec("test-spec", sample_openapi_spec)
        metadata = spec.get_spec_metadata()

        assert metadata["spec_id"] == "test-spec"
        assert metadata["version"] == "openapi3"
        assert metadata["openapi_version"] == "3.0.0"
        assert metadata["title"] == "Sample Pet Store API"
        assert metadata["description"] == "A sample API for managing pets"
        assert metadata["version_info"] == "1.0.0"
        assert metadata["base_path"] == ""
        assert metadata["servers"] == []
        assert metadata["host"] == ""
        assert metadata["schemes"] == []

    def test_get_spec_metadata_swagger_2(self, sample_swagger_spec):
        """Test getting metadata from Swagger 2.0 spec."""
        spec = OpenAPISpec("test-spec", sample_swagger_spec)
        metadata = spec.get_spec_metadata()

        assert metadata["spec_id"] == "test-spec"
        assert metadata["version"] == "swagger2"
        assert metadata["openapi_version"] == "2.0"
        assert metadata["title"] == "Sample User API"
        assert metadata["description"] == "A sample API for managing users"
        assert metadata["version_info"] == "1.0.0"
        assert metadata["base_path"] == "/api/v1"
        assert metadata["servers"] == []
        assert metadata["host"] == "api.example.com"
        assert metadata["schemes"] == ["https"]


class TestSpecManager:
    """Test the SpecManager class."""

    def test_init(self):
        """Test SpecManager initialization."""
        manager = SpecManager()

        assert manager.specs == {}
        assert isinstance(manager.specs, dict)

    def test_load_spec_from_file_success(self, temp_spec_file):
        """Test successfully loading a spec from file."""
        manager = SpecManager()
        spec_id = manager.load_spec_from_file(temp_spec_file, "test-spec")

        assert spec_id == "test-spec"
        assert "test-spec" in manager.specs
        assert manager.specs["test-spec"].spec_id == "test-spec"

    def test_load_spec_from_file_auto_id(self, temp_spec_file):
        """Test loading spec with auto-generated ID."""
        manager = SpecManager()
        spec_id = manager.load_spec_from_file(temp_spec_file)

        assert spec_id.startswith("file:")
        assert spec_id in manager.specs

    def test_load_spec_from_file_not_found(self):
        """Test loading spec from non-existent file."""
        manager = SpecManager()

        with pytest.raises(FileNotFoundError):
            manager.load_spec_from_file("/nonexistent/file.json")

    def test_load_spec_from_file_invalid_json(self):
        """Test loading spec from invalid JSON file."""
        manager = SpecManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            with pytest.raises(Exception):
                manager.load_spec_from_file(temp_file)
        finally:
            os.unlink(temp_file)

    @patch("requests.get")
    def test_load_spec_from_url_success(self, mock_get, sample_openapi_spec):
        """Test successfully loading a spec from URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(sample_openapi_spec).encode()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = sample_openapi_spec
        mock_get.return_value = mock_response

        manager = SpecManager()
        spec_id = manager.load_spec_from_url(
            "https://example.com/api.json", "test-spec"
        )

        assert spec_id == "test-spec"
        assert "test-spec" in manager.specs
        assert manager.specs["test-spec"].spec_id == "test-spec"

    @patch("requests.get")
    def test_load_spec_from_url_auto_id(self, mock_get, sample_openapi_spec):
        """Test loading spec from URL with auto-generated ID."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(sample_openapi_spec).encode()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = sample_openapi_spec
        mock_get.return_value = mock_response

        manager = SpecManager()
        spec_id = manager.load_spec_from_url("https://example.com/api.json")

        assert spec_id.startswith("url:")
        assert spec_id in manager.specs

    @patch("requests.get")
    def test_load_spec_from_url_http_error(self, mock_get):
        """Test loading spec from URL with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not Found")
        mock_get.return_value = mock_response

        manager = SpecManager()

        with pytest.raises(Exception):
            manager.load_spec_from_url("https://example.com/api.json")

    def test_get_spec_found(self, temp_spec_file):
        """Test getting a spec that exists."""
        manager = SpecManager()
        manager.load_spec_from_file(temp_spec_file, "test-spec")

        spec = manager.get_spec("test-spec")
        assert spec is not None
        assert spec.spec_id == "test-spec"

    def test_get_spec_not_found(self):
        """Test getting a spec that doesn't exist."""
        manager = SpecManager()

        spec = manager.get_spec("nonexistent")
        assert spec is None

    def test_list_loaded_specs(self, temp_spec_file):
        """Test listing loaded specs."""
        manager = SpecManager()
        manager.load_spec_from_file(temp_spec_file, "test-spec")

        specs = manager.list_loaded_specs()
        assert "test-spec" in specs
        assert len(specs) == 1

    def test_list_loaded_specs_empty(self):
        """Test listing specs when none are loaded."""
        manager = SpecManager()

        specs = manager.list_loaded_specs()
        assert specs == []

    def test_unload_spec_success(self, temp_spec_file):
        """Test successfully unloading a spec."""
        manager = SpecManager()
        manager.load_spec_from_file(temp_spec_file, "test-spec")

        success = manager.unload_spec("test-spec")
        assert success is True
        assert "test-spec" not in manager.specs

    def test_unload_spec_not_found(self):
        """Test unloading a spec that doesn't exist."""
        manager = SpecManager()

        success = manager.unload_spec("nonexistent")
        assert success is False

    def test_unload_spec_already_unloaded(self, temp_spec_file):
        """Test unloading a spec that's already unloaded."""
        manager = SpecManager()
        manager.load_spec_from_file(temp_spec_file, "test-spec")
        manager.unload_spec("test-spec")

        success = manager.unload_spec("test-spec")
        assert success is False

    def test_load_multiple_specs(self, temp_spec_file, temp_swagger_file):
        """Test loading multiple specs."""
        manager = SpecManager()

        # Load OpenAPI spec
        spec1_id = manager.load_spec_from_file(temp_spec_file, "openapi-spec")
        # Load Swagger spec
        spec2_id = manager.load_spec_from_file(temp_swagger_file, "swagger-spec")

        assert spec1_id == "openapi-spec"
        assert spec2_id == "swagger-spec"
        assert len(manager.specs) == 2
        assert "openapi-spec" in manager.specs
        assert "swagger-spec" in manager.specs

    def test_spec_isolation(self, temp_spec_file, temp_swagger_file):
        """Test that specs are isolated from each other."""
        manager = SpecManager()

        manager.load_spec_from_file(temp_spec_file, "openapi-spec")
        manager.load_spec_from_file(temp_swagger_file, "swagger-spec")

        openapi_spec = manager.get_spec("openapi-spec")
        swagger_spec = manager.get_spec("swagger-spec")

        # Verify they have different content
        assert openapi_spec.version == "openapi3"
        assert swagger_spec.version == "swagger2"
        assert openapi_spec.spec_data["openapi"] == "3.0.0"
        assert swagger_spec.spec_data["swagger"] == "2.0"
