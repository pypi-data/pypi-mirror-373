from enum import StrEnum


class ServiceController(StrEnum):
    REST = "rest"
    MESSAGE = "message"


class ClientController(StrEnum):
    HTTP = "http"
