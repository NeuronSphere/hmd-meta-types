from hmd_meta_types.primitives.attribute import Attribute
from .metatype import MetaType


class Noun(metaclass=MetaType):
    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        attrs = getattr(self, "__attributes", [])
        attr_len = len(attrs)

        if self.i >= attr_len:
            raise StopIteration

        result = attrs[self.i]
        self.i += 1
        return result

    def get_attribute(self, attr_name: str) -> Attribute:
        return vars(type(self))[attr_name]
