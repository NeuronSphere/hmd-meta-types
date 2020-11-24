import json
from json.decoder import JSONDecodeError

import pytest

from hmd_meta_types.parser import DefinitionDecoder


@pytest.fixture()
def definition_json(example_definition):
    return json.dumps(example_definition)


class TestDecoder:
    def test_invalid_metatype(self):
        with pytest.raises(Exception) as e:
            json_str = """
            {
                "name": "test",
                "metatype": "foo"
            }
            """
            json.loads(json_str, cls=DefinitionDecoder)
        assert "Invalid metatype foo in definition." in str(e.value)

    def test_decode(self, definition_json):
        klass = json.loads(definition_json, cls=DefinitionDecoder)

        example = klass(id="test", name="test", type="example", location="local")

        assert klass.__name__ == "ClusterDefinition"

        assert example["name"] == "test"
        assert example.id == "test"

        example.name = "another_test"
        assert example.name == "another_test"
