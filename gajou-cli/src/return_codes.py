from enum import Enum


class ReturnCodes(Enum):
    OK = 0
    ERROR = 1
    FATAL = 2
    DOCKER_ERROR = 125
