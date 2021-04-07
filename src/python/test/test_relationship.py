import re

import pytest
from hmd_meta_types import Entity


class TestRel:
    def test_okay(self, arel, anoun):

        noun1 = anoun(**{"field1": "noun1", "field2": 5, "field3": "b"})
        noun2 = anoun(**{"field1": "noun2", "field2": 10, "field3": "a"})
        rel1 = arel(
            **{
                "ref_from": noun1,
                "ref_to": noun2,
                "field1": "hello",
                "field2": 5,
                "field3": "b",
            }
        )
        assert rel1.field1 == "hello"
        assert rel1.field2 == 5
        assert rel1.field3 == "b"

        assert rel1.serialize() == {
            "field1": "hello",
            "field2": 5,
            "field3": "b",
            "ref_from": {"field1": "noun1", "field2": 5, "field3": "b"},
            "ref_to": {"field1": "noun2", "field2": 10, "field3": "a"},
        }

        assert rel1 == Entity.deserialize(arel, rel1.serialize())

    def test_bad_type(self, arel, anoun):
        noun1 = anoun(**{"field1": "noun1", "field2": 5, "field3": "b"})
        noun2 = anoun(**{"field1": "noun2", "field2": 10, "field3": "a"})

        with pytest.raises(
            Exception,
            match='For field, field1, expected a value of one of the types: "str", was "int"',
        ) as exc:
            rel1 = arel(
                ref_from=noun1,
                ref_to=noun2,
                **{"field1": 5, "field2": 5, "field3": "b"}
            )

    def test_required_args(self, arel, anoun):
        noun1 = anoun(**{"field1": "noun1", "field2": 5, "field3": "b"})

        with pytest.raises(
            Exception,
            match=re.escape(
                "__init__() missing 1 required positional argument: 'ref_to'"
            ),
        ) as exc:
            rel1 = arel(
                ref_from=noun1, **{"field1": "hello", "field2": 5, "field3": "b"}
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

        with pytest.raises(
            Exception, match="To reference must be of type ANoun."
        ) as exc:
            rel1.ref_to = "hello"
