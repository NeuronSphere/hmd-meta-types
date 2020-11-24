from functools import wraps

from hmd_meta_types.metatypes.extension import Extension


def extends(original_cls=None, type_name: str = None):
    def decorator(cls):
        cls_operations = []
        cls_dict = {}

        for key, item in vars(cls).items():
            if hasattr(item, "operation_name"):
                op_name = getattr(item, "operation_name")
                cls_dict[op_name] = item
                cls_operations.append(op_name)
            else:
                cls_dict[key] = item

        class NewExtension(Extension):
            class_dict = cls_dict
            extends = type_name if type_name else "."
            operations = cls_operations

        NewExtension.__name__ = cls.__name__

        return NewExtension

    if original_cls:
        return decorator(original_cls)

    return decorator


def operation(orig_fn=None, operation_name: str = None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        wrapper.operation_name = operation_name if operation_name else fn.__name__
        return wrapper

    if orig_fn:
        return decorator(orig_fn)

    print(operation_name)
    return decorator
