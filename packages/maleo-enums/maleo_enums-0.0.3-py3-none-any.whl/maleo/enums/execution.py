from enum import StrEnum


class ApplicationExecution(StrEnum):
    CONTAINER = "container"
    DIRECT = "direct"


class FunctionExecution(StrEnum):
    ASYNC = "async"
    SYNC = "sync"
