from typing import Callable, Any


class Operation:
    def __init__(self, name: str, fn: Callable = None) -> None:
        self.name = name
        self.fn = fn

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.fn(*args, **kwds)
