from rudi_node_read.utils.type_string import slash_join


class MissingEnvironmentVariableException(Exception):
    def __init__(self, var_name: str, var_use: str = ""):
        super().__init__(f"an environment variable should be defined {var_use}: {var_name}")


class IniMissingValueException(Exception):
    def __init__(self, ini_section: str, ini_subsection: str, err_msg: str):
        super().__init__(f"Missing value in INI config file for parameter {ini_section}.{ini_subsection}: {err_msg}")


class IniUnexpectedValueException(Exception):
    def __init__(self, ini_section: str, ini_subsection: str, err_msg: str):
        super().__init__(f"Unexpected value in INI config file for parameter {ini_section}.{ini_subsection}: {err_msg}")


class UnexpectedValueException(Exception):
    def __init__(self, param_name: str, expected_val, received_val):
        super().__init__(
            f"Unexpected value for parameter '{param_name}': expected '{expected_val}', got '{received_val}'"
        )


class LiteralUnexpectedValueException(Exception):
    def __init__(
        self,
        received_val,
        expected_literal: tuple,
        err_msg: str = "Unexpected value error",
    ):
        super().__init__(f"{err_msg}. Expected {expected_literal}, got '{received_val}'")


def rudi_api_http_error_to_string(status, err_type, err_msg):
    return f"ERR {status} {err_type}: {err_msg}"


class HttpError(Exception):
    def __init__(self, err_msg: str, req_method=None, base_url=None, url=None):
        err_msg = f"{err_msg}"
        if type(err_msg) is dict and "error" in err_msg and "message" in err_msg:
            if "status" in err_msg:
                err_msg = rudi_api_http_error_to_string(err_msg["status"], err_msg["error"], err_msg["message"])
            elif "statusCode" in err_msg:
                err_msg = rudi_api_http_error_to_string(err_msg["statusCode"], err_msg["error"], err_msg["message"])
        if req_method and base_url:
            err_msg = f"for request '{req_method} {slash_join(base_url, url)}' -> {err_msg}"
        super().__init__(f"HTTP ERR {err_msg}")
