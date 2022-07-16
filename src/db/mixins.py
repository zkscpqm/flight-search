from typing import Any


class FormattingMixin:

    @classmethod
    def format_value(cls, value: Any) -> str:
        if isinstance(value, str):
            return f"'{value}'"
        return str(value)
