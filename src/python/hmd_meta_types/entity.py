from abc import ABC, abstractmethod
import functools
from collections import defaultdict


type_mapping = {"integer": int, "string": str, "float": float, "enum": str}


def type_check(field_name: str, field_definition: dict):
    def type_check_decorator(setter):
        @functools.wraps(setter)
        def type_check_wrapper(*args, **kwargs):
            if len(args) != 2:
                raise Exception(
                    f"Unexpected number of arguments in setter: {len(args)}"
                )
            if field_definition.get("required", False):
                if args[1] is None:
                    raise Exception(f"Cannot set required fied, {field_name}, to None.")
            if args[1] is not None:
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

    @property
    def identifier(self):
        if hasattr(self, "_identifier"):
            return self._identifier
        else:
            return None

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @property
    def instance_type(self):
        return self.__class__

    @staticmethod
    @abstractmethod
    def entity_definition():
        pass

    @staticmethod
    def get_namespace_name(entity_definition):
        name = entity_definition["name"]
        namespace = entity_definition["namespace"]
        return ((namespace + ".") if namespace else "") + name

    def serialize(self):
        entity_definition = self.__class__.entity_definition()
        result = {"identifier": self.identifier}
        for attr, val in entity_definition.get("attributes", {}).items():
            result[attr] = getattr(self, attr)

        if hasattr(self, "ref_to"):
            result["ref_to"] = self.ref_to.serialize()

        if hasattr(self, "ref_from"):
            result["ref_from"] = self.ref_from.serialize()

        return result

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
    def ref_from_type():
        pass

    @staticmethod
    @abstractmethod
    def ref_to_type():
        pass

    @property
    def ref_from(self):
        return self._ref_from

    @ref_from.setter
    def ref_from(self, value):
        if not isinstance(value, self.__class__.ref_from_type()):
            raise Exception(
                f"From reference must be of type {self.__class__.ref_from_type().__name__}."
            )
        self._ref_from = value

    @property
    def ref_to(self):
        return self._ref_to

    @ref_to.setter
    def ref_to(self, value):
        if not isinstance(value, self.__class__.ref_to_type()):
            raise Exception(
                f"To reference must be of type {self.__class__.ref_to_type().__name__}."
            )
        self._ref_to = value
