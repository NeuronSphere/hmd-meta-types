from functools import wraps
from typing import Any, Dict

from hmd_meta_types.primitives.operation import Operation


class Extension:
    def __init__(self, config_ext: str, type_name: str = "."):
        self.config_ext = config_ext
        self.extends = type_name

    def __call__(self, cls):
        cls_operations = []
        cdict = {}
        config_fn = lambda cfg, cdict: cdict

        for key, item in vars(cls).items():
            if isinstance(item, Operation):
                op_name = item.name
                cdict[op_name] = item
                cls_operations.append(op_name)
            elif getattr(item, "is_config_fn", False):
                config_fn = item
            else:
                cdict[key] = item

        def merge(cls, odict=dict(), config: Dict[str, Any] = dict()):
            operations = odict.get("_operations", [])
            cls_dict = config_fn(config, cdict)
            return {**odict, **cls_dict, "_operations": [*operations, *cls._operations]}

        cdict["_operations"] = cls_operations
        cdict["apply_extension"] = classmethod(merge)
        cdict["extends"] = self.extends
        cdict["extension_config"] = self.config_ext

        return type(cls.__name__, cls.__bases__, cdict)


def configuration(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    wrapper.is_config_fn = True
    return wrapper
