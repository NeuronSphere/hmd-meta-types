from typing import Dict, Any, List, Union


class Attribute:
    type_map = {
        "string": str,
        "integer": int,
        "float": float,
        "object": dict,
        "array": list,
        "enum": str,
    }

    def __init__(
        self,
        _type: str,
        description: str = "",
        required: bool = False,
        definition: Union[List[str], Dict[str, Any]] = None,
        addtl_metadata: Dict[str, Any] = {},
    ) -> None:
        self.__type = _type
        self.__metadata = {"description": description, **addtl_metadata}
        self.__definition = definition
        self.required = required

        if _type in ["object", "array", "enum"] and definition is None:
            raise Exception("Missing attribute definition")

    def get_type(self):
        return self.__type

    def metadata(self):
        return self.__metadata

    def definition(self):
        return self.__definition

    def __get__(self, obj, owner=None):
        value = getattr(obj, self.private_name, None)
        return value

    def __set__(self, obj, value):
        if value is not None:
            self.__validate(self.__type, value, self.__definition)
        elif self.required:
            raise Exception(f"{self.public_name} is required")
        setattr(obj, self.private_name, value)

    def set_value(self, obj, value):
        self.__set__(obj, value)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"__{name}"

    def __validate(self, _type: str, value: Any, definition: Dict[str, Any]) -> None:
        _pytype = self.type_map.get(_type, str)

        if value is not None and type(value) != _pytype:
            raise Exception(f"Invalid value ({value}) being set to {self.public_name}")

        if _type == "enum" and value not in definition:
            raise Exception(f"Invalid enum value: {value}")

        if _type == "object":
            for key, attr in definition.items():
                if type(attr) == dict:
                    required = attr.get("required", False)
                    if required and key not in value:
                        raise Exception(
                            f"Missing key {key} in attribute {self.public_name}"
                        )
                    self.__validate(
                        attr.get("type", "string"),
                        value.get(key, None),
                        attr.get("definition", {}),
                    )
        elif _type == "array":
            items = definition.get("items", {})
            for item in value:
                self.__validate(
                    items.get("type", "string"), item, items.get("definition", {})
                )
