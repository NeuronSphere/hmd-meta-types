from io import FileIO
import json
from unittest.mock import patch, MagicMock

from hmd_meta_types.utils import load_definition, load_definition_file, snake_to_pascal


class TestBaseUtils:
    def test_snake_to_pascal(self):
        class_name = "example_class"
        assert snake_to_pascal(class_name) == "ExampleClass"

    def test_load_definition(self, cluster_definition_json, cluster_definition):
        loaded_def = load_definition(cluster_definition_json)
        assert loaded_def == cluster_definition

    def test_load_definition_file(self, cluster_definition_json, cluster_definition):
        with patch(f"{__name__}.open") as mock_open:
            mock_open.return_value = MagicMock(spec=FileIO)
            mock_open.return_value.__enter__.return_value.read.return_value = (
                cluster_definition_json
            )
            with open("test.json", "r") as fp:
                loaded_def = load_definition_file(fp)
                assert loaded_def == cluster_definition
