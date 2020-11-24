class Extension:
    class_dict = dict()
    extends = "."
    operations = list()

    @classmethod
    def merge(cls, odict=dict()):
        operations = odict.get("__operations", [])
        return {
            **odict,
            **cls.class_dict,
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
