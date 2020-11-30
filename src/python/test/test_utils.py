from io import FileIO
import json

from hmd_meta_types.utils import load_definition, load_definition_file, snake_to_pascal


class TestBaseUtils:
    def test_snake_to_pascal(self):
        class_name = "example_class"
        assert snake_to_pascal(class_name) == "ExampleClass"

    def test_load_definition(self, definition_json, example_definition):
        loaded_def = load_definition(definition_json)
        assert loaded_def == example_definition

    def test_load_definition_file(self, mocker, definition_json, example_definition):
        mock_open = mocker.patch(f"{__name__}.open")
        mock_open.return_value = mocker.MagicMock(spec=FileIO)
        mock_open.return_value.__enter__.return_value.read.return_value = (
            definition_json
        )
        with open("test.json", "r") as fp:
            loaded_def = load_definition_file(fp)
            assert loaded_def == example_definition
