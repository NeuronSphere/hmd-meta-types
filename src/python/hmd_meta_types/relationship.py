from typing import Type
from abc import abstractmethod

from .entity import Entity
from .noun import Noun


class Relationship(Entity):
    def __init__(self, from_ref: Noun, to_ref: Noun, **kwargs):
        self._from_ref = from_ref
        self._to_ref = to_ref
        super().__init__(**kwargs)

    @property
    @abstractmethod
    def from_ref_type(self):
        pass

    @property
    @abstractmethod
    def to_ref_type(self):
        pass

    @property
    def from_ref(self):
        return self._from_ref

    @from_ref.setter
    def from_ref(self, value):
        if not isinstance(value, self.from_ref_type):
            raise Exception(
                f"From reference must be of type {self.from_ref_type.__name__}."
            )
        self._from_ref = value

    @property
    def to_ref(self):
        return self._to_ref

    @to_ref.setter
    def to_ref(self, value):
        if not isinstance(value, self.to_ref_type):
            raise Exception(
                f"To reference must be of type {self.to_ref_type.__name__}."
            )
        self._from_ref = value
