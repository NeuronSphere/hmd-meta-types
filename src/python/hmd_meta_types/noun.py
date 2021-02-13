from .entity import Entity
from typing import List, Dict
from .relationship import Relationship
from collections import defaultdict


class Noun(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # relationships for which this is the "to" noun
        self.to_rels = defaultdict(list)  # type: Dict[str, List[Relationship]]
        # relationships for which this is the "from" noun
        self.from_rels = defaultdict(list)  # type: Dict[str, List[Relationship]]
