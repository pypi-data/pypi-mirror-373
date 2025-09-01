import json
import os

try:
    import yaml
except ImportError:
    yaml = None


class ConfigLoader:
    """
    Load configuration files (YAML/JSON).
    """

    def __init__(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Config file not found: {filepath}")
        self.filepath = filepath
        self.config = self._load()

    def _load(self):
        if self.filepath.endswith(".yaml") or self.filepath.endswith(".yml"):
            if not yaml:
                raise ImportError("pyyaml is required for YAML configs")
            with open(self.filepath, "r") as f:
                return yaml.safe_load(f)
        elif self.filepath.endswith(".json"):
            with open(self.filepath, "r") as f:
                return json.load(f)
        else:
            raise ValueError("Unsupported config file format")

    def get(self, key, default=None):
        """
        Get nested config values using dot notation.
        """
        parts = key.split(".")
        value = self.config
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, default)
            else:
                return default
        return value
