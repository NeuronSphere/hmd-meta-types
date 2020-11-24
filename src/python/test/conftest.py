import pytest


@pytest.fixture()
def example_definition():
    return {
        "name": "cluster_definition",
        "namespace": "meta.physical",
        "metatype": "noun",
        "attributes": {
            "id": {
                "type": "string",
                "required": True,
                "description": "The unique identifier for the command",
            },
            "name": {
                "description": "The name of the cluster",
                "required": True,
                "type": "string",
            },
            "type": {
                "description": "The cluster type. [Presto, Hive, etc.]",
                "required": True,
                "type": "string",
            },
            "location": {"description": "", "required": True, "type": "string"},
            "state": {
                "description": "The current state of the cluster.",
                "type": "object",
                "definition": {
                    "status": {
                        "description": "The current status of the cluster",
                        "type": "enum",
                        "required": True,
                        "definition": ["running", "stopped", "paused"],
                    },
                    "services": {
                        "description": "a collection of services exposed by the cluster",
                        "type": "array",
                        "required": True,
                        "definition": {
                            "items": {
                                "type": "object",
                                "definition": {
                                    "name": {
                                        "description": "The service name",
                                        "type": "string",
                                        "required": True,
                                    },
                                    "host": {
                                        "description": "The hostname on which the service is exposed.",
                                        "type": "string",
                                        "required": True,
                                    },
                                    "port": {
                                        "description": "The port on which the service is exposed.",
                                        "type": "integer",
                                        "required": True,
                                    },
                                },
                            }
                        },
                    },
                },
            },
        },
    }
