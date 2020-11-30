from hmd_meta_types.primitives.attribute import Attribute
from .metatype import MetaType


class Noun(metaclass=MetaType):
    @classmethod
    def get_attribute(cls, attr_name: str) -> Attribute:
        return vars(cls)[attr_name]
