from abc import ABC, abstractmethod
import functools
from typing import Type

type_mapping = {"integer": int, "string": str, "float": float, "enum": str}


def type_check(field_name: str, field_definition: dict):
    def type_check_decorator(setter):
        @functools.wraps(setter)
        def type_check_wrapper(*args, **kwargs):
            if len(args) != 2:
                raise Exception(
                    f"Unexpected number of arguments in setter: {len(args)}"
                )
            if field_definition["type"] == "enum":
                if args[1] not in field_definition["enum_def"]:
                    raise Exception(
                        f"For field, {field_name}, expected one of {field_definition['enum_def']}, was \"{args[1]}\""
                    )
            elif not isinstance(args[1], type_mapping[field_definition["type"]]):
                raise TypeError(
                    f"For field, {field_name}, expected value of type, \"{type_mapping[field_definition['type']].__name__}\", was \"{type(args[1]).__name__}\""
                )
            setter(*args, **kwargs)

        return type_check_wrapper

    return type_check_decorator


class Entity(ABC):
    def __init__(self, **kwargs):

        entity_definition = self.entity_definition
        defined_fields = set(entity_definition["attributes"].keys())
        required_fields = set(
            [
                attr_name[0]
                for attr_name in filter(
                    lambda item: item[1].get("required") == True,
                    entity_definition["attributes"].items(),
                )
            ]
        )
        fields_present = set(kwargs.keys())

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

    @property
    def instance_type(self):
        return self.__class__

    @property
    @abstractmethod
    def entity_definition(self):
        pass
