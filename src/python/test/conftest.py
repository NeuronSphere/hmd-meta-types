import json
import pytest

from hmd_meta_types.entity import type_check
from hmd_meta_types import Noun, Relationship, Entity


@pytest.fixture()
def anoun():
    class ANoun(Noun):
        _entity_def = {
            "name": "a_noun",
            "namespace": "name.space",
            "attributes": {
                "field1": {"type": "string", "required": True},
                "field2": {"type": "integer"},
                "field3": {"type": "enum", "enum_def": ["a", "b"]},
            },
        }

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @staticmethod
        def entity_definition():
            return ANoun._entity_def

        @staticmethod
        def get_namespace_name():
            return Entity.get_namespace_name(ANoun._entity_def)

        @property
        def field1(self):
            return self._field1

        @field1.setter
        @type_check("field1", _entity_def["attributes"]["field1"])
        def field1(self, value):
            self._field1 = value

        @property
        def field2(self):
            return self._field2

        @field2.setter
        @type_check("field2", _entity_def["attributes"]["field2"])
        def field2(self, value):
            self._field2 = value

        @property
        def field3(self):
            return self._field3

        @field3.setter
        @type_check("field3", _entity_def["attributes"]["field3"])
        def field3(self, value):
            self._field3 = value

    return ANoun


@pytest.fixture()
def arel(anoun):
    class ARel(Relationship):
        _entity_def = {
            "attributes": {
                "field1": {"type": "string", "required": True},
                "field2": {"type": "integer"},
                "field3": {"type": "enum", "enum_def": ["a", "b"]},
            }
        }

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @staticmethod
        def entity_definition():
            return ARel._entity_def

        @staticmethod
        def get_namespace_name():
            return Entity.get_namespace_name(ARel._entity_def)

        @staticmethod
        def ref_from_type():
            return anoun

        @staticmethod
        def ref_to_type():
            return anoun

        @property
        def field1(self):
            return self._field1

        @field1.setter
        @type_check("field1", _entity_def["attributes"]["field1"])
        def field1(self, value):
            self._field1 = value

        @property
        def field2(self):
            return self._field2

        @field2.setter
        @type_check("field2", _entity_def["attributes"]["field2"])
        def field2(self, value):
            self._field2 = value

        @property
        def field3(self):
            return self._field3

        @field3.setter
        @type_check("field3", _entity_def["attributes"]["field3"])
        def field3(self, value):
            self._field3 = value

    return ARel
