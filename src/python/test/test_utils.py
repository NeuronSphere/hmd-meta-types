from io import FileIO
import json
from unittest.mock import patch, MagicMock

from hmd_meta_types.utils import load_definition, load_definition_file, snake_to_pascal


class TestBaseUtils:
    def test_snake_to_pascal(self):
        class_name = "example_class"
        assert snake_to_pascal(class_name) == "ExampleClass"
