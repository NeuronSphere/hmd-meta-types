import json
import pytest

from hmd_meta_types.entity import type_check
from hmd_meta_types.noun import Noun
from hmd_meta_types.relationship import Relationship


@pytest.fixture()
def anoun():
    class ANoun(Noun):
        _entity_def = {
            "attributes": {
                "field1": {"type": "string", "required": True},
                "field2": {"type": "integer"},
                "field3": {"type": "enum", "enum_def": ["a", "b"]},
            }
        }

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @property
        def entity_definition(self):
            return self.__class__._entity_def

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

        @property
        def entity_definition(self):
            return self.__class__._entity_def

        @property
        def from_ref_type(self):
            return anoun

        @property
        def to_ref_type(self):
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
