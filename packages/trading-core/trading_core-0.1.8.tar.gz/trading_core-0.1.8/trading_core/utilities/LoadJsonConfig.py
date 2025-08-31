import json
from pathlib import Path
from typing import Union, Dict, Any

class LoadJsonConfig:
    """
    Simple utility class to load config from JSON file or dict
    """

    def __init__(self, source: Union[str, Path, Dict[str, Any]] = "config.json"):
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {path}")

            with open(path, "r") as f:
                self._config = json.load(f)
            self._path = str(path)
        elif isinstance(source, dict):
            self._config = source
            self._path = "dict"
        else:
            raise ValueError("Config source must be a filepath or dict")

    def __getattr__(self, item):
        """Allow access like config.kafka"""
        value = self._config.get(item)
        if isinstance(value, dict):
            # wrap nested dicts for dot access
            return LoadJsonConfig(value)
        return value

    def __getitem__(self, key):
        """Allow access like config['kafka']"""
        return self._config[key]

    def dict(self):
        """Return raw dict"""
        return self._config

    def __repr__(self):
        return f"<LoadJsonConfig path={self._path}>"
