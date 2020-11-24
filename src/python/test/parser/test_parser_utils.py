import json

import pytest

from hmd_meta_types.parser import load_definition


@pytest.fixture()
def definition_json(example_definition):
    return json.dumps(example_definition)


class TestUtils:
    def test_load_definition(self, definition_json):
        klass = load_definition(definition_json)

        example = klass(id="test", name="test", type="example", location="local")

        assert klass.__name__ == "ClusterDefinition"

        assert example["name"] == "test"
        assert example.id == "test"

        example.name = "another_test"
        assert example.name == "another_test"
