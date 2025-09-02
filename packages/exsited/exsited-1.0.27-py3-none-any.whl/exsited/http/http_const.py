from enum import Enum


class RequestType(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class HTTPConst:
    APPLICATION_JSON = "application/json"
    APPLICATION_PDF = "application/pdf"
    SUCCESS = "success"
    ERROR = "error"
    UTF8_ENCODING = "utf-8"
