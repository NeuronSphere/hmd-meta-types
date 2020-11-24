import json
from typing import Union

from hmd_meta_types.metatypes import Noun
from .decoder import DefinitionDecoder


def load_definition(definition: str) -> Union[Noun]:
    return json.loads(definition, cls=DefinitionDecoder)
