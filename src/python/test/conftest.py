import json
import pytest

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
                "timestampfield": {"type": "timestamp"},
                "dictfield": {"type": "mapping"},
                "listfield": {"type": "collection"},
                "blobfield": {"type": "blob"},
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
            return self._getter(attribute_name="field1")

        @field1.setter
        def field1(self, value):
            self._setter(field_name="field1", value=value)

        @property
        def field2(self):
            return self._getter(attribute_name="field2")

        @field2.setter
        def field2(self, value):
            self._setter(field_name="field2", value=value)

        @property
        def field3(self):
            return self._getter(attribute_name="field3")

        @field3.setter
        def field3(self, value):
            self._setter(field_name="field3", value=value)

        @property
        def timestampfield(self):
            return self._getter(attribute_name="timestampfield")

        @timestampfield.setter
        def timestampfield(self, value):
            self._setter(field_name="timestampfield", value=value)

        @property
        def dictfield(self):
            return self._getter(attribute_name="dictfield")

        @dictfield.setter
        def dictfield(self, value):
            self._setter(field_name="dictfield", value=value)

        @property
        def listfield(self):
            return self._getter(attribute_name="listfield")

        @listfield.setter
        def listfield(self, value):
            self._setter(field_name="listfield", value=value)

        @property
        def blobfield(self):
            return self._getter(attribute_name="blobfield")

        @blobfield.setter
        def blobfield(self, value):
            self._setter(field_name="blobfield", value=value)

    return ANoun


@pytest.fixture()
def arel(anoun):
    class ARel(Relationship):
        _entity_def = {
            "name": "a_relationship",
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
            return self._getter("field1")

        @field1.setter
        def field1(self, value):
            self._setter("field1", value)

        @property
        def field2(self):
            return self._getter("field2")

        @field2.setter
        def field2(self, value):
            self._setter("field2", value)

        @property
        def field3(self):
            return self._getter("field3")

        @field3.setter
        def field3(self, value):
            self._setter("field3", value)

    return ARel


@pytest.fixture()
def validation_noun():
    class ValidationNoun(Noun):
        _entity_def = {
            "name": "a_noun",
            "namespace": "name.space",
            "attributes": {
                "date_str": {
                    "type": "string",
                    "required": True,
                    "validation": {"datetime": "%Y-%m-%d"},
                },
                "time_str": {
                    "type": "string",
                    "required": True,
                    "validation": {"datetime": "%H:%M:%S"},
                },
                "regex_str": {
                    "type": "string",
                    "required": True,
                    "validation": {"regex": "^[a-z]{3}-[A-Z]{3}$"},
                },
                "field2": {"type": "integer", "validation": {"max": 100, "min": 10}},
                "field3": {"type": "enum", "enum_def": ["a", "b"]},
                "timestampfield": {"type": "timestamp"},
                "dictfield": {"type": "mapping"},
                "listfield": {"type": "collection"},
                "blobfield": {"type": "blob"},
            },
        }

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @staticmethod
        def entity_definition():
            return ValidationNoun._entity_def

        @staticmethod
        def get_namespace_name():
            return Entity.get_namespace_name(ValidationNoun._entity_def)

        @property
        def date_str(self):
            return self._getter(attribute_name="date_str")

        @date_str.setter
        def date_str(self, value):
            self._setter(field_name="date_str", value=value)

        @property
        def time_str(self):
            return self._getter(attribute_name="time_str")

        @time_str.setter
        def time_str(self, value):
            self._setter(field_name="time_str", value=value)

        @property
        def regex_str(self):
            return self._getter(attribute_name="regex_str")

        @regex_str.setter
        def regex_str(self, value):
            self._setter(field_name="regex_str", value=value)

        @property
        def field2(self):
            return self._getter(attribute_name="field2")

        @field2.setter
        def field2(self, value):
            self._setter(field_name="field2", value=value)

        @property
        def field3(self):
            return self._getter(attribute_name="field3")

        @field3.setter
        def field3(self, value):
            self._setter(field_name="field3", value=value)

        @property
        def timestampfield(self):
            return self._getter(attribute_name="timestampfield")

        @timestampfield.setter
        def timestampfield(self, value):
            self._setter(field_name="timestampfield", value=value)

        @property
        def dictfield(self):
            return self._getter(attribute_name="dictfield")

        @dictfield.setter
        def dictfield(self, value):
            self._setter(field_name="dictfield", value=value)

        @property
        def listfield(self):
            return self._getter(attribute_name="listfield")

        @listfield.setter
        def listfield(self, value):
            self._setter(field_name="listfield", value=value)

        @property
        def blobfield(self):
            return self._getter(attribute_name="blobfield")

        @blobfield.setter
        def blobfield(self, value):
            self._setter(field_name="blobfield", value=value)

    return ValidationNoun


@pytest.fixture()
def validation_rel():
    class ValidationRel(Relationship):
        _entity_def = {
            "name": "a_noun",
            "namespace": "name.space",
            "attributes": {
                "date_str": {
                    "type": "string",
                    "required": True,
                    "validation": {"datetime": "%Y-%m-%d"},
                },
                "time_str": {
                    "type": "string",
                    "required": True,
                    "validation": {"datetime": "%H:%M:%S"},
                },
                "regex_str": {
                    "type": "string",
                    "required": True,
                    "validation": {"regex": "^[a-z]{3}-[A-Z]{3}$"},
                },
                "field2": {"type": "integer", "validation": {"max": 100, "min": 10}},
                "field3": {"type": "enum", "enum_def": ["a", "b"]},
                "timestampfield": {"type": "timestamp"},
                "dictfield": {"type": "mapping"},
                "listfield": {"type": "collection"},
                "blobfield": {"type": "blob"},
            },
        }

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @staticmethod
        def entity_definition():
            return ValidationRel._entity_def

        @staticmethod
        def get_namespace_name():
            return Entity.get_namespace_name(ValidationRel._entity_def)

        @staticmethod
        def ref_from_type():
            return anoun

        @staticmethod
        def ref_to_type():
            return anoun

        @property
        def date_str(self):
            return self._getter(attribute_name="date_str")

        @date_str.setter
        def date_str(self, value):
            self._setter(field_name="date_str", value=value)

        @property
        def time_str(self):
            return self._getter(attribute_name="time_str")

        @time_str.setter
        def time_str(self, value):
            self._setter(field_name="time_str", value=value)

        @property
        def regex_str(self):
            return self._getter(attribute_name="regex_str")

        @regex_str.setter
        def regex_str(self, value):
            self._setter(field_name="regex_str", value=value)

        @property
        def field2(self):
            return self._getter(attribute_name="field2")

        @field2.setter
        def field2(self, value):
            self._setter(field_name="field2", value=value)

        @property
        def field3(self):
            return self._getter(attribute_name="field3")

        @field3.setter
        def field3(self, value):
            self._setter(field_name="field3", value=value)

        @property
        def timestampfield(self):
            return self._getter(attribute_name="timestampfield")

        @timestampfield.setter
        def timestampfield(self, value):
            self._setter(field_name="timestampfield", value=value)

        @property
        def dictfield(self):
            return self._getter(attribute_name="dictfield")

        @dictfield.setter
        def dictfield(self, value):
            self._setter(field_name="dictfield", value=value)

        @property
        def listfield(self):
            return self._getter(attribute_name="listfield")

        @listfield.setter
        def listfield(self, value):
            self._setter(field_name="listfield", value=value)

        @property
        def blobfield(self):
            return self._getter(attribute_name="blobfield")

        @blobfield.setter
        def blobfield(self, value):
            self._setter(field_name="blobfield", value=value)

    return ValidationRel
