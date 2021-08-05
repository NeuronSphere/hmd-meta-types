from abc import ABC, abstractmethod
import functools
from collections import defaultdict
from typing import Dict, Type, Any, Union
from datetime import datetime, timezone
from dateutil.parser import isoparse
from json import dumps, loads
from base64 import b64encode, b64decode
from copy import deepcopy

type_mapping = {
    "integer": [int],
    "string": [str],
    "float": [float],
    "enum": [str],
    "timestamp": [datetime],
    "epoch": [int],
    "collection": [list],
    "mapping": [dict],
    "blob": [bytes],
}


def get_value(field_def: Dict, value: Any):
    result = value
    if field_def["type"] == "timestamp":
        if result and result.tzinfo and result.tzinfo.utcoffset(result):
            # we have a timzone aware object. make sure its in utc...
            result = result.astimezone(timezone.utc)

    return result


class Entity(ABC):
    def __init__(self, **kwargs):

        entity_definition = self.__class__.entity_definition()
        defined_fields = set(entity_definition["attributes"].keys())
        required_fields = set(
            [
                attr_name[0]
                for attr_name in filter(
                    lambda item: item[1].get("required"),
                    entity_definition["attributes"].items(),
                )
            ]
        )
        fields_present = set(kwargs.keys())
        if "identifier" in fields_present:
            fields_present.remove("identifier")

        # see if all required fields are present...
        required_fields_present = required_fields.intersection(fields_present)
        missing_required_fields = required_fields - required_fields_present
        if missing_required_fields:
            raise Exception(f"Missing required fields: {missing_required_fields}")

        # see if there extra fields present...
        extra_fields = fields_present - defined_fields
        if extra_fields:
            raise Exception(f"Extra fields present: {extra_fields}")

        for field in kwargs:
            setattr(self, field, kwargs[field])

    def _setter(self, field_name, value):
        field_definition = self.entity_definition()["attributes"].get(field_name)
        if field_definition:
            if field_definition.get("required", False):
                if value is None:
                    raise Exception(
                        f"Cannot set required field, {field_name}, to None."
                    )
            if value is not None:
                if field_definition["type"] == "enum":
                    if value not in field_definition["enum_def"]:
                        raise Exception(
                            f"For field, {field_name}, expected one of {field_definition['enum_def']}, was \"{value}\""
                        )
                elif not any(
                    isinstance(value, a_type)
                    for a_type in (type_mapping[field_definition["type"]])
                ):
                    valid_types = [
                        f'"{a_type.__name__}"'
                        for a_type in type_mapping[field_definition["type"]]
                    ]
                    raise TypeError(
                        f"For field, {field_name}, expected a value of one of the types: {', '.join(valid_types)}, was \"{type(value).__name__}\""
                    )
                value = get_value(field_definition, value)

        setattr(self, f"_{field_name}", value)

    def _getter(self, attribute_name):
        if not hasattr(self, f"_{attribute_name}"):
            return None
        else:
            return getattr(self, f"_{attribute_name}")

    @property
    def identifier(self) -> str:
        return self._getter("identifier")

    @identifier.setter
    def identifier(self, value: str):
        self._setter("identifier", value)

    @property
    def instance_type(self):
        return self.__class__

    @staticmethod
    @abstractmethod
    def entity_definition():
        pass

    @staticmethod
    def get_namespace_name(entity_definition) -> str:
        name = entity_definition["name"]
        namespace = entity_definition["namespace"]
        return ((namespace + ".") if namespace else "") + name

    def serialize(self) -> Dict:
        entity_definition = self.__class__.entity_definition()
        result = {}
        if self.identifier:
            result["identifier"] = self.identifier
        for attr, definition in entity_definition.get("attributes", {}).items():
            value = getattr(self, attr)
            if value is not None:
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif definition["type"] in ["collection", "mapping"]:
                    value = b64encode(dumps(value).encode(encoding="utf-8")).decode(
                        "utf-8"
                    )
                elif definition["type"] == "blob":
                    value = b64encode(value).decode("utf-8")
                result[attr] = value

        if hasattr(self, "ref_to"):
            if isinstance(self.ref_to, self.ref_to_type()):
                result["ref_to"] = self.ref_to.identifier
            else:
                result["ref_to"] = self.ref_to

        if hasattr(self, "ref_from"):
            if isinstance(self.ref_from, self.ref_from_type()):
                result["ref_from"] = self.ref_from.identifier
            else:
                result["ref_from"] = self.ref_from

        return result

    @classmethod
    def deserialize(cls, entity_type, data: dict):
        entity_def = entity_type.entity_definition()
        new_data = deepcopy(data)
        for attr, field_def in entity_def.get("attributes", {}).items():
            if attr in new_data:
                result = new_data[attr]
                if result:
                    if field_def["type"] == "timestamp":
                        result = isoparse(result)
                    elif field_def["type"] in ["mapping", "collection"]:
                        result = loads(
                            b64decode(result.encode(encoding="utf-8")).decode("utf-8")
                        )
                    elif field_def["type"] == "blob":
                        result = b64decode(result.encode(encoding="utf-8"))
                new_data[attr] = result

        return entity_type(**new_data)

    def set_equals(self, other):
        entity_def = self.__class__.entity_definition()
        if isinstance(other, self.__class__):
            attributes_to_copy = ["identifier"]
            if hasattr(self, "ref_to"):
                attributes_to_copy += ["ref_from", "ref_to"]
            attributes_to_copy += [
                name for name, _ in entity_def.get("attributes", {}).items()
            ]

            for attr in attributes_to_copy:
                setattr(self, attr, getattr(other, attr))

    def __eq__(self, other):
        entity_def = self.__class__.entity_definition()
        attributes_to_compare = ["identifier"]
        if hasattr(self, "ref_to"):
            attributes_to_compare += ["ref_from", "ref_to"]
        attributes_to_compare += [
            name for name, _ in entity_def.get("attributes", {}).items()
        ]

        return isinstance(other, self.__class__) and all(
            getattr(self, attr) == getattr(other, attr)
            for attr in attributes_to_compare
        )

    def __hash__(self):
        if self.identifier is None:
            raise Exception("Entities must have an identifier to be hashable.")
        return hash(self.identifier)


