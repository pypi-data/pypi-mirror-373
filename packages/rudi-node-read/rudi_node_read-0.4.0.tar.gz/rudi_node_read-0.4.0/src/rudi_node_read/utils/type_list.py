from deepdiff import DeepDiff

from rudi_node_read.utils.typing_utils import get_type_name


def is_iterable(o) -> bool:
    return hasattr(o, "__iter__")


def check_is_list(list_val: str | list) -> list:
    if isinstance(list_val, list):
        return list_val
    raise TypeError(f"input should be a list, got '{get_type_name(list_val)}'")


def check_is_list_or_none(list_val: str | list | None) -> list | None:
    if list_val is None:
        return None
    return check_is_list(list_val=list_val)


def ensure_is_str_list(list_val: str | list[str]):
    if isinstance(list_val, str):
        list_val = list_val.split(",")
    if not isinstance(list_val, list):
        raise TypeError(f"input should be a list, got '{get_type_name(list_val)}'")
    return [val.strip() for val in list_val]


def get_first_list_elt_or_none(elt_list):
    if not elt_list or not isinstance(elt_list, list) or len(elt_list) == 0:
        return None
    return elt_list[0]


def list_diff(list_a: list, list_b: list):
    return [x for x in list_a + list_b if x not in list_a or x not in list_b]


def list_deep_diff(list_a: list, list_b: list, ignore_order: bool = True):
    return DeepDiff(list_a, list_b, ignore_order=ignore_order)


def are_list_different(list_a: list | None, list_b: list | None, ignore_order: bool = True) -> bool:
    """
    Compare two lists (with deep equality on each element of the list)
    :param list_a: a list
    :param list_b: another list
    :param ignore_order: True if list order should be ignored in the comparison. If True, [5,'a'] == ['a',5]
    :return: True if the lists are different
    """
    check_is_list_or_none(list_a)
    check_is_list_or_none(list_b)
    if list_a is None:
        return list_b is not None
    if list_b is None:
        return True
    return bool(list_deep_diff(list_a, list_b, ignore_order=ignore_order))


def are_list_equal(list_a: list | None, list_b: list | None, ignore_order: bool = True):
    return not are_list_different(list_a, list_b, ignore_order)


def merge_lists(list_a: list | None, list_b: list | None):
    if list_b is None:
        return list_a
    if list_a is None:
        return list_b
    if isinstance(list_a, list) and isinstance(list_b, list):
        return list_a + list_b
    if isinstance(list_a, list):
        return list_a + [list_b]
    if isinstance(list_b, list):
        return [list_a] + list_b


def clean_nones(value):
    """
    Recursively remove all None values from dictionaries and lists, and returns
    the result as a new dictionary or list.
    https://stackoverflow.com/a/60124334/1563072
    """
    if isinstance(value, list):
        return [clean_nones(x) for x in value if x is not None]
    elif isinstance(value, dict):
        return {key: clean_nones(val) for key, val in value.items() if val is not None}
    else:
        return value


if __name__ == "__main__":  # pragma: no cover
    tests = "tests"
    a = [1, 2, 3, 4, 5]
    b = [9, 8, 7, 6, {"r": [5, 6]}]
    c = [8, 7, 6, {"r": [5, 6]}, 9]
    print(tests, f"{a} Δ {b}", list_diff(a, b))
    print(tests, f"{a} Δ {c}", list_diff(a, c))
    print(tests, f"{b} Δ {c}", list_diff(b, c))
    print(tests, "b == c", are_list_equal(b, c))
    print(tests, f"{b} == {c} ->", are_list_equal(b, c))
    print(tests, "dict eq ->", {"r": [6, 5]} != {"r": [5, 6]})
