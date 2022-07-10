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


_DEFAULT_LOGGER: nullable(Logger) = None


def set_default_logger(logger: Logger):
    global _DEFAULT_LOGGER
    _DEFAULT_LOGGER = logger


def get_logger(time_fmt: str, date_fmt: str, dt_fmt: str,
               level: LogLevel = None, extra_handlers: list[BaseHandler] = None, set_default: bool = True):
    extra_handlers = extra_handlers or []
    for h in extra_handlers:
        h.set_formats(time_fmt, date_fmt, dt_fmt)

    logger = Logger(
        handlers=[StdoutHandler(time_fmt, date_fmt, dt_fmt)] + extra_handlers,
        min_level=level
    )
    if set_default:
        set_default_logger(logger)
