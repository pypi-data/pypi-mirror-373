from enum import StrEnum


class CacheOrigin(StrEnum):
    CLIENT = "client"
    SERVICE = "service"


class CacheLayer(StrEnum):
    REPOSITORY = "repository"
    SERVICE = "service"
    CONTROLLER = "controller"
