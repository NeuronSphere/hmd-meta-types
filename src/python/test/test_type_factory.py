import pytest
from copy import deepcopy

from hmd_meta_types.hmd_meta_types import build_type_class
from hmd_meta_types.metatypes.metatype import MetaType


class TestTypeFactory:
    def test_build_class(self, example_definition):
        klass = build_type_class(example_definition)

        assert isinstance(klass, MetaType)

    def test_invalid_metatype(self):
        with pytest.raises(Exception) as e:
            build_type_class({"metatype": "foobar"})

        assert "Invalid metatype: foobar" in str(e.value)

    def test_build_class_multiple_bases(self, example_definition):
        base_example = deepcopy(example_definition)
        base_example["name"] = "base_example"
        base_klass = build_type_class(base_example)

        example_definition["name"] = "subtype"
        example_definition["super_types"] = ["base_example"]
        klass = build_type_class(
            example_definition, package_namespace={"base_example": base_klass}
        )
        assert isinstance(klass, MetaType)
        assert issubclass(klass, base_klass)

    def test_build_class_invalid_bases(self, example_definition):
        example_definition["name"] = "subtype"
        example_definition["super_types"] = ["base_example"]
        with pytest.raises(Exception) as e:
            build_type_class(example_definition, package_namespace={"foobar": None})
        assert "Invalid base class in namespace: base_example" in str(e.value)
