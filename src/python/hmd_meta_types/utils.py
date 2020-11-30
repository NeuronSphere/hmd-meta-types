import json


def snake_to_pascal(name: str) -> str:
    names = name.split("_")
    return "".join([n.capitalize() for n in names])


def load_definition(definition: str):
    return json.loads(definition)


def load_definition_file(definition):
    return json.load(definition)
