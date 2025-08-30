import logging
from enum import IntEnum, StrEnum


class LoggerType(StrEnum):
    APPLICATION = "application"
    CACHE = "cache"
    CLIENT = "client"
    CONTROLLER = "controller"
    DATABASE = "database"
    MIDDLEWARE = "middleware"
    REPOSITORY = "repository"
    SERVICE = "service"


class LogLevel(IntEnum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET
