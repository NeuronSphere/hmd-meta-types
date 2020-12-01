from typing import Dict, List, Any

from hmd_meta_types.metatypes.metatype import MetaType
from hmd_meta_types.metatypes import Noun
from hmd_meta_types.metatypes.extension import Extension
from hmd_meta_types.primitives import Operation


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


def operation(orig_fn=None, operation_name: str = None):
    def decorator(fn):
        return Operation(operation_name if operation_name else fn.__name__, fn=fn)

    if orig_fn:
        return decorator(orig_fn)

    return decorator
