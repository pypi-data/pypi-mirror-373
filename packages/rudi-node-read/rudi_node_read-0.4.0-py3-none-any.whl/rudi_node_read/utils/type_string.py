from os.path import abspath, join
from re import compile
from uuid import UUID, uuid4

from rudi_node_read.utils.typing_utils import get_type_name


def is_string(s) -> bool:
    return isinstance(s, str) or issubclass(type(s), str)


def check_is_string(s: str) -> str:
    if not isinstance(s, str):
        raise TypeError(f"input object should be a string, got '{get_type_name(s)}'")
    return s


def check_is_string_or_none(s: str | None) -> str | None:
    if s is None:
        return None
    return check_is_string(s)


ISO_FULL_DATE_REGEX = compile(
    r"^([+-]?[1-9]\d{3})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12]\d)T(2[0-3]|[01]\d):([0-5]\d):([0-5]\d)(?:\.(\d{3}))?("
    r"?:Z|[+-](?:1[0-2]|0\d):[03]0)$"
)


def is_iso_full_date(date_str) -> bool:
    return bool(ISO_FULL_DATE_REGEX.match(date_str))


REGEX_EMAIL = compile(
    r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
)


def is_email(email_str: str):
    return isinstance(email_str, str) and bool(REGEX_EMAIL.match(email_str))


def check_is_email(email_str: str) -> str:
    if email_str is None:
        raise ValueError("a valid email should be provided")
    if not is_email(email_str):
        raise ValueError(f"this is not a valid email: '{email_str}'")
    return email_str


# REGEX_UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')


def uuid4_str() -> str:
    return str(uuid4())


def is_uuid_v4(uuid: str) -> bool:
    if uuid is None:
        return False
    try:
        uuid_v4 = UUID(str(uuid))
        if uuid_v4.version == 4:
            return True
        else:
            return False
    except ValueError:
        return False


def check_is_uuid4(uuid: str | UUID) -> str:
    if uuid is None:
        raise ValueError("Input parameter should not be null")
    try:
        uuid_v4 = UUID(str(uuid))
        if uuid_v4.version == 4:
            return str(uuid_v4)
    except ValueError:
        pass
    raise ValueError(f"Input parameter is not a valid UUID v4: '{uuid}'")


def absolute_path(*args) -> str:
    return abspath(join(*args))


def slash_join(*args) -> str:
    """
    Joins a set of strings with a slash (/) between them (useful for merging URLs or paths fragments)
    """
    non_null_args = []
    for frag in args:
        if frag is None or frag == "":
            pass
        elif not is_string(frag):
            raise AttributeError("input parameters must be strings")
        else:
            non_null_args.append(frag.strip("/"))
    joined_str = "/".join(non_null_args)
    return joined_str
