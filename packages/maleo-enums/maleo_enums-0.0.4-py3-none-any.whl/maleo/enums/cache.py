from enum import StrEnum


class Origin(StrEnum):
    CLIENT = "client"
    SERVICE = "service"


class Layer(StrEnum):
    REPOSITORY = "repository"
    SERVICE = "service"
    CONTROLLER = "controller"
