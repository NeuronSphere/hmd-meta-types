import json

from hmd_meta_types.metatypes import Noun


METATYPES = {"noun": Noun}


class DefinitionDecoder(json.JSONDecoder):
    def __init__(self, extensions=[], *args, **kwargs) -> None:
        self.extensions = extensions
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "name" not in obj:
            return obj

        name = obj["name"]

        if "metatype" not in obj:
            return obj

        metatype = METATYPES.get(obj["metatype"], None)

        if metatype is None:
            raise Exception(f"Invalid metatype {obj['metatype']} in definition.")

        return type(name, (metatype,), {}, definition=obj, extensions=self.extensions)
