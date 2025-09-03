from base64 import urlsafe_b64decode, urlsafe_b64encode
from json import loads
from math import ceil
from time import time


def pad_b64_str(jwt_base64url: str):
    jwt_str_length = len(jwt_base64url)
    div, mod = divmod(jwt_str_length, 4)
    return jwt_base64url if mod == 0 else jwt_base64url.ljust(jwt_str_length + 4 - mod, "=")


def get_jwt_basic_auth(usr: str, pwd: str):
    token = urlsafe_b64encode(bytes(f"{usr}:{pwd}", "utf-8")).decode("ascii").replace("=", "")
    return f"Basic {pad_b64_str(token)}"


def is_jwt_expired(jwt_b64: str) -> bool:
    jwt_head_b64, jwt_body_b64, jwt_sign_b64 = jwt_b64.split(".")
    jwt_body_b64_pad = pad_b64_str(jwt_body_b64)
    jwt_str = urlsafe_b64decode(jwt_body_b64_pad).decode("utf-8")
    jwt_json = loads(jwt_str)
    exp = int(jwt_json["exp"])
    now_epoch_s = ceil(time())
    return exp < now_epoch_s
