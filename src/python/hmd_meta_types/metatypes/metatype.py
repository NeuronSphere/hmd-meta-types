from typing import Dict, Any, Tuple, List
from collections import OrderedDict
from hmd_meta_types.metatypes.extension import Extension

from hmd_meta_types.utils import snake_to_pascal
from ..primitives import Attribute


class MetaType(type):
    __extensions = {".": []}

    def __new__(
        cls,
        name: str,
        bases: Tuple[Any],
        class_dict: Dict[str, Any],
        definition: Dict[str, Any] = None,
        extensions: List[Extension] = list(),
        **kwargs,
    ):
        if definition is None:
            return super().__new__(cls, name, bases, class_dict)

        metatype = definition.get("metatype", None)

        if not metatype:
            return super().__new__(cls, name, bases, class_dict)

        extension_cfgs = definition.pop("extensions", {})

        ns = MetaType.build_initial_namespace(metatype=metatype, definition=definition)
        attrs = definition.get("attributes", [])

        MetaType.add_attributes(ns, attrs)
        ns = MetaType.apply_extensions(ns, extensions=extensions, cfg=extension_cfgs)

        def init(self, *args, **kwargs):
            required = getattr(self, "__required_attributes", [])
            for req in required:
                if req not in kwargs:
                    raise Exception(
                        f"Missing required attribute {req} on {self.__class__.__name__}"
                    )

            for attr in getattr(self, "__attributes", []):
                if attr in kwargs:
                    vars(type(self))[attr].set_value(self, kwargs[attr])

        def get_item(self, key):
            return self.__dict__.get(f"__{key}", None)

        def set_item(self, key, value):
            self.__dict__[f"__{key}"] = value

        ns["__init__"] = init
        ns["__getitem__"] = get_item
        ns["__setitem__"] = set_item

        return super().__new__(cls, snake_to_pascal(name), bases, ns)

    @classmethod
    def build_initial_namespace(
        metacls, metatype: str, definition: Dict[str, Any] = {}
    ) -> Dict:
        ns = dict()
        ns["__typename"] = definition["name"]
        ns["__metatype"] = metatype
        ns["__namespace"] = definition.get("namespace", None)
        ns["__definition"] = definition
        ns["__attributes"] = []
        ns["__required_attributes"] = []

        return ns

    @classmethod
    def add_attributes(metacls, ns: Dict, attrs=list()) -> None:
        for key, attr in attrs.items():
            _type = attr.get("type", "string") if type(attr) == dict else attr
            desc = None
            definition = None
            metadata = None
            if type(attr) == dict:
                desc = attr.get("description", None)
                definition = attr.get("definition", None)
                del attr["type"]
                if "description" in attr:
                    del attr["description"]
                if "definition" in attr:
                    del attr["definition"]
                if attr.get("required", False):
                    ns["__required_attributes"].append(key)
                metadata = attr
            ns[key] = Attribute(
                _type,
                definition=definition,
                required=attr.get("required", False),
                description=desc,
                addtl_metadata=metadata,
            )
            ns["__attributes"].append(key)

    @classmethod
    def apply_extensions(
        metacls, ns: Dict, extensions: List = list(), cfg: Dict[str, Any] = dict()
    ) -> Dict:
        def list_operations(cls):
            return cls._operations

        def get_operation(cls, name: str):
            if name in cls._operations:
                return cls.__dict__.get(name, None)

        for ext in extensions:
            if ext.extends == "." or ext.extends == ns["name"]:
                ext_cfg = cfg.get(ext.extension_config, {})
                ns = ext.apply_extension(ns, config=ext_cfg)
            else:
                ns["_operations"] = []

            ns["list_operations"] = classmethod(list_operations)
            ns["get_operation"] = classmethod(get_operation)

        return ns

    def __iter__(cls):
        cls.i = 0
        return cls

    def __next__(cls):
        attrs = getattr(cls, "__attributes", [])
        attr_len = len(attrs)

        if cls.i >= attr_len:
            raise StopIteration

        result = attrs[cls.i]
        cls.i += 1
        return result
