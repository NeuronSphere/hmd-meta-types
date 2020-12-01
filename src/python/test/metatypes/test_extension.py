from hmd_meta_types import operation
from hmd_meta_types.metatypes import Noun, Extension
from hmd_meta_types.metatypes.extension import configuration
from hmd_meta_types.metatypes.metatype import MetaType


class TestExtensions:
    def test_extends(self):
        @Extension("test")
        class ExampleExt:
            def do_thing(self):
                return "thing"

        assert "do_thing" in ExampleExt.__dict__
        assert getattr(ExampleExt, "extends") == "."

        @Extension("test", type_name="Example")
        class AnotherExt:
            def do_the_thing(self):
                return "the thing"

        assert "do_the_thing" in AnotherExt.__dict__
        assert getattr(AnotherExt, "extends") == "Example"

    def test_operation(self):
        @Extension("test")
        class OpExt:
            @operation
            def run_op(self):
                return "op"

        assert "run_op" in getattr(OpExt, "_operations")

    def test_metatype_registration(self, example_definition):
        @Extension("test")
        class OpExt:
            @operation
            def run_op():
                return "op"

            @operation(operation_name="diff_op")
            def op_again():
                return "diff"

            def no_op():
                return "no op"

        klass = MetaType(
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

    def test_specific_type_extension(self, example_definition):
        @Extension("test", type_name="test")
        class OpExt:
            @operation
            def run_op():
                return "op"

            @operation(operation_name="diff_op")
            def op_again():
                return "diff"

            def no_op():
                return "no op"

        klass = MetaType(
            "example", (Noun,), {}, definition=example_definition, extensions=[OpExt]
        )

        assert "run_op" not in klass.list_operations()
        assert "run_op" not in vars(klass)
        assert "no_op" not in klass.list_operations()
        assert "no_op" not in vars(klass)

    def test_extension_configuration(self, example_definition):
        @Extension("test")
        class OpExt:
            @configuration
            def configure(cfg, cdict):
                for key, val in cfg.items():
                    if not val and key in cdict:
                        del cdict[key]

                return cdict

            @operation
            def run_op():
                return "op"

            @operation(operation_name="diff_op")
            def op_again():
                return "diff"

            def no_op():
                return "no op"

        example_definition["extensions"] = {"test": {"diff_op": False}}
        klass = MetaType(
            "example", (Noun,), {}, definition=example_definition, extensions=[OpExt]
        )

        example = klass(id="test", name="test", type="example", location="local")
        assert example.run_op() == "op"

        op = klass.get_operation("diff_op")
        assert op is None
