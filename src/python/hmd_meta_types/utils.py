def snake_to_pascal(name: str) -> str:
    names = name.split("_")
    return "".join([n.capitalize() for n in names])
