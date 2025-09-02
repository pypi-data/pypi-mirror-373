"""Pytest configuration and shared fixtures for OpenAPI Navigator tests."""

import pytest
import tempfile
import json
import os


@pytest.fixture
def sample_openapi_spec():
    """Sample OpenAPI 3.0 specification for testing."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Sample Pet Store API",
            "version": "1.0.0",
            "description": "A sample API for managing pets",
        },
        "paths": {
            "/pets": {
                "get": {
                    "summary": "List all pets",
                    "operationId": "listPets",
                    "tags": ["pets"],
                    "responses": {
                        "200": {
                            "description": "List of pets",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Pet"},
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create a new pet",
                    "operationId": "createPet",
                    "tags": ["pets"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Pet"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Pet created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Pet"}
                                }
                            },
                        }
                    },
                },
            },
            "/pets/{petId}": {
                "get": {
                    "summary": "Get pet by ID",
                    "operationId": "getPet",
                    "tags": ["pets"],
                    "parameters": [
                        {
                            "name": "petId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Pet details",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Pet"}
                                }
                            },
                        }
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "required": ["id", "name"],
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "Unique identifier for the pet",
                        },
                        "name": {"type": "string", "description": "Name of the pet"},
                        "species": {
                            "type": "string",
                            "description": "Species of the pet",
                        },
                        "age": {
                            "type": "integer",
                            "description": "Age of the pet in years",
                        },
                    },
                }
            }
        },
    }


@pytest.fixture
def sample_swagger_spec():
    """Sample Swagger 2.0 specification for testing."""
    return {
        "swagger": "2.0",
        "info": {
            "title": "Sample User API",
            "version": "1.0.0",
            "description": "A sample API for managing users",
        },
        "basePath": "/api/v1",
        "host": "api.example.com",
        "schemes": ["https"],
        "paths": {
            "/users": {
                "get": {
                    "summary": "List all users",
                    "operationId": "listUsers",
                    "tags": ["users"],
                    "responses": {
                        "200": {
                            "description": "List of users",
                            "schema": {
                                "type": "array",
                                "items": {"$ref": "#/definitions/User"},
                            },
                        }
                    },
                }
            },
            "/users/{userId}": {
                "get": {
                    "summary": "Get user by ID",
                    "operationId": "getUser",
                    "tags": ["users"],
                    "parameters": [
                        {
                            "name": "userId",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User details",
                            "schema": {"$ref": "#/definitions/User"},
                        }
                    },
                }
            },
        },
        "definitions": {
            "User": {
                "type": "object",
                "required": ["id", "username"],
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "Unique identifier for the user",
                    },
                    "username": {
                        "type": "string",
                        "description": "Username of the user",
                    },
                    "email": {
                        "type": "string",
                        "description": "Email address of the user",
                    },
                },
            }
        },
    }


@pytest.fixture
def temp_spec_file(sample_openapi_spec):
    """Create a temporary OpenAPI spec file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_openapi_spec, f, indent=2)
        temp_file = f.name

    yield temp_file

    # Cleanup
    try:
        os.unlink(temp_file)
    except OSError:
        pass


@pytest.fixture
def temp_swagger_file(sample_swagger_spec):
    """Create a temporary Swagger spec file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_swagger_spec, f, indent=2)
        temp_file = f.name

    yield temp_file

    # Cleanup
    try:
        os.unlink(temp_file)
    except OSError:
        pass


@pytest.fixture
def mock_response():
    """Mock response object for testing HTTP requests."""

    class MockResponse:
        def __init__(self, status_code, content, headers=None):
            self.status_code = status_code
            self.content = content
            self.headers = headers or {}
            self.text = content.decode() if isinstance(content, bytes) else content

        def json(self):
            import json

            return json.loads(self.text)

    return MockResponse
