import pytest

from hmd_meta_types.primitives.reference import Reference


class TestReference:
    def test_init(self):
        ref = Reference("test.class")

        assert ref.class_name == "test.class"

    def test_get_set(self):
        class Example:
            ref = Reference("test.class")

        example = Example()
        example.ref = "test"

        assert example.ref == "test"
