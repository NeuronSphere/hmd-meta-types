import json

import pytest

from hmd_meta_types.parser import DefinitionDecoder


@pytest.fixture()
def definition_json(example_definition):
    return json.dumps(example_definition)


class TestDecoder:
    def test_decode(self, definition_json):
        klass = json.loads(definition_json, cls=DefinitionDecoder)

        example = klass(id="test", name="test", type="example", location="local")

        assert klass.__name__ == "ClusterDefinition"

        assert example["name"] == "test"
        assert example.id == "test"

        example.name = "another_test"
        assert example.name == "another_test"
