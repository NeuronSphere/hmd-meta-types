from typing import List
from hmd_meta_types.primitives.attribute import Attribute
from .relationship import Relationship
from .metatype import MetaType


class Noun(metaclass=MetaType):
    __relationships = {"from": {}, "to": {}}

    @classmethod
    def get_attribute(cls, attr_name: str) -> Attribute:
        return vars(cls)[attr_name]

    @classmethod
    def get_definition(cls):
        return getattr(cls, "__definition")

    def serialize(self):
        instance_dict = {"identifier": self.identifier}  # pylint: disable=no-member
        for attr in self.__class__:
            instance_dict[attr] = self[attr]  # pylint: disable=unsubscriptable-object

        return instance_dict

    def get_relationships_from(self, relationship_type: str) -> List[Relationship]:
        return self.__relationships["from"][relationship_type]

    def get_relationships_from_to(
        self, relationship_type: str, to_entity
    ) -> List[Relationship]:
        result = []
        for rel in self.__relationships["from"][relationship_type]:
            if rel.ref_to.identifier == to_entity.identifier:
                result.append(rel)

        return result

    def get_relationships_to(self, relationship_type: str) -> List[Relationship]:
        return self.__relationships["to"][relationship_type]

    def get_relationships_to_from(
        self, relationship_type: str, from_entity
    ) -> List[Relationship]:
        result = []
        for rel in self.__relationships["to"][relationship_type]:
            if rel.ref_from.identifier == from_entity.identifier:
                result.append(rel)

        return result

    def set_relationships_from(
        self, relationship_type: str, relationships: List[Relationship]
    ) -> None:
        self.__relationships["from"][relationship_type] = relationships

    def set_relationships_to(
        self, relationship_type: str, relationships: List[Relationship]
    ) -> None:
        self.__relationships["to"][relationship_type] = relationships
