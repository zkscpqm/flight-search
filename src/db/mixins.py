from typing import Any


class FormattingMixin:

    @classmethod
    def format_value(cls, value: Any) -> str:
        if isinstance(value, str):
            if len(value) > 0 and not (value[0] == value[-1] == "'"):
                value = value.replace("'", "''")
            return f"'{value}'"
        return str(value)
