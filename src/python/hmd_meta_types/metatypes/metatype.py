from typing import Dict, Any, Tuple
from collections import OrderedDict
from ..primitives import Attribute


class MetaType(type):
    def __new__(
        cls,
        name: str,
        bases: Tuple[Any],
        class_dict: Dict[str, Any],
        definition: Dict[str, Any] = None,
        **kwargs,
    ):
        if definition is None:
            return super().__new__(cls, name, bases, class_dict)

        metatype = definition.get("metatype", None)

        if not metatype:
            return super().__new__(cls, name, bases, class_dict)

        if MetaType.__capitalize_name(metatype) not in [
            base.__name__ for base in bases
        ]:
            raise Exception(f"Invalid metatype defined for {name}: {metatype}")

        ns = OrderedDict()
        ns["__metatype"] = metatype
        ns["__namespace"] = definition.get("namespace", None)
        ns["__definition"] = definition
        attrs = definition.get("attributes", [])
        ns["__attributes"] = []
        ns["__required_attributes"] = []

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
                _type, definition=definition, description=desc, addtl_metadata=metadata
            )
            ns["__attributes"].append(key)

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
            return self.__dict__[key]

        def set_item(self, key, value):
            self.__dict__[key] = value

        ns["__init__"] = init
        ns["__getitem__"] = get_item
        ns["__setitem__"] = set_item

        return super().__new__(cls, name, bases, ns)

    @staticmethod
    def __capitalize_name(name: str) -> str:
        names = name.split("_")
        return "".join([n.capitalize() for n in names])
