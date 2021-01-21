import pytest

from hmd_meta_types.relationship import Relationship
from hmd_meta_types.entity import Entity, type_check


class TestRel:
    def test_okay(self, arel, anoun):

        noun1 = anoun(**{"field1": "noun1", "field2": 5, "field3": "b"})
        noun2 = anoun(**{"field1": "noun2", "field2": 10, "field3": "a"})
        rel1 = arel(
            ref_from=noun1,
            ref_to=noun2,
            **{"field1": "hello", "field2": 5, "field3": "b"}
        )
        assert rel1.field1 == "hello"
        assert noun1.field2 == 5
        assert noun1.field3 == "b"

    def test_bad_type(self, arel, anoun):
        noun1 = anoun(**{"field1": "noun1", "field2": 5, "field3": "b"})
        noun2 = anoun(**{"field1": "noun2", "field2": 10, "field3": "a"})

        with pytest.raises(Exception) as exc:
            rel1 = arel(
                ref_from=noun1,
                ref_to=noun2,
                **{"field1": 5, "field2": 5, "field3": "b"}
            )

        assert (
            str(exc.value)
            == 'For field, field1, expected value of type, "str", was "int"'
        )

    def test_required_args(self, arel, anoun):
        noun1 = anoun(**{"field1": "noun1", "field2": 5, "field3": "b"})

        with pytest.raises(Exception) as exc:
            rel1 = arel(
                ref_from=noun1, **{"field1": "hello", "field2": 5, "field3": "b"}
            )

        assert (
            str(exc.value)
            == "__init__() missing 1 required positional argument: 'ref_to'"
        )

    def test_set_invalid_ref(self, arel, anoun):

        noun1 = anoun(**{"field1": "noun1", "field2": 5, "field3": "b"})
        noun2 = anoun(**{"field1": "noun2", "field2": 10, "field3": "a"})
        rel1 = arel(
            ref_from=noun1,
            ref_to=noun2,
            **{"field1": "hello", "field2": 5, "field3": "b"}
        )
        assert rel1.field1 == "hello"
        assert noun1.field2 == 5
        assert noun1.field3 == "b"

        with pytest.raises(Exception) as exc:
            rel1.ref_to = "hello"

        assert str(exc.value) == "To reference must be of type ANoun."
