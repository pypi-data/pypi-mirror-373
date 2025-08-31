from enum import StrEnum


class Service(StrEnum):
    REST = "rest"
    MESSAGE = "message"


class Client(StrEnum):
    HTTP = "http"
