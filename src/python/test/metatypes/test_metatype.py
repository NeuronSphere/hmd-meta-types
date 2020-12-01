import pytest
from hmd_meta_types.metatypes.metatype import MetaType


class TestMetaType:
    def test_metaclass(self):
        class Example(metaclass=MetaType):
            pass

        definition = {
            "name": "cluster_definition",
            "namespace": "meta.physical",
            "metatype": "example",
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
        klass = type("cluster_definition", (Example,), {}, definition=definition)

        assert hasattr(klass, "__metatype")
        assert getattr(klass, "__metatype") == "example"

        assert hasattr(klass, "__namespace")
        assert getattr(klass, "__namespace") == "meta.physical"

        assert hasattr(klass, "__definition")
        assert getattr(klass, "__definition") == definition

        assert hasattr(klass, "__attributes")
        assert getattr(klass, "__attributes") == [
            "id",
            "name",
            "type",
            "location",
            "state",
        ]
        assert klass.__name__ == "ClusterDefinition"
        assert klass.get_type_name() == "cluster_definition"

        example = klass(id="test", name="test", type="exampe", location="local")

        assert example["name"] == "test"
        assert example.id == "test"
        example["location"] = "cloud"
        assert example.location == "cloud"

        example.name = "another_test"
        assert example.name == "another_test"

    def test_missing_metatype(self):
        definition = {"foo": "bar"}

        class Example(metaclass=MetaType):
            pass

        klass = type("FooBar", (Example,), {}, definition=definition)

        assert not hasattr(klass, "__metatype")

    def test_missing_required_attributes(self):
        class Example(metaclass=MetaType):
            pass

        definition = {
            "name": "cluster_definition",
            "namespace": "meta.physical",
            "metatype": "example",
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
        klass = type("cluster_definition", (Example,), {}, definition=definition)

        with pytest.raises(Exception) as e:
            example = klass()

        assert "Missing required attribute id on ClusterDefinition" in str(e.value)
