from datetime import datetime as dt

from .logging_handlers import BaseHandler, Message, StdoutHandler
from .log_level import LogLevelEnum, LogLevel
from ..types import nullable


class Logger:

    def __init__(self, handlers: list[BaseHandler], min_level: LogLevel = LogLevelEnum.INFO):
        self.level: LogLevel = min_level
        self.handlers: list[BaseHandler] = handlers

    def _write(self, message: str, level: LogLevel, *args, **kwargs):
        if level.level < self.level.level:
            return

        message = Message(
            timestamp=dt.now(),
            level=level,
            msg=message
        )
        for handler in self.handlers:
            handler.write(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        self._write(message, LogLevelEnum.DEBUG, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self._write(message, LogLevelEnum.INFO, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self._write(message, LogLevelEnum.WARNING, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self._write(message, LogLevelEnum.ERROR, *args, **kwargs)


def get_logger(time_fmt: str, date_fmt: str, dt_fmt: str,
               level: LogLevel = LogLevelEnum.INFO, extra_handlers: list[BaseHandler] = None) -> Logger:
    extra_handlers = extra_handlers or []
    for h in extra_handlers:
        h.set_formats(time_fmt, date_fmt, dt_fmt)

    return Logger(
        handlers=[StdoutHandler(time_fmt, date_fmt, dt_fmt)] + extra_handlers,
        min_level=level
    )


_DEFAULT_LOGGER: Logger = get_logger(
    time_fmt="%H:%M:%S", date_fmt="%d-%m-%Y", dt_fmt="%d-%m-%Y_%H:%M:%S", level=LogLevelEnum.INFO
)


def set_default_logger(logger: Logger):
    global _DEFAULT_LOGGER
    _DEFAULT_LOGGER = logger


def get_default_logger() -> nullable(Logger):
    return _DEFAULT_LOGGER
