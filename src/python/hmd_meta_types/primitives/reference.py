class Reference:
    def __init__(self, class_name: str):
        self.class_name = class_name

    def __get__(self, obj, owner=None):
        value = getattr(obj, self.private_name, None)
        return {"id": value, "reference": self.class_name}

    def __set__(self, obj, value):
        setattr(obj, self.private_name, value)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"__{name}"
