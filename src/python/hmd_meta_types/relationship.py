from abc import abstractmethod

from .entity import Entity
from .noun import Noun


class Relationship(Entity):
    def __init__(self, ref_from: Noun, ref_to: Noun, **kwargs):
        self._ref_from = ref_from
        self._ref_to = ref_to
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
        self._ref_from = value
