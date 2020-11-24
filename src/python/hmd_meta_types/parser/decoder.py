import json

from hmd_meta_types.metatypes import Noun


METATYPES = {"noun": Noun}


class DefinitionDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs) -> None:
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "name" not in obj:
            return obj

        name = obj["name"]

        if "metatype" not in obj:
            return obj

        metatype = METATYPES.get(obj["metatype"], None)

        if metatype is None:
            raise json.JSONDecodeError(f"Invalid metatype {metatype} in definition.")

        return type(name, (metatype,), {}, definition=obj)
