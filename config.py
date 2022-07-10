import json
from pathlib import Path
from typing import Any

from util.config_meta import BaseConfig


class Configuration(BaseConfig):

    def __init__(self, file: Path):
        with open(file) as f:
            config_map = json.load(f)
        self._conf_map: dict = config_map
        self._set_dynamic_config_properties(config_map)

    def _set_dynamic_config_properties(self, conf_map: dict) -> Any:

        def _set(k: str, _v: Any):
            if isinstance(_v, dict):
                for sub_k, sub_v in _v.items():
                    _set(f"{k}_{sub_k}", sub_v)
            else:
                setattr(self, k, _v)

        for key, v in conf_map.items():
            _set(key, v)

