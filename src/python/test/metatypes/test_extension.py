from hmd_meta_types import extends, operation
from hmd_meta_types.metatypes import Noun


class TestExtensions:
    def test_extends(self):
        @extends
        class ExampleExt:
            def do_thing(self):
                return "thing"

        assert "do_thing" in getattr(ExampleExt, "class_dict")
        assert getattr(ExampleExt, "extends") == "."

        @extends(type_name="Example")
        class AnotherExt:
            def do_the_thing(self):
                return "the thing"

        assert "do_the_thing" in getattr(AnotherExt, "class_dict")
        assert getattr(AnotherExt, "extends") == "Example"

    def test_operation(self):
        @extends
        class OpExt:
            @operation
            def run_op(self):
                return "op"

        assert "run_op" in OpExt.list_operations()

    def test_metatype_registration(self, example_definition):
        @extends
        class OpExt:
            @operation
            def run_op(self):
                return "op"

            @operation(operation_name="diff_op")
            def op_again(self):
                return "diff"

            def no_op(self):
                return "no op"

        klass = type(
            "example", (Noun,), {}, definition=example_definition, extensions=[OpExt]
        )

        assert "run_op" in klass.list_operations()
        assert "run_op" in vars(klass)
        assert "no_op" not in klass.list_operations()
        assert "no_op" in vars(klass)

        example = klass(id="test", name="test", type="example", location="local")
        assert example.run_op() == "op"

        assert example.diff_op() == "diff"

        op = klass.get_operation("run_op")
        assert op is not None
