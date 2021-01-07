from hmd_meta_types.primitives.attribute import Attribute
from .metatype import MetaType


class Relationship(metaclass=MetaType):
    @classmethod
    def get_attribute(cls, attr_name: str) -> Attribute:
        return vars(cls)[attr_name]

    @classmethod
    def get_definition(cls):
        return getattr(cls, "__definition")

    def get_ref_id(self, reference):
        if isinstance(reference, int):
            return reference
        elif hasattr(reference, "identifier"):
            return getattr(reference, "identifier")
        else:
            return None

    def serialize(self):
        instance_dict = {"identifier": self.identifier}  # pylint: disable=no-member
        instance_dict["ref_to"] = self.get_ref_id(
            self["ref_to"]
        )  # pylint: disable=unsubscriptable-object
        instance_dict["ref_from"] = self.get_ref_id(
            self["ref_from"]
        )  # pylint: disable=unsubscriptable-object

        for attr in self.__class__:
            if attr not in ["ref_from", "ref_to"]:
                instance_dict[attr] = self[
                    attr
                ]  # pylint: disable=unsubscriptable-object

        return instance_dict
