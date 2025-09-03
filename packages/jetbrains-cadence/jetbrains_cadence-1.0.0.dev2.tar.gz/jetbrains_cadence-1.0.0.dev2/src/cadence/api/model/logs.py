from abc import abstractmethod, ABC
from enum import Enum

from pydantic import BaseModel


class LogType(Enum):
    UNKNOWN = "UNKNOWN"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class Log(BaseModel):
    text: str
    type: LogType


class ExecutionLogs(BaseModel):
    offset: int
    count: int
    logs: list[Log]


class LogStream(ABC):
    @abstractmethod
    def read_next_log(self) -> Log | None:
        pass
