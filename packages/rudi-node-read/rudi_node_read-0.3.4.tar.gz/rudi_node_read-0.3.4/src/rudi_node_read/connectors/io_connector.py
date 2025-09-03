from http.client import HTTPSConnection, HTTPConnection
from json import dumps, loads, JSONDecodeError
from typing import Literal, get_args
from urllib.parse import urlsplit

from rudi_node_read.utils.err import HttpError, LiteralUnexpectedValueException
from rudi_node_read.utils.log import log_d_if, log_e, log_d
from rudi_node_read.utils.serializable import Serializable
from rudi_node_read.utils.type_string import slash_join

HttpRequestMethod = Literal["GET", "PUT", "DEL", "POST"]
HTTP_REQUEST_METHODS = get_args(HttpRequestMethod)

STATUS = "status"
REDIRECTION = "redirection"


def https_download(resource_url: str, should_show_debug_line: bool = False):
    here = "https_download"
    (scheme, netloc, path, query, fragment) = urlsplit(resource_url)
    if scheme != "https":
        raise NotImplementedError("only HTTPS protocol is supported")
    connection = HTTPSConnection(netloc)
    connection.request(method="GET", url=resource_url)
    response = connection.getresponse()
    if response.status != 200:
        log_e(here, f"ERR {response.status}", resource_url)
        return None
    else:
        log_d_if(should_show_debug_line, here, f"OK {response.status}", resource_url)
        data = response.read()
        # log_d('https_download', 'data', data)
        connection.close()
        return data


class Connector(Serializable):
    _default_connector = None

    def __init__(self, server_url: str):
        self.scheme = None
        self.host = None
        self.path = None
        self.base_url = None
        self._set_url(server_url)

    def _set_url(self, server_url: str):
        (scheme, netloc, path, query, fragment) = urlsplit(server_url)
        if scheme != "http" and scheme != "https":
            raise NotImplementedError("only http and https are supported")
        self.scheme = scheme
        self.host = netloc
        self.path = path
        self.base_url = slash_join(f"{self.scheme}://{self.host}", self.path)
        log_d("Connector", "base_url", self.base_url)

    def full_url(self, url: str = "/"):
        return slash_join(self.base_url, url)

    def full_path(self, url: str = "/"):
        return slash_join("/", self.path, url)

    def request(
        self,
        url: str = "/",
        req_method: HttpRequestMethod = "GET",
        body: dict = None,
        headers: dict = None,
        should_log_response: bool = False,
    ) -> (str, dict):
        """Send a http(obj) request"""

        connection = HTTPSConnection(self.host) if self.scheme == "https" else HTTPConnection(self.host)
        if req_method not in HTTP_REQUEST_METHODS:
            raise LiteralUnexpectedValueException(req_method, HTTP_REQUEST_METHODS, "incorrect type for request method")

        if not headers:
            headers = {"Content-Type": "text/plain", "Accept": "application/json"}
        if body and isinstance(body, dict):
            headers["Content-type"] = "application/json"
            body = dumps(body)

        path_url = self.full_path(url)
        log_d(f"{self.__class__.__name__}.request", "to", self.full_url(url))
        try:
            connection.request(req_method, path_url, body, headers)
        except ConnectionRefusedError as e:
            log_e(
                self.__class__.__name__,
                "Error on request",
                req_method,
                self.full_url(url),
            )
            log_e(self.__class__.__name__, "ERR", e)
            raise e
        return self.parse_response(connection, url, req_method, headers, body, should_log_response)

    def parse_response(
        self,
        connection: HTTPConnection,
        url: str,
        req_method: HttpRequestMethod,
        headers: dict,
        body: dict,
        should_log_response: bool = True,
    ):
        """Basic parsing of the result"""
        here = f"{self.__class__.__name__}.parse_response"
        response = connection.getresponse()
        # log_d(here, "Response", response.getcode(), response.getheaders(), response.info())
        if response.status in [301, 302, 307, 308]:
            res = {STATUS: response.status, REDIRECTION: response.getheader("location")}
            log_d_if(should_log_response, here, "A redirection occurs")
            return res
        if (
            response.status not in [200, 500, 501]
            and not (530 <= response.status < 540)
            and not (400 <= response.status < 500)
        ):
            return None

        rdata = response.read()
        try:
            response_data = loads(rdata)
            log_d_if(should_log_response, here, "Response is a JSON", response_data)
        except (TypeError, JSONDecodeError):
            response_data = repr(rdata)
            log_d_if(should_log_response, here, "Response is not a JSON", response_data)
        connection.close()
        if type(response_data) is str:
            log_d_if(should_log_response, here, "Response is a string", response_data)
            if response.status == 200:
                return rdata.decode("utf8")
        if response.status == 200:
            return response_data
        if response.status >= 400:
            log_e(here, "Connection error", response_data)
            log_e(here, "Request in error", req_method, self.full_url(url))
            raise HttpError(response_data, req_method, self.base_url, url)
