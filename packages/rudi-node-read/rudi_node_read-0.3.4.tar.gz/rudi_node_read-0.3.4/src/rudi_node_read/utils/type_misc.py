def get_type_name(obj):
    return type(obj).__name__


def is_type(obj, type_name: str):
    return get_type_name(obj) == type_name


def is_list(obj):
    return isinstance(obj, list)


def is_array(obj):
    return isinstance(obj, list)


def is_list_or_dict(obj):
    return isinstance(obj, (list, dict))


def check_type(obj, type_name: str, param_name: str | None = None):
    param_str = "Parameter" if param_name is None else f"Parameter '{param_name}'"
    if not is_type(obj, type_name):
        raise TypeError(f"{param_str} should be a '{type_name}', got '{get_type_name(obj)}'")


def to_float(val):
    try:
        f_val = float(val)
    except (TypeError, ValueError):
        raise ValueError(f"could not convert value into a float: '{val}'")
    return f_val
