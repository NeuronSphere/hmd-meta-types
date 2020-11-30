from typing import Dict, List, Any
from functools import wraps

from hmd_meta_types.metatypes.metatype import MetaType
from hmd_meta_types.metatypes import Noun
from hmd_meta_types.metatypes.extension import Extension


def build_type_class(
    definition: Dict[str, Any],
    extensions: List[Extension] = list(),
    package_namespace: Dict[str, MetaType] = dict(),
) -> MetaType:
    metatypes = {"noun": Noun}
    metatype = metatypes.get(definition["metatype"], None)
    if metatype is None:
        raise Exception(f"Invalid metatype: {definition['metatype']}")

    bases = definition.get("super_types", [])
    super_types = []

    for base in bases:
        base_class = package_namespace.get(base, None)
        if base_class is None or not isinstance(base_class, MetaType):
            raise Exception(f"Invalid base class in namespace: {base}")
        super_types.append(base_class)

    return MetaType(
        definition["name"],
        tuple(super_types) if len(super_types) > 0 else (metatype,),
        {},
        definition=definition,
        extensions=extensions,
    )


def extends(original_cls=None, type_name: str = None):
    def decorator(cls):
        cls_operations = []
        cls_dict = {}

        for key, item in vars(cls).items():
            if hasattr(item, "operation_name"):
                op_name = getattr(item, "operation_name")
                cls_dict[op_name] = item
                cls_operations.append(op_name)
            else:
                cls_dict[key] = item

        class NewExtension(Extension):
            class_dict = cls_dict
            extends = type_name if type_name else "."
            operations = cls_operations

        NewExtension.__name__ = cls.__name__

        return NewExtension

    if original_cls:
        return decorator(original_cls)

    return decorator


def operation(orig_fn=None, operation_name: str = None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        wrapper.operation_name = operation_name if operation_name else fn.__name__
        return wrapper

    if orig_fn:
        return decorator(orig_fn)

    return decorator
