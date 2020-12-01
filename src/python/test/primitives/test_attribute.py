import pytest

from hmd_meta_types.primitives.attribute import Attribute


class TestAttribute:
    def test_init(self):
        attr = Attribute("string", "test", addtl_metadata={"test": "124"})

        assert attr.get_type() == "string"
        assert attr.metadata() == {"description": "test", "test": "124"}

        with pytest.raises(Exception) as e:
            attr = Attribute("enum", "test", addtl_metadata={"test": "124"})
        assert "Missing attribute definition" in str(e.value)

        attr = Attribute(
            "array",
            "test",
            definition={
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
            addtl_metadata={"test": "124"},
        )

        assert attr.definition() == {
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
        }

    def test_get_set_simple(self):
        class Example:
            attr = Attribute("string", "test", addtl_metadata={"test": "124"})

        example = Example()
        example.attr = "test"

        assert example.attr == "test"

        with pytest.raises(Exception) as e:
            example.attr = 1

        assert "Invalid value (1) being set to attr" in str(e.value)

        class ExampleTwo:
            attr = Attribute("integer", "test", addtl_metadata={"test": "124"})

        example = ExampleTwo()
        example.attr = 1

        assert example.attr == 1
        example.attr = None
        assert example.attr is None

        class ExampleThree:
            attr = Attribute(
                "integer", "test", required=True, addtl_metadata={"test": "124"}
            )

        example = ExampleThree()
        example.attr = 1

        assert example.attr == 1
        with pytest.raises(Exception) as e:
            example.attr = None

        assert "attr is required" in str(e.value)

    def test_get_set_complex(self):
        class ExampleEnum:
            attr = Attribute(
                "enum",
                "test",
                definition=["running", "stopped", "paused"],
                addtl_metadata={"test": "124"},
            )

        example = ExampleEnum()
        example.attr = "running"

        assert example.attr == "running"

        with pytest.raises(Exception) as e:
            example.attr = "closed"

        assert "Invalid enum value: closed" in str(e.value)

        class ExampleArray:
            attr = Attribute(
                "array",
                "test",
                definition={
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
                            },
                            "port": {
                                "description": "The port on which the service is exposed.",
                                "type": "integer",
                                "required": True,
                            },
                        },
                    }
                },
                addtl_metadata={"test": "124"},
            )

        example = ExampleArray()
        example.attr = [{"name": "test", "host": "localhost", "port": 3306}]

        assert example.attr == [{"name": "test", "host": "localhost", "port": 3306}]

        with pytest.raises(Exception) as e:
            example.attr = [{"name": "test"}]
        assert "Missing key port in attribute attr" in str(e.value)

        with pytest.raises(Exception) as e:
            example.attr = [{"name": "test", "host": "localhost", "port": "3306"}]
        assert "Invalid value (3306) being set to attr" in str(e.value)

        class ExampleObject:
            attr = Attribute(
                "object",
                "test",
                definition={
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
            )

        example = ExampleObject()
        example.attr = {"name": "test", "host": "localhost", "port": 3306}

        assert example.attr == {"name": "test", "host": "localhost", "port": 3306}

        with pytest.raises(Exception) as e:
            example.attr = {"name": "test"}

        assert "Missing key host in attribute attr" in str(e.value)
