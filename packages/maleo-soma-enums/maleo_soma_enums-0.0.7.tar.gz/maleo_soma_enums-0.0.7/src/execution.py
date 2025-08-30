from enum import StrEnum


class ApplicationExecution(StrEnum):
    DIRECT = "direct"
    CONTAINER = "container"


class Execution(StrEnum):
    SYNC = "sync"
    ASYNC = "async"
