import pytest

from hmd_meta_types.metatypes.noun import Noun
from hmd_meta_types.primitives.attribute import Attribute


@pytest.fixture()
def example(example_definition):
    definition = example_definition

    Example = type("cluster_definition", (Noun,), {}, definition=definition)

    return Example(id="test", name="test", type="example", location="local")


class TestNoun:
    def test_init(self, example):
        assert example["name"] == "test"
        assert example.id == "test"

        example.name = "another_test"
        assert example.name == "another_test"

    def test_iter(self, example):
        ex_iter = iter(example)
        assert next(ex_iter) == "id"
        assert next(ex_iter) == "name"
