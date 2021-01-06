import pytest
from copy import deepcopy

from hmd_meta_types.hmd_meta_types import build_type_class
from hmd_meta_types.metatypes.metatype import MetaType


class TestTypeFactory:
    def test_build_class(self, cluster_definition):
        klass = build_type_class(cluster_definition)

        assert isinstance(klass, MetaType)

    def test_invalid_metatype(self):
        with pytest.raises(Exception) as e:
            build_type_class({"metatype": "foobar"})

        assert "Invalid metatype: foobar" in str(e.value)

    def test_build_class_multiple_bases(self, cluster_definition):
        base_example = deepcopy(cluster_definition)
        base_example["name"] = "base_example"
        base_klass = build_type_class(base_example)

        cluster_definition["name"] = "subtype"
        cluster_definition["super_types"] = ["base_example"]
        klass = build_type_class(
            cluster_definition, package_namespace={"base_example": base_klass}
        )
        assert isinstance(klass, MetaType)
        assert issubclass(klass, base_klass)

    def test_build_class_invalid_bases(self, cluster_definition):
        cluster_definition["name"] = "subtype"
        cluster_definition["super_types"] = ["base_example"]
        with pytest.raises(Exception) as e:
            build_type_class(cluster_definition, package_namespace={"foobar": None})
        assert "Invalid base class in namespace: base_example" in str(e.value)
