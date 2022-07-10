import dataclasses


@dataclasses.dataclass
class LogLevel:
    level: int
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.level)


class LogLevelEnum:
    DEBUG:   LogLevel = LogLevel(-1, "DEBUG")
    INFO:    LogLevel = LogLevel(10, "INFO")
    WARNING: LogLevel = LogLevel(40, "WARN")
    ERROR:   LogLevel = LogLevel(99, "ERROR")
    NONE:    LogLevel = LogLevel(1 << 32, "")

    @classmethod
    def custom(cls, level: int, name: str, save: bool = False) -> LogLevel:
        lvl = LogLevel(level=level, name=name)
        if save:
            setattr(cls, name.upper(), lvl)
        return lvl

    @classmethod
    def by_name(cls, name: str) -> LogLevel:
        return getattr(cls, name.upper(), None)