class Noun(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # relationships for which this is the "to" noun
        self.to_rels = defaultdict(list)  # type: Dict[str, List[Relationship]]
        # relationships for which this is the "from" noun
        self.from_rels = defaultdict(list)  # type: Dict[str, List[Relationship]]


class Relationship(Entity):
    def __init__(self, ref_from: Noun, ref_to: Noun, **kwargs):
        self.ref_from = ref_from
        self.ref_to = ref_to
        super().__init__(**kwargs)

    @staticmethod
    @abstractmethod
    def ref_from_type() -> Type[Noun]:
        pass

    @staticmethod
    @abstractmethod
    def ref_to_type() -> Type[Noun]:
        pass

    @property
    def ref_from(self) -> Union[Noun, str]:
        return self._ref_from

    @ref_from.setter
    def ref_from(self, value: Union[Noun, str]):
        if not isinstance(value, self.__class__.ref_from_type()) and not isinstance(
            value, str
        ):
            raise Exception(
                f'From reference must be of type {self.__class__.ref_from_type().__name__} or str, got "{value}".'
            )
        self._ref_from = value
        if isinstance(value, Noun):
            if self not in value.from_rels[self.__class__.get_namespace_name()]:
                value.from_rels[self.__class__.get_namespace_name()].append(self)

    @property
    def ref_to(self) -> Union[Noun, str]:
        return self._ref_to

    @ref_to.setter
    def ref_to(self, value: Union[Noun, str]):
        if not isinstance(value, self.__class__.ref_to_type()) and not isinstance(
            value, str
        ):
            raise Exception(
                f"To reference must be of type {self.__class__.ref_to_type().__name__} or str."
            )
        self._ref_to = value
        if isinstance(value, Noun):
            if self not in value.to_rels[self.__class__.get_namespace_name()]:
                value.to_rels[self.__class__.get_namespace_name()].append(self)
