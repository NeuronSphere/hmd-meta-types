class Extension:
    class_dict = dict()
    extends = "."
    operations = list()

    @classmethod
    def merge(cls, odict=dict()):
        operations = odict.get("__operations", [])
        cls_dict = {
            k: v
            for k, v in cls.class_dict.items()
            if not k.startswith("__") and not k.endswith("__")
        }
        return {
            **odict,
            **cls_dict,
            "__operations": [*operations, *cls.operations],
            "list_operations": cls.list_operations,
            "get_operation": cls.get_operation,
        }

    @classmethod
    def list_operations(cls):
        return cls.operations

    @classmethod
    def get_operation(cls, name: str):
        if name in cls.operations:
            return cls.class_dict[name]
