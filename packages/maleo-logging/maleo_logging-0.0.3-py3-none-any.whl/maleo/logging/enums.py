import logging
from enum import IntEnum, StrEnum


class Level(IntEnum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


class LoggerType(StrEnum):
    BASE = "base"
    APPLICATION = "application"
    CACHE = "cache"
    CLIENT = "client"
    CONTROLLER = "controller"
    DATABASE = "database"
    EXCEPTION = "exception"
    MIDDLEWARE = "middleware"
    REPOSITORY = "repository"
    SERVICE = "service"
