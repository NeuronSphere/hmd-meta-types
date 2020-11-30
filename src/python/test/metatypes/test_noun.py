import pytest

from hmd_meta_types.metatypes.noun import Noun
from hmd_meta_types.metatypes.metatype import MetaType
from hmd_meta_types.primitives.attribute import Attribute


@pytest.fixture()
def example_class(example_definition):
    definition = example_definition

    Example = MetaType("cluster_definition", (Noun,), {}, definition=definition)
    return Example


@pytest.fixture()
def example(example_class):

    return example_class(id="test", name="test", type="example", location="local")


class TestNoun:
    def test_init(self, example):
        assert example["name"] == "test"
        assert example.id == "test"

        example.name = "another_test"
        assert example.name == "another_test"

    def test_iter(self, example_class):
        ex_iter = iter(example_class)

        assert next(ex_iter) == "id"
        assert next(ex_iter) == "name"
        assert next(ex_iter) == "type"
        assert next(ex_iter) == "location"

        with pytest.raises(StopIteration):
            for i in ex_iter:
                pass
            next(ex_iter)

    def test_get_attribute(self, example_class):
        attr = example_class.get_attribute("name")

        assert isinstance(attr, Attribute)
        assert attr.metadata() == {
            "description": "The name of the cluster",
            "required": True,
        }
        assert attr.get_type() == "string"

    def test_get_definition(self, example_class, example_definition):
        assert example_class.get_definition() == example_definition
