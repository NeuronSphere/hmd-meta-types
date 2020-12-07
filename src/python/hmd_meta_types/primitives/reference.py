class Reference:
    def __init__(self, class_name: str, is_list: bool = False):
        self.class_name = class_name
        self.is_list = is_list

    def __get__(self, obj, owner=None):
        value = getattr(obj, self.private_name, None)
        if self.is_list and value is None:
            return []
        elif self.is_list:
            return [{"id": value, "reference": self.class_name}]
        return {"id": value, "reference": self.class_name}

    def __set__(self, obj, value):
        setattr(obj, self.private_name, value)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"__{name}"

    def set_value(self, obj, value):
        self.__set__(obj, value)
