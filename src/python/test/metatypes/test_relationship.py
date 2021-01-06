import pytest

from hmd_meta_types.metatypes.metatype import MetaType
from hmd_meta_types.primitives.attribute import Attribute
from hmd_meta_types.hmd_meta_types import build_type_class


@pytest.fixture()
def parent(cluster_definition):
    definition = cluster_definition
    return build_type_class(definition)


@pytest.fixture()
def parent_instance(parent):
    return parent(id=1, name="test", type="example", location="a")


@pytest.fixture()
def child(sub_definition):
    definition = sub_definition
    return build_type_class(definition)


@pytest.fixture()
def child_instance(child):
    return child(id=1, name="test", type="example", location="a")


@pytest.fixture()
def relationship(cluster_definition_rel):
    definition = cluster_definition_rel
    return build_type_class(definition)


@pytest.fixture()
def relationship_instance(relationship, parent_instance, child_instance):
    parent_instance.identifier = "parent"
    child_instance.identifier = "child"
    return relationship(
        ref_from=parent_instance,
        ref_to=child_instance,
        id=1,
        name="rel1",
        type="rel_type",
        location="a",
    )


class TestRelationship:
    def test_init(self, relationship_instance):
        assert relationship_instance.name == "rel1"
        assert relationship_instance.id == 1

        relationship_instance.name = "another_test"
        assert relationship_instance.name == "another_test"

        assert relationship_instance.serialize() == {
            "name": "another_test",
            "identifier": None,
            "id": 1,
            "type": "rel_type",
            "location": "a",
            "ref_from": {
                "class_name": "meta.physical.cluster_definition",
                "identifier": "parent",
            },
            "ref_to": {
                "class_name": "meta.physical.sub_definition",
                "identifier": "child",
            },
        }
