import abc
import dataclasses
import datetime
import sys
from datetime import datetime as dt
from pathlib import Path

from .log_level import LogLevelEnum, LogLevel
from ..types import nullable


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

    def _format(self, message: Message) -> str:
        return f"[{message.timestamp.strftime(self.time_fmt)}][{message.level}] {message.msg}"


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

        s_ = super()._format(message)

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


class FileHandler(BaseHandler):

    def __init__(self, out: Path, err_out: Path = None, time_fmt: str = None, date_fmt: str = None, dt_fmt: str = None):
        super().__init__(time_fmt, date_fmt, dt_fmt)
        out_file, err_out_file = self._resolve_paths(out, err_out)

        self.out: Path = out_file
        self.err_out: nullable(Path) = err_out_file

    def _resolve_paths(self, out: Path, err_out: Path = None) -> tuple[Path, Path]:

        def __resolve(path: Path, fallback_fname: str) -> nullable(Path):
            if path:
                if path.exists():
                    if path.is_dir():
                        path /= fallback_fname
                else:
                    if path.suffix:
                        path.parents[0].mkdir(parents=True, exist_ok=True)
                        path.touch()
                    else:
                        path.mkdir()
                        path /= fallback_fname
            else:
                return None
            return path

        return (
            __resolve(out, fallback_fname=f"{datetime.datetime.now().strftime(self.date_fmt)}-out.log"),
            __resolve(err_out, fallback_fname=f"{datetime.datetime.now().strftime(self.date_fmt)}-err_out.log")
        )

    def _format(self, message: Message) -> str:
        return super()._format(message) + '\n'

    def write(self, message: Message, *args, **kwargs):
        out__ = self._format(message)
        with open(self.out, 'a+') as h:
            h.write(out__)

        if message.level.level >= LogLevelEnum.ERROR.level and self.err_out is not None:
            with open(self.err_out, 'a+') as err_h:
                err_h.write(out__)
