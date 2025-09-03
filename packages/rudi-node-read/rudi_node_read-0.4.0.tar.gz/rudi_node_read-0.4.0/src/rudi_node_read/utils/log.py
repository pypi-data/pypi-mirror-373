from datetime import datetime
from os import getenv
from time import time

SHOULD_LOG = bool(getenv("RUDI_NODE_DEV")) or bool(getenv("RNR_LOGS"))


def log(*args):
    if SHOULD_LOG:
        if len(args) < 2:
            print(f"D {now()}")
        elif len(args) == 2:
            print(f"{args[0]} {now()} [{args[1]}] <")
        elif len(args) == 3:
            print(f"{args[0]} {now()} [{args[1]}] {args[2]}")
        else:
            try:
                print(f"{args[0]} {now()} [{args[1]}] {args[2]}:", *args[3:])
            except UnicodeDecodeError:
                print(f"{args[0]} {now()} [{args[1]}] {args[2]}:", str(*args[3:]))


def log_e(*args):
    log("E", *args)


def log_i(*args):
    log("I", *args)


def log_d(*args):
    log("D", *args)


def log_d_if(should_print: bool, *args):
    if should_print:
        log_d(*args)


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def decorator_timer(some_function):
    def _wrap(*args, **kwargs):
        multiplier = 1
        begin = time()
        for count in range(multiplier):
            result = some_function(*args, **kwargs)
        duration = (time() - begin) / multiplier
        return result, duration

    return _wrap


def log_assert(cond: bool, ok_tag: str = "OK", ko_tag: str = "!! KO !!"):
    return ok_tag if cond else ko_tag
