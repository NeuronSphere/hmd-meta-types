import pytest

from hmd_meta_types.noun import Noun
from hmd_meta_types.entity import Entity, type_check


class TestNoun:
    def test_namespace_name(self, anoun):
        assert anoun.get_namespace_name() == "name.space.a_noun"

    def test_okay(self, anoun):
        noun1 = anoun(**{"field1": "hello", "field2": 5, "field3": "b"})
        assert noun1.field1 == "hello"
        assert noun1.field2 == 5
        assert noun1.field3 == "b"

    def test_instance_type(self, anoun):
        noun1 = anoun(**{"field1": "hello", "field2": 5})

        assert noun1.instance_type == anoun

    def test_bad_type(self, anoun):
        with pytest.raises(Exception) as exc:
            noun1 = anoun(**{"field1": 5, "field2": 5})

        assert (
            str(exc.value)
            == 'For field, field1, expected value of type, "str", was "int"'
        )

    def test_missing_required_field(self, anoun):
        with pytest.raises(Exception) as exc:
            noun1 = anoun(**{"field2": 5})

        assert str(exc.value) == "Missing required fields: {'field1'}"

    def test_bad_enum_type(self, anoun):
        with pytest.raises(Exception) as exc:
            noun1 = anoun(**{"field1": "hello", "field2": 5, "field3": "c"})

        assert (
            str(exc.value) == "For field, field3, expected one of ['a', 'b'], was \"c\""
        )
