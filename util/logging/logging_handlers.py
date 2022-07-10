import abc
import dataclasses
import sys
from datetime import datetime as dt

from .log_level import LogLevelEnum, LogLevel


class ColourMap:
    END: str = '\x1b[0m'
    OK_BLUE: str = '\033[94m'
    OK_CYAN: str = '\033[96m'
    OK_GREEN: str = '\033[92m'
    WARNING: str = '\033[93m'
    FAIL: str = '\033[91m'


@dataclasses.dataclass
class Message:
    timestamp: dt
    level: LogLevel
    msg: str


class BaseHandler(metaclass=abc.ABCMeta):
    time_fmt: str
    date_fmt: str
    dt_fmt: str

    def __init__(self, time_fmt: str = None, date_fmt: str = None, dt_fmt: str = None):
        self.set_formats(time_fmt, date_fmt, dt_fmt)

    def set_formats(self, time_fmt: str = None, date_fmt: str = None, dt_fmt: str = None):
        self.time_fmt: str = time_fmt
        self.date_fmt: str = date_fmt
        self.dt_fmt: str = dt_fmt

    @abc.abstractmethod
    def write(self, message: Message, *args, **kwargs):
        raise NotImplemented


class StdoutHandler(BaseHandler):

    def __init__(self, time_fmt: str, date_fmt: str, dt_fmt: str):
        super().__init__(time_fmt, date_fmt, dt_fmt)

    def write(self, message: Message, *args, **kwargs):
        print(self._format(message), *args, **kwargs)

    @staticmethod
    def _colour(s: str, colour: str) -> str:
        if sys.platform not in {'linux', 'cygwin', 'darwin'}:
            return s
        return f"{colour}{s}{ColourMap.END}"

    def _format(self, message: Message) -> str:

        s_ = f"[{message.timestamp.strftime(self.time_fmt)}][{message.level}] {message.msg}"

        match message.level:
            case LogLevelEnum.DEBUG:
                return self._colour(s_, ColourMap.END)
            case LogLevelEnum.INFO:
                return self._colour(s_, ColourMap.OK_GREEN)
            case LogLevelEnum.WARNING:
                return self._colour(s_, ColourMap.WARNING)
            case LogLevelEnum.ERROR:
                return self._colour(s_, ColourMap.FAIL)
        return self._colour(s_, ColourMap.OK_CYAN)
