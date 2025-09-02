"""Integration tests for the OpenAPI Navigator."""

import tempfile
import json
import os
from openapi_navigator.spec_manager import SpecManager


class TestIntegrationWorkflows:
    """Test complete workflows with the OpenAPI Navigator."""

    def test_complete_workflow_openapi_3(self, sample_openapi_spec):
        """Test complete workflow with OpenAPI 3.0 specification."""
        manager = SpecManager()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_openapi_spec, f, indent=2)
            temp_file = f.name

        try:
            # 1. Load the specification
            spec_id = manager.load_spec_from_file(temp_file, "pet-store")
            assert spec_id == "pet-store"
            assert "pet-store" in manager.list_loaded_specs()

            # 2. Get the spec object
            spec = manager.get_spec("pet-store")
            assert spec is not None
            assert spec.version == "openapi3"
            assert spec.spec_id == "pet-store"

            # 3. Test endpoint operations
            endpoints = spec.search_endpoints("")
            assert len(endpoints) == 3

            # Test specific endpoint retrieval
            list_pets = spec.get_endpoint("/pets", "GET")
            assert list_pets["summary"] == "List all pets"
            assert list_pets["operationId"] == "listPets"

            # Test endpoint search
            create_results = spec.search_endpoints("create")
            assert len(create_results) == 1
            assert create_results[0]["summary"] == "Create a new pet"

            # 4. Test schema operations
            schemas = spec.search_schemas("")
            assert len(schemas) == 1
            assert schemas[0]["name"] == "Pet"

            # Test specific schema retrieval
            pet_schema = spec.get_schema("Pet")
            assert pet_schema["type"] == "object"
            assert "id" in pet_schema["required"]
            assert "name" in pet_schema["required"]

            # Test schema search
            pet_results = spec.search_schemas("Pet")
            assert len(pet_results) == 1
            assert pet_results[0]["name"] == "Pet"

            # 5. Test metadata
            metadata = spec.get_spec_metadata()
            assert metadata["title"] == "Sample Pet Store API"
            assert metadata["version"] == "openapi3"
            assert metadata["openapi_version"] == "3.0.0"

            # 6. Unload the specification
            success = manager.unload_spec("pet-store")
            assert success is True
            assert "pet-store" not in manager.list_loaded_specs()

        finally:
            # Cleanup
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    def test_complete_workflow_swagger_2(self, sample_swagger_spec):
        """Test complete workflow with Swagger 2.0 specification."""
        manager = SpecManager()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_swagger_spec, f, indent=2)
            temp_file = f.name

        try:
            # 1. Load the specification
            spec_id = manager.load_spec_from_file(temp_file, "user-api")
            assert spec_id == "user-api"
            assert "user-api" in manager.list_loaded_specs()

            # 2. Get the spec object
            spec = manager.get_spec("user-api")
            assert spec is not None
            assert spec.version == "swagger2"
            assert spec.spec_id == "user-api"

            # 3. Test endpoint operations
            endpoints = spec.search_endpoints("")
            assert len(endpoints) == 2

            # Test specific endpoint retrieval
            list_users = spec.get_endpoint("/users", "GET")
            assert list_users["summary"] == "List all users"
            assert list_users["operationId"] == "listUsers"

            # Test endpoint search
            user_results = spec.search_endpoints("user")
            assert len(user_results) == 2

            # 4. Test schema operations
            schemas = spec.search_schemas("")
            assert len(schemas) == 1
            assert schemas[0]["name"] == "User"

            # Test specific schema retrieval
            user_schema = spec.get_schema("User")
            assert user_schema["type"] == "object"
            assert "id" in user_schema["required"]
            assert "username" in user_schema["required"]

            # 5. Test metadata (Swagger 2.0 specific fields)
            metadata = spec.get_spec_metadata()
            assert metadata["title"] == "Sample User API"
            assert metadata["version"] == "swagger2"
            assert metadata["openapi_version"] == "2.0"
            assert metadata["base_path"] == "/api/v1"
            assert metadata["host"] == "api.example.com"
            assert metadata["schemes"] == ["https"]

            # 6. Unload the specification
            success = manager.unload_spec("user-api")
            assert success is True
            assert "user-api" not in manager.list_loaded_specs()

        finally:
            # Cleanup
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    def test_multiple_specs_workflow(self, sample_openapi_spec, sample_swagger_spec):
        """Test working with multiple specifications simultaneously."""
        manager = SpecManager()

        # Create temporary files
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1:
            json.dump(sample_openapi_spec, f1, indent=2)
            temp_file1 = f1.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f2:
            json.dump(sample_swagger_spec, f2, indent=2)
            temp_file2 = f2.name

        try:
            # Load both specifications
            spec1_id = manager.load_spec_from_file(temp_file1, "pet-store")
            spec2_id = manager.load_spec_from_file(temp_file2, "user-api")

            assert spec1_id == "pet-store"
            assert spec2_id == "user-api"
            assert len(manager.list_loaded_specs()) == 2

            # Get both specs
            pet_spec = manager.get_spec("pet-store")
            user_spec = manager.get_spec("user-api")

            # Verify they're different
            assert pet_spec.version == "openapi3"
            assert user_spec.version == "swagger2"
            assert pet_spec.spec_data["openapi"] == "3.0.0"
            assert user_spec.spec_data["swagger"] == "2.0"

            # Test operations on both specs
            pet_endpoints = pet_spec.search_endpoints("")
            user_endpoints = user_spec.search_endpoints("")

            assert len(pet_endpoints) == 3
            assert len(user_endpoints) == 2

            # Test schema operations on both
            pet_schemas = pet_spec.search_schemas("")
            user_schemas = user_spec.search_schemas("")

            assert len(pet_schemas) == 1
            assert len(user_schemas) == 1
            assert pet_schemas[0]["name"] == "Pet"
            assert user_schemas[0]["name"] == "User"

            # Unload both specs
            manager.unload_spec("pet-store")
            manager.unload_spec("user-api")

            assert len(manager.list_loaded_specs()) == 0

        finally:
            # Cleanup
            try:
                os.unlink(temp_file1)
                os.unlink(temp_file2)
            except OSError:
                pass

    def test_error_recovery_workflow(self, sample_openapi_spec):
        """Test error recovery and graceful degradation."""
        manager = SpecManager()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_openapi_spec, f, indent=2)
            temp_file = f.name

        try:
            # Load specification
            spec_id = manager.load_spec_from_file(temp_file, "test-spec")
            assert spec_id == "test-spec"

            # Test operations on valid spec
            spec = manager.get_spec("test-spec")
            endpoints = spec.search_endpoints("")
            assert len(endpoints) == 3

            # Test error handling for non-existent endpoints/schemas
            non_existent_endpoint = spec.get_endpoint("/nonexistent", "GET")
            assert non_existent_endpoint is None

            non_existent_schema = spec.get_schema("Nonexistent")
            assert non_existent_schema is None

            # Test error handling for non-existent spec
            non_existent_spec = manager.get_spec("nonexistent")
            assert non_existent_spec is None

            # Test unloading non-existent spec
            success = manager.unload_spec("nonexistent")
            assert success is False

            # Verify original spec is still there
            assert "test-spec" in manager.list_loaded_specs()

            # Clean up
            manager.unload_spec("test-spec")

        finally:
            # Cleanup
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    def test_search_functionality_workflow(self, sample_openapi_spec):
        """Test comprehensive search functionality."""
        manager = SpecManager()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_openapi_spec, f, indent=2)
            temp_file = f.name

        try:
            # Load specification
            manager.load_spec_from_file(temp_file, "test-spec")
            spec = manager.get_spec("test-spec")

            # Test endpoint search variations
            all_endpoints = spec.search_endpoints("")
            assert len(all_endpoints) == 3

            pet_endpoints = spec.search_endpoints("pet")
            assert len(pet_endpoints) == 3

            create_endpoints = spec.search_endpoints("create")
            assert len(create_endpoints) == 1

            list_endpoints = spec.search_endpoints("list")
            assert len(list_endpoints) == 1

            # Test schema search variations
            all_schemas = spec.search_schemas("")
            assert len(all_schemas) == 1

            pet_schemas = spec.search_schemas("Pet")
            assert len(pet_schemas) == 1

            # Test fuzzy matching
            partial_endpoints = spec.search_endpoints("et")
            assert len(partial_endpoints) == 3

            partial_schemas = spec.search_schemas("et")
            assert len(partial_schemas) == 1

            # Clean up
            manager.unload_spec("test-spec")

        finally:
            # Cleanup
            try:
                os.unlink(temp_file)
            except OSError:
                pass
