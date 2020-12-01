from hmd_meta_types.primitives.attribute import Attribute
from .metatype import MetaType


class Noun(metaclass=MetaType):
    @classmethod
    def get_attribute(cls, attr_name: str) -> Attribute:
        return vars(cls)[attr_name]

    @classmethod
    def get_definition(cls):
        return getattr(cls, "__definition")

    def serialize(self):
        instance_dict = {}
        for attr in self.__class__:
            instance_dict[attr] = self[attr]

        return instance_dict
