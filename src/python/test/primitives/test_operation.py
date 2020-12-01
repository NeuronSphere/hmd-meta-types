import pytest

from hmd_meta_types.primitives import Operation


class TestOperation:
    def test_operation_init_defaults(self):
        op = Operation("test_op")

        assert op.name == "test_op"
        assert op.fn is None

        op = Operation("test_op", fn=lambda self: self.name)

        assert op.fn is not None
        assert op.fn(op) == "test_op"

    def test_operation_is_callable(self):
        op = Operation("test_op", fn=lambda self: self.name)

        assert op() == "test_op"

    def test_operation_call_accepts_args(self):
        op = Operation("test_op", fn=lambda self, arg1: arg1)

        assert op("test") == "test"

    def test_operation_call_accepts_kwds(self):
        op = Operation("test_op", fn=lambda self, arg1, test=None: test)

        assert op("nope", test="test") == "test"
